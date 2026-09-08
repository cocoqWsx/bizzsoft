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
