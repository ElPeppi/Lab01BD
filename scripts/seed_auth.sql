-- =============================================================================
-- Script 3 de 4: contraseñas de prueba (hash PBKDF2-SHA256 generado con Django)
-- Ejecutar después de seed_datos.sql. Credenciales de DEMOSTRACIÓN:
--   admin.biblioteca@uninorte.edu.co  /  Admin123!     (empleado, rol admin)
--   bibliotecario@uninorte.edu.co     /  Usuario123!   (empleado, rol bibliotecario)
--   cualquier usuario del seed        /  Usuario123!   (acastro está bloqueado a propósito)
-- En la BD solo se guarda el hash (algoritmo$iteraciones$sal$hash), nunca la clave.
-- =============================================================================

SET NAMES utf8mb4;
USE biblioteca;

UPDATE empleado SET clave_hash = 'pbkdf2_sha256$1500000$ufvW2PHjBu4s0IsfvrczIh$49bRFNcIq4XlM6nvMztTqfreENbgYRMl3YJgD1saqq0='
WHERE correo = 'admin.biblioteca@uninorte.edu.co';

UPDATE empleado SET clave_hash = 'pbkdf2_sha256$1500000$i3BTy2LIVfYl4e8PKZziYX$UtViLGsSRFpyPesZm/nGA4fGJzlyYZ0s+aqWVBl41jw='
WHERE correo = 'bibliotecario@uninorte.edu.co';

UPDATE usuario SET clave_hash = 'pbkdf2_sha256$1500000$i3BTy2LIVfYl4e8PKZziYX$UtViLGsSRFpyPesZm/nGA4fGJzlyYZ0s+aqWVBl41jw='
WHERE id_usuario > 0;  -- el WHERE evita el "safe update mode" de Workbench
