from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import connection, transaction

from catalogo.models import Autor, Categoria, Editorial, Libro
from ejemplares.models import Ejemplar
from prestamos.models import Configuracion
from usuarios.models import Empleado, PoliticaPrestamo, Usuario


CATEGORIAS_DATA = [
    "Novela Existencial y Psicológica",
    "Ficción Latinoamericana y Realismo Mágico",
    "Distopía y Crítica Social",
    "Poesía y Dramaturgia",
    "Filosofía, Ética y Psicoanálisis",
    "Ciencia y Biología Evolutiva",
    "Crónica, Contracultura y Ficción Contemporánea",
    "Clásicos de la Literatura Universal",
]

EDITORIALES_DATA = [
    "Editorial Alfaguara",
    "Seix Barral",
    "Tusquets Editores",
    "Anagrama",
    "Alianza Editorial",
    "Penguin Random House",
    "Editorial Herder",
    "Editorial Akal",
    "Fondo de Cultura Económica",
    "Publicación Independiente / KDP",
]

# 30 títulos universales, existenciales, reflexivos y de culto con copias físicas
LIBROS_SEED = [
    {
        "isbn": "978-8420482811",
        "titulo": "El evangelio según Jesucristo",
        "anio": 1991,
        "editorial": "Editorial Alfaguara",
        "categoria": "Novela Existencial y Psicológica",
        "autores": ["José Saramago"],
        "descripcion": "Una reinterpretación profundamente humana, heterodoxa y conmovedora de la vida de Jesús en conflicto con el destino y la divinidad.",
        "ubicacion_base": "Sala Literatura Universal - Pasillo B - Estante 1",
        "ejemplares": [
            ("BC-0001", "disponible", "bueno"),
            ("BC-0002", "disponible", "bueno"),
            ("BC-0003", "prestado", "bueno"),
            ("BC-0004", "disponible", "danado"),
        ],
    },
    {
        "isbn": "978-8432217272",
        "titulo": "El beso de la mujer araña",
        "anio": 1976,
        "editorial": "Seix Barral",
        "categoria": "Ficción Latinoamericana y Realismo Mágico",
        "autores": ["Manuel Puig"],
        "descripcion": "Dos prisioneros en una celda argentina comparten relatos de películas y tejen un vínculo íntimo atravesado por la política, el afecto y la represión.",
        "ubicacion_base": "Sala Literatura Latinoamericana - Pasillo C - Estante 2",
        "ejemplares": [
            ("BC-0005", "disponible", "bueno"),
            ("BC-0006", "prestado", "bueno"),
            ("BC-0007", "disponible", "bueno"),
        ],
    },
    {
        "isbn": "978-9588883656",
        "titulo": "En diciembre llegaban las brisas",
        "anio": 1987,
        "editorial": "Editorial Alfaguara",
        "categoria": "Ficción Latinoamericana y Realismo Mágico",
        "autores": ["Marvel Moreno"],
        "descripcion": "Retrato monumental y transgresor de la sociedad barranquillera a través de tres mujeres que desafían la opresión patriarcal bajo el viento del Caribe.",
        "ubicacion_base": "Sala Caribe y Colombia - Pasillo A - Estante 1",
        "ejemplares": [
            ("BC-0008", "disponible", "bueno"),
            ("BC-0009", "disponible", "bueno"),
            ("BC-0010", "perdido", "bueno"),
        ],
    },
    {
        "isbn": "979-8317427757",
        "titulo": "La Rata con Thinner: Y otras anécdotas cotidianas de la sociedad latinoamericana",
        "anio": 2024,
        "editorial": "Publicación Independiente / KDP",
        "categoria": "Crónica, Contracultura y Ficción Contemporánea",
        "autores": ["Omar Ramírez Ramírez"],
        "descripcion": "Antología de relatos crudos, bizarros y tragicómicos de internet y la cultura urbana de supervivencia en América Latina.",
        "ubicacion_base": "Sala Narrativa Contemporánea - Estante Z-9",
        "ejemplares": [
            ("BC-0011", "disponible", "bueno"),
            ("BC-0012", "disponible", "bueno"),
            ("BC-0013", "disponible", "danado"),
        ],
    },
    {
        "isbn": "978-8492913749",
        "titulo": "Indigno de ser humano",
        "anio": 1948,
        "editorial": "Alianza Editorial",
        "categoria": "Novela Existencial y Psicológica",
        "autores": ["Osamu Dazai"],
        "descripcion": "Testamento desgarrador sobre la alienación, el miedo a la sociedad y la imposibilidad de comprender a los demás seres humanos.",
        "ubicacion_base": "Sala Literatura Universal - Pasillo B - Estante 3",
        "ejemplares": [
            ("BC-0014", "disponible", "bueno"),
            ("BC-0015", "prestado", "bueno"),
            ("BC-0016", "disponible", "bueno"),
        ],
    },
    {
        "isbn": "978-8425432026",
        "titulo": "El hombre en busca de sentido",
        "anio": 1946,
        "editorial": "Editorial Herder",
        "categoria": "Filosofía, Ética y Psicoanálisis",
        "autores": ["Viktor Frankl"],
        "descripcion": "Memoria de supervivencia en campos de concentración nazis y desarrollo de la logoterapia sobre el propósito último de la existencia.",
        "ubicacion_base": "Sala Humanidades y Filosofía - Estante H-2",
        "ejemplares": [
            ("BC-0017", "disponible", "bueno"),
            ("BC-0018", "disponible", "bueno"),
            ("BC-0019", "prestado", "bueno"),
        ],
    },
    {
        "isbn": "978-8498388015",
        "titulo": "El cuento de la criada",
        "anio": 1985,
        "editorial": "Penguin Random House",
        "categoria": "Distopía y Crítica Social",
        "autores": ["Margaret Atwood"],
        "descripcion": "Distopía demoledora sobre la teocracia totalitaria de Gilead, el control absoluto de los cuerpos femeninos y la resistencia silenciosa.",
        "ubicacion_base": "Sala Ficción y Distopías - Estante D-1",
        "ejemplares": [
            ("BC-0020", "disponible", "bueno"),
            ("BC-0021", "disponible", "bueno"),
            ("BC-0022", "disponible", "bueno"),
        ],
    },
    {
        "isbn": "978-8446002932",
        "titulo": "El origen de la vida",
        "anio": 1936,
        "editorial": "Editorial Akal",
        "categoria": "Ciencia y Biología Evolutiva",
        "autores": ["Aleksandr Oparin", "J. B. S. Haldane"],
        "descripcion": "Obra fundacional de la bioquímica moderna sobre la evolución química prebiótica y el surgimiento de la vida en la Tierra primitiva.",
        "ubicacion_base": "Sala Ciencias Naturales - Estante BIO-1",
        "ejemplares": [
            ("BC-0023", "disponible", "bueno"),
            ("BC-0024", "prestado", "bueno"),
            ("BC-0025", "disponible", "danado"),
        ],
    },
    {
        "isbn": "978-8420664262",
        "titulo": "Sonetos del amor oscuro",
        "anio": 1936,
        "editorial": "Alianza Editorial",
        "categoria": "Poesía y Dramaturgia",
        "autores": ["Federico García Lorca"],
        "descripcion": "Once cumbres líricas del amor clandestino, el desgarro, el deseo apasionado y la muerte en el ocaso de la República española.",
        "ubicacion_base": "Sala Poesía y Teatro - Estante P-3",
        "ejemplares": [
            ("BC-0026", "disponible", "bueno"),
            ("BC-0027", "disponible", "bueno"),
            ("BC-0028", "perdido", "bueno"),
        ],
    },
    {
        "isbn": "978-8439732938",
        "titulo": "Temporada de huracanes",
        "anio": 2017,
        "editorial": "Penguin Random House",
        "categoria": "Crónica, Contracultura y Ficción Contemporánea",
        "autores": ["Fernanda Melchor"],
        "descripcion": "Polifonía torrencial y salvaje sobre el asesinato de La Bruja en un pueblo sumido en la violencia, la miseria y el desamparo.",
        "ubicacion_base": "Sala Narrativa Contemporánea - Estante NC-2",
        "ejemplares": [
            ("BC-0029", "disponible", "bueno"),
            ("BC-0030", "disponible", "bueno"),
            ("BC-0031", "disponible", "bueno"),
        ],
    },
    {
        "isbn": "978-8433998859",
        "titulo": "Nuestra parte de noche",
        "anio": 2019,
        "editorial": "Anagrama",
        "categoria": "Crónica, Contracultura y Ficción Contemporánea",
        "autores": ["Mariana Enríquez"],
        "descripcion": "Terror sobrenatural y horror político durante la dictadura argentina; un padre médium intenta salvar a su hijo de una logia devota a la Oscuridad.",
        "ubicacion_base": "Sala Narrativa Contemporánea - Estante NC-2",
        "ejemplares": [
            ("BC-0032", "disponible", "bueno"),
            ("BC-0033", "prestado", "bueno"),
            ("BC-0034", "disponible", "bueno"),
            ("BC-0035", "disponible", "bueno"),
        ],
    },
    {
        "isbn": "978-8490660300",
        "titulo": "Distancia de rescate",
        "anio": 2014,
        "editorial": "Alianza Editorial",
        "categoria": "Ficción Latinoamericana y Realismo Mágico",
        "autores": ["Samanta Schweblin"],
        "descripcion": "Pesadilla hipnótica en el campo argentino atravesada por el envenenamiento invisible de agrotóxicos y el miedo maternal.",
        "ubicacion_base": "Sala Literatura Latinoamericana - Pasillo C - Estante 1",
        "ejemplares": [
            ("BC-0036", "disponible", "bueno"),
            ("BC-0037", "disponible", "bueno"),
            ("BC-0038", "disponible", "bueno"),
        ],
    },
    {
        "isbn": "978-8432248238",
        "titulo": "El túnel",
        "anio": 1948,
        "editorial": "Seix Barral",
        "categoria": "Novela Existencial y Psicológica",
        "autores": ["Ernesto Sabato"],
        "descripcion": "La obsesión enfermiza del pintor Juan Pablo Castel por María Iribarne y el aislamiento insalvable de la conciencia humana.",
        "ubicacion_base": "Sala Literatura Universal - Pasillo B - Estante 2",
        "ejemplares": [
            ("BC-0039", "disponible", "bueno"),
            ("BC-0040", "disponible", "bueno"),
            ("BC-0041", "perdido", "danado"),
        ],
    },
    {
        "isbn": "978-8432215681",
        "titulo": "Sobre héroes y tumbas",
        "anio": 1961,
        "editorial": "Seix Barral",
        "categoria": "Novela Existencial y Psicológica",
        "autores": ["Ernesto Sabato"],
        "descripcion": "Una de las cumbres de la novela latinoamericana que incluye el célebre e inquietante Informe sobre Ciegos.",
        "ubicacion_base": "Sala Literatura Universal - Pasillo B - Estante 2",
        "ejemplares": [
            ("BC-0042", "disponible", "bueno"),
            ("BC-0043", "disponible", "bueno"),
            ("BC-0044", "prestado", "bueno"),
        ],
    },
    {
        "isbn": "978-8420651361",
        "titulo": "La metamorfosis",
        "anio": 1915,
        "editorial": "Alianza Editorial",
        "categoria": "Clásicos de la Literatura Universal",
        "autores": ["Franz Kafka"],
        "descripcion": "Gregorio Samsa amanece convertido en un monstruoso insecto; la deshumanización del trabajo y el rechazo familiar.",
        "ubicacion_base": "Sala Clásicos Universales - Pasillo K - Estante 1",
        "ejemplares": [
            ("BC-0045", "disponible", "bueno"),
            ("BC-0046", "prestado", "bueno"),
            ("BC-0047", "disponible", "bueno"),
        ],
    },
    {
        "isbn": "978-8420651378",
        "titulo": "El proceso",
        "anio": 1925,
        "editorial": "Alianza Editorial",
        "categoria": "Clásicos de la Literatura Universal",
        "autores": ["Franz Kafka"],
        "descripcion": "Josef K. es arrestado una mañana sin saber por qué, atrapado en los laberintos absurdos e implacables de la burocracia judicial.",
        "ubicacion_base": "Sala Clásicos Universales - Pasillo K - Estante 1",
        "ejemplares": [
            ("BC-0048", "disponible", "bueno"),
            ("BC-0049", "disponible", "bueno"),
            ("BC-0050", "disponible", "bueno"),
        ],
    },
    {
        "isbn": "978-8420668048",
        "titulo": "El extranjero",
        "anio": 1942,
        "editorial": "Alianza Editorial",
        "categoria": "Novela Existencial y Psicológica",
        "autores": ["Albert Camus"],
        "descripcion": "Meursault experimenta la vida con total indiferencia moral ante el calor de Argel, hasta que un disparo en la playa sella su destino.",
        "ubicacion_base": "Sala Existencialismo - Estante EX-1",
        "ejemplares": [
            ("BC-0051", "disponible", "bueno"),
            ("BC-0052", "disponible", "bueno"),
            ("BC-0053", "prestado", "bueno"),
        ],
    },
    {
        "isbn": "978-8420668055",
        "titulo": "La peste",
        "anio": 1947,
        "editorial": "Alianza Editorial",
        "categoria": "Novela Existencial y Psicológica",
        "autores": ["Albert Camus"],
        "descripcion": "Alegoría de la resistencia humana, la solidaridad y la lucha contra el absurdo ante una epidemia que sitia la ciudad de Orán.",
        "ubicacion_base": "Sala Existencialismo - Estante EX-1",
        "ejemplares": [
            ("BC-0054", "disponible", "bueno"),
            ("BC-0055", "disponible", "danado"),
            ("BC-0056", "disponible", "bueno"),
        ],
    },
    {
        "isbn": "978-8420684178",
        "titulo": "Crimen y castigo",
        "anio": 1866,
        "editorial": "Alianza Editorial",
        "categoria": "Clásicos de la Literatura Universal",
        "autores": ["Fiódor Dostoyevski"],
        "descripcion": "Raskólnikov asesina a una vieja usurera creyendo estar por encima de la moral ordinaria, hundiéndose en una espiral de fiebre y culpa.",
        "ubicacion_base": "Sala Novela Rusa y Clásicos - Estante R-1",
        "ejemplares": [
            ("BC-0057", "disponible", "bueno"),
            ("BC-0058", "disponible", "bueno"),
            ("BC-0059", "disponible", "bueno"),
        ],
    },
    {
        "isbn": "978-8420684185",
        "titulo": "Memorias del subsuelo",
        "anio": 1864,
        "editorial": "Alianza Editorial",
        "categoria": "Novela Existencial y Psicológica",
        "autores": ["Fiódor Dostoyevski"],
        "descripcion": "Monólogo visceral y cínico de un funcionario retirado que expone las contradicciones más oscuras de la naturaleza humana.",
        "ubicacion_base": "Sala Novela Rusa y Clásicos - Estante R-1",
        "ejemplares": [
            ("BC-0060", "disponible", "bueno"),
            ("BC-0061", "prestado", "bueno"),
            ("BC-0062", "disponible", "bueno"),
        ],
    },
    {
        "isbn": "978-8420674254",
        "titulo": "Demian",
        "anio": 1919,
        "editorial": "Alianza Editorial",
        "categoria": "Novela Existencial y Psicológica",
        "autores": ["Hermann Hesse"],
        "descripcion": "El despertar espiritual, el conflicto entre el mundo de la luz y las sombras, y el camino individual hacia uno mismo guiado por Max Demian.",
        "ubicacion_base": "Sala Literatura Universal - Pasillo B - Estante 4",
        "ejemplares": [
            ("BC-0063", "disponible", "bueno"),
            ("BC-0064", "disponible", "bueno"),
            ("BC-0065", "perdido", "bueno"),
        ],
    },
    {
        "isbn": "978-8420674261",
        "titulo": "El lobo estepario",
        "anio": 1927,
        "editorial": "Alianza Editorial",
        "categoria": "Novela Existencial y Psicológica",
        "autores": ["Hermann Hesse"],
        "descripcion": "Harry Haller debate su doble naturaleza entre hombre burgués refinado e instinto de lobo solitario marginado de la sociedad.",
        "ubicacion_base": "Sala Literatura Universal - Pasillo B - Estante 4",
        "ejemplares": [
            ("BC-0066", "disponible", "bueno"),
            ("BC-0067", "disponible", "bueno"),
            ("BC-0068", "disponible", "bueno"),
        ],
    },
    {
        "isbn": "978-8420482828",
        "titulo": "Ensayo sobre la ceguera",
        "anio": 1995,
        "editorial": "Editorial Alfaguara",
        "categoria": "Novela Existencial y Psicológica",
        "autores": ["José Saramago"],
        "descripcion": "Una epidemia de 'ceguera blanca' desnuda la fragilidad de la civilización y el descenso al instinto más salvaje del ser humano.",
        "ubicacion_base": "Sala Literatura Universal - Pasillo B - Estante 1",
        "ejemplares": [
            ("BC-0069", "disponible", "bueno"),
            ("BC-0070", "prestado", "bueno"),
            ("BC-0071", "disponible", "bueno"),
            ("BC-0072", "disponible", "danado"),
        ],
    },
    {
        "isbn": "978-8437604947",
        "titulo": "Pedro Páramo",
        "anio": 1955,
        "editorial": "Fondo de Cultura Económica",
        "categoria": "Ficción Latinoamericana y Realismo Mágico",
        "autores": ["Juan Rulfo"],
        "descripcion": "Juan Preciado llega a Comala en busca de su padre Pedro Páramo, descubriendo un pueblo fantasma poblado de murmullos de almas en pena.",
        "ubicacion_base": "Sala Literatura Latinoamericana - Pasillo C - Estante 3",
        "ejemplares": [
            ("BC-0073", "disponible", "bueno"),
            ("BC-0074", "disponible", "bueno"),
            ("BC-0075", "disponible", "bueno"),
        ],
    },
    {
        "isbn": "978-8433966636",
        "titulo": "Los detectives salvajes",
        "anio": 1998,
        "editorial": "Anagrama",
        "categoria": "Crónica, Contracultura y Ficción Contemporánea",
        "autores": ["Roberto Bolaño"],
        "descripcion": "Arturo Belano y Ulises Lima emprenden una búsqueda quijotesca por el desierto de Sonora tras las huellas de la poeta Cesárea Tinajero.",
        "ubicacion_base": "Sala Narrativa Contemporánea - Estante NC-1",
        "ejemplares": [
            ("BC-0076", "disponible", "bueno"),
            ("BC-0077", "disponible", "bueno"),
            ("BC-0078", "prestado", "bueno"),
        ],
    },
    {
        "isbn": "978-8483100653",
        "titulo": "La insoportable levedad del ser",
        "anio": 1984,
        "editorial": "Tusquets Editores",
        "categoria": "Novela Existencial y Psicológica",
        "autores": ["Milan Kundera"],
        "descripcion": "Tomás, Teresa, Sabina y Franz entretejen amor, celos, fidelidad y traición bajo la sombra de la Primavera de Praga de 1968.",
        "ubicacion_base": "Sala Literatura Universal - Pasillo B - Estante 5",
        "ejemplares": [
            ("BC-0079", "disponible", "bueno"),
            ("BC-0080", "disponible", "bueno"),
            ("BC-0081", "disponible", "bueno"),
        ],
    },
    {
        "isbn": "978-8432228032",
        "titulo": "El perfume: Historia de un asesino",
        "anio": 1985,
        "editorial": "Seix Barral",
        "categoria": "Novela Existencial y Psicológica",
        "autores": ["Patrick Süskind"],
        "descripcion": "Jean-Baptiste Grenouille nace con un olfato prodigioso pero sin olor propio, obsesionándose con destilar el perfume supremo de doncellas.",
        "ubicacion_base": "Sala Literatura Universal - Pasillo B - Estante 5",
        "ejemplares": [
            ("BC-0082", "disponible", "bueno"),
            ("BC-0083", "disponible", "bueno"),
            ("BC-0084", "perdido", "danado"),
        ],
    },
    {
        "isbn": "978-8499890944",
        "titulo": "1984",
        "anio": 1949,
        "editorial": "Penguin Random House",
        "categoria": "Distopía y Crítica Social",
        "autores": ["George Orwell"],
        "descripcion": "La vigilancia ubicua del Gran Hermano, la Policía del Pensamiento y la neolengua destruyen cualquier rastro de libertad individual.",
        "ubicacion_base": "Sala Ficción y Distopías - Estante D-2",
        "ejemplares": [
            ("BC-0085", "disponible", "bueno"),
            ("BC-0086", "disponible", "bueno"),
            ("BC-0087", "disponible", "bueno"),
        ],
    },
    {
        "isbn": "978-8499890951",
        "titulo": "Un mundo feliz",
        "anio": 1932,
        "editorial": "Penguin Random House",
        "categoria": "Distopía y Crítica Social",
        "autores": ["Aldous Huxley"],
        "descripcion": "Sociedad futurista condicionada biológicamente y adormecida por el soma y el placer superficial a cambio de la renuncia al dolor y la verdad.",
        "ubicacion_base": "Sala Ficción y Distopías - Estante D-2",
        "ejemplares": [
            ("BC-0088", "disponible", "bueno"),
            ("BC-0089", "prestado", "bueno"),
            ("BC-0090", "disponible", "bueno"),
        ],
    },
    {
        "isbn": "978-8497592208",
        "titulo": "Cien años de soledad",
        "anio": 1967,
        "editorial": "Penguin Random House",
        "categoria": "Ficción Latinoamericana y Realismo Mágico",
        "autores": ["Gabriel García Márquez"],
        "descripcion": "Saga fundacional de la estirpe Buendía en Macondo, marcada por la soledad, el incesto, las guerras y los prodigios del Caribe.",
        "ubicacion_base": "Sala Caribe y Colombia - Pasillo A - Estante 1",
        "ejemplares": [
            ("BC-0091", "disponible", "bueno"),
            ("BC-0092", "disponible", "bueno"),
            ("BC-0093", "disponible", "danado"),
        ],
    },
]


class Command(BaseCommand):
    help = (
        "Carga datos de prueba coherentes en la base de datos: políticas, categorías, "
        "editoriales, autores, 30 libros universales y más de 90 ejemplares físicos con estados variados."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--limpiar",
            action="store_true",
            help="Elimina los datos existentes de ejemplares y catálogo antes de volver a poblar.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["limpiar"]:
            self.stdout.write(self.style.WARNING("Limpiando datos previos..."))
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM multa;")
                cursor.execute("DELETE FROM devolucion;")
                cursor.execute("DELETE FROM prestamo;")
                cursor.execute("DELETE FROM ejemplar;")
                cursor.execute("DELETE FROM libro_autor;")
                cursor.execute("DELETE FROM libro;")
                cursor.execute("DELETE FROM autor;")
                cursor.execute("DELETE FROM categoria;")
                cursor.execute("DELETE FROM editorial;")

        # 1. Políticas de préstamo y configuración base
        PoliticaPrestamo.objects.update_or_create(
            rol="estudiante",
            defaults={"dias_prestamo": 7, "max_prestamos": 3},
        )
        PoliticaPrestamo.objects.update_or_create(
            rol="docente",
            defaults={"dias_prestamo": 15, "max_prestamos": 5},
        )
        Configuracion.objects.update_or_create(
            clave="tarifa_multa_dia",
            defaults={"valor": "1000"},
        )

        # 2. Categorías
        categorias_map = {}
        for nombre_cat in CATEGORIAS_DATA:
            cat, _ = Categoria.objects.get_or_create(nombre=nombre_cat)
            categorias_map[nombre_cat] = cat

        # 3. Editoriales
        editoriales_map = {}
        for nombre_ed in EDITORIALES_DATA:
            ed, _ = Editorial.objects.get_or_create(nombre=nombre_ed)
            editoriales_map[nombre_ed] = ed

        # 4. Libros, Autores y Ejemplares Físicos
        autores_map = {}
        total_libros = 0
        total_ejemplares = 0

        for item in LIBROS_SEED:
            libro, _ = Libro.objects.update_or_create(
                isbn=item["isbn"],
                defaults={
                    "titulo": item["titulo"],
                    "anio": item["anio"],
                    "descripcion": item["descripcion"],
                    "editorial": editoriales_map[item["editorial"]],
                    "categoria": categorias_map[item["categoria"]],
                    "eliminado": False,
                },
            )
            total_libros += 1

            # Asociar autores en tabla puente libro_autor
            for nombre_autor in item["autores"]:
                if nombre_autor not in autores_map:
                    autor_obj = Autor.objects.filter(nombre=nombre_autor).first()
                    if not autor_obj:
                        autor_obj = Autor.objects.create(nombre=nombre_autor)
                    autores_map[nombre_autor] = autor_obj
                else:
                    autor_obj = autores_map[nombre_autor]

                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT IGNORE INTO libro_autor (id_libro, id_autor) VALUES (%s, %s)",
                        [libro.id_libro, autor_obj.id_autor],
                    )

            # Crear ejemplares físicos para este libro
            for codigo, estado, condicion in item["ejemplares"]:
                Ejemplar.objects.update_or_create(
                    codigo_barras=codigo,
                    defaults={
                        "libro": libro,
                        "ubicacion": item["ubicacion_base"],
                        "estado": estado,
                        "condicion": condicion,
                        "eliminado": False,
                    },
                )
                total_ejemplares += 1

        # 5. Usuarios y Empleados básicos de prueba
        clave_demo = make_password("Biblioteca2026*")
        Empleado.objects.update_or_create(
            correo="bibliotecario@uninorte.edu.co",
            defaults={
                "nombres": "Carlos Mendoza (Bibliotecario)",
                "clave_hash": clave_demo,
                "rol": "bibliotecario",
            },
        )
        Empleado.objects.update_or_create(
            correo="admin.biblioteca@uninorte.edu.co",
            defaults={
                "nombres": "Laura Gómez (Administradora)",
                "clave_hash": clave_demo,
                "rol": "admin",
            },
        )

        rol_est = PoliticaPrestamo.objects.get(rol="estudiante")
        rol_doc = PoliticaPrestamo.objects.get(rol="docente")

        usuarios_demo = [
            ("200150101", "1045678901", "María José Pérez", "majo@uninorte.edu.co", rol_est, "Ingeniería de Sistemas", "activo"),
            ("200150102", "1045678902", "Natalia Rodríguez", "nati@uninorte.edu.co", rol_est, "Ingeniería de Sistemas", "activo"),
            ("200150103", "1045678903", "Jader Martínez", "jader@uninorte.edu.co", rol_est, "Ingeniería de Sistemas", "activo"),
            ("200150104", "1045678904", "Eliud Hernández", "eliud@uninorte.edu.co", rol_est, "Ingeniería de Sistemas", "activo"),
            ("DOC-9001", "72123456", "Dr. Roberto Angulo", "rangulo@uninorte.edu.co", rol_doc, "Departamento de Sistemas", "activo"),
            ("200150199", "1045678999", "Andrés Castro", "acastro@uninorte.edu.co", rol_est, "Ingeniería Industrial", "bloqueado"),
        ]
        for cod, ident, nom, corr, rol_obj, carr, est in usuarios_demo:
            Usuario.objects.update_or_create(
                codigo=cod,
                defaults={
                    "identificacion": ident,
                    "nombres": nom,
                    "correo": corr,
                    "clave_hash": clave_demo,
                    "rol": rol_obj,
                    "carrera": carr,
                    "estado": est,
                    "eliminado": False,
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeder ejecutado con éxito: {total_libros} libros universales y de culto, "
                f"{len(autores_map)} autores y {total_ejemplares} ejemplares físicos cargados."
            )
        )
