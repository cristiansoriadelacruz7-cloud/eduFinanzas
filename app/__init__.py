"""
Inicialización de la aplicación Flask EduFinanzas.
Configura la aplicación, la base de datos SQLAlchemy y los blueprints (rutas).
"""

import os
import sys

# Permitir ejecutar este archivo directamente (python app/__init__.py)
# agregando la raíz del proyecto al path para que encuentre config.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, send_from_directory

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
    # Fallar rápido si la BD no responde (crítico en serverless)
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "connect_args": {"connect_timeout": 4},
        "pool_pre_ping": True,
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
                _tablas_listas["ok"] = True
            except Exception as exc:  # noqa: BLE001
                print(f"[AVISO] BD aún no disponible: {exc}")


    # ---------- Servir el frontend estático (mismo origen que /api) ----------
    @app.route('/')
    def raiz():
        # La página de entrada es el login
        return send_from_directory(os.path.join(FRONTEND_DIR, 'pages'), 'login.html')

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
