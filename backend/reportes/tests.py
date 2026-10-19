from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalogo.models import Categoria, Editorial, Libro
from ejemplares.models import Ejemplar
from prestamos.models import Configuracion, Devolucion, Multa, Prestamo
from usuarios.authentication import UsuarioToken
from usuarios.models import Empleado, PoliticaPrestamo, Usuario


class ReportesTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        Configuracion.objects.create(clave="tarifa_multa_dia", valor="1000")
        
        self.rol_estudiante = PoliticaPrestamo.objects.create(
            rol="estudiante", dias_prestamo=7, max_prestamos=3
        )
        self.usuario = Usuario.objects.create(
            codigo="2001",
            identificacion="1001",
            nombres="Carlos Mendoza",
            correo="carlos@uninorte.edu.co",
            clave_hash="hash123",
            rol=self.rol_estudiante,
            carrera="Ingeniería de Sistemas",
        )
        self.empleado = Empleado.objects.create(
            nombres="Laura Bibliotecaria",
            correo="laura@uninorte.edu.co",
            clave_hash="hash456",
            rol="bibliotecario",
        )
        self.editorial = Editorial.objects.create(nombre="Editorial Norma")
        self.categoria = Categoria.objects.create(nombre="Bases de Datos")
        self.libro = Libro.objects.create(
            isbn="978-0-123456-47-2",
            titulo="Fundamentos de Sistemas de Bases de Datos",
            anio=2021,
            editorial=self.editorial,
            categoria=self.categoria,
        )
        self.ejemplar1 = Ejemplar.objects.create(
            codigo_barras="EJ-001",
            ubicacion="Estante A-1",
            libro=self.libro,
            estado=Ejemplar.ESTADO_PRESTADO,
        )
        self.ejemplar2 = Ejemplar.objects.create(
            codigo_barras="EJ-002",
            ubicacion="Estante A-2",
            libro=self.libro,
            estado=Ejemplar.ESTADO_DISPONIBLE,
        )

        hoy = timezone.localdate()
        # Préstamo vencido (hace 4 días)
        self.prestamo_vencido = Prestamo.objects.create(
            usuario=self.usuario,
            ejemplar=self.ejemplar1,
            empleado=self.empleado,
            estado=Prestamo.APROBADO,
            fecha_solicitud=timezone.now() - timedelta(days=12),
            fecha_aprobacion=timezone.now() - timedelta(days=11),
            fecha_prestamo=hoy - timedelta(days=11),
            fecha_vencimiento=hoy - timedelta(days=4),
        )

    def autenticar_empleado(self):
        self.client.force_authenticate(
            UsuarioToken("empleado", self.empleado.pk, "bibliotecario", self.empleado.nombres)
        )

    def autenticar_usuario(self):
        self.client.force_authenticate(
            UsuarioToken("usuario", self.usuario.pk, "estudiante", self.usuario.nombres)
        )

    def test_reportes_requieren_permiso_empleado(self):
        # Sin token
        resp = self.client.get("/api/reportes/resumen/")
        self.assertEqual(resp.status_code, 401)

        # Como usuario estándar (estudiante)
        self.autenticar_usuario()
        resp = self.client.get("/api/reportes/resumen/")
        self.assertEqual(resp.status_code, 403)

    def test_resumen_reportes(self):
        self.autenticar_empleado()
        resp = self.client.get("/api/reportes/resumen/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("libros", data)
        self.assertIn("ejemplares", data)
        self.assertIn("prestamos", data)
        self.assertIn("multas", data)
        self.assertIn("usuarios", data)
        self.assertEqual(data["libros"]["total"], 1)
        self.assertEqual(data["ejemplares"]["total"], 2)
        self.assertEqual(data["prestamos"]["vencidos"], 1)

    def test_libros_populares(self):
        self.autenticar_empleado()
        resp = self.client.get("/api/reportes/libros-populares/")
        self.assertEqual(resp.status_code, 200)
        libros = resp.json()
        self.assertGreaterEqual(len(libros), 1)
        self.assertEqual(libros[0]["titulo"], "Fundamentos de Sistemas de Bases de Datos")
        self.assertEqual(libros[0]["total_prestamos"], 1)

    def test_morosos(self):
        self.autenticar_empleado()
        resp = self.client.get("/api/reportes/morosos/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["total_morosos"], 1)
        moroso = data["morosos"][0]
        self.assertEqual(moroso["usuario"]["codigo"], "2001")
        self.assertEqual(moroso["dias_retraso"], 4)
        self.assertEqual(Decimal(moroso["multa_estimada"]), Decimal("4000.00"))

    def test_exportar_csv(self):
        self.autenticar_empleado()
        resp = self.client.get("/api/reportes/exportar/?tipo=morosos")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "text/csv; charset=utf-8-sig")
        content = resp.content.decode("utf-8-sig")
        self.assertIn("Carlos Mendoza", content)
        self.assertIn("Fundamentos de Sistemas de Bases de Datos", content)
