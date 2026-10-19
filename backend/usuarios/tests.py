from datetime import timedelta

from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalogo.models import Categoria, Editorial, Libro
from ejemplares.models import Ejemplar
from prestamos.models import Devolucion, Multa, Prestamo

from .authentication import UsuarioToken
from .models import Empleado, PoliticaPrestamo, Usuario


class BaseTest(TestCase):
    """Dos usuarios, un admin y un bibliotecario. Las peticiones salen como el admin."""

    def setUp(self):
        self.client = APIClient()
        self.rol = PoliticaPrestamo.objects.create(rol="estudiante", dias_prestamo=7, max_prestamos=3)
        PoliticaPrestamo.objects.create(rol="docente", dias_prestamo=15, max_prestamos=5)
        self.ana = Usuario.objects.create(
            codigo="U1", identificacion="1", nombres="Ana", correo="ana@x.co",
            clave_hash="x", rol=self.rol)
        self.luis = Usuario.objects.create(
            codigo="U2", identificacion="2", nombres="Luis", correo="luis@x.co",
            clave_hash="x", rol=self.rol)
        self.admin = Empleado.objects.create(nombres="Admin", correo="admin@x.co", clave_hash="x", rol="admin")
        self.biblio = Empleado.objects.create(nombres="Beto", correo="beto@x.co", clave_hash="x")
        self.client.force_authenticate(UsuarioToken("empleado", self.admin.pk, "admin", "Admin"))

    def url(self, usuario):
        return f"/api/usuarios/{usuario.pk}/"

    def ejemplar(self, codigo="E1"):
        libro, _ = Libro.objects.get_or_create(
            isbn="111", defaults={
                "titulo": "Don Quijote", "anio": 1605,
                "editorial": Editorial.objects.create(nombre="Ed"),
                "categoria": Categoria.objects.create(nombre="Cat"),
            })
        return Ejemplar.objects.create(codigo_barras=codigo, ubicacion="A1", libro=libro)


class EdicionTests(BaseTest):
    def test_consultar_un_usuario(self):
        r = self.client.get(self.url(self.ana))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["codigo"], "U1")
        self.assertNotIn("clave", r.data)

    def test_editar_datos(self):
        r = self.client.patch(self.url(self.ana), {"nombres": " Ana María ", "rol": "docente",
                                                   "carrera": "Derecho"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.ana.refresh_from_db()
        self.assertEqual((self.ana.nombres, self.ana.rol_id, self.ana.carrera), ("Ana María", "docente", "Derecho"))

    def test_editar_con_sus_mismos_datos_no_cuenta_como_repetido(self):
        r = self.client.put(self.url(self.ana), {
            "codigo": "U1", "identificacion": "1", "nombres": "Ana", "correo": "ana@x.co",
            "rol": "estudiante", "carrera": "",
        }, format="json")
        self.assertEqual(r.status_code, 200)

    def test_codigo_de_otro_usuario_es_400(self):
        r = self.client.patch(self.url(self.ana), {"codigo": "U2"}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("codigo", r.data)

    def test_editar_sin_clave_conserva_la_anterior_y_con_clave_la_cambia(self):
        self.client.patch(self.url(self.ana), {"nombres": "Ana"}, format="json")
        self.ana.refresh_from_db()
        self.assertEqual(self.ana.clave_hash, "x")
        self.client.patch(self.url(self.ana), {"clave": "NuevaClave1"}, format="json")
        self.ana.refresh_from_db()
        self.assertTrue(check_password("NuevaClave1", self.ana.clave_hash))

    def test_registrar_exige_clave_inicial(self):
        r = self.client.post("/api/usuarios/", {
            "codigo": "U3", "identificacion": "3", "nombres": "Eva", "correo": "eva@x.co", "rol": "estudiante",
        }, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("clave", r.data)

    def test_bibliotecario_no_puede_editar(self):
        self.client.force_authenticate(UsuarioToken("empleado", self.biblio.pk, "bibliotecario", "Beto"))
        self.assertEqual(self.client.get(self.url(self.ana)).status_code, 200)
        r = self.client.patch(self.url(self.ana), {"nombres": "Otra"}, format="json")
        self.assertEqual(r.status_code, 403)


class BloqueoTests(BaseTest):
    def test_bloquear_y_desbloquear(self):
        r = self.client.patch(self.url(self.ana), {"estado": "bloqueado"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.ana.refresh_from_db()
        self.assertEqual(self.ana.estado, "bloqueado")
        self.client.patch(self.url(self.ana), {"estado": "activo"}, format="json")
        self.ana.refresh_from_db()
        self.assertEqual(self.ana.estado, "activo")

    def test_estado_invalido_es_400(self):
        r = self.client.patch(self.url(self.ana), {"estado": "suspendido"}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_usuario_bloqueado_no_puede_pedir_prestamos(self):
        ejemplar = self.ejemplar()
        self.client.patch(self.url(self.ana), {"estado": "bloqueado"}, format="json")
        self.client.force_authenticate(UsuarioToken("usuario", self.ana.pk, "estudiante", "Ana"))
        r = self.client.post("/api/prestamos/", {"libro": ejemplar.libro_id}, format="json")
        self.assertEqual(r.status_code, 409)
        self.assertEqual(Prestamo.objects.count(), 0)


class EliminacionTests(BaseTest):
    def test_eliminar_es_logico_y_lo_saca_del_listado(self):
        r = self.client.delete(self.url(self.ana))
        self.assertEqual(r.status_code, 204)
        self.ana.refresh_from_db()
        self.assertTrue(self.ana.eliminado)
        codigos = [u["codigo"] for u in self.client.get("/api/usuarios/").data]
        self.assertEqual(codigos, ["U2"])
        self.assertEqual(self.client.get(self.url(self.ana)).status_code, 404)

    def test_no_se_elimina_con_un_prestamo_en_curso(self):
        Prestamo.objects.create(usuario=self.ana, ejemplar=self.ejemplar())  # solicitud pendiente
        r = self.client.delete(self.url(self.ana))
        self.assertEqual(r.status_code, 409)
        self.ana.refresh_from_db()
        self.assertFalse(self.ana.eliminado)

    def test_no_se_elimina_con_multas_sin_pagar(self):
        hoy = timezone.localdate()
        prestamo = Prestamo.objects.create(
            usuario=self.ana, ejemplar=self.ejemplar(), empleado=self.biblio, estado=Prestamo.DEVUELTO,
            fecha_aprobacion=timezone.now(), fecha_prestamo=hoy - timedelta(days=10),
            fecha_vencimiento=hoy - timedelta(days=3))
        devolucion = Devolucion.objects.create(prestamo=prestamo, empleado=self.biblio)
        multa = Multa.objects.create(devolucion=devolucion, monto=3000)
        self.assertEqual(self.client.delete(self.url(self.ana)).status_code, 409)

        Multa.objects.filter(pk=multa.pk).update(pagada=True, fecha_pago=hoy)
        self.assertEqual(self.client.delete(self.url(self.ana)).status_code, 204)

    def test_bibliotecario_no_puede_eliminar(self):
        self.client.force_authenticate(UsuarioToken("empleado", self.biblio.pk, "bibliotecario", "Beto"))
        self.assertEqual(self.client.delete(self.url(self.ana)).status_code, 403)
