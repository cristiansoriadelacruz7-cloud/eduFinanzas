"""Rutas de autenticación: registro, login, logout y sesión actual."""

from flask import Blueprint, request, jsonify, session

from app.extensions import db
from app.models.db import Usuario

auth_bp = Blueprint('auth', __name__)


@auth_bp.post('/api/registro')
def registro():
    datos = request.get_json(silent=True) or {}
    nombre = (datos.get('nombre') or '').strip()
    correo = (datos.get('correo') or '').strip().lower()
    contrasena = datos.get('contrasena') or ''

    if not nombre or not correo or not contrasena:
        return jsonify({'ok': False, 'error': 'Faltan campos obligatorios'}), 400
    if len(contrasena) < 6:
        return jsonify({'ok': False, 'error': 'La contraseña debe tener al menos 6 caracteres'}), 400

    if Usuario.query.filter_by(correo=correo).first():
        return jsonify({'ok': False, 'error': 'correo_duplicado'}), 409

    usuario = Usuario(nombre=nombre, correo=correo)
    usuario.set_password(contrasena)
    db.session.add(usuario)
    db.session.commit()

    session['usuario_id'] = usuario.id
    return jsonify({'ok': True, 'usuario': usuario.a_dict()}), 201


@auth_bp.post('/api/login')
def login():
    datos = request.get_json(silent=True) or {}
    correo = (datos.get('correo') or '').strip().lower()
    contrasena = datos.get('contrasena') or ''

    usuario = Usuario.query.filter_by(correo=correo).first()
    if not usuario:
        return jsonify({'ok': False, 'error': 'credenciales_invalidas'}), 401

    # Verifica hash normal; acepta texto plano solo en cuentas de prueba antiguas
    ok = False
    try:
        ok = usuario.check_password(contrasena)
    except Exception:
        ok = False
    if not ok and usuario.contrasena_hash and usuario.contrasena_hash == contrasena:
        ok = True

    if not ok:
        return jsonify({'ok': False, 'error': 'credenciales_invalidas'}), 401

    session['usuario_id'] = usuario.id
    return jsonify({'ok': True, 'usuario': usuario.a_dict()})


@auth_bp.post('/api/logout')
def logout():
    session.pop('usuario_id', None)
    return jsonify({'ok': True})


@auth_bp.post('/api/seed')
def seed():
    """Crea/repara cuentas de prueba con contrasenas hasheadas (solo desarrollo)."""
    pruebas = [
        ('Antony Demo', 'demo@edufinanzas.pe', '123456'),
        ('Maria Gomez', 'maria@edufinanzas.pe', '123456'),
        ('Carlos Ruiz', 'carlos@edufinanzas.pe', '123456'),
        ('Laura Patel', 'laura@edufinanzas.pe', '123456'),
    ]
    creados = []
    reparados = []
    for nombre, correo, clave in pruebas:
        u = Usuario.query.filter_by(correo=correo).first()
        if not u:
            u = Usuario(nombre=nombre, correo=correo)
            u.set_password(clave)
            db.session.add(u)
            creados.append(correo)
            continue
        # Reparar contrasenas de prueba que no validan con el hash actual
        try:
            valida = u.check_password(clave)
        except Exception:
            valida = False
        if not valida:
            u.set_password(clave)
            reparados.append(correo)
    if creados or reparados:
        db.session.commit()
    return jsonify({'ok': True, 'creados': creados, 'reparados': reparados})


@auth_bp.get('/api/sesion')
def sesion_actual():
    uid = session.get('usuario_id')
    if not uid:
        return jsonify({'ok': False, 'error': 'sin_sesion'}), 401
    usuario = Usuario.query.get(uid)
    if not usuario:
        return jsonify({'ok': False, 'error': 'sin_sesion'}), 401
    return jsonify({'ok': True, 'usuario': usuario.a_dict()})


# ---------- Login con Google (Google Identity Services) ----------
@auth_bp.get('/api/auth/google/config')
def google_config():
    """Expone el CLIENT ID al frontend (no es secreto)."""
    import os
    cid = os.getenv("GOOGLE_CLIENT_ID", "")
    try:
        from config import GOOGLE_CLIENT_ID as _cid
        cid = _cid or cid
    except Exception:
        pass
    return jsonify({'ok': True, 'clientId': cid, 'configurado': bool(cid)})


@auth_bp.post('/api/auth/google')
def login_google():
    """Recibe el ID token de Google (credential), lo verifica y crea/vincula al usuario."""
    import os
    datos = request.get_json(silent=True) or {}
    token = (datos.get('credential') or datos.get('id_token') or '').strip()
    if not token:
        return jsonify({'ok': False, 'error': 'credential_requerido'}), 400

    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    try:
        from config import GOOGLE_CLIENT_ID as _cid
        client_id = _cid or client_id
    except Exception:
        pass
    if not client_id:
        return jsonify({'ok': False, 'error': 'google_no_configurado'}), 500

    # Verificar el token contra Google
    info = None
    try:
        from google.oauth2 import id_token as google_id_token
        from google.auth.transport import requests as google_requests
        info = google_id_token.verify_oauth2_token(
            token, google_requests.Request(), client_id
        )
    except ImportError:
        # Fallback sin librería: endpoint tokeninfo (solo desarrollo)
        try:
            import urllib.request, json as _json
            url = 'https://oauth2.googleapis.com/tokeninfo?id_token=' + token
            with urllib.request.urlopen(url, timeout=8) as resp:
                info = _json.loads(resp.read().decode())
        except Exception:
            return jsonify({'ok': False, 'error': 'token_invalido'}), 401
    except Exception:
        return jsonify({'ok': False, 'error': 'token_invalido'}), 401

    if not info or info.get('aud') != client_id:
        return jsonify({'ok': False, 'error': 'token_invalido'}), 401
    if not info.get('email_verified'):
        return jsonify({'ok': False, 'error': 'email_no_verificado'}), 401

    correo = (info.get('email') or '').strip().lower()
    google_sub = info.get('sub') or ''
    nombre = (info.get('name') or correo.split('@')[0] or 'Usuario').strip()
    avatar = info.get('picture') or None
    if not correo or not google_sub:
        return jsonify({'ok': False, 'error': 'token_invalido'}), 401

    # 1) ¿Ya existe por google_id? 2) ¿Existe por correo? (vincular) 3) crear nuevo
    usuario = Usuario.query.filter_by(google_id=google_sub).first()
    if not usuario:
        usuario = Usuario.query.filter_by(correo=correo).first()
        if usuario:
            usuario.google_id = google_sub
            if avatar and not usuario.avatar_url:
                usuario.avatar_url = avatar
        else:
            usuario = Usuario(
                nombre=nombre[:100],
                correo=correo,
                contrasena_hash=None,
                google_id=google_sub,
                avatar_url=avatar,
            )
            db.session.add(usuario)
    else:
        # Refrescar datos básicos
        if avatar:
            usuario.avatar_url = avatar
        if nombre and usuario.nombre != nombre:
            usuario.nombre = nombre[:100]

    db.session.commit()

    session['usuario_id'] = usuario.id
    return jsonify({'ok': True, 'usuario': usuario.a_dict()})
