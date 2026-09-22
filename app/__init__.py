"""
Inicialización de la aplicación Flask EduFinanzas.
Configura la aplicación, la base de datos SQLAlchemy y los blueprints (rutas).
"""

import os
import sys

# Permitir ejecutar este archivo directamente (python app/__init__.py)
# agregando la raíz del proyecto al path para que encuentre config.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, redirect, request, send_from_directory
from werkzeug.exceptions import HTTPException

from app.extensions import db

# Carpeta del frontend estático
FRONTEND_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend'
)


def create_app():
    """Factory: crea y configura la aplicación Flask."""
    app = Flask(__name__)

    # Configuración
    from config import SQLALCHEMY_DATABASE_URI, SECRET_KEY, DEBUG
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # Fallar rápido y reciclar conexiones (crítico en serverless con MySQL compartido)
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "connect_args": {"connect_timeout": 4},
        "pool_pre_ping": True,
        "pool_size": 2,
        "max_overflow": 0,
        "pool_recycle": 240,
    }
    if DEBUG:
        app.config["TEMPLATES_AUTO_RELOAD"] = True

    # Inicializar extensiones
    db.init_app(app)

    # Registrar blueprints (rutas API)
    from app.routes.auth_routes import auth_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.ingreso_routes import ingreso_bp
    from app.routes.gasto_routes import gasto_bp
    from app.routes.ahorro_routes import ahorro_bp
    from app.routes.reporte_routes import reporte_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(ingreso_bp)
    app.register_blueprint(gasto_bp)
    app.register_blueprint(ahorro_bp)
    app.register_blueprint(reporte_bp)

    # ---------- Creación de tablas diferida ----------
    # En serverless NO se debe tocar la BD durante el arranque de la función:
    # se hace una sola vez, en la primera petición real, y sin bloquear si falla.
    _tablas_listas = {"ok": False}

    @app.before_request
    def _asegurar_tablas():
        if _tablas_listas["ok"]:
            return
        with app.app_context():
            try:
                db.create_all()
                # Migración ligera: tablas ya existentes no ganan columnas
                # nuevas con create_all, así que se agregan si faltan
                # (necesario para el Login con Google en BD ya creadas).
                try:
                    from sqlalchemy import text as _text
                    with db.engine.connect() as _con:
                        for _sql in (
                            "ALTER TABLE usuarios ADD COLUMN google_id VARCHAR(255) NULL",
                            "ALTER TABLE usuarios ADD COLUMN avatar_url VARCHAR(500) NULL",
                            "ALTER TABLE usuarios MODIFY COLUMN contrasena_hash VARCHAR(255) NULL",
                        ):
                            try:
                                _con.execute(_text(_sql))
                                _con.commit()
                            except Exception:
                                _con.rollback()  # la columna ya existe: seguir
                        try:
                            _con.execute(_text(
                                "CREATE UNIQUE INDEX uq_usuarios_google "
                                "ON usuarios (google_id)"
                            ))
                            _con.commit()
                        except Exception:
                            _con.rollback()  # índice ya existe o MySQL lo omite: seguir
                except Exception as _e:  # noqa: BLE001
                    print(f"[AVISO] Migración Google omitida: {_e}")
                _tablas_listas["ok"] = True
            except Exception as exc:  # noqa: BLE001
                print(f"[AVISO] BD aún no disponible: {exc}")


    # ---------- Diagnóstico: errores visibles en respuesta y logs ----------
    @app.errorhandler(Exception)
    def _error_interno(exc):
        import traceback
        traceback.print_exc()  # queda en los Runtime Logs de Vercel
        if isinstance(exc, HTTPException):
            return jsonify({'ok': False, 'error': exc.description}), exc.code
        detalle = f"{type(exc).__name__}: {exc}"[:300]
        return jsonify({'ok': False, 'error': 'ERROR_INTERNO_SERVIDOR', 'detalle': detalle}), 500

    # ---------- Favicon (evita el 404 en consola) ----------
    @app.route('/favicon.ico')
    def favicon():
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
               '<text y="19" font-size="19">💰</text></svg>')
        return app.response_class(svg, mimetype='image/svg+xml')

    # ---------- Diagnóstico de base de datos (temporal para depurar) ----------
    @app.route('/api/diagnostico')
    def diagnostico():
        if request.args.get('clave') != 'edu2026':
            return jsonify({'ok': False, 'error': 'clave_requerida'}), 403

        import sqlalchemy
        from sqlalchemy import create_engine, text
        from sqlalchemy.engine import make_url
        from config import SQLALCHEMY_DATABASE_URI as uri

        u = make_url(uri)
        info = {
            'python': sys.version.split()[0],
            'sqlalchemy': sqlalchemy.__version__,
            'driver': u.drivername,
            'host': u.host,
            'puerto': u.port,
            'base_datos': u.database,
            'password_recibida': bool(u.password),
            'variables_entorno': {
                'DATABASE_URL_definida': bool(os.getenv('DATABASE_URL')),
                'DB_HOST': os.getenv('DB_HOST'),
                'DB_USER': os.getenv('DB_USER'),
                'DB_NAME': os.getenv('DB_NAME'),
                'DB_PASSWORD_definida': bool(os.getenv('DB_PASSWORD')),
                'FLASK_DEBUG': os.getenv('FLASK_DEBUG'),
            },
        }
        try:
            motor = create_engine(uri, connect_args={'connect_timeout': 5})
            with motor.connect() as con:
                con.execute(text('SELECT 1'))
            info['conexion'] = 'OK - la app SÍ llega a la base de datos'
        except Exception as exc:  # noqa: BLE001
            info['conexion'] = f"FALLO -> {type(exc).__name__}: {exc}"
        return jsonify({'ok': True, **info})

    # ---------- Servir el frontend estático (mismo origen que /api) ----------
    @app.route('/')
    def raiz():
        # Redirigir a la ruta real del login: así los enlaces relativos
        # (dashboard.html, registro.html...) resuelven siempre bien
        return redirect('/pages/login.html')

    @app.route('/pages/<path:ruta>')
    def servir_paginas(ruta):
        return send_from_directory(os.path.join(FRONTEND_DIR, 'pages'), ruta)

    @app.route('/css/<path:ruta>')
    def servir_css(ruta):
        return send_from_directory(os.path.join(FRONTEND_DIR, 'css'), ruta)

    @app.route('/js/<path:ruta>')
    def servir_js(ruta):
        return send_from_directory(os.path.join(FRONTEND_DIR, 'js'), ruta)

    @app.route('/assets/<path:ruta>')
    def servir_assets(ruta):
        return send_from_directory(os.path.join(FRONTEND_DIR, 'assets'), ruta)

    # ---------- SEO: archivos para motores de búsqueda ----------
    @app.route('/robots.txt')
    def robots_txt():
        return send_from_directory(FRONTEND_DIR, 'robots.txt')

    @app.route('/sitemap.xml')
    def sitemap_xml():
        respuesta = send_from_directory(FRONTEND_DIR, 'sitemap.xml')
        respuesta.headers['Content-Type'] = 'application/xml'
        return respuesta

    return app


# Instancia WSGI global (la consumen wsgi.py, api/index.py y gunicorn).
# Ya NO toca la base de datos durante el import: eso se hace en la
# primera petición vía _asegurar_tablas().
app = create_app()


if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 5000))
    app_local = create_app()
    with app_local.app_context():
        from app.models.db import Usuario, Categoria, Ingreso, Gasto, MetaAhorro  # noqa: F401
        db.create_all()
        print("[OK] Base de datos conectada correctamente")
        print(f"[DB] URI: {app_local.config['SQLALCHEMY_DATABASE_URI']}")
    app_local.run(debug=True, port=puerto)
