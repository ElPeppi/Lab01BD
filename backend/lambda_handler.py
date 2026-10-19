"""
Punto de entrada de AWS Lambda.

API Gateway (HTTP API) entrega cada petición como un "evento" JSON; apig-wsgi lo
convierte en una petición WSGI normal para Django y convierte la respuesta de vuelta.
Así el mismo Django que corre en local con `runserver` corre en Lambda sin cambios.
Django se inicializa una sola vez por contenedor (en el arranque en frío) y se reutiliza
en las siguientes invocaciones mientras el contenedor siga vivo.
"""
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from apig_wsgi import make_lambda_handler  # noqa: E402
from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
handler = make_lambda_handler(application)
