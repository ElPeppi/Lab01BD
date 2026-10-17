from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from django.urls import reverse

from .models import Ejemplar


class EjemplarModelAndUrlsTests(SimpleTestCase):
    def test_ejemplar_clean_valida_estado_y_condicion(self):
        ej = Ejemplar(
            codigo_barras="  BC-0001  ",
            ubicacion="  Sala General - Estante A1  ",
            estado=Ejemplar.ESTADO_DISPONIBLE,
            condicion=Ejemplar.CONDICION_BUENO,
            eliminado=False,
        )
        ej.clean()
        self.assertEqual(ej.codigo_barras, "BC-0001")
        self.assertEqual(ej.ubicacion, "Sala General - Estante A1")
        self.assertTrue(ej.esta_disponible)

    def test_ejemplar_estado_invalido_lanza_error(self):
        ej = Ejemplar(
            codigo_barras="BC-9999",
            ubicacion="Sala 1",
            estado="otro_estado",
            condicion="bueno",
        )
        with self.assertRaises(ValidationError):
            ej.clean()

    def test_urls_ejemplares_e_inventario_resuelven(self):
        self.assertEqual(reverse("ejemplares:lista"), "/ejemplares/")
        self.assertEqual(reverse("ejemplares:crear"), "/ejemplares/nuevo/")
        self.assertEqual(reverse("ejemplares:detalle", args=[1]), "/ejemplares/1/")
        self.assertEqual(reverse("ejemplares:editar", args=[1]), "/ejemplares/1/editar/")
        self.assertEqual(reverse("ejemplares:dar_baja", args=[1]), "/ejemplares/1/baja/")
        self.assertEqual(reverse("ejemplares:reporte_inventario"), "/ejemplares/inventario/")
        self.assertEqual(reverse("reporte_inventario_global"), "/reportes/inventario/")
