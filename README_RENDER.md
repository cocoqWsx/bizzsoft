# BizzSoft listo para Render

## Publicarlo
1. Crea un repositorio en GitHub llamado `bizzsoft`.
2. Sube a la raíz del repositorio todos los archivos de este proyecto.
3. En Render selecciona **New > Blueprint**.
4. Conecta GitHub y selecciona el repositorio `bizzsoft`.
5. Render detectará `render.yaml`. Aplica el Blueprint.
6. Espera a que termine el despliegue.
7. Render te mostrará una dirección pública terminada en `.onrender.com`.

## Configuración incluida
- Gunicorn para ejecutar Django.
- WhiteNoise para CSS, JavaScript y el logo.
- SECRET_KEY generada por Render.
- DEBUG desactivado automáticamente en Render.
- Configuración de ALLOWED_HOSTS para el dominio de Render.

## Base de datos
Esta primera versión no guarda clientes, usuarios ni consultas. Por eso se mantiene SQLite.
Cuando BizzSoft empiece a guardar datos, conviene pasar a PostgreSQL.
