"""
Runner de pruebas para un proyecto database-first.

Las tablas del proyecto son managed=False: las crea scripts/Inicializacion.sql, no Django.
Por eso `manage.py test` no las encontraría en la BD de pruebas. Este runner, después de
crear la BD temporal (test_biblioteca), ejecuta ahí los CREATE TABLE de ese mismo script,
así las pruebas corren contra el esquema real (CHECK, UNIQUE y la columna generada incluidos).

Nunca toca la BD real: se niega a ejecutar si el nombre no empieza por "test_".
Requiere un usuario de MySQL con permiso para crear bases de datos (p. ej. un MySQL local);
los usuarios del grupo en RDS solo tienen permisos sobre biblioteca.*.
"""
import re
from pathlib import Path

from django.conf import settings
from django.db import connections
from django.test.runner import DiscoverRunner

DDL = Path(settings.BASE_DIR).parent / "scripts" / "Inicializacion.sql"


def sentencias_create_table(sql):
    sin_comentarios = re.sub(r"--[^\n]*", "", sql)
    return [s.strip() for s in sin_comentarios.split(";") if s.strip().upper().startswith("CREATE TABLE")]


class RunnerConEsquemaReal(DiscoverRunner):
    def setup_databases(self, **kwargs):
        configuracion = super().setup_databases(**kwargs)
        sentencias = sentencias_create_table(DDL.read_text(encoding="utf-8"))
        for alias in connections:
            conexion = connections[alias]
            nombre = conexion.settings_dict["NAME"]
            if not nombre.startswith("test_"):
                raise RuntimeError(f"Se esperaba una BD de pruebas y se obtuvo '{nombre}'.")
            with conexion.cursor() as cursor:
                for sentencia in sentencias:
                    cursor.execute(sentencia)
        return configuracion
