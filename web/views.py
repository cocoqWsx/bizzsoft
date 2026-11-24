import json
import hashlib
import hmac
import logging
import os
import requests
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.templatetags.static import static
from .asistente import responder
from .models import Lead, WhatsAppSession

logger = logging.getLogger(__name__)


def inicio(request):
    get_token(request)
    canonical_url = request.build_absolute_uri("/")
    social_image_url = request.build_absolute_uri(static("web/img/logo-bizsoft-simbolo-v14.png"))
    structured_data = json.dumps({
        "@context": "https://schema.org", "@type": "Organization", "name": "BizSoft",
        "url": canonical_url, "logo": social_image_url,
        "description": "Desarrollo de aplicaciones móviles para empresas, integradas con software, inteligencia artificial, automatización, datos y ciberseguridad.",
        "areaServed": {"@type": "Country", "name": "Perú"}
    }, ensure_ascii=False)
    whatsapp_number = "51978778434"  # Número público de contacto BizzSoft (Perú: +51)
    return render(request, "web/index.html", {
        "canonical_url": canonical_url,
        "social_image_url": social_image_url,
        "structured_data": structured_data,
        "whatsapp_number": whatsapp_number,
    })



def google_site_verification(request):
    return HttpResponse(
        "google-site-verification: google72049cf8fcf9f3a0.html",
        content_type="text/html; charset=utf-8",
    )


def robots_txt(request):
    # Sitio público: permitir el rastreo de Google y otros buscadores.
    content = (
        "User-agent: *\n"
        "Allow: /\n\n"
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}\n"
    )
    response = HttpResponse(content, content_type="text/plain; charset=utf-8")
    # Evita que un robots.txt anterior quede servido desde caché durante el despliegue.
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


def sitemap_xml(request):
    paths = ["/", "/software-para-empresas/", "/desarrollo-apps-empresas/", "/automatizacion-empresarial/", "/inteligencia-artificial-para-empresas/", "/ciberseguridad-para-empresas/", "/software-para-talleres/"]
    entries = []
    for i, path in enumerate(paths):
        priority = "1.0" if path == "/" else "0.8"
        entries.append(f"  <url>\n    <loc>{request.build_absolute_uri(path)}</loc>\n    <changefreq>weekly</changefreq>\n    <priority>{priority}</priority>\n  </url>")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(entries) + '\n</urlset>'
    return HttpResponse(xml, content_type="application/xml; charset=utf-8")


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
    "desarrollo-apps-empresas": {
        "title": "Desarrollo de apps para empresas en Perú | BizSoft",
        "description": "Desarrollo de aplicaciones móviles para empresas en Perú. BizSoft diseña apps para Android y iPhone conectadas con clientes, operaciones, datos y sistemas empresariales.",
        "eyebrow": "APLICACIONES MÓVILES PARA EMPRESAS",
        "h1": "Apps diseñadas alrededor de tu negocio",
        "intro": "Diseñamos aplicaciones móviles cuando una app es la mejor forma de acercar un servicio al cliente, acompañar al equipo o llevar una operación al teléfono. La aplicación se integra con los procesos y sistemas que realmente necesita tu empresa.",
        "items": [("Apps para clientes", "Reservas, pedidos, seguimiento, promociones y servicios desde el móvil."), ("Apps para equipos", "Operaciones, visitas, incidencias, inventario y tareas desde cualquier lugar."), ("Android y iPhone", "Diseñamos soluciones móviles preparadas para los principales ecosistemas de smartphones."), ("Integración empresarial", "Conectamos la app con APIs, bases de datos, software, IA y automatizaciones cuando el proyecto lo requiere.")],
        "problem": "¿Tu empresa necesita llevar un servicio, proceso o experiencia directamente al teléfono de clientes o colaboradores?",
    },
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


# -------------------- WHATSAPP CLOUD API --------------------

def _enviar_whatsapp(destinatario, texto):
    """Envía una respuesta de texto usando WhatsApp Cloud API de Meta."""
    phone_id = os.environ.get("WA_PHONE_NUMBER_ID", "").strip()
    token = os.environ.get("WA_ACCESS_TOKEN", "").strip()
    version = os.environ.get("WA_GRAPH_VERSION", "v26.0").strip()
    if not phone_id or not token:
        logger.error("Faltan WA_PHONE_NUMBER_ID o WA_ACCESS_TOKEN.")
        return False
    url = f"https://graph.facebook.com/{version}/{phone_id}/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "recipient_type": "individual", "to": destinatario,
               "type": "text", "text": {"preview_url": False, "body": texto[:4096]}}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code >= 400:
            logger.error("WhatsApp API error %s: %s", response.status_code, response.text[:1000])
            return False
        return True
    except requests.RequestException:
        logger.exception("No se pudo conectar con WhatsApp Cloud API.")
        return False


def _firma_meta_valida(request):
    """Comprueba X-Hub-Signature-256 con el App Secret de Meta."""
    app_secret = os.environ.get("WA_APP_SECRET", "").strip()
    firma = request.headers.get("X-Hub-Signature-256", "")
    if not app_secret or not firma.startswith("sha256="):
        return False
    digest = hmac.new(app_secret.encode("utf-8"), request.body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(firma[7:], digest)


def _texto_respuesta_bizsoft(resultado):
    partes = [resultado.get("mensaje", "Gracias por escribir a BizzSoft.")]
    detalle = resultado.get("detalle") or []
    if detalle:
        partes.append("\n".join(f"• {item}" for item in detalle))
    opciones = resultado.get("opciones") or []
    if opciones:
        partes.append("También puedes consultar sobre:\n" + "\n".join(f"• {item}" for item in opciones))
    partes.append("\nSi deseas una cotización, responde con tu nombre, empresa y qué solución necesitas.")
    return "\n\n".join(partes)[:4096]


@csrf_exempt
def whatsapp_webhook(request):
    """Webhook de Meta: GET valida la URL; POST recibe mensajes entrantes."""
    if request.method == "GET":
        verify_token = os.environ.get("WA_VERIFY_TOKEN", "")
        mode = request.GET.get("hub.mode", "")
        token = request.GET.get("hub.verify_token", "")
        challenge = request.GET.get("hub.challenge", "")
        if mode == "subscribe" and verify_token and hmac.compare_digest(token, verify_token):
            return HttpResponse(challenge, content_type="text/plain")
        return HttpResponse("Token de verificación incorrecto", status=403)
    if request.method != "POST":
        return HttpResponse(status=405)
    if not _firma_meta_valida(request):
        logger.warning("Webhook de WhatsApp rechazado: firma no válida o WA_APP_SECRET ausente.")
        return HttpResponse("Firma no válida", status=403)
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return HttpResponse("JSON no válido", status=400)

    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            for message in change.get("value", {}).get("messages", []):
                if message.get("type") != "text":
                    continue
                remitente = (message.get("from") or "").strip()
                texto = (message.get("text") or {}).get("body", "").strip()
                message_id = message.get("id", "")
                if not remitente or not texto:
                    continue
                if message_id and WhatsAppSession.objects.filter(ultimo_message_id=message_id).exists():
                    continue
                session, _ = WhatsAppSession.objects.get_or_create(numero=remitente)
                try:
                    resultado = responder(texto, session.estado or {})
                    session.estado = resultado.get("estado") or {}
                    session.ultimo_message_id = message_id
                    session.save(update_fields=["estado", "ultimo_message_id", "actualizado"])
                    _enviar_whatsapp(remitente, _texto_respuesta_bizsoft(resultado))
                except Exception:
                    logger.exception("Error procesando mensaje de WhatsApp de %s", remitente)
                    _enviar_whatsapp(remitente, "Gracias por contactar a BizzSoft. Tuvimos un inconveniente al procesar tu consulta. "
                                     "Déjanos tu nombre y un resumen de lo que necesitas; nuestro equipo podrá revisarlo.")
    return HttpResponse("EVENT_RECEIVED", status=200)
