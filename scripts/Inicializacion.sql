-- =============================================================================
-- LABORATORIO 01 - BASES DE DATOS (Uninorte) - BibliotecaUN
-- Script 1 de 4: estructura (DDL). Orden de ejecución:
--   1. Inicializacion.sql   (este: crea la BD y las 13 tablas)
--   2. seed_datos.sql       (catálogo, ejemplares, usuarios y empleados)
--   3. seed_auth.sql        (contraseñas de prueba con hash real)
--   4. seed_prestamos.sql   (préstamos de ejemplo + conciliación de estados)
-- Los usuarios de MySQL del grupo NO se crean aquí (ver usuarios_bd.example.sql):
-- las contraseñas no deben quedar en el repositorio.
-- =============================================================================

SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS biblioteca CHARACTER SET utf8mb4;
USE biblioteca;

DROP TABLE IF EXISTS multa, devolucion, prestamo, ejemplar, libro_autor,
  empleado, usuario, libro, configuracion, politica_prestamo,
  autor, categoria, editorial;

CREATE TABLE editorial (
	id_editorial INT AUTO_INCREMENT PRIMARY KEY,
    nombre		 VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE categoria (
	id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre 		 VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE autor (
	id_autor	 INT AUTO_INCREMENT PRIMARY KEY,
    nombre		 VARCHAR(120) NOT NULL
);

CREATE TABLE politica_prestamo (
	rol			   VARCHAR(20) PRIMARY KEY,
	dias_prestamo  INT NOT NULL CHECK (dias_prestamo > 0),
    max_prestamos  INT NOT NULL CHECK (max_prestamos > 0),
    CONSTRAINT ck_rol_politica CHECK (rol IN ('estudiante','docente'))
);

CREATE TABLE configuracion (
	clave	VARCHAR(50) PRIMARY KEY,
    valor	VARCHAR(100) NOT NULL
);

CREATE TABLE libro (
  id_libro     INT AUTO_INCREMENT PRIMARY KEY,
  isbn         VARCHAR(17)  NOT NULL UNIQUE,
  titulo       VARCHAR(200) NOT NULL,
  anio         SMALLINT     NOT NULL,
  descripcion  TEXT,
  id_editorial INT NOT NULL,
  id_categoria INT NOT NULL,
  eliminado    BOOLEAN NOT NULL DEFAULT FALSE,
  CONSTRAINT fk_libro_editorial FOREIGN KEY (id_editorial)
    REFERENCES editorial (id_editorial) ON DELETE RESTRICT,
  CONSTRAINT fk_libro_categoria FOREIGN KEY (id_categoria)
    REFERENCES categoria (id_categoria) ON DELETE RESTRICT,
  CONSTRAINT ck_libro_anio CHECK (anio BETWEEN 1400 AND 2100),
  INDEX idx_libro_titulo (titulo)
);

CREATE TABLE usuario (
  id_usuario     INT AUTO_INCREMENT PRIMARY KEY,
  codigo         VARCHAR(20)  NOT NULL UNIQUE,
  identificacion VARCHAR(20)  NOT NULL UNIQUE,
  nombres        VARCHAR(120) NOT NULL,
  correo         VARCHAR(120) NOT NULL UNIQUE,
  clave_hash     VARCHAR(255) NOT NULL,
  rol            VARCHAR(20)  NOT NULL,
  carrera        VARCHAR(100) NULL,
  estado         VARCHAR(10)  NOT NULL DEFAULT 'activo',
  eliminado      BOOLEAN NOT NULL DEFAULT FALSE,
  CONSTRAINT fk_usuario_politica FOREIGN KEY (rol)
    REFERENCES politica_prestamo (rol) ON DELETE RESTRICT,
  CONSTRAINT ck_usuario_estado CHECK (estado IN ('activo','bloqueado'))
);

CREATE TABLE empleado (
  id_empleado INT AUTO_INCREMENT PRIMARY KEY,
  nombres     VARCHAR(120) NOT NULL,
  correo      VARCHAR(120) NOT NULL UNIQUE,
  clave_hash  VARCHAR(255) NOT NULL,
  rol         VARCHAR(20)  NOT NULL DEFAULT 'bibliotecario',
  CONSTRAINT ck_empleado_rol CHECK (rol IN ('bibliotecario','admin'))
);

CREATE TABLE libro_autor (
  id_libro INT NOT NULL,
  id_autor INT NOT NULL,
  PRIMARY KEY (id_libro, id_autor),
  CONSTRAINT fk_la_libro FOREIGN KEY (id_libro)
    REFERENCES libro (id_libro) ON DELETE CASCADE,
  CONSTRAINT fk_la_autor FOREIGN KEY (id_autor)
    REFERENCES autor (id_autor) ON DELETE RESTRICT,
  INDEX idx_la_autor (id_autor)
);

CREATE TABLE ejemplar (
  id_ejemplar   INT AUTO_INCREMENT PRIMARY KEY,
  codigo_barras VARCHAR(30) NOT NULL UNIQUE,
  ubicacion     VARCHAR(60) NOT NULL,
  estado        VARCHAR(12) NOT NULL DEFAULT 'disponible',
  condicion     VARCHAR(10) NOT NULL DEFAULT 'bueno',
  id_libro      INT NOT NULL,
  eliminado     BOOLEAN NOT NULL DEFAULT FALSE,
  CONSTRAINT fk_ejemplar_libro FOREIGN KEY (id_libro)
    REFERENCES libro (id_libro) ON DELETE RESTRICT,
  CONSTRAINT ck_ejemplar_estado CHECK (estado IN ('disponible','prestado','perdido')),
  CONSTRAINT ck_ejemplar_condicion CHECK (condicion IN ('bueno','danado')),
  INDEX idx_ejemplar_libro_estado (id_libro, estado)
);

CREATE TABLE prestamo (
  id_prestamo       INT AUTO_INCREMENT PRIMARY KEY,
  id_usuario        INT NOT NULL,
  id_ejemplar       INT NOT NULL,
  id_empleado       INT NULL,
  fecha_solicitud   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  fecha_aprobacion  DATETIME NULL,
  fecha_prestamo    DATE NULL,
  fecha_vencimiento DATE NULL,
  estado            VARCHAR(12) NOT NULL DEFAULT 'solicitado',
  motivo_rechazo    VARCHAR(255) NULL,

  ejemplar_abierto  INT GENERATED ALWAYS AS (
    CASE WHEN estado IN ('solicitado','aprobado') THEN id_ejemplar END
  ) STORED,

  CONSTRAINT fk_prestamo_usuario  FOREIGN KEY (id_usuario)  REFERENCES usuario (id_usuario),
  CONSTRAINT fk_prestamo_ejemplar FOREIGN KEY (id_ejemplar) REFERENCES ejemplar (id_ejemplar),
  CONSTRAINT fk_prestamo_empleado FOREIGN KEY (id_empleado) REFERENCES empleado (id_empleado),

  CONSTRAINT ck_prestamo_estado
    CHECK (estado IN ('solicitado','aprobado','rechazado','devuelto')),
  CONSTRAINT ck_prestamo_fechas
    CHECK (fecha_vencimiento IS NULL OR fecha_prestamo IS NULL
           OR fecha_vencimiento > fecha_prestamo),
  CONSTRAINT ck_prestamo_coherencia CHECK (
       (estado = 'solicitado' AND id_empleado IS NULL AND fecha_aprobacion IS NULL)
    OR (estado = 'rechazado'  AND id_empleado IS NOT NULL AND motivo_rechazo IS NOT NULL)
    OR (estado IN ('aprobado','devuelto') AND id_empleado IS NOT NULL
        AND fecha_prestamo IS NOT NULL AND fecha_vencimiento IS NOT NULL)
  ),

  UNIQUE KEY uq_ejemplar_abierto (ejemplar_abierto),
  INDEX idx_prestamo_usuario (id_usuario, estado),
  INDEX idx_prestamo_estado_venc (estado, fecha_vencimiento),
  INDEX idx_prestamo_fecha (fecha_prestamo)
);

CREATE TABLE devolucion (
  id_devolucion    INT AUTO_INCREMENT PRIMARY KEY,
  id_prestamo      INT NOT NULL UNIQUE,
  id_empleado      INT NOT NULL,
  fecha_devolucion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  observaciones    VARCHAR(500) NULL,
  CONSTRAINT fk_devolucion_prestamo FOREIGN KEY (id_prestamo) REFERENCES prestamo (id_prestamo),
  CONSTRAINT fk_devolucion_empleado FOREIGN KEY (id_empleado) REFERENCES empleado (id_empleado)
);

CREATE TABLE multa (
  id_multa      INT AUTO_INCREMENT PRIMARY KEY,
  id_devolucion INT NOT NULL UNIQUE,
  monto         DECIMAL(10,2) NOT NULL,
  pagada        BOOLEAN NOT NULL DEFAULT FALSE,
  fecha_pago    DATE NULL,
  CONSTRAINT fk_multa_devolucion FOREIGN KEY (id_devolucion) REFERENCES devolucion (id_devolucion),
  CONSTRAINT ck_multa_monto CHECK (monto > 0),
  CONSTRAINT ck_multa_pago CHECK (
    (pagada = FALSE AND fecha_pago IS NULL) OR (pagada = TRUE AND fecha_pago IS NOT NULL)
  )
);

INSERT INTO politica_prestamo VALUES ('estudiante', 7, 3), ('docente', 15, 5);
INSERT INTO configuracion VALUES ('tarifa_multa_dia', '1000');