"""Rutas de planes, suscripciones, licencias y notificaciones."""
import random
import string
from datetime import date, datetime, timedelta

from flask import Blueprint, jsonify, request, session

from app.extensions import db
from app.models.db import Usuario, Licencia, Suscripcion, Notificacion

plan_bp = Blueprint('plan', __name__)


def _usuario_actual():
    uid = session.get('usuario_id')
    return Usuario.query.get(uid) if uid else None


def _generar_codigo():
    partes = []
    for _ in range(4):
        partes.append(''.join(random.choices(string.ascii_uppercase + string.digits, k=4)))
    return '-'.join(partes)


@plan_bp.get('/api/plan')
def info_plan():
    usuario = _usuario_actual()
    if not usuario:
        return jsonify({'ok': False, 'error': 'sin_sesion'}), 401
    if hasattr(usuario, 'es_pro'):
        usuario.es_pro()
        db.session.commit()
    return jsonify({'ok': True, 'usuario': usuario.a_dict()})


@plan_bp.post('/api/plan/activar-pro')
def activar_pro_suscripcion():
    usuario = _usuario_actual()
    if not usuario:
        return jsonify({'ok': False, 'error': 'sin_sesion'}), 401
    datos = request.get_json(silent=True) or {}
    dias = datos.get('dias', 30)
    try:
        dias = int(dias)
        if dias <= 0:
            dias = 30
    except Exception:
        dias = 30

    vence = date.today() + timedelta(days=dias)
    usuario.plan = 'pro'
    usuario.tipo_acceso = 'suscripcion'
    usuario.pro_hasta = vence
    usuario.licencia_id = None

    sub = Suscripcion(
        usuario_id=usuario.id,
        plan='pro',
        estado='activa',
        metodo_pago='simulado',
        iniciado_en=datetime.now(),
        vence_en=datetime.combine(vence, datetime.min.time()),
        transaccion_id='SIM-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)),
    )
    db.session.add(sub)

    notif = Notificacion(
        usuario_id=usuario.id,
        titulo='¡Bienvenido a Plan Pro!',
        mensaje=f'Tu suscripción Pro ha sido activada correctamente. Válida hasta {vence.strftime("%d/%m/%Y")}.',
        tipo='exito',
        solo_pro=True,
    )
    db.session.add(notif)

    db.session.commit()
    return jsonify({'ok': True, 'mensaje': 'Plan Pro activado por suscripción', 'usuario': usuario.a_dict(), 'vence_en': str(vence)})


@plan_bp.post('/api/plan/activar-licencia')
def activar_licencia():
    usuario = _usuario_actual()
    if not usuario:
        return jsonify({'ok': False, 'error': 'sin_sesion'}), 401
    datos = request.get_json(silent=True) or {}
    codigo = (datos.get('codigo') or '').strip().upper()
    if not codigo:
        return jsonify({'ok': False, 'error': 'Ingresa un código de licencia'}), 400

    lic = Licencia.query.filter_by(codigo=codigo).first()
    if not lic:
        return jsonify({'ok': False, 'error': 'Código de licencia inválido'}), 400
    if lic.usada:
        return jsonify({'ok': False, 'error': 'Este código de licencia ya ha sido utilizado'}), 400

    vence = date.today() + timedelta(days=int(lic.duracion_dias or 30))
    usuario.plan = 'pro'
    usuario.tipo_acceso = 'licencia'
    usuario.pro_hasta = vence
    usuario.licencia_id = lic.id

    lic.usada = True
    lic.usada_por_id = usuario.id
    lic.usada_en = datetime.now()

    notif = Notificacion(
        usuario_id=usuario.id,
        titulo='¡Licencia Pro activada!',
        mensaje=f'Tu licencia ha sido canjeada con éxito. Plan Pro válido hasta {vence.strftime("%d/%m/%Y")}.',
        tipo='exito',
        solo_pro=True,
    )
    db.session.add(notif)
    db.session.commit()
    return jsonify({'ok': True, 'mensaje': 'Licencia activada correctamente', 'usuario': usuario.a_dict(), 'vence_en': str(vence)})


@plan_bp.post('/api/plan/generar-licencia')
def generar_licencia():
    usuario = _usuario_actual()
    if not usuario:
        return jsonify({'ok': False, 'error': 'sin_sesion'}), 401
    datos = request.get_json(silent=True) or {}
    dias = datos.get('dias', 30)
    cantidad = datos.get('cantidad', 1)
    try:
        dias = int(dias)
        cantidad = int(cantidad)
        if dias <= 0: dias = 30
        if cantidad <= 0: cantidad = 1
        if cantidad > 10: cantidad = 10
    except Exception:
        dias = 30
        cantidad = 1

    creadas = []
    for _ in range(cantidad):
        codigo = _generar_codigo()
        lic = Licencia(codigo=codigo, tipo='pro', duracion_dias=dias, usada=False)
        db.session.add(lic)
        creadas.append(codigo)
    db.session.commit()
    return jsonify({'ok': True, 'mensaje': f'{len(creadas)} licencia(s) generada(s)', 'licencias': creadas, 'dias': dias})


@plan_bp.get('/api/notificaciones')
def listar_notificaciones():
    usuario = _usuario_actual()
    if not usuario:
        return jsonify({'ok': False, 'error': 'sin_sesion'}), 401
    if hasattr(usuario, 'es_pro'):
        usuario.es_pro()
        db.session.commit()
    es_pro = usuario.plan == 'pro'
    q = Notificacion.query.filter_by(usuario_id=usuario.id)
    if not es_pro:
        q = q.filter_by(solo_pro=False)
    notifs = q.order_by(Notificacion.creada_en.desc()).all()
    return jsonify({'ok': True, 'es_pro': es_pro, 'notificaciones': [n.a_dict() for n in notifs]})


@plan_bp.post('/api/notificaciones/crear-demo')
def crear_demo_notificaciones():
    usuario = _usuario_actual()
    if not usuario:
        return jsonify({'ok': False, 'error': 'sin_sesion'}), 401
    if not (usuario.plan == 'pro'):
        return jsonify({'ok': False, 'error': 'Solo disponible para usuarios Pro'}), 403

    demos = [
        ('Alerta de presupuesto', 'Has superado el 80% de tu presupuesto diario. Revisa tus gastos.', 'alerta'),
        ('Meta casi completada', '¡Te falta poco para completar tu meta de ahorro! Sigue así.', 'exito'),
        ('Nuevo reporte disponible', 'Ya puedes ver tu reporte mensual detallado en la sección Reportes.', 'info'),
    ]
    for t, m, tipo in demos:
        db.session.add(Notificacion(usuario_id=usuario.id, titulo=t, mensaje=m, tipo=tipo, solo_pro=True))
    db.session.commit()
    return jsonify({'ok': True, 'mensaje': 'Notificaciones demo creadas para Plan Pro'})


@plan_bp.post('/api/notificaciones/<int:nid>/leer')
def marcar_leida(nid):
    usuario = _usuario_actual()
    if not usuario:
        return jsonify({'ok': False, 'error': 'sin_sesion'}), 401
    n = Notificacion.query.filter_by(id=nid, usuario_id=usuario.id).first()
    if not n:
        return jsonify({'ok': False, 'error': 'Notificación no encontrada'}), 404
    n.leida = True
    db.session.commit()
    return jsonify({'ok': True})
