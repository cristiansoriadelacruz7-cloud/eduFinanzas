-- ============================================================
-- EduFinanzas - Base de datos (MySQL 8.x)
-- Archivo: database/edufinanzas.sql
-- Uso:     mysql -u root -p < database/edufinanzas.sql
-- ============================================================

DROP DATABASE IF EXISTS edufinanzas;
CREATE DATABASE edufinanzas
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE edufinanzas;

-- ============================================================
-- TABLA: usuarios
-- Modela app/models/usuario.py
-- ============================================================
CREATE TABLE usuarios (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre          VARCHAR(100)             NOT NULL,
    correo          VARCHAR(150)             NOT NULL,
    contrasena_hash VARCHAR(255)             NOT NULL,
    fecha_registro  DATETIME                 NOT NULL DEFAULT CURRENT_TIMESTAMP,
    activo          TINYINT(1)               NOT NULL DEFAULT 1,

    CONSTRAINT uq_usuarios_correo UNIQUE (correo)
) ENGINE = InnoDB;

-- ============================================================
-- TABLA: categorias
-- Modela app/models/categoria.py
-- tipo distingue si la categoría aplica a ingresos o gastos
-- ============================================================
CREATE TABLE categorias (
    id       INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre   VARCHAR(80)                     NOT NULL,
    tipo     ENUM('ingreso', 'gasto')        NOT NULL,
    icono    VARCHAR(10)                     NULL,
    color    CHAR(9)                         NULL,

    CONSTRAINT uq_categoria_tipo UNIQUE (nombre, tipo)
) ENGINE = InnoDB;

-- ============================================================
-- TABLA: ingresos
-- Modela app/models/ingreso.py
-- ============================================================
CREATE TABLE ingresos (
    id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    usuario_id   INT UNSIGNED            NOT NULL,
    categoria_id INT UNSIGNED            NOT NULL,
    monto        DECIMAL(10, 2)          NOT NULL,
    descripcion  VARCHAR(200)            NULL,
    fecha        DATE                    NOT NULL,
    creado_en    DATETIME                NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_ingresos_monto CHECK (monto > 0),
    CONSTRAINT fk_ingresos_usuario   FOREIGN KEY (usuario_id)   REFERENCES usuarios(id)   ON DELETE CASCADE,
    CONSTRAINT fk_ingresos_categoria FOREIGN KEY (categoria_id) REFERENCES categorias(id),

    INDEX idx_ingresos_usuario_fecha (usuario_id, fecha),
    INDEX idx_ingresos_categoria (categoria_id)
) ENGINE = InnoDB;

-- ============================================================
-- TABLA: gastos
-- Modela app/models/gasto.py
-- ============================================================
CREATE TABLE gastos (
    id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    usuario_id   INT UNSIGNED            NOT NULL,
    categoria_id INT UNSIGNED            NOT NULL,
    monto        DECIMAL(10, 2)          NOT NULL,
    descripcion  VARCHAR(200)            NULL,
    fecha        DATE                    NOT NULL,
    creado_en    DATETIME                NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_gastos_monto CHECK (monto > 0),
    CONSTRAINT fk_gastos_usuario   FOREIGN KEY (usuario_id)   REFERENCES usuarios(id) ON DELETE CASCADE,
    CONSTRAINT fk_gastos_categoria FOREIGN KEY (categoria_id) REFERENCES categorias(id),

    INDEX idx_gastos_usuario_fecha (usuario_id, fecha),
    INDEX idx_gastos_categoria (categoria_id)
) ENGINE = InnoDB;

-- ============================================================
-- TABLA: metas_ahorro
-- Modela app/models/meta_ahorro.py
-- ============================================================
CREATE TABLE metas_ahorro (
    id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    usuario_id     INT UNSIGNED                                  NOT NULL,
    nombre         VARCHAR(100)                                  NOT NULL,
    monto_objetivo DECIMAL(10, 2)                                NOT NULL,
    monto_actual   DECIMAL(10, 2)               NOT NULL DEFAULT 0.00,
    fecha_limite   DATE                                          NULL,
    estado         ENUM('activa', 'completada', 'cancelada')     NOT NULL DEFAULT 'activa',
    creado_en      DATETIME                                      NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_meta_objetivo CHECK (monto_objetivo > 0),
    CONSTRAINT ck_meta_actual   CHECK (monto_actual >= 0),
    CONSTRAINT fk_metas_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,

    INDEX idx_metas_usuario_estado (usuario_id, estado)
) ENGINE = InnoDB;

-- ============================================================
-- DATOS INICIALES: categorías
-- (coinciden con las categorías usadas en el frontend)
-- ============================================================
INSERT INTO categorias (nombre, tipo, icono, color) VALUES
    ('Beca',            'ingreso', '🎓', '#16A34A'),
    ('Trabajo',         'ingreso', '💼', '#0EA5E9'),
    ('Apoyo familiar',  'ingreso', '🏠', '#14B8A6'),
    ('Freelance',       'ingreso', '💻', '#8B5CF6'),
    ('Otros',           'ingreso', '🔹', '#94A3B8'),
    ('Alimentación',    'gasto',   '🍔', '#F59E0B'),
    ('Transporte',      'gasto',   '🚌', '#3B82F6'),
    ('Estudios',        'gasto',   '📚', '#8B5CF6'),
    ('Entretenimiento', 'gasto',   '🎮', '#EC4899'),
    ('Otros',           'gasto',   '🔹', '#94A3B8');

-- ============================================================
-- USUARIO DEMO
-- Contraseña: demo123  -> hash generado con werkzeug:
--   python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('demo123'))"
-- Reemplaza el hash por uno generado si cambias la contraseña.
-- ============================================================
INSERT INTO usuarios (nombre, correo, contrasena_hash) VALUES
    ('Antony Demo', 'demo@edufinanzas.pe',
     'pbkdf2:sha256:600000$REEMPLAZAR_POR_HASH_GENERADO');

-- ============================================================
-- CUENTAS DE PRESTA PARA PROBAR EL SISTEMA
-- (Contraseñas: 123456 — serán hasheadas por el backend Flask en producción)
-- ============================================================
INSERT INTO usuarios (nombre, correo, contrasena_hash) VALUES
    ('Maria Gomez', 'maria@edufinanzas.pe',
     'pbkdf2:sha256$123456mockhash1'),
    ('Carlos Ruiz', 'carlos@edufinanzas.pe',
     'pbkdf2:sha256$123456mockhash2'),
    ('Laura Patel', 'laura@edufinanzas.pe',
     'pbkdf2:sha256$123456mockhash3');

-- ============================================================
-- DATOS DE EJEMPLO para el usuario demo
-- ============================================================
SET @uid = (SELECT id FROM usuarios WHERE correo = 'demo@edufinanzas.pe' LIMIT 1);

INSERT INTO ingresos (usuario_id, categoria_id, monto, descripcion, fecha) VALUES
    (@uid, (SELECT id FROM categorias WHERE nombre = 'Beca' AND tipo = 'ingreso'),           500.00, 'Beca mensual',      CURDATE() - INTERVAL 20 DAY),
    (@uid, (SELECT id FROM categorias WHERE nombre = 'Trabajo' AND tipo = 'ingreso'),        400.00, 'Sueldo medio tiempo', CURDATE() - INTERVAL 12 DAY);

INSERT INTO gastos (usuario_id, categoria_id, monto, descripcion, fecha) VALUES
    (@uid, (SELECT id FROM categorias WHERE nombre = 'Alimentación' AND tipo = 'gasto'), 180.00, 'Mercado del mes',  CURDATE() - INTERVAL 18 DAY),
    (@uid, (SELECT id FROM categorias WHERE nombre = 'Transporte' AND tipo = 'gasto'),    90.00, 'Recarga de tarjeta', CURDATE() - INTERVAL 15 DAY),
    (@uid, (SELECT id FROM categorias WHERE nombre = 'Estudios' AND tipo = 'gasto'),      80.00, 'Cuadernos y fotocopias', CURDATE() - INTERVAL 10 DAY),
    (@uid, (SELECT id FROM categorias WHERE nombre = 'Entretenimiento' AND tipo = 'gasto'), 50.00, 'Cine con amigos', CURDATE() - INTERVAL 6 DAY),
    (@uid, (SELECT id FROM categorias WHERE nombre = 'Alimentación' AND tipo = 'gasto'),   50.00, 'Almuerzos universidad', CURDATE());

INSERT INTO metas_ahorro (usuario_id, nombre, monto_objetivo, monto_actual, fecha_limite, estado) VALUES
    (@uid, 'Laptop',               2500.00, 1750.00, CURDATE() + INTERVAL 120 DAY, 'activa'),
    (@uid, 'Fondo de emergencia',   500.00,  120.00, CURDATE() + INTERVAL 60 DAY,  'activa');
