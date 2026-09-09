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

## Módulo Quiero invertir
Se reemplazó la sección visible "Quiero emprender" por "Quiero invertir".
El asistente incluye un analizador preliminar de oportunidades para inmuebles, terrenos, negocios, mercadería, maquinaria, vehículos y otros activos. Calcula descuento negociado, inversión total declarada, resultado potencial, ROI y margen cuando el usuario aporta un precio realista de salida. También propone perfiles de compradores y recuerda validar documentación, demanda, liquidez y costos.

Los resultados son escenarios de decisión basados en los datos ingresados por el usuario; no constituyen tasación, asesoría financiera ni garantía de rentabilidad.
