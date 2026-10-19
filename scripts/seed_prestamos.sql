-- =============================================================================
-- Script 4 de 4: préstamos de ejemplo + conciliación de estados
-- Se puede ejecutar varias veces (idempotente). Ejecutar después de seed_auth.sql.
-- =============================================================================

SET NAMES utf8mb4;
USE biblioteca;

-- 1) Conciliación: el estado del ejemplar se deriva de sus préstamos.
--    Un ejemplar "prestado" sin préstamo aprobado vuelve a "disponible"...
UPDATE ejemplar e
SET e.estado = 'disponible'
WHERE e.estado = 'prestado'
  AND NOT EXISTS (SELECT 1 FROM prestamo p
                  WHERE p.id_ejemplar = e.id_ejemplar AND p.estado = 'aprobado');

--    ...y uno con préstamo aprobado queda "prestado".
UPDATE ejemplar e
SET e.estado = 'prestado'
WHERE EXISTS (SELECT 1 FROM prestamo p
              WHERE p.id_ejemplar = e.id_ejemplar AND p.estado = 'aprobado');

-- 2) Préstamos de ejemplo, con fechas relativas a hoy para que siempre haya
--    vigentes y vencidos. Cada INSERT solo ocurre si ese ejemplar no tiene
--    un préstamo abierto (respeta uq_ejemplar_abierto) y deja cupo libre a cada usuario.
--    (usuario, ejemplar, días desde el préstamo, días de plazo según su rol)
INSERT INTO prestamo (id_usuario, id_ejemplar, id_empleado, fecha_solicitud, fecha_aprobacion,
                      fecha_prestamo, fecha_vencimiento, estado)
SELECT u.id_usuario, e.id_ejemplar, emp.id_empleado,
       NOW() - INTERVAL d.hace DAY, NOW() - INTERVAL d.hace DAY,
       CURDATE() - INTERVAL d.hace DAY,
       CURDATE() - INTERVAL d.hace DAY + INTERVAL pol.dias_prestamo DAY,
       'aprobado'
FROM (SELECT 'majo@uninorte.edu.co'    AS correo, 'BC-0002' AS codigo, 2  AS hace UNION ALL  -- vigente
      SELECT 'nati@uninorte.edu.co',              'BC-0008',            12        UNION ALL  -- vencido 5 días
      SELECT 'jader@uninorte.edu.co',             'BC-0016',            9         UNION ALL  -- vencido 2 días
      SELECT 'rangulo@uninorte.edu.co',           'BC-0023',            3) d                -- docente, vigente
JOIN usuario u            ON u.correo = d.correo
JOIN politica_prestamo pol ON pol.rol = u.rol
JOIN ejemplar e           ON e.codigo_barras = d.codigo
JOIN empleado emp         ON emp.correo = 'bibliotecario@uninorte.edu.co'
WHERE e.estado = 'disponible' AND e.eliminado = FALSE
  AND NOT EXISTS (SELECT 1 FROM prestamo p
                  WHERE p.id_ejemplar = e.id_ejemplar AND p.estado IN ('solicitado','aprobado'));

-- 3) Los ejemplares recién prestados pasan a "prestado"
UPDATE ejemplar e
SET e.estado = 'prestado'
WHERE EXISTS (SELECT 1 FROM prestamo p
              WHERE p.id_ejemplar = e.id_ejemplar AND p.estado = 'aprobado');

-- Verificación: no debe haber incoherencias (ambas consultas deben dar 0)
SELECT COUNT(*) AS prestados_sin_prestamo FROM ejemplar e
WHERE e.estado = 'prestado'
  AND NOT EXISTS (SELECT 1 FROM prestamo p WHERE p.id_ejemplar = e.id_ejemplar AND p.estado = 'aprobado');
SELECT COUNT(*) AS aprobados_en_ejemplar_no_prestado FROM prestamo p
JOIN ejemplar e ON e.id_ejemplar = p.id_ejemplar
WHERE p.estado = 'aprobado' AND e.estado <> 'prestado';
