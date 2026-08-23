"""Rutas del dashboard: resumen financiero, presupuesto diario y alertas."""

from datetime import date, datetime
from calendar import monthrange

from flask import Blueprint, jsonify, session, request

from app.extensions import db
from app.models.db import Usuario, Ingreso, Gasto, MetaAhorro, Preferencia

dashboard_bp = Blueprint('dashboard', __name__)


def _usuario_actual():
    uid = session.get('usuario_id')
    return Usuario.query.get(uid) if uid else None


def _dias_restantes_mes():
    hoy = date.today()
    return monthrange(hoy.year, hoy.month)[1] - hoy.day + 1


def limite_diario_de(usuario):
    """Devuelve (limite, fuente). Si el usuario definió un presupuesto
    propio se respeta; si no, se reparte lo disponible en el mes."""
    pref = Preferencia.query.get(usuario.id)
    if pref and pref.presupuesto_diario is not None:
        return round(float(pref.presupuesto_diario), 2), 'personalizado'
    auto = round(max(usuario_disponible(usuario) / _dias_restantes_mes(), 0), 2)
    return auto, 'automatico'


def _en_mes_actual(fecha):
    hoy = date.today()
    return fecha.year == hoy.year and fecha.month == hoy.month


@dashboard_bp.get('/api/dashboard')
def resumen():
    usuario = _usuario_actual()
    if not usuario:
        return jsonify({'ok': False, 'error': 'sin_sesion'}), 401

    hoy = date.today()

    ingresos = [i for i in usuario.ingresos if _en_mes_actual(i.fecha)]
    gastos = [g for g in usuario.gastos if _en_mes_actual(g.fecha)]

    total_ingresos = sum(float(i.monto) for i in ingresos)
    total_gastos = sum(float(g.monto) for g in gastos)
    ahorro = total_ingresos - total_gastos

    # Gastos por categoría (del mes)
    por_categoria = {}
    for g in gastos:
        nombre = g.categoria.nombre if g.categoria else 'Otros'
        entrada = por_categoria.setdefault(nombre, {
            'monto': 0.0,
            'color': (g.categoria.color if g.categoria else '#94A3B8'),
            'icono': (g.categoria.icono if g.categoria else '🔹'),
        })
        entrada['monto'] += float(g.monto)

    categorias = [
        {'nombre': k, **v, 'porcentaje': round(v['monto'] / total_gastos * 100) if total_gastos else 0}
        for k, v in por_categoria.items()
    ]
    categorias.sort(key=lambda c: -c['porcentaje'])

    # Últimos movimientos combinados (ingresos + gastos), top 5 por fecha
    movimientos = (
        [{'tipo': 'ingreso', **i.a_dict()} for i in usuario.ingresos]
        + [{'tipo': 'gasto', **g.a_dict()} for g in usuario.gastos]
    )
    movimientos.sort(key=lambda m: m['fecha'], reverse=True)

    # Presupuesto diario
    dias_restantes = _dias_restantes_mes()
    gastado_hoy = sum(float(g.monto) for g in usuario.gastos if g.fecha == hoy)
    limite_diario, fuente_limite = limite_diario_de(usuario)

    # Metas activas
    metas = [m.a_dict() for m in usuario.metas_ahorro if m.estado == 'activa']

    return jsonify({
        'ok': True,
        'usuario': {'nombre': usuario.nombre},
        'disponible': usuario_disponible(usuario),
        'total_ingresos_mes': total_ingresos,
        'total_gastos_mes': total_gastos,
        'ahorro_mes': ahorro,
        'dias_restantes': dias_restantes,
        'limite_diario': limite_diario,
        'fuente_limite': fuente_limite,
        'gastado_hoy': gastado_hoy,
        'categorias': categorias,
        'movimientos': movimientos[:5],
        'metas': metas[:3],
    })


def usuario_disponible(usuario):
    """Dinero disponible = ingresos históricos - gastos históricos."""
    total_ingresos = sum(float(i.monto) for i in usuario.ingresos)
    total_gastos = sum(float(g.monto) for g in usuario.gastos)
    return round(total_ingresos - total_gastos, 2)


@dashboard_bp.get('/api/presupuesto')
def ver_presupuesto():
    usuario = _usuario_actual()
    if not usuario:
        return jsonify({'ok': False, 'error': 'sin_sesion'}), 401
    limite, fuente = limite_diario_de(usuario)
    pref = Preferencia.query.get(usuario.id)
    return jsonify({
        'ok': True,
        'limite_diario': limite,
        'fuente': fuente,
        'presupuesto_guardado': (float(pref.presupuesto_diario)
                                 if pref and pref.presupuesto_diario is not None else None),
        'disponible': usuario_disponible(usuario),
        'dias_restantes': _dias_restantes_mes(),
    })


@dashboard_bp.put('/api/presupuesto')
def fijar_presupuesto():
    """Fija un presupuesto diario propio; con monto null vuelve al automático."""
    usuario = _usuario_actual()
    if not usuario:
        return jsonify({'ok': False, 'error': 'sin_sesion'}), 401

    datos = request.get_json(silent=True) or {}
    monto = datos.get('monto')

    pref = Preferencia.query.get(usuario.id)
    if monto is None:
        # Volver al cálculo automático
        if pref:
            pref.presupuesto_diario = None
            db.session.commit()
        limite, fuente = limite_diario_de(usuario)
        return jsonify({'ok': True, 'limite_diario': limite, 'fuente': fuente})

    try:
        monto = round(float(monto), 2)
        assert monto > 0
    except Exception:
        return jsonify({'ok': False, 'error': 'Monto inválido'}), 400

    if not pref:
        pref = Preferencia(usuario_id=usuario.id)
        db.session.add(pref)
    pref.presupuesto_diario = monto
    db.session.commit()
    return jsonify({'ok': True, 'limite_diario': monto, 'fuente': 'personalizado'})
