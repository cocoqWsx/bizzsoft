from django.urls import path
from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("api/recomendar/", views.recomendar, name="recomendar"),
]
