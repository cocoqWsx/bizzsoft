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
    paths = ["/", "/software-para-empresas/", "/automatizacion-empresarial/", "/inteligencia-artificial-para-empresas/", "/ciberseguridad-para-empresas/", "/software-para-talleres/"]
    entries = []
    for i, path in enumerate(paths):
        priority = "1.0" if path == "/" else "0.8"
        entries.append(f"  <url>\n    <loc>{request.build_absolute_uri(path)}</loc>\n    <changefreq>weekly</changefreq>\n    <priority>{priority}</priority>\n  </url>")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(entries) + '\n</urlset>'
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

SEO_PAGES = {
    "software-para-empresas": {
        "title": "Software para empresas en Perú | BizSoft",
        "description": "Diseñamos software para empresas en Perú: sistemas de gestión, soluciones a medida, integraciones y herramientas para mejorar operaciones y ventas.",
        "eyebrow": "SOFTWARE PARA EMPRESAS EN PERÚ",
        "h1": "Software diseñado alrededor de los problemas de tu empresa",
        "intro": "No empezamos por una plataforma genérica. Analizamos cómo trabaja tu empresa y diseñamos una solución tecnológica adaptada a la necesidad real.",
        "items": [("Sistemas a medida", "Aplicaciones para organizar clientes, servicios, operaciones y procesos."), ("Gestión empresarial", "Herramientas para centralizar información y reducir trabajo manual."), ("Integraciones", "Conectamos sistemas, datos y servicios para evitar tareas repetitivas."), ("Evolución por módulos", "La solución puede crecer con nuevas funciones según el negocio.")],
        "problem": "¿Tu empresa usa hojas de cálculo, registros dispersos o procesos que ya no escalan?",
    },
    "automatizacion-empresarial": {
        "title": "Automatización empresarial en Perú | BizSoft",
        "description": "Automatización de procesos para empresas en Perú. Analizamos tareas repetitivas e integramos software e IA para ahorrar tiempo y mejorar operaciones.",
        "eyebrow": "AUTOMATIZACIÓN EMPRESARIAL",
        "h1": "Automatiza tareas repetitivas y enfoca a tu equipo en lo importante",
        "intro": "Identificamos tareas manuales que consumen tiempo y evaluamos qué partes pueden automatizarse de forma práctica y medible.",
        "items": [("Procesos repetitivos", "Automatización de registros, seguimiento y tareas operativas."), ("Integraciones", "Flujos entre herramientas para reducir duplicación de trabajo."), ("Alertas y recordatorios", "Seguimiento automático de eventos y tareas importantes."), ("Medición", "Indicadores para comprobar si la automatización realmente mejora el proceso.")],
        "problem": "¿Tu equipo repite todos los días tareas que podrían realizarse automáticamente?",
    },
    "inteligencia-artificial-para-empresas": {
        "title": "Inteligencia artificial para empresas en Perú | BizSoft",
        "description": "Soluciones de inteligencia artificial para empresas en Perú: asistentes, análisis de datos, clasificación, predicción y automatización según cada necesidad.",
        "eyebrow": "IA PARA EMPRESAS",
        "h1": "Inteligencia artificial aplicada a necesidades reales del negocio",
        "intro": "Usamos IA cuando aporta valor al problema: para analizar información, asistir tareas, detectar patrones o apoyar decisiones. No añadimos IA solo por tendencia.",
        "items": [("Asistentes", "Herramientas para orientar consultas y apoyar tareas internas."), ("Análisis de datos", "Detección de patrones e información útil para decisiones."), ("Predicción", "Modelos orientativos basados en datos históricos cuando el caso lo permite."), ("Automatización con IA", "Flujos que combinan reglas, software e inteligencia artificial.")],
        "problem": "¿Tienes datos o tareas donde la IA podría aportar valor, pero no sabes por dónde empezar?",
    },
    "ciberseguridad-para-empresas": {
        "title": "Ciberseguridad para empresas en Perú | BizSoft",
        "description": "Ciberseguridad defensiva para empresas en Perú: prevención de fraude, análisis de riesgos, vulnerabilidades y fortalecimiento de la seguridad digital.",
        "eyebrow": "CIBERSEGURIDAD PARA EMPRESAS",
        "h1": "Protege tu negocio frente a riesgos y fraude digital",
        "intro": "Ayudamos a identificar riesgos, fortalecer controles y organizar una respuesta responsable ante incidentes digitales desde un enfoque defensivo.",
        "items": [("Prevención", "Revisión de riesgos y prácticas para reducir exposición."), ("Vulnerabilidades", "Análisis defensivo y recomendaciones de fortalecimiento."), ("Fraude digital", "Identificación de señales sospechosas y preservación responsable de evidencias."), ("Capacitación", "Buenas prácticas para que el personal reduzca errores y riesgos.")],
        "problem": "¿Te preocupa el phishing, la suplantación, el fraude o la seguridad de tus sistemas?",
    },
    "software-para-talleres": {
        "title": "Software para talleres automotrices en Perú | BizSoft",
        "description": "Software para talleres automotrices: clientes, vehículos, órdenes de trabajo, inventario, mantenimientos, recordatorios y reportes en un solo sistema.",
        "eyebrow": "SOLUCIONES PARA TALLERES AUTOMOTRICES",
        "h1": "Organiza clientes, vehículos y órdenes de trabajo en un solo sistema",
        "intro": "Una solución para talleres puede centralizar la operación y facilitar el seguimiento desde el ingreso del vehículo hasta el próximo mantenimiento.",
        "items": [("Clientes y vehículos", "Historial por cliente, placa, kilometraje y vehículo."), ("Órdenes de trabajo", "Servicios, estados, precios, repuestos y seguimiento."), ("Inventario", "Control de repuestos y materiales utilizados."), ("Recordatorios", "Próximos mantenimientos y oportunidades de seguimiento al cliente.")],
        "problem": "¿Tu taller todavía controla trabajos, clientes o mantenimientos en cuadernos, chats o archivos separados?",
    },
}

def pagina_seo(request, slug):
    page = SEO_PAGES.get(slug)
    if not page:
        from django.http import Http404
        raise Http404
    canonical_url = request.build_absolute_uri()
    social_image_url = request.build_absolute_uri(static("web/img/logo-bizsoft-simbolo-v14.png"))
    data = dict(page)
    data.update({"canonical_url": canonical_url, "social_image_url": social_image_url})
    return render(request, "web/servicio.html", data)
