# Integración de WhatsApp automático para BizzSoft

Esta versión añade un botón flotante de WhatsApp en la web y un webhook de WhatsApp Cloud API. Los mensajes de texto entrantes se procesan con el asistente ya existente en `web/asistente.py`; el estado se conserva por número.

## Requisitos
- Cuenta Meta Business y aplicación en Meta for Developers con WhatsApp Cloud API.
- Número habilitado para WhatsApp Business Platform.
- Phone Number ID, token de acceso, App Secret y token de verificación creado por ti.
- Sitio desplegado con HTTPS público.

Documentación oficial: https://developers.facebook.com/docs/whatsapp/

## Variables privadas en Render
En Render > servicio BizzSoft > Environment configura:

| Variable | Valor |
|---|---|
| `WA_DISPLAY_NUMBER` | Tu número público internacional, solo dígitos. Ej.: `51987654321` |
| `WA_PHONE_NUMBER_ID` | Phone Number ID de Cloud API; no es el número telefónico |
| `WA_ACCESS_TOKEN` | Token de acceso de Meta |
| `WA_APP_SECRET` | App Secret de tu aplicación Meta |
| `WA_VERIFY_TOKEN` | Contraseña larga creada por ti para verificar el webhook |
| `WA_GRAPH_VERSION` | `v26.0` |

Nunca publiques estos secretos en GitHub, HTML o capturas.

## Configurar el webhook en Meta
1. Abre tu aplicación en Meta for Developers y configura WhatsApp.
2. En WhatsApp > Configuration / Webhooks registra la URL `https://TU-DOMINIO.onrender.com/webhooks/whatsapp/`.
3. En Verify Token escribe exactamente el valor de `WA_VERIFY_TOKEN`.
4. Suscribe el campo `messages`.
5. Comprueba que el token de acceso tenga permiso `whatsapp_business_messaging`.

Meta verifica la URL con GET y envía POST al llegar mensajes. El endpoint valida `X-Hub-Signature-256` con el App Secret.

## Migración de base de datos
Ejecuta `python manage.py migrate` después de desplegar. La migración `0002_whatsapp_session` crea la tabla que guarda el estado de conversación.

## Prueba
Desde otro teléfono escribe al número conectado a Cloud API: `Hola, ¿qué servicios ofrece BizzSoft?`. El asistente debe responder y continuar el diagnóstico si contestas sus preguntas. El botón flotante de la web aparece cuando `WA_DISPLAY_NUMBER` está configurado.

## Alcance y límites
- Responde automáticamente a mensajes entrantes de texto. No procesa audios, imágenes ni documentos.
- Reutiliza las reglas y flujos existentes de `web/asistente.py`; no se ha añadido un modelo de IA generativa.
- WhatsApp aplica una ventana de atención de 24 horas desde el último mensaje del cliente para respuestas libres; fuera de ella se requieren plantillas aprobadas para iniciar o reanudar mensajes.
- Informa a los usuarios que pueden interactuar con un asistente automático y ofrece una vía de atención humana. Respeta las políticas de WhatsApp y la normativa de protección de datos.
- La integración no se activa solo con subir el ZIP: requiere configurar Meta y las variables privadas de Render.
