REGLAS = [
    (["venta","ventas","cliente","clientes","lead","leads","vender"], "Impulso comercial",
     ["Generación y clasificación de leads","Automatización comercial","Análisis de clientes y oportunidades","Desarrollo web orientado a conversión"]),
    (["automatizar","automatización","proceso","procesos","demora","repetitivo"], "Automatización de procesos",
     ["Mapeo del proceso actual","Automatización de tareas repetitivas","Paneles de seguimiento","Integración de sistemas"]),
    (["municipalidad","entidad","estado","ciudadano","expediente","trámite","tramite"], "Modernización y gestión pública",
     ["Digitalización y simplificación de procesos","Mejora del servicio al ciudadano","Indicadores de gestión","Capacitación del personal"]),
    (["política pública","politica publica","políticas públicas","politicas publicas"], "Políticas públicas",
     ["Definición del problema público","Análisis de evidencia y datos","Diseño de alternativas","Indicadores de seguimiento y evaluación"]),
    (["ciber","seguridad","phishing","delito","ataque","vulnerabilidad","fraude"], "Ciberseguridad y prevención",
     ["Evaluación de vulnerabilidades","Protección de información","Análisis de riesgos","Capacitación preventiva"]),
    (["personal","equipo","capacitación","capacitacion","productividad","talento"], "Potenciación del personal",
     ["Capacitación digital","Herramientas de productividad","Automatización operativa","Indicadores de desempeño"]),
]

def recomendar_soluciones(texto):
    consulta = (texto or "").strip().lower()

    if not consulta:
        return {
            "titulo":"Cuéntanos qué necesitas mejorar",
            "soluciones":["Aumentar ventas","Automatizar procesos","Mejorar un servicio público","Fortalecer ciberseguridad"]
        }

    for palabras, titulo, soluciones in REGLAS:
        if any(p in consulta for p in palabras):
            return {"titulo": titulo, "soluciones": soluciones}

    return {
        "titulo":"Podemos analizar tu necesidad",
        "soluciones":["Diagnóstico inicial","Oportunidades de mejora","Propuesta tecnológica o de gestión","Plan de implementación"]
    }
