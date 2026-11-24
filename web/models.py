from django.db import models

class Lead(models.Model):
    nombre = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=40, blank=True)
    empresa = models.CharField(max_length=160, blank=True)
    necesidad = models.TextField()
    origen = models.CharField(max_length=80, default="web")
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]

    def __str__(self):
        return f"{self.nombre} - {self.creado:%Y-%m-%d}"


class WhatsAppSession(models.Model):
    """Conserva el estado de conversación del asistente por número de WhatsApp."""
    numero = models.CharField(max_length=32, unique=True)
    estado = models.JSONField(default=dict, blank=True)
    ultimo_message_id = models.CharField(max_length=180, blank=True, db_index=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"WhatsApp {self.numero}"
