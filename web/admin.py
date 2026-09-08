from django.contrib import admin
from .models import Lead

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("nombre", "email", "telefono", "empresa", "creado")
    search_fields = ("nombre", "email", "telefono", "empresa", "necesidad")
    list_filter = ("creado", "origen")
