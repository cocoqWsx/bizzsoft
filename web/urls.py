from django.urls import path
from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("api/asistente/", views.asistente, name="asistente"),
    path("api/lead/", views.captar_lead, name="captar_lead"),
]
