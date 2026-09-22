"""
Modelos ORM de EduFinanzas (SQLAlchemy).
Mapean a las tablas existentes en MySQL: usuarios, categorias,
ingresos, gastos, metas_ahorro.
"""

from app.extensions import db


class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(150), unique=True, nullable=False)
    # Nullable: las cuentas creadas con Google no tienen contraseña local
    contrasena_hash = db.Column(db.String(255), nullable=True)
    # Login con Google (Identity Services)
    google_id = db.Column(db.String(255), unique=True, nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp())
    activo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Usuario {self.correo}>'

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.contrasena_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        if not self.contrasena_hash:
            return False
        return check_password_hash(self.contrasena_hash, password)

    def a_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'correo': self.correo,
            'avatar_url': self.avatar_url,
            'con_google': bool(self.google_id),
            'fecha_registro': str(self.fecha_registro),
        }


class Categoria(db.Model):
    __tablename__ = 'categorias'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    tipo = db.Column(db.Enum('ingreso', 'gasto'), nullable=False)
    icono = db.Column(db.String(10))
    color = db.Column(db.String(9))

    __table_args__ = (
        db.UniqueConstraint('nombre', 'tipo', name='uq_categoria_tipo'),
    )

    def __repr__(self):
        return f'<Categoria {self.nombre} ({self.tipo})>'

    def a_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'tipo': self.tipo,
            'icono': self.icono,
            'color': self.color,
        }


class Ingreso(db.Model):
    __tablename__ = 'ingresos'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    monto = db.Column(db.DECIMAL(10, 2), nullable=False)
    descripcion = db.Column(db.String(200))
    fecha = db.Column(db.Date, nullable=False)
    creado_en = db.Column(db.DateTime, default=db.func.current_timestamp())

    usuario = db.relationship('Usuario', backref='ingresos', lazy=True)
    categoria = db.relationship('Categoria', backref='ingresos', lazy=True)

    __table_args__ = (
        db.CheckConstraint('monto > 0', name='ck_ingresos_monto'),
    )

    def __repr__(self):
        return f'<Ingreso {self.monto} - {self.descripcion}>'

    def a_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'categoria_id': self.categoria_id,
            'categoria': self.categoria.nombre if self.categoria else None,
            'icono': self.categoria.icono if self.categoria else None,
            'monto': float(self.monto),
            'descripcion': self.descripcion,
            'fecha': str(self.fecha),
        }


class Gasto(db.Model):
    __tablename__ = 'gastos'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    monto = db.Column(db.DECIMAL(10, 2), nullable=False)
    descripcion = db.Column(db.String(200))
    fecha = db.Column(db.Date, nullable=False)
    creado_en = db.Column(db.DateTime, default=db.func.current_timestamp())

    usuario = db.relationship('Usuario', backref='gastos', lazy=True)
    categoria = db.relationship('Categoria', backref='gastos', lazy=True)

    __table_args__ = (
        db.CheckConstraint('monto > 0', name='ck_gastos_monto'),
    )

    def __repr__(self):
        return f'<Gasto {self.monto} - {self.descripcion}>'

    def a_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'categoria_id': self.categoria_id,
            'categoria': self.categoria.nombre if self.categoria else None,
            'icono': self.categoria.icono if self.categoria else None,
            'color': self.categoria.color if self.categoria else None,
            'monto': float(self.monto),
            'descripcion': self.descripcion,
            'fecha': str(self.fecha),
        }


class MetaAhorro(db.Model):
    __tablename__ = 'metas_ahorro'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    monto_objetivo = db.Column(db.DECIMAL(10, 2), nullable=False)
    monto_actual = db.Column(db.DECIMAL(10, 2), default=0.00)
    fecha_limite = db.Column(db.Date)
    estado = db.Column(db.Enum('activa', 'completada', 'cancelada'), default='activa')
    creado_en = db.Column(db.DateTime, default=db.func.current_timestamp())

    usuario = db.relationship('Usuario', backref='metas_ahorro', lazy=True)

    __table_args__ = (
        db.CheckConstraint('monto_objetivo > 0', name='ck_meta_objetivo'),
        db.CheckConstraint('monto_actual >= 0', name='ck_meta_actual'),
    )

    def __repr__(self):
        return f'<Meta {self.nombre} {self.monto_actual}/{self.monto_objetivo}>'

    def a_dict(self):
        progreso = 0
        if self.monto_objetivo and float(self.monto_objetivo) > 0:
            progreso = min(round(float(self.monto_actual) / float(self.monto_objetivo) * 100, 1), 100)
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'nombre': self.nombre,
            'monto_objetivo': float(self.monto_objetivo),
            'monto_actual': float(self.monto_actual),
            'fecha_limite': str(self.fecha_limite) if self.fecha_limite else None,
            'estado': self.estado,
            'progreso': progreso,
        }


class Preferencia(db.Model):
    """Preferencias por usuario (1:1). Si presupuesto_diario es NULL,
    el límite se calcula automáticamente."""
    __tablename__ = 'preferencias'

    # usuarios.id es INT UNSIGNED en la BD existente: la FK debe coincidir
    from sqlalchemy.dialects.mysql import INTEGER as MYSQL_INT_UNSIGNED
    usuario_id = db.Column(MYSQL_INT_UNSIGNED(unsigned=True),
                           db.ForeignKey('usuarios.id'), primary_key=True)
    presupuesto_diario = db.Column(db.DECIMAL(10, 2), nullable=True)

    usuario = db.relationship('Usuario', backref='preferencia', lazy=True)

    def __repr__(self):
        return f'<Preferencia usuario={self.usuario_id} diario={self.presupuesto_diario}>'
