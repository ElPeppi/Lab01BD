import json
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST

from catalogo.models import Categoria, Libro, LibroAutor
from prestamos.models import Prestamo
from .forms import EjemplarForm, FiltroEjemplarForm
from .models import Ejemplar


def _calcular_resumen_estados(queryset):
    """Calcula totales y porcentajes desglosados por estado y condición."""
    agregados = queryset.aggregate(
        total=Count("id_ejemplar"),
        disponibles=Count("id_ejemplar", filter=Q(estado=Ejemplar.ESTADO_DISPONIBLE)),
        prestados=Count("id_ejemplar", filter=Q(estado=Ejemplar.ESTADO_PRESTADO)),
        perdidos=Count("id_ejemplar", filter=Q(estado=Ejemplar.ESTADO_PERDIDO)),
        buenos=Count("id_ejemplar", filter=Q(condicion=Ejemplar.CONDICION_BUENO)),
        danados=Count("id_ejemplar", filter=Q(condicion=Ejemplar.CONDICION_DANADO)),
    )
    total = agregados["total"] or 0
    agregados["pct_disponibles"] = round((agregados["disponibles"] / total) * 100, 1) if total else 0.0
    agregados["pct_prestados"] = round((agregados["prestados"] / total) * 100, 1) if total else 0.0
    agregados["pct_perdidos"] = round((agregados["perdidos"] / total) * 100, 1) if total else 0.0
    return agregados


def lista_ejemplares(request):
    """Vista para listar y filtrar ejemplares físicos."""
    form_filtro = FiltroEjemplarForm(request.GET or None)
    qs = Ejemplar.objects.select_related("libro", "libro__editorial", "libro__categoria")

    mostrar_bajas = False
    if form_filtro.is_valid():
        q = form_filtro.cleaned_data.get("q")
        libro = form_filtro.cleaned_data.get("libro")
        categoria = form_filtro.cleaned_data.get("categoria")
        estado = form_filtro.cleaned_data.get("estado")
        condicion = form_filtro.cleaned_data.get("condicion")
        mostrar_bajas = form_filtro.cleaned_data.get("mostrar_bajas")

        if not mostrar_bajas:
            qs = qs.filter(eliminado=False)
        if q:
            qs = qs.filter(
                Q(codigo_barras__icontains=q)
                | Q(ubicacion__icontains=q)
                | Q(libro__titulo__icontains=q)
                | Q(libro__isbn__icontains=q)
            )
        if libro:
            qs = qs.filter(libro=libro)
        if categoria:
            qs = qs.filter(libro__categoria=categoria)
        if estado:
            qs = qs.filter(estado=estado)
        if condicion:
            qs = qs.filter(condicion=condicion)
    else:
        qs = qs.filter(eliminado=False)

    qs = qs.order_by("libro__titulo", "codigo_barras")
    resumen = _calcular_resumen_estados(qs)

    context = {
        "ejemplares": qs,
        "form_filtro": form_filtro,
        "resumen": resumen,
        "mostrar_bajas": mostrar_bajas,
    }
    return render(request, "ejemplares/lista_ejemplares.html", context)


def crear_ejemplar(request):
    """Vista para registrar un nuevo ejemplar físico."""
    initial = {}
    libro_id = request.GET.get("libro")
    if libro_id and libro_id.isdigit():
        initial["libro"] = int(libro_id)

    if request.method == "POST":
        form = EjemplarForm(request.POST)
        if form.is_valid():
            ejemplar = form.save(commit=False)
            ejemplar.eliminado = False
            ejemplar.save()
            messages.success(
                request,
                f"Ejemplar '{ejemplar.codigo_barras}' registrado exitosamente para '{ejemplar.libro.titulo}'.",
            )
            return redirect("ejemplares:lista")
    else:
        form = EjemplarForm(initial=initial)

    return render(
        request,
        "ejemplares/form_ejemplar.html",
        {
            "form": form,
            "titulo_pagina": "Registrar Nuevo Ejemplar Físico",
            "accion": "Registrar Ejemplar",
            "es_edicion": False,
        },
    )


def detalle_ejemplar(request, pk):
    """Vista con el detalle completo del ejemplar y su historial de préstamos."""
    ejemplar = get_object_or_404(
        Ejemplar.objects.select_related("libro", "libro__editorial", "libro__categoria"),
        pk=pk,
    )
    autores = [
        la.autor
        for la in LibroAutor.objects.filter(libro=ejemplar.libro).select_related("autor")
    ]
    historial_prestamos = (
        Prestamo.objects.filter(ejemplar=ejemplar)
        .select_related("usuario", "empleado")
        .order_by("-fecha_solicitud")
    )
    otros_ejemplares = (
        Ejemplar.objects.filter(libro=ejemplar.libro, eliminado=False)
        .exclude(pk=ejemplar.pk)
        .order_by("codigo_barras")
    )

    return render(
        request,
        "ejemplares/detalle_ejemplar.html",
        {
            "ejemplar": ejemplar,
            "autores": autores,
            "historial_prestamos": historial_prestamos,
            "otros_ejemplares": otros_ejemplares,
        },
    )


def editar_ejemplar(request, pk):
    """Vista para editar un ejemplar físico existente."""
    ejemplar = get_object_or_404(Ejemplar.objects.select_related("libro"), pk=pk)

    if request.method == "POST":
        form = EjemplarForm(request.POST, instance=ejemplar)
        if form.is_valid():
            ejemplar = form.save()
            messages.success(
                request,
                f"Ejemplar '{ejemplar.codigo_barras}' actualizado correctamente.",
            )
            return redirect("ejemplares:detalle", pk=ejemplar.pk)
    else:
        form = EjemplarForm(instance=ejemplar)

    return render(
        request,
        "ejemplares/form_ejemplar.html",
        {
            "form": form,
            "ejemplar": ejemplar,
            "titulo_pagina": f"Editar Ejemplar {ejemplar.codigo_barras}",
            "accion": "Guardar Cambios",
            "es_edicion": True,
        },
    )


def dar_baja_ejemplar(request, pk):
    """Vista para dar de baja lógica (eliminado=True) a un ejemplar físico."""
    ejemplar = get_object_or_404(Ejemplar.objects.select_related("libro"), pk=pk)

    if ejemplar.estado == Ejemplar.ESTADO_PRESTADO:
        messages.error(
            request,
            f"No se puede dar de baja el ejemplar '{ejemplar.codigo_barras}' porque actualmente se encuentra PRESTADO.",
        )
        return redirect("ejemplares:detalle", pk=ejemplar.pk)

    if request.method == "POST":
        ejemplar.eliminado = True
        ejemplar.save(update_fields=["eliminado"])
        messages.warning(
            request,
            f"El ejemplar '{ejemplar.codigo_barras}' ha sido dado de baja del inventario activo.",
        )
        return redirect("ejemplares:lista")

    return render(
        request,
        "ejemplares/confirmar_baja.html",
        {"ejemplar": ejemplar},
    )


@require_POST
def reactivar_ejemplar(request, pk):
    """Reactiva un ejemplar previamente dado de baja."""
    ejemplar = get_object_or_404(Ejemplar, pk=pk)
    ejemplar.eliminado = False
    ejemplar.save(update_fields=["eliminado"])
    messages.success(
        request,
        f"El ejemplar '{ejemplar.codigo_barras}' ha sido reactivado en el inventario.",
    )
    return redirect("ejemplares:detalle", pk=ejemplar.pk)


def reporte_inventario(request):
    """
    Reporte de Inventario por Estado:
    Visualiza el total global y el desglose de ejemplares filtrados por estado
    (disponible, prestado, perdido), condición, categoría y resumen por título de libro.
    """
    estado_filtro = (request.GET.get("estado") or "").strip()
    condicion_filtro = (request.GET.get("condicion") or "").strip()
    categoria_id = (request.GET.get("categoria") or "").strip()
    q = (request.GET.get("q") or "").strip()

    base_activos = Ejemplar.objects.filter(eliminado=False).select_related(
        "libro", "libro__editorial", "libro__categoria"
    )
    resumen_global = _calcular_resumen_estados(base_activos)
    resumen_global["dados_de_baja"] = Ejemplar.objects.filter(eliminado=True).count()

    # Aplicar filtros sobre el listado y desglose
    ejemplares_filtrados = base_activos
    if estado_filtro in {
        Ejemplar.ESTADO_DISPONIBLE,
        Ejemplar.ESTADO_PRESTADO,
        Ejemplar.ESTADO_PERDIDO,
    }:
        ejemplares_filtrados = ejemplares_filtrados.filter(estado=estado_filtro)
    else:
        estado_filtro = ""

    if condicion_filtro in {Ejemplar.CONDICION_BUENO, Ejemplar.CONDICION_DANADO}:
        ejemplares_filtrados = ejemplares_filtrados.filter(condicion=condicion_filtro)
    else:
        condicion_filtro = ""

    if categoria_id.isdigit():
        ejemplares_filtrados = ejemplares_filtrados.filter(libro__categoria_id=int(categoria_id))
    else:
        categoria_id = ""

    if q:
        ejemplares_filtrados = ejemplares_filtrados.filter(
            Q(codigo_barras__icontains=q)
            | Q(ubicacion__icontains=q)
            | Q(libro__titulo__icontains=q)
            | Q(libro__isbn__icontains=q)
        )

    ejemplares_filtrados = ejemplares_filtrados.order_by("estado", "libro__titulo", "codigo_barras")
    resumen_filtrado = _calcular_resumen_estados(ejemplares_filtrados)

    # Desglose de inventario por cada Libro
    libros_qs = Libro.objects.filter(eliminado=False).select_related("editorial", "categoria")
    if categoria_id:
        libros_qs = libros_qs.filter(categoria_id=int(categoria_id))
    if q:
        libros_qs = libros_qs.filter(
            Q(titulo__icontains=q)
            | Q(isbn__icontains=q)
            | Q(ejemplar__codigo_barras__icontains=q)
            | Q(ejemplar__ubicacion__icontains=q)
        ).distinct()

    desglose_por_libro = (
        libros_qs.annotate(
            total_ejemplares=Count("ejemplar", filter=Q(ejemplar__eliminado=False)),
            disponibles=Count(
                "ejemplar",
                filter=Q(
                    ejemplar__eliminado=False,
                    ejemplar__estado=Ejemplar.ESTADO_DISPONIBLE,
                ),
            ),
            prestados=Count(
                "ejemplar",
                filter=Q(
                    ejemplar__eliminado=False,
                    ejemplar__estado=Ejemplar.ESTADO_PRESTADO,
                ),
            ),
            perdidos=Count(
                "ejemplar",
                filter=Q(
                    ejemplar__eliminado=False,
                    ejemplar__estado=Ejemplar.ESTADO_PERDIDO,
                ),
            ),
            danados=Count(
                "ejemplar",
                filter=Q(
                    ejemplar__eliminado=False,
                    ejemplar__condicion=Ejemplar.CONDICION_DANADO,
                ),
            ),
        )
        .order_by("titulo")
    )

    if estado_filtro == Ejemplar.ESTADO_DISPONIBLE:
        desglose_por_libro = desglose_por_libro.filter(disponibles__gt=0)
    elif estado_filtro == Ejemplar.ESTADO_PRESTADO:
        desglose_por_libro = desglose_por_libro.filter(prestados__gt=0)
    elif estado_filtro == Ejemplar.ESTADO_PERDIDO:
        desglose_por_libro = desglose_por_libro.filter(perdidos__gt=0)

    # Desglose por Categoría
    desglose_por_categoria = (
        Categoria.objects.annotate(
            total=Count(
                "libro__ejemplar",
                filter=Q(libro__eliminado=False, libro__ejemplar__eliminado=False),
            ),
            disponibles=Count(
                "libro__ejemplar",
                filter=Q(
                    libro__eliminado=False,
                    libro__ejemplar__eliminado=False,
                    libro__ejemplar__estado=Ejemplar.ESTADO_DISPONIBLE,
                ),
            ),
            prestados=Count(
                "libro__ejemplar",
                filter=Q(
                    libro__eliminado=False,
                    libro__ejemplar__eliminado=False,
                    libro__ejemplar__estado=Ejemplar.ESTADO_PRESTADO,
                ),
            ),
            perdidos=Count(
                "libro__ejemplar",
                filter=Q(
                    libro__eliminado=False,
                    libro__ejemplar__eliminado=False,
                    libro__ejemplar__estado=Ejemplar.ESTADO_PERDIDO,
                ),
            ),
        )
        .filter(total__gt=0)
        .order_by("-total", "nombre")
    )

    categorias = Categoria.objects.all().order_by("nombre")

    context = {
        "resumen_global": resumen_global,
        "resumen_filtrado": resumen_filtrado,
        "ejemplares": ejemplares_filtrados,
        "desglose_por_libro": desglose_por_libro,
        "desglose_por_categoria": desglose_por_categoria,
        "categorias": categorias,
        "estado_filtro": estado_filtro,
        "condicion_filtro": condicion_filtro,
        "categoria_id": int(categoria_id) if categoria_id else None,
        "q": q,
        "estados_choices": Ejemplar.ESTADO_CHOICES,
        "condiciones_choices": Ejemplar.CONDICION_CHOICES,
    }
    return render(request, "ejemplares/reporte_inventario.html", context)


# ============================================================================
# ENDPOINTS JSON / API OPCIONALES (para integración con JS / Fetch / React)
# ============================================================================

def _serializar_ejemplar(ej):
    return {
        "id_ejemplar": ej.id_ejemplar,
        "codigo_barras": ej.codigo_barras,
        "ubicacion": ej.ubicacion,
        "estado": ej.estado,
        "condicion": ej.condicion,
        "eliminado": bool(ej.eliminado),
        "id_libro": ej.libro_id,
        "libro_titulo": ej.libro.titulo if ej.libro_id else None,
        "libro_isbn": ej.libro.isbn if ej.libro_id else None,
    }


@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_ejemplares(request):
    """Endpoint JSON para listar (GET) o crear (POST) ejemplares."""
    if request.method == "GET":
        qs = Ejemplar.objects.select_related("libro").filter(eliminado=False)
        estado = request.GET.get("estado")
        libro_id = request.GET.get("id_libro") or request.GET.get("libro")
        q = request.GET.get("q")
        if estado:
            qs = qs.filter(estado=estado)
        if libro_id and str(libro_id).isdigit():
            qs = qs.filter(libro_id=int(libro_id))
        if q:
            qs = qs.filter(
                Q(codigo_barras__icontains=q)
                | Q(ubicacion__icontains=q)
                | Q(libro__titulo__icontains=q)
            )
        data = [_serializar_ejemplar(ej) for ej in qs.order_by("id_ejemplar")]
        return JsonResponse({"count": len(data), "results": data})

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido."}, status=400)

    form = EjemplarForm(
        {
            "codigo_barras": payload.get("codigo_barras"),
            "libro": payload.get("id_libro") or payload.get("libro"),
            "ubicacion": payload.get("ubicacion"),
            "estado": payload.get("estado", Ejemplar.ESTADO_DISPONIBLE),
            "condicion": payload.get("condicion", Ejemplar.CONDICION_BUENO),
        }
    )
    if form.is_valid():
        ej = form.save(commit=False)
        ej.eliminado = False
        ej.save()
        return JsonResponse(_serializar_ejemplar(ej), status=201)
    return JsonResponse({"errors": form.errors}, status=400)


@csrf_exempt
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def api_detalle_ejemplar(request, pk):
    """Endpoint JSON para consultar, actualizar o dar de baja un ejemplar."""
    ej = get_object_or_404(Ejemplar.objects.select_related("libro"), pk=pk)

    if request.method == "GET":
        return JsonResponse(_serializar_ejemplar(ej))

    if request.method == "DELETE":
        if ej.estado == Ejemplar.ESTADO_PRESTADO:
            return JsonResponse(
                {"error": "No se puede dar de baja un ejemplar prestado."}, status=400
            )
        ej.eliminado = True
        ej.save(update_fields=["eliminado"])
        return JsonResponse({"mensaje": "Ejemplar dado de baja correctamente."})

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido."}, status=400)

    datos = {
        "codigo_barras": payload.get("codigo_barras", ej.codigo_barras),
        "libro": payload.get("id_libro") or payload.get("libro") or ej.libro_id,
        "ubicacion": payload.get("ubicacion", ej.ubicacion),
        "estado": payload.get("estado", ej.estado),
        "condicion": payload.get("condicion", ej.condicion),
    }
    form = EjemplarForm(datos, instance=ej)
    if form.is_valid():
        ej = form.save()
        return JsonResponse(_serializar_ejemplar(ej))
    return JsonResponse({"errors": form.errors}, status=400)


@require_http_methods(["GET"])
def api_reporte_inventario(request):
    """Endpoint JSON con el reporte de inventario por estado."""
    estado = request.GET.get("estado")
    qs = Ejemplar.objects.filter(eliminado=False).select_related("libro")
    resumen_global = _calcular_resumen_estados(qs)

    if estado in {
        Ejemplar.ESTADO_DISPONIBLE,
        Ejemplar.ESTADO_PRESTADO,
        Ejemplar.ESTADO_PERDIDO,
    }:
        qs = qs.filter(estado=estado)

    return JsonResponse(
        {
            "resumen_global": resumen_global,
            "filtro_estado": estado or "todos",
            "total_filtrado": qs.count(),
            "ejemplares": [_serializar_ejemplar(ej) for ej in qs.order_by("codigo_barras")],
        }
    )
