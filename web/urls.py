from django.urls import path
from . import views
urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("google72049cf8fcf9f3a0.html", views.google_site_verification, name="google_site_verification"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
    path("software-para-empresas/", views.pagina_seo, {"slug": "software-para-empresas"}, name="software_empresas"),
    path("desarrollo-apps-empresas/", views.pagina_seo, {"slug": "desarrollo-apps-empresas"}, name="apps_empresas"),
    path("automatizacion-empresarial/", views.pagina_seo, {"slug": "automatizacion-empresarial"}, name="automatizacion_empresarial"),
    path("inteligencia-artificial-para-empresas/", views.pagina_seo, {"slug": "inteligencia-artificial-para-empresas"}, name="ia_empresas"),
    path("ciberseguridad-para-empresas/", views.pagina_seo, {"slug": "ciberseguridad-para-empresas"}, name="ciberseguridad_empresas"),
    path("software-para-talleres/", views.pagina_seo, {"slug": "software-para-talleres"}, name="software_talleres"),
    path("api/asistente/", views.asistente, name="asistente"),
    path("api/lead/", views.captar_lead, name="captar_lead"),
]
