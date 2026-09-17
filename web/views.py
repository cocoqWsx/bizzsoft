import json
from django.http import JsonResponse, HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.templatetags.static import static
from .asistente import responder
from .models import Lead


def inicio(request):
    get_token(request)
    canonical_url = request.build_absolute_uri("/")
    social_image_url = request.build_absolute_uri(static("web/img/logo-bizsoft-simbolo-v14.png"))
    structured_data = json.dumps({
        "@context": "https://schema.org", "@type": "Organization", "name": "BizSoft",
        "url": canonical_url, "logo": social_image_url,
        "description": "Soluciones tecnológicas para empresas con software, inteligencia artificial, automatización, análisis de datos y ciberseguridad.",
        "areaServed": {"@type": "Country", "name": "Perú"}
    }, ensure_ascii=False)
    return render(request, "web/index.html", {"canonical_url": canonical_url, "social_image_url": social_image_url, "structured_data": structured_data})



def google_site_verification(request):
    return HttpResponse(
        "google-site-verification: google72049cf8fcf9f3a0.html",
        content_type="text/html; charset=utf-8",
    )


def robots_txt(request):
    content = f"User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /api/\n\nSitemap: {request.build_absolute_uri('/sitemap.xml')}\n"
    return HttpResponse(content, content_type="text/plain; charset=utf-8")


def sitemap_xml(request):
    home_url = request.build_absolute_uri("/")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url>\n    <loc>%s</loc>\n    <changefreq>weekly</changefreq>\n    <priority>1.0</priority>\n  </url>\n</urlset>' % home_url
    return HttpResponse(xml, content_type="application/xml; charset=utf-8")


@require_POST
def asistente(request):
    data = json.loads(request.body.decode("utf-8"))
    return JsonResponse(responder(data.get("consulta", ""), data.get("estado") or {}))


@require_POST
def captar_lead(request):
    data = json.loads(request.body.decode("utf-8"))
    nombre = (data.get("nombre") or "").strip(); email = (data.get("email") or "").strip()
    telefono = (data.get("telefono") or "").strip(); empresa = (data.get("empresa") or "").strip()
    necesidad = (data.get("necesidad") or "").strip()
    if not nombre: return JsonResponse({"ok": False, "error": "Ingresa tu nombre."}, status=400)
    if not (email or telefono): return JsonResponse({"ok": False, "error": "Ingresa un correo o teléfono para poder contactarte."}, status=400)
    if email:
        try: validate_email(email)
        except ValidationError: return JsonResponse({"ok": False, "error": "El correo no parece válido."}, status=400)
    if not necesidad: return JsonResponse({"ok": False, "error": "Cuéntanos brevemente qué necesitas."}, status=400)
    lead = Lead.objects.create(nombre=nombre, email=email, telefono=telefono, empresa=empresa, necesidad=necesidad, origen="web")
    return JsonResponse({"ok": True, "mensaje": "Gracias. Hemos registrado tu solicitud y podremos contactarte con los datos que dejaste.", "lead_id": lead.id})
