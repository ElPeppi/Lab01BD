from rest_framework.permissions import SAFE_METHODS, BasePermission


def _u(request):
    u = request.user
    return u if u and u.is_authenticated else None


class EsEmpleado(BasePermission):
    def has_permission(self, request, view):
        u = _u(request)
        return bool(u and getattr(u, "tipo", None) == "empleado")


class EsAdmin(BasePermission):
    def has_permission(self, request, view):
        u = _u(request)
        return bool(u and getattr(u, "rol", None) == "admin")


class EsUsuario(BasePermission):
    def has_permission(self, request, view):
        u = _u(request)
        return bool(u and getattr(u, "tipo", None) == "usuario")

class SoloLecturaOEmpleado(BasePermission):
    """Cualquier sesión puede consultar (GET); solo el personal puede crear, editar o borrar."""

    def has_permission(self, request, view):
        u = _u(request)
        if not u:
            return False
        if request.method in SAFE_METHODS:
            return True
        return getattr(u, "tipo", None) == "empleado"
