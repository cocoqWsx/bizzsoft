# BizzSoft mejorado

Incluye:
- Nueva línea para personas que quieren emprender y no saben qué negocio iniciar.
- Asistente conversacional local con preguntas de seguimiento.
- Recomendaciones para ventas, automatización, gestión pública, ciberseguridad, personal y políticas públicas.
- Formulario para captar prospectos/clientes.
- Modelo `Lead` visible desde Django Admin.
- Soporte opcional para PostgreSQL mediante `DATABASE_URL`.

IMPORTANTE:
En Render Free, si usas SQLite los leads pueden perderse cuando el servicio se recrea o se redepliega.
Para captar clientes de forma seria, configura una base PostgreSQL persistente y define `DATABASE_URL`.
