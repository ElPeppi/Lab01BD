from django.urls import path
from . import views

app_name = "usuarios"
urlpatterns = [
    path("login/", views.login, name="login"),
    path("refresh/", views.refresh, name="refresh"),
    path("me/", views.me, name="me"),
]