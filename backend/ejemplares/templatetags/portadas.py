import urllib.parse
from django import template

register = template.Library()

# Portadas reales verificadas para los 30 libros del catálogo base (clave: ISBN sin guiones)
PORTADAS_VERIFICADAS = {
    "9788420482811": "https://covers.openlibrary.org/b/id/1052034-M.jpg",   # El evangelio según Jesucristo
    "9788432217272": "https://covers.openlibrary.org/b/id/5443170-M.jpg",   # El beso de la mujer araña
    "9789588883656": "https://covers.openlibrary.org/b/id/4137436-M.jpg",   # En diciembre llegaban las brisas
    "9798317427757": "https://images.cdn3.buscalibre.com/fit-in/360x360/ec/61/ec6158daec8d12f308293578dc0338a6.jpg",  # La Rata con Thinner
    "9788492913749": "https://covers.openlibrary.org/b/id/13003444-M.jpg",  # Indigno de ser humano
    "9788425432026": "https://covers.openlibrary.org/b/id/8516506-M.jpg",   # El hombre en busca de sentido
    "9788498388015": "https://covers.openlibrary.org/b/id/8231851-M.jpg",   # El cuento de la criada
    "9788446002932": "https://covers.openlibrary.org/b/id/5240412-M.jpg",   # El origen de la vida
    "9788420664262": "https://covers.openlibrary.org/b/id/3837453-M.jpg",   # Sonetos del amor oscuro
    "9788439732938": "https://covers.openlibrary.org/b/id/10354466-M.jpg",  # Temporada de huracanes
    "9788433998859": "https://covers.openlibrary.org/b/id/10239068-M.jpg",  # Nuestra parte de noche
    "9788490660300": "https://covers.openlibrary.org/b/id/7395966-M.jpg",   # Distancia de rescate
    "9788432248238": "https://covers.openlibrary.org/b/id/5517733-M.jpg",   # El túnel
    "9788432215681": "https://covers.openlibrary.org/b/id/8078732-M.jpg",   # Sobre héroes y tumbas
    "9788420651361": "https://covers.openlibrary.org/b/id/12820198-M.jpg",  # La metamorfosis
    "9788420651378": "https://covers.openlibrary.org/b/id/997423-M.jpg",    # El proceso
    "9788420668048": "https://covers.openlibrary.org/b/id/13151269-M.jpg",  # El extranjero
    "9788420668055": "https://covers.openlibrary.org/b/id/13151272-M.jpg",  # La peste
    "9788420684178": "https://covers.openlibrary.org/b/id/12328823-M.jpg",  # Crimen y castigo
    "9788420684185": "https://covers.openlibrary.org/b/id/10445973-M.jpg",  # Memorias del subsuelo
    "9788420674254": "https://covers.openlibrary.org/b/id/12569297-M.jpg",  # Demian
    "9788420674261": "https://covers.openlibrary.org/b/id/3221083-M.jpg",   # El lobo estepario
    "9788420482828": "https://covers.openlibrary.org/b/id/10482411-M.jpg",  # Ensayo sobre la ceguera
    "9788437604947": "https://covers.openlibrary.org/b/id/5419076-M.jpg",   # Pedro Páramo
    "9788433966636": "https://covers.openlibrary.org/b/id/3706128-M.jpg",   # Los detectives salvajes
    "9788483100653": "https://covers.openlibrary.org/b/id/13184405-M.jpg",  # La insoportable levedad del ser
    "9788432228032": "https://covers.openlibrary.org/b/id/10910286-M.jpg",  # El perfume
    "9788499890944": "https://covers.openlibrary.org/b/id/9267242-M.jpg",   # 1984
    "9788499890951": "https://covers.openlibrary.org/b/id/8231823-M.jpg",   # Un mundo feliz
    "9788497592208": "https://covers.openlibrary.org/b/id/12627383-M.jpg",  # Cien años de soledad
}


def _limpiar_isbn(isbn_raw):
    if not isbn_raw:
        return ""
    return "".join(ch for ch in str(isbn_raw) if ch.isalnum())


@register.filter
def url_portada(libro_o_isbn):
    """
    Devuelve la URL de la carátula del libro a partir de su objeto Libro o su ISBN.
    Usa el catálogo de portadas verificadas y OpenLibrary Covers API para libros nuevos.
    """
    isbn_raw = getattr(libro_o_isbn, "isbn", libro_o_isbn)
    isbn_limpio = _limpiar_isbn(isbn_raw)
    if isbn_limpio in PORTADAS_VERIFICADAS:
        return PORTADAS_VERIFICADAS[isbn_limpio]
    if isbn_limpio:
        return f"https://covers.openlibrary.org/b/isbn/{isbn_limpio}-M.jpg?default=false"
    return svg_portada_fallback(libro_o_isbn)


@register.filter
def svg_portada_fallback(libro_o_titulo):
    """
    Genera una carátula SVG elegante en data-URI como respaldo automático
    si un libro nuevo no tiene portada en OpenLibrary o no hay conexión.
    """
    titulo = getattr(libro_o_titulo, "titulo", str(libro_o_titulo or "Libro"))
    iniciales = "".join(p[0].upper() for p in titulo.split()[:2] if p) or "LB"
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="120" height="175" viewBox="0 0 120 175">'
        f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0%" stop-color="#1e3a8a"/><stop offset="100%" stop-color="#0f172a"/>'
        f'</linearGradient></defs>'
        f'<rect width="120" height="175" rx="6" fill="url(#g)"/>'
        f'<rect x="8" y="8" width="104" height="159" rx="4" fill="none" stroke="#93c5fd" stroke-opacity="0.35" stroke-width="1.5"/>'
        f'<text x="60" y="95" text-anchor="middle" fill="#f8fafc" font-family="Georgia, serif" font-size="28" font-weight="bold">{iniciales}</text>'
        f'</svg>'
    )
    return "data:image/svg+xml;utf8," + urllib.parse.quote(svg)
