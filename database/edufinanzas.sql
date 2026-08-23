-- Respaldo de la base de datos EduFinanzas
-- Generado desde la instancia en la nube (AlwaysData)
-- Usuarios semilla: contrasena '123456'

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `categorias`;
CREATE TABLE `categorias` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `nombre` varchar(80) NOT NULL,
  `tipo` enum('ingreso','gasto') NOT NULL,
  `icono` varchar(10) DEFAULT NULL,
  `color` char(9) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_categoria_tipo` (`nombre`,`tipo`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `categorias` (`id`, `nombre`, `tipo`, `icono`, `color`) VALUES ('1', 'Beca', 'ingreso', '🎓', '#16A34A');
INSERT INTO `categorias` (`id`, `nombre`, `tipo`, `icono`, `color`) VALUES ('2', 'Trabajo', 'ingreso', '💼', '#0EA5E9');
INSERT INTO `categorias` (`id`, `nombre`, `tipo`, `icono`, `color`) VALUES ('3', 'Apoyo familiar', 'ingreso', '🏠', '#14B8A6');
INSERT INTO `categorias` (`id`, `nombre`, `tipo`, `icono`, `color`) VALUES ('4', 'Freelance', 'ingreso', '💻', '#8B5CF6');
INSERT INTO `categorias` (`id`, `nombre`, `tipo`, `icono`, `color`) VALUES ('5', 'Otros', 'ingreso', '🔹', '#94A3B8');
INSERT INTO `categorias` (`id`, `nombre`, `tipo`, `icono`, `color`) VALUES ('6', 'Alimentación', 'gasto', '🍔', '#F59E0B');
INSERT INTO `categorias` (`id`, `nombre`, `tipo`, `icono`, `color`) VALUES ('7', 'Transporte', 'gasto', '🚌', '#3B82F6');
INSERT INTO `categorias` (`id`, `nombre`, `tipo`, `icono`, `color`) VALUES ('8', 'Estudios', 'gasto', '📚', '#8B5CF6');
INSERT INTO `categorias` (`id`, `nombre`, `tipo`, `icono`, `color`) VALUES ('9', 'Entretenimiento', 'gasto', '🎮', '#EC4899');
INSERT INTO `categorias` (`id`, `nombre`, `tipo`, `icono`, `color`) VALUES ('10', 'Otros', 'gasto', '🔹', '#94A3B8');

DROP TABLE IF EXISTS `gastos`;
CREATE TABLE `gastos` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `usuario_id` int(10) unsigned NOT NULL,
  `categoria_id` int(10) unsigned NOT NULL,
  `monto` decimal(10,2) NOT NULL,
  `descripcion` varchar(200) DEFAULT NULL,
  `fecha` date NOT NULL,
  `creado_en` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_gastos_usuario_fecha` (`usuario_id`,`fecha`),
  KEY `idx_gastos_categoria` (`categoria_id`),
  CONSTRAINT `fk_gastos_categoria` FOREIGN KEY (`categoria_id`) REFERENCES `categorias` (`id`),
  CONSTRAINT `fk_gastos_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE,
  CONSTRAINT `ck_gastos_monto` CHECK (`monto` > 0)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `gastos` (`id`, `usuario_id`, `categoria_id`, `monto`, `descripcion`, `fecha`, `creado_en`) VALUES ('1', '1', '6', '180.00', 'Mercado del mes', '2026-08-06', '2026-08-24 00:20:37');
INSERT INTO `gastos` (`id`, `usuario_id`, `categoria_id`, `monto`, `descripcion`, `fecha`, `creado_en`) VALUES ('2', '1', '7', '90.00', 'Recarga de tarjeta', '2026-08-09', '2026-08-24 00:20:37');
INSERT INTO `gastos` (`id`, `usuario_id`, `categoria_id`, `monto`, `descripcion`, `fecha`, `creado_en`) VALUES ('3', '1', '8', '80.00', 'Cuadernos y fotocopias', '2026-08-14', '2026-08-24 00:20:37');
INSERT INTO `gastos` (`id`, `usuario_id`, `categoria_id`, `monto`, `descripcion`, `fecha`, `creado_en`) VALUES ('4', '1', '9', '50.00', 'Cine con amigos', '2026-08-18', '2026-08-24 00:20:37');
INSERT INTO `gastos` (`id`, `usuario_id`, `categoria_id`, `monto`, `descripcion`, `fecha`, `creado_en`) VALUES ('5', '1', '6', '50.00', 'Almuerzos universidad', '2026-08-24', '2026-08-24 00:20:37');

DROP TABLE IF EXISTS `ingresos`;
CREATE TABLE `ingresos` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `usuario_id` int(10) unsigned NOT NULL,
  `categoria_id` int(10) unsigned NOT NULL,
  `monto` decimal(10,2) NOT NULL,
  `descripcion` varchar(200) DEFAULT NULL,
  `fecha` date NOT NULL,
  `creado_en` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_ingresos_usuario_fecha` (`usuario_id`,`fecha`),
  KEY `idx_ingresos_categoria` (`categoria_id`),
  CONSTRAINT `fk_ingresos_categoria` FOREIGN KEY (`categoria_id`) REFERENCES `categorias` (`id`),
  CONSTRAINT `fk_ingresos_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE,
  CONSTRAINT `ck_ingresos_monto` CHECK (`monto` > 0)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `ingresos` (`id`, `usuario_id`, `categoria_id`, `monto`, `descripcion`, `fecha`, `creado_en`) VALUES ('1', '1', '1', '500.00', 'Beca mensual', '2026-08-04', '2026-08-24 00:20:37');
INSERT INTO `ingresos` (`id`, `usuario_id`, `categoria_id`, `monto`, `descripcion`, `fecha`, `creado_en`) VALUES ('2', '1', '2', '400.00', 'Sueldo medio tiempo', '2026-08-12', '2026-08-24 00:20:37');

DROP TABLE IF EXISTS `metas_ahorro`;
CREATE TABLE `metas_ahorro` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `usuario_id` int(10) unsigned NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `monto_objetivo` decimal(10,2) NOT NULL,
  `monto_actual` decimal(10,2) NOT NULL DEFAULT 0.00,
  `fecha_limite` date DEFAULT NULL,
  `estado` enum('activa','completada','cancelada') NOT NULL DEFAULT 'activa',
  `creado_en` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_metas_usuario_estado` (`usuario_id`,`estado`),
  CONSTRAINT `fk_metas_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE,
  CONSTRAINT `ck_meta_objetivo` CHECK (`monto_objetivo` > 0),
  CONSTRAINT `ck_meta_actual` CHECK (`monto_actual` >= 0)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `metas_ahorro` (`id`, `usuario_id`, `nombre`, `monto_objetivo`, `monto_actual`, `fecha_limite`, `estado`, `creado_en`) VALUES ('1', '1', 'Laptop', '2500.00', '1750.00', '2026-12-22', 'activa', '2026-08-24 00:20:37');
INSERT INTO `metas_ahorro` (`id`, `usuario_id`, `nombre`, `monto_objetivo`, `monto_actual`, `fecha_limite`, `estado`, `creado_en`) VALUES ('2', '1', 'Fondo de emergencia', '500.00', '120.00', '2026-10-23', 'activa', '2026-08-24 00:20:37');

DROP TABLE IF EXISTS `preferencias`;
CREATE TABLE `preferencias` (
  `usuario_id` int(10) unsigned NOT NULL,
  `presupuesto_diario` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`usuario_id`),
  CONSTRAINT `preferencias_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


DROP TABLE IF EXISTS `usuarios`;
CREATE TABLE `usuarios` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `correo` varchar(150) NOT NULL,
  `contrasena_hash` varchar(255) NOT NULL,
  `fecha_registro` datetime NOT NULL DEFAULT current_timestamp(),
  `activo` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_usuarios_correo` (`correo`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `usuarios` (`id`, `nombre`, `correo`, `contrasena_hash`, `fecha_registro`, `activo`) VALUES ('1', 'Antony Demo', 'demo@edufinanzas.pe', 'scrypt:32768:8:1$gNh0OvqozoLc4YAk$cd3e3b413141fcda0c4df9f2f6ec1f12fbbbbc1b508843f17a7a400b2067b80a0b5173f29231c25db3e5c14f2c132135fc51fac710c49d2cf97e67377700e10d', '2026-08-24 00:20:37', '1');
INSERT INTO `usuarios` (`id`, `nombre`, `correo`, `contrasena_hash`, `fecha_registro`, `activo`) VALUES ('2', 'Maria Gomez', 'maria@edufinanzas.pe', 'scrypt:32768:8:1$gNh0OvqozoLc4YAk$cd3e3b413141fcda0c4df9f2f6ec1f12fbbbbc1b508843f17a7a400b2067b80a0b5173f29231c25db3e5c14f2c132135fc51fac710c49d2cf97e67377700e10d', '2026-08-24 00:20:37', '1');
INSERT INTO `usuarios` (`id`, `nombre`, `correo`, `contrasena_hash`, `fecha_registro`, `activo`) VALUES ('3', 'Carlos Ruiz', 'carlos@edufinanzas.pe', 'scrypt:32768:8:1$gNh0OvqozoLc4YAk$cd3e3b413141fcda0c4df9f2f6ec1f12fbbbbc1b508843f17a7a400b2067b80a0b5173f29231c25db3e5c14f2c132135fc51fac710c49d2cf97e67377700e10d', '2026-08-24 00:20:37', '1');
INSERT INTO `usuarios` (`id`, `nombre`, `correo`, `contrasena_hash`, `fecha_registro`, `activo`) VALUES ('4', 'Laura Patel', 'laura@edufinanzas.pe', 'scrypt:32768:8:1$gNh0OvqozoLc4YAk$cd3e3b413141fcda0c4df9f2f6ec1f12fbbbbc1b508843f17a7a400b2067b80a0b5173f29231c25db3e5c14f2c132135fc51fac710c49d2cf97e67377700e10d', '2026-08-24 00:20:37', '1');

SET FOREIGN_KEY_CHECKS = 1;
