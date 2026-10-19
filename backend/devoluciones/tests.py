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


class BaseTest(TestCase):
    """Datos mínimos: un usuario, un empleado, un libro y una tarifa de 1000 por día."""

    def setUp(self):
        self.client = APIClient()
        Configuracion.objects.create(clave="tarifa_multa_dia", valor="1000")
        rol = PoliticaPrestamo.objects.create(rol="estudiante", dias_prestamo=7, max_prestamos=3)
        self.usuario = Usuario.objects.create(
            codigo="U1", identificacion="1", nombres="Ana", correo="ana@x.co",
            clave_hash="x", rol=rol)
        self.empleado = Empleado.objects.create(nombres="Beto", correo="beto@x.co", clave_hash="x")
        editorial = Editorial.objects.create(nombre="Ed")
        categoria = Categoria.objects.create(nombre="Cat")
        self.libro = Libro.objects.create(
            isbn="111", titulo="Don Quijote", anio=1605, editorial=editorial, categoria=categoria)
        # Las peticiones salen como el empleado (equivale a mandar su JWT)
        self.como_empleado()

    def como_empleado(self):
        self.client.force_authenticate(UsuarioToken("empleado", self.empleado.pk, "bibliotecario", "Beto"))

    def como_usuario(self, usuario=None):
        u = usuario or self.usuario
        self.client.force_authenticate(UsuarioToken("usuario", u.pk, "estudiante", u.nombres))

    def prestamo_aprobado(self, dias_vencido=0, codigo="E1", usuario=None):
        """Un préstamo aprobado que vence dentro de 3 días (o venció hace dias_vencido)."""
        ejemplar = Ejemplar.objects.create(
            codigo_barras=codigo, ubicacion="A1", libro=self.libro,
            estado=Ejemplar.ESTADO_PRESTADO)
        hoy = timezone.localdate()
        vence = hoy - timedelta(days=dias_vencido) if dias_vencido else hoy + timedelta(days=3)
        return Prestamo.objects.create(
            usuario=usuario or self.usuario, ejemplar=ejemplar, empleado=self.empleado,
            estado=Prestamo.APROBADO, fecha_aprobacion=timezone.now(),
            fecha_prestamo=vence - timedelta(days=7), fecha_vencimiento=vence)

    def devolver(self, prestamo, **extra):
        cuerpo = {"prestamo": prestamo.pk, **extra}
        return self.client.post("/api/devoluciones/", cuerpo, format="json")


class DevolucionTests(BaseTest):
    def test_devolucion_a_tiempo_no_genera_multa(self):
        prestamo = self.prestamo_aprobado()
        r = self.devolver(prestamo, observaciones="Todo bien")
        self.assertEqual(r.status_code, 201)
        self.assertIsNone(r.data["multa"])
        self.assertEqual(r.data["dias_retraso"], 0)
        prestamo.refresh_from_db()
        self.assertEqual(prestamo.estado, Prestamo.DEVUELTO)
        prestamo.ejemplar.refresh_from_db()
        self.assertEqual(prestamo.ejemplar.estado, Ejemplar.ESTADO_DISPONIBLE)
        self.assertEqual(Multa.objects.count(), 0)

    def test_devolucion_tardia_genera_multa_por_dias(self):
        prestamo = self.prestamo_aprobado(dias_vencido=4)
        r = self.devolver(prestamo)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["dias_retraso"], 4)
        multa = Multa.objects.get()
        self.assertEqual(multa.monto, Decimal("4000"))
        self.assertFalse(multa.pagada)
        self.assertEqual(r.data["multa"]["monto"], "4000.00")

    def test_tarifa_sale_de_configuracion(self):
        Configuracion.objects.filter(clave="tarifa_multa_dia").update(valor="250")
        self.devolver(self.prestamo_aprobado(dias_vencido=2))
        self.assertEqual(Multa.objects.get().monto, Decimal("500"))

    def test_ejemplar_danado_queda_marcado(self):
        prestamo = self.prestamo_aprobado()
        self.devolver(prestamo, condicion="danado")
        prestamo.ejemplar.refresh_from_db()
        self.assertEqual(prestamo.ejemplar.condicion, "danado")
        self.assertEqual(prestamo.ejemplar.estado, Ejemplar.ESTADO_DISPONIBLE)

    def test_no_se_puede_devolver_dos_veces(self):
        prestamo = self.prestamo_aprobado()
        self.assertEqual(self.devolver(prestamo).status_code, 201)
        r = self.devolver(prestamo)
        self.assertEqual(r.status_code, 409)
        self.assertEqual(Devolucion.objects.count(), 1)

    def test_prestamo_no_aprobado_se_rechaza(self):
        prestamo = self.prestamo_aprobado()
        # una solicitud no tiene empleado ni fecha de aprobación (lo exige ck_prestamo_coherencia)
        Prestamo.objects.filter(pk=prestamo.pk).update(
            estado=Prestamo.SOLICITADO, empleado=None, fecha_aprobacion=None)
        self.assertEqual(self.devolver(prestamo).status_code, 409)
        self.assertEqual(Devolucion.objects.count(), 0)

    def test_empleado_sale_del_token_y_no_del_cuerpo(self):
        prestamo = self.prestamo_aprobado()
        r = self.client.post(
            "/api/devoluciones/", {"prestamo": prestamo.pk, "empleado": 999}, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["empleado"], self.empleado.pk)

    def test_prestamo_inexistente_es_400(self):
        r = self.client.post("/api/devoluciones/", {"prestamo": 999}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_condicion_invalida_es_400(self):
        r = self.devolver(self.prestamo_aprobado(), condicion="roto")
        self.assertEqual(r.status_code, 400)

    def test_sin_tarifa_configurada_no_deja_a_medias(self):
        Configuracion.objects.all().delete()
        prestamo = self.prestamo_aprobado(dias_vencido=2)
        self.assertEqual(self.devolver(prestamo).status_code, 500)
        # la transacción se revierte: el préstamo sigue aprobado y no hay devolución
        prestamo.refresh_from_db()
        self.assertEqual(prestamo.estado, Prestamo.APROBADO)
        self.assertEqual(Devolucion.objects.count(), 0)

    def test_listado_y_filtro_con_multa(self):
        self.devolver(self.prestamo_aprobado(codigo="E1"))
        self.devolver(self.prestamo_aprobado(dias_vencido=1, codigo="E2"))
        self.assertEqual(len(self.client.get("/api/devoluciones/").data), 2)
        r = self.client.get("/api/devoluciones/?con_multa=true")
        self.assertEqual(len(r.data), 1)
        self.assertEqual(r.data[0]["libro_titulo"], "Don Quijote")


class MultaTests(BaseTest):
    def setUp(self):
        super().setUp()
        self.devolver(self.prestamo_aprobado(dias_vencido=3))
        self.multa = Multa.objects.get()

    def test_pagar_multa(self):
        r = self.client.post(f"/api/multas/{self.multa.pk}/pagar/")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.data["pagada"])
        self.multa.refresh_from_db()
        self.assertEqual(self.multa.fecha_pago, timezone.localdate())

    def test_no_se_paga_dos_veces(self):
        self.client.post(f"/api/multas/{self.multa.pk}/pagar/")
        r = self.client.post(f"/api/multas/{self.multa.pk}/pagar/")
        self.assertEqual(r.status_code, 409)

    def test_filtros_pagada_y_usuario(self):
        self.assertEqual(len(self.client.get("/api/multas/?pagada=false").data), 1)
        self.assertEqual(len(self.client.get("/api/multas/?pagada=true").data), 0)
        self.assertEqual(len(self.client.get(f"/api/multas/?usuario={self.usuario.pk}").data), 1)

    def test_multas_no_se_crean_ni_borran_por_la_api(self):
        self.assertEqual(self.client.post("/api/multas/", {"monto": 1}).status_code, 405)
        self.assertEqual(self.client.delete(f"/api/multas/{self.multa.pk}/").status_code, 405)


class PermisosTests(BaseTest):
    """Quién puede registrar devoluciones y cobrar multas, y quién ve qué."""

    def setUp(self):
        super().setUp()
        self.devolver(self.prestamo_aprobado(dias_vencido=2))  # Ana: 1 devolución con multa
        otro = Usuario.objects.create(
            codigo="U2", identificacion="2", nombres="Carlos", correo="carlos@x.co",
            clave_hash="x", rol=self.usuario.rol)
        self.otro = otro
        self.devolver(self.prestamo_aprobado(dias_vencido=1, codigo="E2", usuario=otro))
        self.multa_ana = Multa.objects.get(devolucion__prestamo__usuario=self.usuario)

    def test_sin_sesion_todo_es_401(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get("/api/devoluciones/").status_code, 401)
        self.assertEqual(self.client.get("/api/multas/").status_code, 401)
        self.assertEqual(self.client.post(f"/api/multas/{self.multa_ana.pk}/pagar/").status_code, 401)

    def test_usuario_no_registra_devoluciones_ni_paga_multas(self):
        self.como_usuario()
        r = self.client.post("/api/devoluciones/", {"prestamo": self.prestamo_aprobado(codigo="E3").pk}, format="json")
        self.assertEqual(r.status_code, 403)
        self.assertEqual(self.client.post(f"/api/multas/{self.multa_ana.pk}/pagar/").status_code, 403)

    def test_usuario_solo_ve_lo_suyo(self):
        self.como_usuario()
        devoluciones = self.client.get("/api/devoluciones/").data
        multas = self.client.get(f"/api/multas/?usuario={self.otro.pk}").data  # intenta ver las de otro
        self.assertEqual([d["usuario"] for d in devoluciones], [self.usuario.pk])
        self.assertEqual(multas, [])
        self.assertEqual(len(self.client.get("/api/multas/").data), 1)

    def test_personal_ve_todo(self):
        self.assertEqual(len(self.client.get("/api/devoluciones/").data), 2)
        self.assertEqual(len(self.client.get("/api/multas/").data), 2)

