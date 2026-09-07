import json
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.views.decorators.http import require_POST
from .ia import recomendar_soluciones

def inicio(request):
    get_token(request)
    return render(request, "web/index.html")

@require_POST
def recomendar(request):
    data = json.loads(request.body.decode("utf-8"))
    consulta = data.get("consulta", "")
    return JsonResponse(recomendar_soluciones(consulta))
