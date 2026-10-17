-- =============================================================================
-- LABORATORIO 01 - BASES DE DATOS
-- Script de Carga de Datos de Prueba (Seeders): 30 Libros Universales y de Culto
-- y 93 Ejemplares Físicos
-- Ejecutar después de scripts/Inicializacion.sql
-- =============================================================================

USE biblioteca;

-- 1. Políticas de préstamo y Configuración
INSERT IGNORE INTO politica_prestamo (rol, dias_prestamo, max_prestamos) VALUES
('estudiante', 7, 3),
('docente', 15, 5);

INSERT IGNORE INTO configuracion (clave, valor) VALUES
('tarifa_multa_dia', '1000');

-- 2. Editoriales (10 editoriales)
INSERT INTO editorial (id_editorial, nombre) VALUES
(1, 'Editorial Alfaguara'),
(2, 'Seix Barral'),
(3, 'Tusquets Editores'),
(4, 'Anagrama'),
(5, 'Alianza Editorial'),
(6, 'Penguin Random House'),
(7, 'Editorial Herder'),
(8, 'Editorial Akal'),
(9, 'Fondo de Cultura Económica'),
(10, 'Publicación Independiente / KDP')
ON DUPLICATE KEY UPDATE nombre = VALUES(nombre);

-- 3. Categorías (8 categorías temáticas)
INSERT INTO categoria (id_categoria, nombre) VALUES
(1, 'Novela Existencial y Psicológica'),
(2, 'Ficción Latinoamericana y Realismo Mágico'),
(3, 'Distopía y Crítica Social'),
(4, 'Poesía y Dramaturgia'),
(5, 'Filosofía, Ética y Psicoanálisis'),
(6, 'Ciencia y Biología Evolutiva'),
(7, 'Crónica, Contracultura y Ficción Contemporánea'),
(8, 'Clásicos de la Literatura Universal')
ON DUPLICATE KEY UPDATE nombre = VALUES(nombre);

-- 4. Autores
INSERT INTO autor (id_autor, nombre) VALUES
(1, 'José Saramago'),
(2, 'Manuel Puig'),
(3, 'Marvel Moreno'),
(4, 'Omar Ramírez Ramírez'),
(5, 'Osamu Dazai'),
(6, 'Viktor Frankl'),
(7, 'Margaret Atwood'),
(8, 'Aleksandr Oparin'),
(9, 'J. B. S. Haldane'),
(10, 'Federico García Lorca'),
(11, 'Fernanda Melchor'),
(12, 'Mariana Enríquez'),
(13, 'Samanta Schweblin'),
(14, 'Ernesto Sabato'),
(15, 'Franz Kafka'),
(16, 'Albert Camus'),
(17, 'Fiódor Dostoyevski'),
(18, 'Hermann Hesse'),
(19, 'Juan Rulfo'),
(20, 'Roberto Bolaño'),
(21, 'Milan Kundera'),
(22, 'Patrick Süskind'),
(23, 'George Orwell'),
(24, 'Aldous Huxley'),
(25, 'Gabriel García Márquez')
ON DUPLICATE KEY UPDATE nombre = VALUES(nombre);

-- 5. Libros (30 Títulos solicitados)
INSERT INTO libro (id_libro, isbn, titulo, anio, descripcion, id_editorial, id_categoria, eliminado) VALUES
(1, '978-8420482811', 'El evangelio según Jesucristo', 1991, 'Una reinterpretación profundamente humana, heterodoxa y conmovedora de la vida de Jesús en conflicto con el destino y la divinidad.', 1, 1, FALSE),
(2, '978-8432217272', 'El beso de la mujer araña', 1976, 'Dos prisioneros en una celda argentina comparten relatos de películas y tejen un vínculo íntimo atravesado por la política, el afecto y la represión.', 2, 2, FALSE),
(3, '978-9588883656', 'En diciembre llegaban las brisas', 1987, 'Retrato monumental y transgresor de la sociedad barranquillera a través de tres mujeres que desafían la opresión patriarcal bajo el viento del Caribe.', 1, 2, FALSE),
(4, '979-8317427757', 'La Rata con Thinner: Y otras anécdotas cotidianas de la sociedad latinoamericana', 2024, 'Antología de relatos crudos, bizarros y tragicómicos de internet y la cultura urbana de supervivencia en América Latina.', 10, 7, FALSE),
(5, '978-8492913749', 'Indigno de ser humano', 1948, 'Testamento desgarrador sobre la alienación, el miedo a la sociedad y la imposibilidad de comprender a los demás seres humanos.', 5, 1, FALSE),
(6, '978-8425432026', 'El hombre en busca de sentido', 1946, 'Memoria de supervivencia en campos de concentración nazis y desarrollo de la logoterapia sobre el propósito último de la existencia.', 7, 5, FALSE),
(7, '978-8498388015', 'El cuento de la criada', 1985, 'Distopía demoledora sobre la teocracia totalitaria de Gilead, el control absoluto de los cuerpos femeninos y la resistencia silenciosa.', 6, 3, FALSE),
(8, '978-8446002932', 'El origen de la vida', 1936, 'Obra fundacional de la bioquímica moderna sobre la evolución química prebiótica y el surgimiento de la vida en la Tierra primitiva.', 8, 6, FALSE),
(9, '978-8420664262', 'Sonetos del amor oscuro', 1936, 'Once cumbres líricas del amor clandestino, el desgarro, el deseo apasionado y la muerte en el ocaso de la República española.', 5, 4, FALSE),
(10, '978-8439732938', 'Temporada de huracanes', 2017, 'Polifonía torrencial y salvaje sobre el asesinato de La Bruja en un pueblo sumido en la violencia, la miseria y el desamparo.', 6, 7, FALSE),
(11, '978-8433998859', 'Nuestra parte de noche', 2019, 'Terror sobrenatural y horror político durante la dictadura argentina; un padre médium intenta salvar a su hijo de una logia devota a la Oscuridad.', 4, 7, FALSE),
(12, '978-8490660300', 'Distancia de rescate', 2014, 'Pesadilla hipnótica en el campo argentino atravesada por el envenenamiento invisible de agrotóxicos y el miedo maternal.', 5, 2, FALSE),
(13, '978-8432248238', 'El túnel', 1948, 'La obsesión enfermiza del pintor Juan Pablo Castel por María Iribarne y el aislamiento insalvable de la conciencia humana.', 2, 1, FALSE),
(14, '978-8432215681', 'Sobre héroes y tumbas', 1961, 'Una de las cumbres de la novela latinoamericana que incluye el célebre e inquietante Informe sobre Ciegos.', 2, 1, FALSE),
(15, '978-8420651361', 'La metamorfosis', 1915, 'Gregorio Samsa amanece convertido en un monstruoso insecto; la deshumanización del trabajo y el rechazo familiar.', 5, 8, FALSE),
(16, '978-8420651378', 'El proceso', 1925, 'Josef K. es arrestado una mañana sin saber por qué, atrapado en los laberintos absurdos e implacables de la burocracia judicial.', 5, 8, FALSE),
(17, '978-8420668048', 'El extranjero', 1942, 'Meursault experimenta la vida con total indiferencia moral ante el calor de Argel, hasta que un disparo en la playa sella su destino.', 5, 1, FALSE),
(18, '978-8420668055', 'La peste', 1947, 'Alegoría de la resistencia humana, la solidaridad y la lucha contra el absurdo ante una epidemia que sitia la ciudad de Orán.', 5, 1, FALSE),
(19, '978-8420684178', 'Crimen y castigo', 1866, 'Raskólnikov asesina a una vieja usurera creyendo estar por encima de la moral ordinaria, hundiéndose en una espiral de fiebre y culpa.', 5, 8, FALSE),
(20, '978-8420684185', 'Memorias del subsuelo', 1864, 'Monólogo visceral y cínico de un funcionario retirado que expone las contradicciones más oscuras de la naturaleza humana.', 5, 1, FALSE),
(21, '978-8420674254', 'Demian', 1919, 'El despertar espiritual, el conflicto entre el mundo de la luz y las sombras, y el camino individual hacia uno mismo guiado por Max Demian.', 5, 1, FALSE),
(22, '978-8420674261', 'El lobo estepario', 1927, 'Harry Haller debate su doble naturaleza entre hombre burgués refinado e instinto de lobo solitario marginado de la sociedad.', 5, 1, FALSE),
(23, '978-8420482828', 'Ensayo sobre la ceguera', 1995, 'Una epidemia de ceguera blanca desnuda la fragilidad de la civilización y el descenso al instinto más salvaje del ser humano.', 1, 1, FALSE),
(24, '978-8437604947', 'Pedro Páramo', 1955, 'Juan Preciado llega a Comala en busca de su padre Pedro Páramo, descubriendo un pueblo fantasma poblado de murmullos de almas en pena.', 9, 2, FALSE),
(25, '978-8433966636', 'Los detectives salvajes', 1998, 'Arturo Belano y Ulises Lima emprenden una búsqueda quijotesca por el desierto de Sonora tras las huellas de la poeta Cesárea Tinajero.', 4, 7, FALSE),
(26, '978-8483100653', 'La insoportable levedad del ser', 1984, 'Tomás, Teresa, Sabina y Franz entretejen amor, celos, fidelidad y traición bajo la sombra de la Primavera de Praga de 1968.', 3, 1, FALSE),
(27, '978-8432228032', 'El perfume: Historia de un asesino', 1985, 'Jean-Baptiste Grenouille nace con un olfato prodigioso pero sin olor propio, obsesionándose con destilar el perfume supremo de doncellas.', 2, 1, FALSE),
(28, '978-8499890944', '1984', 1949, 'La vigilancia ubicua del Gran Hermano, la Policía del Pensamiento y la neolengua destruyen cualquier rastro de libertad individual.', 6, 3, FALSE),
(29, '978-8499890951', 'Un mundo feliz', 1932, 'Sociedad futurista condicionada biológicamente y adormecida por el soma y el placer superficial a cambio de la renuncia al dolor y la verdad.', 6, 3, FALSE),
(30, '978-8497592208', 'Cien años de soledad', 1967, 'Saga fundacional de la estirpe Buendía en Macondo, marcada por la soledad, el incesto, las guerras y los prodigios del Caribe.', 6, 2, FALSE)
ON DUPLICATE KEY UPDATE
  titulo = VALUES(titulo),
  anio = VALUES(anio),
  descripcion = VALUES(descripcion),
  id_editorial = VALUES(id_editorial),
  id_categoria = VALUES(id_categoria);

-- 6. Relación Libro_Autor
INSERT IGNORE INTO libro_autor (id_libro, id_autor) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4),
(5, 5),
(6, 6),
(7, 7),
(8, 8), (8, 9),
(9, 10),
(10, 11),
(11, 12),
(12, 13),
(13, 14),
(14, 14),
(15, 15),
(16, 15),
(17, 16),
(18, 16),
(19, 17),
(20, 17),
(21, 18),
(22, 18),
(23, 1),
(24, 19),
(25, 20),
(26, 21),
(27, 22),
(28, 23),
(29, 24),
(30, 25);

-- 7. Ejemplares Físicos (93 ejemplares en total)
INSERT INTO ejemplar (codigo_barras, ubicacion, estado, condicion, id_libro, eliminado) VALUES
('BC-0001', 'Sala Literatura Universal - Pasillo B - Estante 1', 'disponible', 'bueno', 1, FALSE),
('BC-0002', 'Sala Literatura Universal - Pasillo B - Estante 1', 'disponible', 'bueno', 1, FALSE),
('BC-0003', 'Sala Literatura Universal - Pasillo B - Estante 1', 'prestado',   'bueno', 1, FALSE),
('BC-0004', 'Sala Literatura Universal - Pasillo B - Estante 1', 'disponible', 'danado', 1, FALSE),

('BC-0005', 'Sala Literatura Latinoamericana - Pasillo C - Estante 2', 'disponible', 'bueno', 2, FALSE),
('BC-0006', 'Sala Literatura Latinoamericana - Pasillo C - Estante 2', 'prestado',   'bueno', 2, FALSE),
('BC-0007', 'Sala Literatura Latinoamericana - Pasillo C - Estante 2', 'disponible', 'bueno', 2, FALSE),

('BC-0008', 'Sala Caribe y Colombia - Pasillo A - Estante 1', 'disponible', 'bueno', 3, FALSE),
('BC-0009', 'Sala Caribe y Colombia - Pasillo A - Estante 1', 'disponible', 'bueno', 3, FALSE),
('BC-0010', 'Sala Caribe y Colombia - Pasillo A - Estante 1', 'perdido',    'bueno', 3, FALSE),

('BC-0011', 'Sala Narrativa Contemporánea - Estante Z-9', 'disponible', 'bueno', 4, FALSE),
('BC-0012', 'Sala Narrativa Contemporánea - Estante Z-9', 'disponible', 'bueno', 4, FALSE),
('BC-0013', 'Sala Narrativa Contemporánea - Estante Z-9', 'disponible', 'danado', 4, FALSE),

('BC-0014', 'Sala Literatura Universal - Pasillo B - Estante 3', 'disponible', 'bueno', 5, FALSE),
('BC-0015', 'Sala Literatura Universal - Pasillo B - Estante 3', 'prestado',   'bueno', 5, FALSE),
('BC-0016', 'Sala Literatura Universal - Pasillo B - Estante 3', 'disponible', 'bueno', 5, FALSE),

('BC-0017', 'Sala Humanidades y Filosofía - Estante H-2', 'disponible', 'bueno', 6, FALSE),
('BC-0018', 'Sala Humanidades y Filosofía - Estante H-2', 'disponible', 'bueno', 6, FALSE),
('BC-0019', 'Sala Humanidades y Filosofía - Estante H-2', 'prestado',   'bueno', 6, FALSE),

('BC-0020', 'Sala Ficción y Distopías - Estante D-1', 'disponible', 'bueno', 7, FALSE),
('BC-0021', 'Sala Ficción y Distopías - Estante D-1', 'disponible', 'bueno', 7, FALSE),
('BC-0022', 'Sala Ficción y Distopías - Estante D-1', 'disponible', 'bueno', 7, FALSE),

('BC-0023', 'Sala Ciencias Naturales - Estante BIO-1', 'disponible', 'bueno', 8, FALSE),
('BC-0024', 'Sala Ciencias Naturales - Estante BIO-1', 'prestado',   'bueno', 8, FALSE),
('BC-0025', 'Sala Ciencias Naturales - Estante BIO-1', 'disponible', 'danado', 8, FALSE),

('BC-0026', 'Sala Poesía y Teatro - Estante P-3', 'disponible', 'bueno', 9, FALSE),
('BC-0027', 'Sala Poesía y Teatro - Estante P-3', 'disponible', 'bueno', 9, FALSE),
('BC-0028', 'Sala Poesía y Teatro - Estante P-3', 'perdido',    'bueno', 9, FALSE),

('BC-0029', 'Sala Narrativa Contemporánea - Estante NC-2', 'disponible', 'bueno', 10, FALSE),
('BC-0030', 'Sala Narrativa Contemporánea - Estante NC-2', 'disponible', 'bueno', 10, FALSE),
('BC-0031', 'Sala Narrativa Contemporánea - Estante NC-2', 'disponible', 'bueno', 10, FALSE),

('BC-0032', 'Sala Narrativa Contemporánea - Estante NC-2', 'disponible', 'bueno', 11, FALSE),
('BC-0033', 'Sala Narrativa Contemporánea - Estante NC-2', 'prestado',   'bueno', 11, FALSE),
('BC-0034', 'Sala Narrativa Contemporánea - Estante NC-2', 'disponible', 'bueno', 11, FALSE),
('BC-0035', 'Sala Narrativa Contemporánea - Estante NC-2', 'disponible', 'bueno', 11, FALSE),

('BC-0036', 'Sala Literatura Latinoamericana - Pasillo C - Estante 1', 'disponible', 'bueno', 12, FALSE),
('BC-0037', 'Sala Literatura Latinoamericana - Pasillo C - Estante 1', 'disponible', 'bueno', 12, FALSE),
('BC-0038', 'Sala Literatura Latinoamericana - Pasillo C - Estante 1', 'disponible', 'bueno', 12, FALSE),

('BC-0039', 'Sala Literatura Universal - Pasillo B - Estante 2', 'disponible', 'bueno', 13, FALSE),
('BC-0040', 'Sala Literatura Universal - Pasillo B - Estante 2', 'disponible', 'bueno', 13, FALSE),
('BC-0041', 'Sala Literatura Universal - Pasillo B - Estante 2', 'perdido',    'danado', 13, FALSE),

('BC-0042', 'Sala Literatura Universal - Pasillo B - Estante 2', 'disponible', 'bueno', 14, FALSE),
('BC-0043', 'Sala Literatura Universal - Pasillo B - Estante 2', 'disponible', 'bueno', 14, FALSE),
('BC-0044', 'Sala Literatura Universal - Pasillo B - Estante 2', 'prestado',   'bueno', 14, FALSE),

('BC-0045', 'Sala Clásicos Universales - Pasillo K - Estante 1', 'disponible', 'bueno', 15, FALSE),
('BC-0046', 'Sala Clásicos Universales - Pasillo K - Estante 1', 'prestado',   'bueno', 15, FALSE),
('BC-0047', 'Sala Clásicos Universales - Pasillo K - Estante 1', 'disponible', 'bueno', 15, FALSE),

('BC-0048', 'Sala Clásicos Universales - Pasillo K - Estante 1', 'disponible', 'bueno', 16, FALSE),
('BC-0049', 'Sala Clásicos Universales - Pasillo K - Estante 1', 'disponible', 'bueno', 16, FALSE),
('BC-0050', 'Sala Clásicos Universales - Pasillo K - Estante 1', 'disponible', 'bueno', 16, FALSE),

('BC-0051', 'Sala Existencialismo - Estante EX-1', 'disponible', 'bueno', 17, FALSE),
('BC-0052', 'Sala Existencialismo - Estante EX-1', 'disponible', 'bueno', 17, FALSE),
('BC-0053', 'Sala Existencialismo - Estante EX-1', 'prestado',   'bueno', 17, FALSE),

('BC-0054', 'Sala Existencialismo - Estante EX-1', 'disponible', 'bueno', 18, FALSE),
('BC-0055', 'Sala Existencialismo - Estante EX-1', 'disponible', 'danado', 18, FALSE),
('BC-0056', 'Sala Existencialismo - Estante EX-1', 'disponible', 'bueno', 18, FALSE),

('BC-0057', 'Sala Novela Rusa y Clásicos - Estante R-1', 'disponible', 'bueno', 19, FALSE),
('BC-0058', 'Sala Novela Rusa y Clásicos - Estante R-1', 'disponible', 'bueno', 19, FALSE),
('BC-0059', 'Sala Novela Rusa y Clásicos - Estante R-1', 'disponible', 'bueno', 19, FALSE),

('BC-0060', 'Sala Novela Rusa y Clásicos - Estante R-1', 'disponible', 'bueno', 20, FALSE),
('BC-0061', 'Sala Novela Rusa y Clásicos - Estante R-1', 'prestado',   'bueno', 20, FALSE),
('BC-0062', 'Sala Novela Rusa y Clásicos - Estante R-1', 'disponible', 'bueno', 20, FALSE),

('BC-0063', 'Sala Literatura Universal - Pasillo B - Estante 4', 'disponible', 'bueno', 21, FALSE),
('BC-0064', 'Sala Literatura Universal - Pasillo B - Estante 4', 'disponible', 'bueno', 21, FALSE),
('BC-0065', 'Sala Literatura Universal - Pasillo B - Estante 4', 'perdido',    'bueno', 21, FALSE),

('BC-0066', 'Sala Literatura Universal - Pasillo B - Estante 4', 'disponible', 'bueno', 22, FALSE),
('BC-0067', 'Sala Literatura Universal - Pasillo B - Estante 4', 'disponible', 'bueno', 22, FALSE),
('BC-0068', 'Sala Literatura Universal - Pasillo B - Estante 4', 'disponible', 'bueno', 22, FALSE),

('BC-0069', 'Sala Literatura Universal - Pasillo B - Estante 1', 'disponible', 'bueno', 23, FALSE),
('BC-0070', 'Sala Literatura Universal - Pasillo B - Estante 1', 'prestado',   'bueno', 23, FALSE),
('BC-0071', 'Sala Literatura Universal - Pasillo B - Estante 1', 'disponible', 'bueno', 23, FALSE),
('BC-0072', 'Sala Literatura Universal - Pasillo B - Estante 1', 'disponible', 'danado', 23, FALSE),

('BC-0073', 'Sala Literatura Latinoamericana - Pasillo C - Estante 3', 'disponible', 'bueno', 24, FALSE),
('BC-0074', 'Sala Literatura Latinoamericana - Pasillo C - Estante 3', 'disponible', 'bueno', 24, FALSE),
('BC-0075', 'Sala Literatura Latinoamericana - Pasillo C - Estante 3', 'disponible', 'bueno', 24, FALSE),

('BC-0076', 'Sala Narrativa Contemporánea - Estante NC-1', 'disponible', 'bueno', 25, FALSE),
('BC-0077', 'Sala Narrativa Contemporánea - Estante NC-1', 'disponible', 'bueno', 25, FALSE),
('BC-0078', 'Sala Narrativa Contemporánea - Estante NC-1', 'prestado',   'bueno', 25, FALSE),

('BC-0079', 'Sala Literatura Universal - Pasillo B - Estante 5', 'disponible', 'bueno', 26, FALSE),
('BC-0080', 'Sala Literatura Universal - Pasillo B - Estante 5', 'disponible', 'bueno', 26, FALSE),
('BC-0081', 'Sala Literatura Universal - Pasillo B - Estante 5', 'disponible', 'bueno', 26, FALSE),

('BC-0082', 'Sala Literatura Universal - Pasillo B - Estante 5', 'disponible', 'bueno', 27, FALSE),
('BC-0083', 'Sala Literatura Universal - Pasillo B - Estante 5', 'disponible', 'bueno', 27, FALSE),
('BC-0084', 'Sala Literatura Universal - Pasillo B - Estante 5', 'perdido',    'danado', 27, FALSE),

('BC-0085', 'Sala Ficción y Distopías - Estante D-2', 'disponible', 'bueno', 28, FALSE),
('BC-0086', 'Sala Ficción y Distopías - Estante D-2', 'disponible', 'bueno', 28, FALSE),
('BC-0087', 'Sala Ficción y Distopías - Estante D-2', 'disponible', 'bueno', 28, FALSE),

('BC-0088', 'Sala Ficción y Distopías - Estante D-2', 'disponible', 'bueno', 29, FALSE),
('BC-0089', 'Sala Ficción y Distopías - Estante D-2', 'prestado',   'bueno', 29, FALSE),
('BC-0090', 'Sala Ficción y Distopías - Estante D-2', 'disponible', 'bueno', 29, FALSE),

('BC-0091', 'Sala Caribe y Colombia - Pasillo A - Estante 1', 'disponible', 'bueno', 30, FALSE),
('BC-0092', 'Sala Caribe y Colombia - Pasillo A - Estante 1', 'disponible', 'bueno', 30, FALSE),
('BC-0093', 'Sala Caribe y Colombia - Pasillo A - Estante 1', 'disponible', 'danado', 30, FALSE)
ON DUPLICATE KEY UPDATE
  ubicacion = VALUES(ubicacion),
  estado = VALUES(estado),
  condicion = VALUES(condicion),
  id_libro = VALUES(id_libro),
  eliminado = VALUES(eliminado);

-- 8. Empleados y Usuarios básicos de prueba
INSERT INTO empleado (nombres, correo, clave_hash, rol) VALUES
('Carlos Mendoza (Bibliotecario)', 'bibliotecario@uninorte.edu.co', 'pbkdf2_sha256$600000$demo$hashbibliotecario', 'bibliotecario'),
('Laura Gómez (Administradora)', 'admin.biblioteca@uninorte.edu.co', 'pbkdf2_sha256$600000$demo$hashadmin', 'admin')
ON DUPLICATE KEY UPDATE nombres = VALUES(nombres), rol = VALUES(rol);

INSERT INTO usuario (codigo, identificacion, nombres, correo, clave_hash, rol, carrera, estado, eliminado) VALUES
('200150101', '1045678901', 'María José Pérez', 'majo@uninorte.edu.co', 'pbkdf2_sha256$600000$demo$hash1', 'estudiante', 'Ingeniería de Sistemas', 'activo', FALSE),
('200150102', '1045678902', 'Natalia Rodríguez', 'nati@uninorte.edu.co', 'pbkdf2_sha256$600000$demo$hash2', 'estudiante', 'Ingeniería de Sistemas', 'activo', FALSE),
('200150103', '1045678903', 'Jader Martínez', 'jader@uninorte.edu.co', 'pbkdf2_sha256$600000$demo$hash3', 'estudiante', 'Ingeniería de Sistemas', 'activo', FALSE),
('200150104', '1045678904', 'Eliud Hernández', 'eliud@uninorte.edu.co', 'pbkdf2_sha256$600000$demo$hash4', 'estudiante', 'Ingeniería de Sistemas', 'activo', FALSE),
('DOC-9001',  '72123456',   'Dr. Roberto Angulo', 'rangulo@uninorte.edu.co', 'pbkdf2_sha256$600000$demo$hash5', 'docente', 'Departamento de Sistemas', 'activo', FALSE),
('200150199', '1045678999', 'Andrés Castro', 'acastro@uninorte.edu.co', 'pbkdf2_sha256$600000$demo$hash6', 'estudiante', 'Ingeniería Industrial', 'bloqueado', FALSE)
ON DUPLICATE KEY UPDATE nombres = VALUES(nombres), estado = VALUES(estado);
