"""Rutas CRUD de ingresos."""

from datetime import date, datetime

from flask import Blueprint, request, jsonify, session

from app.extensions import db
from app.models.db import Usuario, Ingreso, Categoria

ingreso_bp = Blueprint('ingreso', __name__)


def _usuario_actual():
    uid = session.get('usuario_id')
    return Usuario.query.get(uid) if uid else None


@ingreso_bp.get('/api/ingresos')
def listar():
    usuario = _usuario_actual()
    if not usuario:
        return jsonify({'ok': False, 'error': 'sin_sesion'}), 401
    ingresos = sorted(usuario.ingresos, key=lambda i: i.fecha, reverse=True)
    return jsonify({'ok': True, 'ingresos': [i.a_dict() for i in ingresos]})


@ingreso_bp.post('/api/ingresos')
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
    categoria = Categoria.query.filter_by(id=categoria_id, tipo='ingreso').first() \
        if categoria_id else Categoria.query.filter_by(nombre='Otros', tipo='ingreso').first()
    if not categoria:
        return jsonify({'ok': False, 'error': 'Categoría inválida'}), 400

    fecha = _parsear_fecha(datos.get('fecha'))
    ingreso = Ingreso(
        usuario_id=usuario.id,
        categoria_id=categoria.id,
        monto=monto,
        descripcion=(datos.get('descripcion') or '').strip()[:200] or None,
        fecha=fecha,
    )
    db.session.add(ingreso)
    db.session.commit()
    return jsonify({'ok': True, 'ingreso': ingreso.a_dict()}), 201


@ingreso_bp.delete('/api/ingresos/<int:ingreso_id>')
def eliminar(ingreso_id):
    usuario = _usuario_actual()
    if not usuario:
        return jsonify({'ok': False, 'error': 'sin_sesion'}), 401
    ingreso = Ingreso.query.filter_by(id=ingreso_id, usuario_id=usuario.id).first()
    if not ingreso:
        return jsonify({'ok': False, 'error': 'no_encontrado'}), 404
    db.session.delete(ingreso)
    db.session.commit()
    return jsonify({'ok': True})


def _parsear_fecha(valor):
    if not valor:
        return date.today()
    try:
        return datetime.strptime(str(valor)[:10], '%Y-%m-%d').date()
    except ValueError:
        return date.today()
