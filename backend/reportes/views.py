import csv
from datetime import datetime
from decimal import Decimal

from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from catalogo.models import Categoria, Editorial, Libro
from ejemplares.models import Ejemplar
from prestamos.models import Configuracion, Devolucion, Multa, Prestamo
from usuarios.models import Usuario
from usuarios.permissions import EsEmpleado


def _obtener_tarifa_multa_dia():
    try:
        conf = Configuracion.objects.get(clave="tarifa_multa_dia")
        return Decimal(conf.valor)
    except Exception:
        return Decimal("1000.00")


class ResumenReportesView(APIView):
    """
    Indicadores clave (KPIs) generales del sistema de biblioteca.
    Solo accesible para el personal (empleados/admin).
    """
    permission_classes = [EsEmpleado]

    def get(self, request):
        hoy = timezone.localdate()

        # Libros y ejemplares
        total_libros = Libro.objects.filter(eliminado=False).count()
        ejemplares_qs = Ejemplar.objects.filter(eliminado=False)
        total_ejemplares = ejemplares_qs.count()
        ejemplares_disponibles = ejemplares_qs.filter(estado=Ejemplar.ESTADO_DISPONIBLE).count()
        ejemplares_prestados = ejemplares_qs.filter(estado=Ejemplar.ESTADO_PRESTADO).count()
        ejemplares_perdidos = ejemplares_qs.filter(estado=Ejemplar.ESTADO_PERDIDO).count()
        ejemplares_danados = ejemplares_qs.filter(condicion=Ejemplar.CONDICION_DANADO).count()

        # Préstamos
        prestamos_qs = Prestamo.objects.all()
        total_prestamos = prestamos_qs.count()
        prestamos_solicitados = prestamos_qs.filter(estado=Prestamo.SOLICITADO).count()
        prestamos_aprobados = prestamos_qs.filter(estado=Prestamo.APROBADO).count()
        prestamos_devueltos = prestamos_qs.filter(estado=Prestamo.DEVUELTO).count()
        prestamos_rechazados = prestamos_qs.filter(estado=Prestamo.RECHAZADO).count()
        prestamos_vencidos = prestamos_qs.filter(
            estado=Prestamo.APROBADO,
            fecha_vencimiento__lt=hoy
        ).count()

        # Multas y finanzas
        multas_qs = Multa.objects.all()
        total_multas = multas_qs.count()
        multas_pagadas = multas_qs.filter(pagada=True).count()
        multas_pendientes = multas_qs.filter(pagada=False).count()
        monto_total = multas_qs.aggregate(total=Sum("monto"))["total"] or Decimal("0.00")
        monto_pagado = multas_qs.filter(pagada=True).aggregate(total=Sum("monto"))["total"] or Decimal("0.00")
        monto_pendiente = multas_qs.filter(pagada=False).aggregate(total=Sum("monto"))["total"] or Decimal("0.00")

        # Usuarios
        usuarios_qs = Usuario.objects.filter(eliminado=False)
        total_usuarios = usuarios_qs.count()
        usuarios_activos = usuarios_qs.filter(estado="activo").count()
        usuarios_bloqueados = usuarios_qs.filter(estado="bloqueado").count()

        return Response({
            "libros": {
                "total": total_libros,
            },
            "ejemplares": {
                "total": total_ejemplares,
                "disponibles": ejemplares_disponibles,
                "prestados": ejemplares_prestados,
                "perdidos": ejemplares_perdidos,
                "danados": ejemplares_danados,
            },
            "prestamos": {
                "total": total_prestamos,
                "solicitados": prestamos_solicitados,
                "aprobados": prestamos_aprobados,
                "devueltos": prestamos_devueltos,
                "rechazados": prestamos_rechazados,
                "vencidos": prestamos_vencidos,
            },
            "multas": {
                "total": total_multas,
                "pagadas": multas_pagadas,
                "pendientes": multas_pendientes,
                "monto_total": str(monto_total),
                "monto_pagado": str(monto_pagado),
                "monto_pendiente": str(monto_pendiente),
            },
            "usuarios": {
                "total": total_usuarios,
                "activos": usuarios_activos,
                "bloqueados": usuarios_bloqueados,
            }
        })


class LibrosPopularesView(APIView):
    """
    Libros con mayor frecuencia de préstamos, con filtros por fechas, categoría y editorial.
    """
    permission_classes = [EsEmpleado]

    def get(self, request):
        p = request.query_params
        desde = p.get("desde")
        hasta = p.get("hasta")
        categoria_id = p.get("categoria")
        editorial_id = p.get("editorial")
        limit = int(p.get("limit", 10))

        filtro_prestamo = Q()
        if desde:
            fecha_d = parse_date(desde)
            if fecha_d:
                filtro_prestamo &= Q(ejemplar__prestamo__fecha_solicitud__date__gte=fecha_d)
        if hasta:
            fecha_h = parse_date(hasta)
            if fecha_h:
                filtro_prestamo &= Q(ejemplar__prestamo__fecha_solicitud__date__lte=fecha_h)

        qs = Libro.objects.filter(eliminado=False)
        if categoria_id and categoria_id.isdigit():
            qs = qs.filter(categoria_id=int(categoria_id))
        if editorial_id and editorial_id.isdigit():
            qs = qs.filter(editorial_id=int(editorial_id))

        qs = qs.annotate(
            total_prestamos=Count("ejemplar__prestamo", filter=filtro_prestamo),
            prestamos_activos=Count(
                "ejemplar__prestamo",
                filter=Q(ejemplar__prestamo__estado=Prestamo.APROBADO)
            ),
            ejemplares_disponibles=Count(
                "ejemplar",
                filter=Q(ejemplar__eliminado=False, ejemplar__estado=Ejemplar.ESTADO_DISPONIBLE),
                distinct=True
            ),
            ejemplares_totales=Count(
                "ejemplar",
                filter=Q(ejemplar__eliminado=False),
                distinct=True
            )
        ).select_related("categoria", "editorial").order_by("-total_prestamos", "titulo")[:limit]

        resultados = [
            {
                "id_libro": libro.id_libro,
                "isbn": libro.isbn,
                "titulo": libro.titulo,
                "anio": libro.anio,
                "categoria": libro.categoria.nombre if libro.categoria else None,
                "editorial": libro.editorial.nombre if libro.editorial else None,
                "total_prestamos": libro.total_prestamos,
                "prestamos_activos": libro.prestamos_activos,
                "ejemplares_disponibles": libro.ejemplares_disponibles,
                "ejemplares_totales": libro.ejemplares_totales,
            }
            for libro in qs
        ]

        return Response(resultados)


class MorososView(APIView):
    """
    Préstamos vencidos y morosidad actual: préstamos aprobados cuya fecha de vencimiento ya pasó.
    Calcula días de retraso y multa proyectada según la tarifa configurada.
    """
    permission_classes = [EsEmpleado]

    def get(self, request):
        p = request.query_params
        carrera = p.get("carrera")
        dias_minimos = int(p.get("dias_minimos", 0))

        hoy = timezone.localdate()
        tarifa = _obtener_tarifa_multa_dia()

        qs = (
            Prestamo.objects
            .filter(estado=Prestamo.APROBADO, fecha_vencimiento__lt=hoy)
            .select_related("usuario", "ejemplar__libro", "ejemplar")
            .order_by("fecha_vencimiento")
        )

        if carrera:
            qs = qs.filter(usuario__carrera__icontains=carrera)

        morosos = []
        for prestamo in qs:
            dias_retraso = (hoy - prestamo.fecha_vencimiento).days
            if dias_retraso < dias_minimos:
                continue

            multa_estimada = Decimal(dias_retraso) * tarifa
            morosos.append({
                "id_prestamo": prestamo.id_prestamo,
                "usuario": {
                    "id_usuario": prestamo.usuario.id_usuario,
                    "codigo": prestamo.usuario.codigo,
                    "identificacion": prestamo.usuario.identificacion,
                    "nombres": prestamo.usuario.nombres,
                    "correo": prestamo.usuario.correo,
                    "carrera": prestamo.usuario.carrera,
                    "rol": getattr(prestamo.usuario.rol, "rol", str(prestamo.usuario.rol)),
                },
                "ejemplar": {
                    "id_ejemplar": prestamo.ejemplar.id_ejemplar,
                    "codigo_barras": prestamo.ejemplar.codigo_barras,
                    "ubicacion": prestamo.ejemplar.ubicacion,
                    "libro_titulo": prestamo.ejemplar.libro.titulo,
                    "libro_isbn": prestamo.ejemplar.libro.isbn,
                },
                "fecha_prestamo": str(prestamo.fecha_prestamo),
                "fecha_vencimiento": str(prestamo.fecha_vencimiento),
                "dias_retraso": dias_retraso,
                "tarifa_dia": str(tarifa),
                "multa_estimada": str(multa_estimada),
            })

        return Response({
            "total_morosos": len(morosos),
            "tarifa_dia": str(tarifa),
            "total_multa_estimada": str(sum(Decimal(m["multa_estimada"]) for m in morosos)),
            "morosos": morosos
        })


class PrestamosPeriodoView(APIView):
    """
    Reporte histórico de préstamos por estado y rango de fechas.
    """
    permission_classes = [EsEmpleado]

    def get(self, request):
        p = request.query_params
        desde = p.get("desde")
        hasta = p.get("hasta")
        estado = p.get("estado")

        qs = Prestamo.objects.select_related("usuario", "ejemplar__libro").order_by("-fecha_solicitud")

        if desde:
            fecha_d = parse_date(desde)
            if fecha_d:
                qs = qs.filter(fecha_solicitud__date__gte=fecha_d)
        if hasta:
            fecha_h = parse_date(hasta)
            if fecha_h:
                qs = qs.filter(fecha_solicitud__date__lte=fecha_h)
        if estado and estado in ["solicitado", "aprobado", "rechazado", "devuelto"]:
            qs = qs.filter(estado=estado)

        conteo_estados = {
            "solicitado": qs.filter(estado=Prestamo.SOLICITADO).count(),
            "aprobado": qs.filter(estado=Prestamo.APROBADO).count(),
            "devuelto": qs.filter(estado=Prestamo.DEVUELTO).count(),
            "rechazado": qs.filter(estado=Prestamo.RECHAZADO).count(),
        }

        # Listado resumido para la tabla
        items = []
        for prestamo in qs[:100]:
            items.append({
                "id_prestamo": prestamo.id_prestamo,
                "estado": prestamo.estado,
                "usuario_codigo": prestamo.usuario.codigo,
                "usuario_nombres": prestamo.usuario.nombres,
                "libro_titulo": prestamo.ejemplar.libro.titulo,
                "ejemplar_codigo": prestamo.ejemplar.codigo_barras,
                "fecha_solicitud": prestamo.fecha_solicitud.isoformat() if prestamo.fecha_solicitud else None,
                "fecha_prestamo": str(prestamo.fecha_prestamo) if prestamo.fecha_prestamo else None,
                "fecha_vencimiento": str(prestamo.fecha_vencimiento) if prestamo.fecha_vencimiento else None,
                "vencido": prestamo.vencido,
                "dias_retraso": prestamo.dias_retraso,
            })

        return Response({
            "total": qs.count(),
            "conteo_estados": conteo_estados,
            "prestamos": items
        })


class MultasRecaudoView(APIView):
    """
    Reporte financiero y de control de multas: recaudado vs pendiente por cobrar.
    """
    permission_classes = [EsEmpleado]

    def get(self, request):
        p = request.query_params
        desde = p.get("desde")
        hasta = p.get("hasta")
        pagada_param = p.get("pagada")

        qs = Multa.objects.select_related(
            "devolucion__prestamo__usuario",
            "devolucion__prestamo__ejemplar__libro"
        ).order_by("-devolucion__fecha_devolucion")

        if desde:
            fecha_d = parse_date(desde)
            if fecha_d:
                qs = qs.filter(devolucion__fecha_devolucion__date__gte=fecha_d)
        if hasta:
            fecha_h = parse_date(hasta)
            if fecha_h:
                qs = qs.filter(devolucion__fecha_devolucion__date__lte=fecha_h)
        if pagada_param in ["true", "1"]:
            qs = qs.filter(pagada=True)
        elif pagada_param in ["false", "0"]:
            qs = qs.filter(pagada=False)

        total_multas = qs.count()
        pagadas_count = qs.filter(pagada=True).count()
        pendientes_count = qs.filter(pagada=False).count()
        monto_total = qs.aggregate(t=Sum("monto"))["t"] or Decimal("0.00")
        monto_pagado = qs.filter(pagada=True).aggregate(t=Sum("monto"))["t"] or Decimal("0.00")
        monto_pendiente = qs.filter(pagada=False).aggregate(t=Sum("monto"))["t"] or Decimal("0.00")

        detalle = []
        for m in qs[:100]:
            dev = m.devolucion
            prest = dev.prestamo
            detalle.append({
                "id_multa": m.id_multa,
                "monto": str(m.monto),
                "pagada": m.pagada,
                "fecha_pago": str(m.fecha_pago) if m.fecha_pago else None,
                "fecha_devolucion": dev.fecha_devolucion.isoformat() if dev.fecha_devolucion else None,
                "usuario_codigo": prest.usuario.codigo,
                "usuario_nombres": prest.usuario.nombres,
                "libro_titulo": prest.ejemplar.libro.titulo,
            })

        return Response({
            "resumen": {
                "total_multas": total_multas,
                "pagadas_count": pagadas_count,
                "pendientes_count": pendientes_count,
                "monto_total": str(monto_total),
                "monto_pagado": str(monto_pagado),
                "monto_pendiente": str(monto_pendiente),
            },
            "multas": detalle
        })


class UsuariosActividadView(APIView):
    """
    Usuarios con mayor actividad en préstamos y control de multas.
    """
    permission_classes = [EsEmpleado]

    def get(self, request):
        p = request.query_params
        rol = p.get("rol")
        carrera = p.get("carrera")
        limit = int(p.get("limit", 10))

        qs = Usuario.objects.filter(eliminado=False)
        if rol in ["estudiante", "docente"]:
            qs = qs.filter(rol__rol=rol)
        if carrera:
            qs = qs.filter(carrera__icontains=carrera)

        qs = qs.annotate(
            total_prestamos=Count("prestamo"),
            prestamos_activos=Count(
                "prestamo",
                filter=Q(prestamo__estado=Prestamo.APROBADO)
            ),
            prestamos_devueltos=Count(
                "prestamo",
                filter=Q(prestamo__estado=Prestamo.DEVUELTO)
            ),
            multas_count=Count("prestamo__devolucion__multa"),
            multas_pendientes=Count(
                "prestamo__devolucion__multa",
                filter=Q(prestamo__devolucion__multa__pagada=False)
            ),
            total_monto_multas=Sum("prestamo__devolucion__multa__monto")
        ).order_by("-total_prestamos", "nombres")[:limit]

        resultados = [
            {
                "id_usuario": u.id_usuario,
                "codigo": u.codigo,
                "nombres": u.nombres,
                "correo": u.correo,
                "carrera": u.carrera,
                "rol": getattr(u.rol, "rol", str(u.rol)),
                "estado": u.estado,
                "total_prestamos": u.total_prestamos,
                "prestamos_activos": u.prestamos_activos,
                "prestamos_devueltos": u.prestamos_devueltos,
                "multas_count": u.multas_count,
                "multas_pendientes": u.multas_pendientes,
                "total_monto_multas": str(u.total_monto_multas or Decimal("0.00")),
            }
            for u in qs
        ]

        return Response(resultados)


class ExportarCSVReportesView(APIView):
    """
    Exporta datos de reportes en formato CSV con codificación utf-8-sig (compatible con Excel).
    """
    permission_classes = [EsEmpleado]

    def get(self, request):
        tipo = request.query_params.get("tipo", "libros-populares")
        response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
        ahora_str = timezone.localdate().strftime("%Y%m%d")

        if tipo == "libros-populares":
            response["Content-Disposition"] = f'attachment; filename="reporte_libros_populares_{ahora_str}.csv"'
            writer = csv.writer(response)
            writer.writerow(["ID", "ISBN", "Título", "Año", "Categoría", "Editorial", "Total Préstamos", "Préstamos Activos", "Ejemplares Disponibles", "Total Ejemplares"])
            libros = Libro.objects.filter(eliminado=False).annotate(
                total_p=Count("ejemplar__prestamo"),
                activos_p=Count("ejemplar__prestamo", filter=Q(ejemplar__prestamo__estado=Prestamo.APROBADO)),
                disp=Count("ejemplar", filter=Q(ejemplar__eliminado=False, ejemplar__estado=Ejemplar.ESTADO_DISPONIBLE), distinct=True),
                tot=Count("ejemplar", filter=Q(ejemplar__eliminado=False), distinct=True)
            ).select_related("categoria", "editorial").order_by("-total_p")
            for libro in libros:
                writer.writerow([
                    libro.id_libro, libro.isbn, libro.titulo, libro.anio,
                    libro.categoria.nombre if libro.categoria else "",
                    libro.editorial.nombre if libro.editorial else "",
                    libro.total_p, libro.activos_p, libro.disp, libro.tot
                ])
            return response

        elif tipo == "morosos":
            response["Content-Disposition"] = f'attachment; filename="reporte_morosos_{ahora_str}.csv"'
            writer = csv.writer(response)
            writer.writerow(["ID Préstamo", "Código Usuario", "Nombre Usuario", "Correo", "Carrera", "Código Ejemplar", "Título Libro", "Fecha Préstamo", "Fecha Vencimiento", "Días Retraso", "Multa Estimada"])
            hoy = timezone.localdate()
            tarifa = _obtener_tarifa_multa_dia()
            prestamos = Prestamo.objects.filter(
                estado=Prestamo.APROBADO, fecha_vencimiento__lt=hoy
            ).select_related("usuario", "ejemplar__libro").order_by("fecha_vencimiento")
            for p in prestamos:
                retraso = (hoy - p.fecha_vencimiento).days
                multa = Decimal(retraso) * tarifa
                writer.writerow([
                    p.id_prestamo, p.usuario.codigo, p.usuario.nombres, p.usuario.correo,
                    p.usuario.carrera or "", p.ejemplar.codigo_barras, p.ejemplar.libro.titulo,
                    p.fecha_prestamo, p.fecha_vencimiento, retraso, multa
                ])
            return response

        elif tipo == "multas":
            response["Content-Disposition"] = f'attachment; filename="reporte_multas_{ahora_str}.csv"'
            writer = csv.writer(response)
            writer.writerow(["ID Multa", "Código Usuario", "Nombre Usuario", "Título Libro", "Monto", "Pagada", "Fecha Pago", "Fecha Devolución"])
            multas = Multa.objects.select_related(
                "devolucion__prestamo__usuario", "devolucion__prestamo__ejemplar__libro"
            ).order_by("-devolucion__fecha_devolucion")
            for m in multas:
                dev = m.devolucion
                prest = dev.prestamo
                writer.writerow([
                    m.id_multa, prest.usuario.codigo, prest.usuario.nombres,
                    prest.ejemplar.libro.titulo, m.monto, "SÍ" if m.pagada else "NO",
                    m.fecha_pago or "", dev.fecha_devolucion.strftime("%Y-%m-%d %H:%M") if dev.fecha_devolucion else ""
                ])
            return response

        return Response({"error": "Tipo de reporte no válido."}, status=status.HTTP_400_BAD_REQUEST)
