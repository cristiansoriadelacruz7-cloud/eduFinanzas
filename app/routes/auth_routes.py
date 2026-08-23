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
    if not ok and usuario.contrasena_hash == contrasena:
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
