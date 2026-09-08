import re

IDEAS = {
    "bajo": [
        {"titulo": "Servicio digital para pequeños negocios",
         "por_que": "Puede empezar con poca inversión y venderse por internet o contacto directo.",
         "validacion": "Habla con 10 negocios de tu zona y detecta tareas repetitivas o problemas de ventas."},
        {"titulo": "Reventa especializada por internet",
         "por_que": "Permite probar demanda sin abrir un local grande.",
         "validacion": "Elige un nicho, compara precios y publica 5 productos antes de comprar inventario amplio."},
        {"titulo": "Generación de leads para empresas",
         "por_que": "Muchas empresas pagan por conseguir prospectos y oportunidades comerciales.",
         "validacion": "Escoge un rubro y prepara una pequeña muestra de prospectos para demostrar el servicio."},
    ],
    "medio": [
        {"titulo": "Distribución B2B de productos especializados",
         "por_que": "Puede tener ventas recurrentes si se encuentra un nicho con demanda.",
         "validacion": "Entrevista a compradores de 3 a 5 empresas antes de comprar stock."},
        {"titulo": "Comercio electrónico de nicho",
         "por_que": "Combina inventario controlado con ventas digitales.",
         "validacion": "Prueba marketplace o anuncios y mide consultas antes de ampliar inventario."},
        {"titulo": "Servicios de automatización para MYPE",
         "por_que": "Ayuda a empresas a reducir tiempo y costos con tecnología.",
         "validacion": "Ofrece un piloto pequeño a una empresa y mide el ahorro generado."},
    ],
    "alto": [
        {"titulo": "Negocio físico con apoyo digital",
         "por_que": "Con mayor capital se puede combinar local, inventario y captación online.",
         "validacion": "Haz un estudio de zona, competencia, alquiler y punto de equilibrio antes de firmar contratos."},
        {"titulo": "Distribución y comercialización a empresas",
         "por_que": "El capital permite manejar stock y atender contratos mayores.",
         "validacion": "Consigue pedidos pequeños o cartas de intención antes de invertir fuerte."},
        {"titulo": "Plataforma o servicio tecnológico especializado",
         "por_que": "Puede crecer si resuelve un problema repetido en un nicho concreto.",
         "validacion": "Construye una versión mínima y consigue 3 clientes piloto."},
    ],
}

def capital_nivel(texto):
    nums = re.findall(r"(?:s\/\.?\s*)?(\d[\d,\.]*)", texto.lower())
    if not nums:
        return None
    try:
        n = float(nums[0].replace(",", ""))
    except ValueError:
        return None
    if n < 3000:
        return "bajo"
    if n < 15000:
        return "medio"
    return "alto"

def es_emprender(texto):
    t = texto.lower()
    claves = [
        "no se que negocio", "no sé qué negocio", "quiero emprender",
        "poner un negocio", "iniciar un negocio", "que negocio puedo",
        "qué negocio puedo", "idea de negocio", "negocio me recomiendas",
    ]
    return any(k in t for k in claves)

def intencion(texto):
    t = texto.lower()
    grupos = [
        ("ventas", ["venta", "ventas", "cliente", "clientes", "lead", "leads", "vender"]),
        ("automatizacion", ["automatizar", "automatización", "proceso", "procesos", "repetitivo", "demora"]),
        ("publico", ["municipalidad", "entidad pública", "estado", "ciudadano", "expediente", "trámite", "tramite"]),
        ("ciberseguridad", ["ciber", "seguridad", "phishing", "ataque", "vulnerabilidad", "fraude"]),
        ("personal", ["personal", "equipo", "capacitación", "capacitacion", "productividad"]),
        ("politicas", ["política pública", "politica publica", "políticas públicas", "politicas publicas"]),
    ]
    for nombre, palabras in grupos:
        if any(p in t for p in palabras):
            return nombre
    return "general"

def responder(texto, estado=None):
    estado = estado or {}
    consulta = (texto or "").strip()

    if not consulta:
        return {
            "mensaje": "Cuéntame qué quieres lograr. Por ejemplo: “quiero iniciar un negocio”, “quiero aumentar mis ventas” o “quiero automatizar un proceso”.",
            "opciones": ["Quiero iniciar un negocio", "Quiero aumentar ventas", "Quiero automatizar procesos"],
            "estado": {}
        }

    if estado.get("flujo") == "emprender":
        paso = estado.get("paso", "capital")

        if paso == "capital":
            nivel = capital_nivel(consulta)
            if not nivel:
                return {
                    "mensaje": "Para orientarte mejor, dime aproximadamente cuánto capital podrías invertir.",
                    "opciones": ["S/ 2,000", "S/ 5,000", "S/ 20,000"],
                    "estado": {"flujo": "emprender", "paso": "capital"}
                }
            return {
                "mensaje": "Perfecto. ¿Qué prefieres: vender por internet, atender empresas, tener un local físico o todavía no tienes preferencia?",
                "opciones": ["Internet", "Vender a empresas", "Local físico", "No tengo preferencia"],
                "estado": {"flujo": "emprender", "paso": "modelo", "nivel": nivel}
            }

        if paso == "modelo":
            estado["modelo"] = consulta
            estado["paso"] = "tiempo"
            return {
                "mensaje": "¿Cuánto tiempo podrías dedicarle al negocio?",
                "opciones": ["Tiempo completo", "Medio tiempo", "Solo fines de semana"],
                "estado": estado
            }

        if paso == "tiempo":
            estado["tiempo"] = consulta
            ideas = IDEAS[estado.get("nivel", "medio")]
            detalle = [
                f"{i+1}. {idea['titulo']} — {idea['por_que']} Validación: {idea['validacion']}"
                for i, idea in enumerate(ideas)
            ]
            return {
                "mensaje": "Con lo que me has contado, estas son tres líneas de negocio que vale la pena validar antes de invertir fuerte:",
                "detalle": detalle,
                "opciones": ["Quiero hablar con BizzSoft", "Empezar de nuevo"],
                "estado": {"flujo": "emprender", "paso": "resultado", "nivel": estado.get("nivel", "medio")}
            }

        if paso == "resultado" and "empezar de nuevo" in consulta.lower():
            return {
                "mensaje": "Empecemos otra vez. ¿Con cuánto capital aproximado cuentas?",
                "opciones": ["S/ 2,000", "S/ 5,000", "S/ 20,000"],
                "estado": {"flujo": "emprender", "paso": "capital"}
            }

    if es_emprender(consulta):
        return {
            "mensaje": "Sí, puedo ayudarte a buscar una oportunidad de negocio de forma más ordenada. Primero necesito conocer tu capital aproximado.",
            "opciones": ["S/ 2,000", "S/ 5,000", "S/ 20,000"],
            "estado": {"flujo": "emprender", "paso": "capital"}
        }

    respuestas = {
        "ventas": ("Para aumentar ventas conviene trabajar en tres frentes: conseguir prospectos, convertirlos mejor y dar seguimiento.",
                   ["Generación y clasificación de leads", "Automatización comercial", "Análisis de clientes y oportunidades", "Web orientada a conversión"]),
        "automatizacion": ("Podemos empezar identificando qué tareas consumen más tiempo y cuáles se repiten.",
                           ["Mapeo del proceso", "Automatización de tareas", "Integración de sistemas", "Panel de seguimiento"]),
        "publico": ("En una entidad pública conviene partir del problema del ciudadano y del proceso interno que lo genera.",
                    ["Simplificación de procesos", "Digitalización de trámites", "Indicadores de gestión", "Capacitación del personal"]),
        "ciberseguridad": ("La ciberseguridad debe empezar por riesgos y activos críticos, no solo por herramientas.",
                          ["Evaluación de vulnerabilidades", "Análisis de riesgos", "Protección de información", "Capacitación preventiva"]),
        "personal": ("Para potenciar al personal podemos combinar capacitación, herramientas y medición de desempeño.",
                     ["Capacitación digital", "Automatización operativa", "Herramientas de productividad", "Indicadores de desempeño"]),
        "politicas": ("Una propuesta de política pública debe partir de un problema claramente definido y evidencia verificable.",
                      ["Definición del problema", "Análisis de evidencia", "Diseño de alternativas", "Indicadores y evaluación"]),
        "general": ("Puedo ayudarte a convertir tu necesidad en una ruta de trabajo. Cuéntame un poco más sobre el problema, quién lo tiene y qué resultado quieres conseguir.",
                    ["Quiero iniciar un negocio", "Quiero aumentar ventas", "Quiero automatizar procesos"]),
    }
    msg, detalle = respuestas[intencion(consulta)]
    return {"mensaje": msg, "detalle": detalle, "opciones": [], "estado": {}}
