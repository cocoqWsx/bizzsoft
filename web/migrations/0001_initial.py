from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Lead",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=120)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("telefono", models.CharField(blank=True, max_length=40)),
                ("empresa", models.CharField(blank=True, max_length=160)),
                ("necesidad", models.TextField()),
                ("origen", models.CharField(default="web", max_length=80)),
                ("creado", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-creado"]},
        ),
    ]
