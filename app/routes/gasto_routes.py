"""Rutas CRUD de gastos."""

from datetime import date, datetime

from flask import Blueprint, request, jsonify, session

from app.extensions import db
from app.models.db import Usuario, Gasto, Categoria

gasto_bp = Blueprint('gasto', __name__)


def _usuario_actual():
    uid = session.get('usuario_id')
    return Usuario.query.get(uid) if uid else None


@gasto_bp.get('/api/gastos')
def listar():
    usuario = _usuario_actual()
    if not usuario:
        return jsonify({'ok': False, 'error': 'sin_sesion'}), 401
    gastos = sorted(usuario.gastos, key=lambda g: g.fecha, reverse=True)
    return jsonify({'ok': True, 'gastos': [g.a_dict() for g in gastos]})


@gasto_bp.post('/api/gastos')
def crear():
    usuario = _usuario_actual()
    if not usuario:
        return jsonify({'ok': False, 'error': 'sin_sesion'}), 401

    datos = request.get_json(silent=True) or {}
    try:
        monto = round(float(datos.get('monto')), 2)
        assert monto > 0
    except Exception:
        return jsonify({'ok': False, 'error': 'Monto inválido'}), 400

    categoria_id = datos.get('categoria_id')
    categoria = Categoria.query.filter_by(id=categoria_id, tipo='gasto').first() \
        if categoria_id else Categoria.query.filter_by(nombre='Otros', tipo='gasto').first()
    if not categoria:
        return jsonify({'ok': False, 'error': 'Categoría inválida'}), 400

    fecha = _parsear_fecha(datos.get('fecha'))
    gasto = Gasto(
        usuario_id=usuario.id,
        categoria_id=categoria.id,
        monto=monto,
        descripcion=(datos.get('descripcion') or '').strip()[:200] or None,
        fecha=fecha,
    )
    db.session.add(gasto)
    db.session.commit()
    return jsonify({'ok': True, 'gasto': gasto.a_dict()}), 201


@gasto_bp.delete('/api/gastos/<int:gasto_id>')
def eliminar(gasto_id):
    usuario = _usuario_actual()
    if not usuario:
        return jsonify({'ok': False, 'error': 'sin_sesion'}), 401
    gasto = Gasto.query.filter_by(id=gasto_id, usuario_id=usuario.id).first()
    if not gasto:
        return jsonify({'ok': False, 'error': 'no_encontrado'}), 404
    db.session.delete(gasto)
    db.session.commit()
    return jsonify({'ok': True})


def _parsear_fecha(valor):
    if not valor:
        return date.today()
    try:
        return datetime.strptime(str(valor)[:10], '%Y-%m-%d').date()
    except ValueError:
        return date.today()
