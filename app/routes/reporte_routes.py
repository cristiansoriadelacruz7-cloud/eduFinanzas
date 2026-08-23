"""Rutas de reportes y utilidades (categorías)."""

from datetime import date

from flask import Blueprint, jsonify, session

from app.extensions import db
from app.models.db import Usuario, Categoria

reporte_bp = Blueprint('reporte', __name__)

_NOMBRES_MESES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                  'Jul', 'Ago', 'Set', 'Oct', 'Nov', 'Dic']


def _usuario_actual():
    uid = session.get('usuario_id')
    return Usuario.query.get(uid) if uid else None


@reporte_bp.get('/api/categorias')
def categorias():
    usuario = _usuario_actual()
    if not usuario:
        return jsonify({'ok': False, 'error': 'sin_sesion'}), 401
    todas = Categoria.query.order_by(Categoria.tipo, Categoria.id).all()
    ingresos = [c.a_dict() for c in todas if c.tipo == 'ingreso']
    gastos = [c.a_dict() for c in todas if c.tipo == 'gasto']
    return jsonify({'ok': True, 'ingresos': ingresos, 'gastos': gastos})


@reporte_bp.get('/api/reportes')
def reportes():
    """Resumen global del usuario: totales históricos y por categoría."""
    usuario = _usuario_actual()
    if not usuario:
        return jsonify({'ok': False, 'error': 'sin_sesion'}), 401

    total_ingresos = sum(float(i.monto) for i in usuario.ingresos)
    total_gastos = sum(float(g.monto) for g in usuario.gastos)

    por_categoria = {}
    for g in usuario.gastos:
        nombre = g.categoria.nombre if g.categoria else 'Otros'
        entrada = por_categoria.setdefault(nombre, {
            'monto': 0.0,
            'color': (g.categoria.color if g.categoria else '#94A3B8'),
            'icono': (g.categoria.icono if g.categoria else '🔹'),
        })
        entrada['monto'] += float(g.monto)

    categorias = sorted(
        ({'nombre': k, **v} for k, v in por_categoria.items()),
        key=lambda c: -c['monto'],
    )

    # Evolución mensual: últimos 6 meses
    hoy = date.today()
    por_mes = []
    for i in range(5, -1, -1):
        mes, anio = hoy.month - i, hoy.year
        while mes <= 0:
            mes += 12
            anio -= 1
        ingresos_mes = sum(float(x.monto) for x in usuario.ingresos
                           if x.fecha.year == anio and x.fecha.month == mes)
        gastos_mes = sum(float(x.monto) for x in usuario.gastos
                         if x.fecha.year == anio and x.fecha.month == mes)
        por_mes.append({
            'mes': f"{_NOMBRES_MESES[mes - 1]} {str(anio)[2:]}",
            'ingresos': round(ingresos_mes, 2),
            'gastos': round(gastos_mes, 2),
        })

    return jsonify({
        'ok': True,
        'total_ingresos': round(total_ingresos, 2),
        'total_gastos': round(total_gastos, 2),
        'ahorro_total': round(total_ingresos - total_gastos, 2),
        'categorias': categorias,
        'por_mes': por_mes,
    })
