import json
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .asistente import responder
from .models import Lead

def inicio(request):
    get_token(request)
    return render(request, "web/index.html")

@require_POST
def asistente(request):
    data = json.loads(request.body.decode("utf-8"))
    return JsonResponse(responder(data.get("consulta", ""), data.get("estado") or {}))

@require_POST
def captar_lead(request):
    data = json.loads(request.body.decode("utf-8"))
    nombre = (data.get("nombre") or "").strip()
    email = (data.get("email") or "").strip()
    telefono = (data.get("telefono") or "").strip()
    empresa = (data.get("empresa") or "").strip()
    necesidad = (data.get("necesidad") or "").strip()

    if not nombre:
        return JsonResponse({"ok": False, "error": "Ingresa tu nombre."}, status=400)
    if not (email or telefono):
        return JsonResponse({"ok": False, "error": "Ingresa un correo o teléfono para poder contactarte."}, status=400)
    if email:
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({"ok": False, "error": "El correo no parece válido."}, status=400)
    if not necesidad:
        return JsonResponse({"ok": False, "error": "Cuéntanos brevemente qué necesitas."}, status=400)

    lead = Lead.objects.create(
        nombre=nombre, email=email, telefono=telefono,
        empresa=empresa, necesidad=necesidad, origen="web"
    )

    return JsonResponse({
        "ok": True,
        "mensaje": "Gracias. Hemos registrado tu solicitud y podremos contactarte con los datos que dejaste.",
        "lead_id": lead.id,
    })
