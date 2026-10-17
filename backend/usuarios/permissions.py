from rest_framework.permissions import BasePermission


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