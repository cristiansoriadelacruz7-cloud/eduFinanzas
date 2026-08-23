"""Rutas CRUD de metas de ahorro."""

from datetime import date

from flask import Blueprint, request, jsonify, session

from app.extensions import db
from app.models.db import Usuario, MetaAhorro
from app.routes.ingreso_routes import _parsear_fecha  # reutiliza el parser

ahorro_bp = Blueprint('ahorro', __name__)


def _usuario_actual():
    uid = session.get('usuario_id')
    return Usuario.query.get(uid) if uid else None


@ahorro_bp.get('/api/metas')
def listar():
    usuario = _usuario_actual()
    if not usuario:
        return jsonify({'ok': False, 'error': 'sin_sesion'}), 401
    return jsonify({'ok': True, 'metas': [m.a_dict() for m in usuario.metas_ahorro]})


@ahorro_bp.post('/api/metas')
def crear():
    usuario = _usuario_actual()
    if not usuario:
        return jsonify({'ok': False, 'error': 'sin_sesion'}), 401

    datos = request.get_json(silent=True) or {}
    nombre = (datos.get('nombre') or '').strip()
    if not nombre:
        return jsonify({'ok': False, 'error': 'El nombre es obligatorio'}), 400

    try:
        objetivo = round(float(datos.get('monto_objetivo')), 2)
        assert objetivo > 0
    except Exception:
        return jsonify({'ok': False, 'error': 'Monto objetivo inválido'}), 400

    try:
        inicial = round(float(datos.get('monto_inicial') or 0), 2)
        assert inicial >= 0
    except Exception:
        return jsonify({'ok': False, 'error': 'Monto inicial inválido'}), 400

    fecha_limite = _parsear_fecha(datos['fecha_limite']) if datos.get('fecha_limite') else None

    meta = MetaAhorro(
        usuario_id=usuario.id,
        nombre=nombre[:100],
        monto_objetivo=objetivo,
        monto_actual=inicial,
        fecha_limite=fecha_limite,
    )
    db.session.add(meta)
    db.session.commit()
    return jsonify({'ok': True, 'meta': meta.a_dict()}), 201


@ahorro_bp.put('/api/metas/<int:meta_id>/aportar')
def aportar(meta_id):
    usuario = _usuario_actual()
    if not usuario:
        return jsonify({'ok': False, 'error': 'sin_sesion'}), 401

    meta = MetaAhorro.query.filter_by(id=meta_id, usuario_id=usuario.id).first()
    if not meta:
        return jsonify({'ok': False, 'error': 'no_encontrado'}), 404

    datos = request.get_json(silent=True) or {}
    try:
        monto = round(float(datos.get('monto')), 2)
        assert monto > 0
    except Exception:
        return jsonify({'ok': False, 'error': 'Monto inválido'}), 400

    meta.monto_actual = float(meta.monto_actual) + monto
    if float(meta.monto_actual) >= float(meta.monto_objetivo):
        meta.estado = 'completada'
    db.session.commit()
    return jsonify({'ok': True, 'meta': meta.a_dict()})


@ahorro_bp.delete('/api/metas/<int:meta_id>')
def eliminar(meta_id):
    usuario = _usuario_actual()
    if not usuario:
        return jsonify({'ok': False, 'error': 'sin_sesion'}), 401
    meta = MetaAhorro.query.filter_by(id=meta_id, usuario_id=usuario.id).first()
    if not meta:
        return jsonify({'ok': False, 'error': 'no_encontrado'}), 404
    db.session.delete(meta)
    db.session.commit()
    return jsonify({'ok': True})
