from django.urls import path
from . import views
urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("google72049cf8fcf9f3a0.html", views.google_site_verification, name="google_site_verification"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
    path("api/asistente/", views.asistente, name="asistente"),
    path("api/lead/", views.captar_lead, name="captar_lead"),
]
