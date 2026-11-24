from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("web", "0001_initial")]
    operations = [migrations.CreateModel(name="WhatsAppSession", fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("numero", models.CharField(max_length=32, unique=True)),
        ("estado", models.JSONField(blank=True, default=dict)),
        ("ultimo_message_id", models.CharField(blank=True, db_index=True, max_length=180)),
        ("creado", models.DateTimeField(auto_now_add=True)),
        ("actualizado", models.DateTimeField(auto_now=True)),
    ])]
