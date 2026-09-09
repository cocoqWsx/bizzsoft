import re


def numero(texto):
    """Extrae un importe escrito como 35000, 35,000, 35.000 o S/ 35000."""
    m = re.search(r"(-?\d[\d.,]*)", (texto or "").replace(" ", ""))
    if not m:
        return None
    raw = m.group(1)
    if re.fullmatch(r"-?\d{1,3}([.,]\d{3})+", raw):
        raw = raw.replace(",", "").replace(".", "")
    elif "," in raw and "." in raw:
        if raw.rfind(",") > raw.rfind("."):
            raw = raw.replace(".", "").replace(",", ".")
        else:
            raw = raw.replace(",", "")
    else:
        raw = raw.replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return None


def moneda_texto(n, moneda):
    simbolo = "US$" if moneda == "USD" else "S/"
    return f"{simbolo} {n:,.2f}"


# -------------------- INVERSIÓN --------------------

def es_inversion(t):
    t = t.lower()
    claves = [
        "quiero invertir", "analizar una inversión", "analizar una inversion",
        "me conviene comprar", "quiero comprar para vender", "oportunidad de inversión",
        "oportunidad de inversion", "regatear", "negociar precio", "reventa"
    ]
    return any(k in t for k in claves)


def tipo_activo(t):
    t = t.lower()
    grupos = [
        ("inmueble", ["casa", "departamento", "depa", "terreno", "local", "inmueble"]),
        ("vehiculo", ["auto", "carro", "vehículo", "vehiculo", "moto", "camioneta"]),
        ("maquinaria", ["máquina", "maquina", "equipo", "herramienta"]),
        ("mercaderia", ["producto", "mercadería", "mercaderia", "stock", "lote", "reventa"]),
        ("negocio", ["negocio", "empresa", "tienda", "restaurante"]),
        ("tecnologia", ["software", "tecnología", "tecnologia", "computadora", "laptop"]),
    ]
    for nombre, palabras in grupos:
        if any(p in t for p in palabras):
            return nombre
    return "otro"


def compradores(tipo):
    return {
        "inmueble": "familias, inversionistas inmobiliarios, compradores para alquiler o personas que buscan la zona",
        "vehiculo": "usuarios finales, conductores independientes, pequeñas empresas o revendedores especializados",
        "maquinaria": "talleres, MYPE del rubro, emprendedores productivos o empresas que necesiten ampliar capacidad",
        "mercaderia": "consumidor final, comercios minoristas, distribuidores o empresas del nicho",
        "negocio": "emprendedores del rubro, competidores, operadores que quieran expandirse o inversionistas",
        "tecnologia": "profesionales, estudiantes, MYPE o empresas con esa necesidad tecnológica",
        "otro": "el comprador dependerá del uso del activo; primero debemos definir quién obtiene más valor de él",
    }[tipo]


def iniciar_inversion():
    return {
        "mensaje": "Empecemos el diagnóstico de inversión. ¿Qué estás pensando comprar o financiar?",
        "opciones": ["Casa o departamento", "Terreno", "Negocio", "Productos para reventa", "Maquinaria", "Vehículo"],
        "estado": {"flujo": "inversion", "paso": "activo"},
    }


def flujo_inversion(consulta, estado):
    paso = estado.get("paso", "activo")
    if paso == "activo":
        estado.update(activo=consulta, tipo=tipo_activo(consulta), paso="moneda")
        return {"mensaje": "¿En qué moneda estás evaluando la operación?", "opciones": ["Soles", "Dólares"], "estado": estado}
    if paso == "moneda":
        moneda = "USD" if "dól" in consulta.lower() or "dol" in consulta.lower() or "usd" in consulta.lower() else "PEN"
        estado.update(moneda=moneda, paso="pedido")
        return {"mensaje": "¿Cuál es el precio que pide actualmente el vendedor?", "opciones": [], "estado": estado}
    if paso == "pedido":
        n = numero(consulta)
        if n is None or n <= 0:
            return {"mensaje": "No pude reconocer el importe. Por ejemplo, escribe 40000.", "opciones": [], "estado": estado}
        estado.update(precio_pedido=n, paso="negociado")
        return {"mensaje": "¿A qué precio crees que podrías negociarlo o a qué precio ya te lo dejaron?", "opciones": [], "estado": estado}
    if paso == "negociado":
        n = numero(consulta)
        if n is None or n <= 0:
            return {"mensaje": "Escribe el precio negociado como un número, por ejemplo 35000.", "opciones": [], "estado": estado}
        estado.update(precio_negociado=n, paso="referencia")
        return {"mensaje": "¿Cuál sería un precio de venta REALISTA según operaciones o anuncios comparables? Si aún no lo sabes, escribe 0.", "opciones": [], "estado": estado}
    if paso == "referencia":
        n = numero(consulta)
        if n is None or n < 0:
            return {"mensaje": "Escribe un importe de referencia o 0 si todavía no lo conoces.", "opciones": [], "estado": estado}
        estado.update(precio_reventa=n, paso="costos")
        return {"mensaje": "¿Cuánto estimas en costos adicionales totales? Incluye mejoras, trámites, transporte, comisiones, publicidad, impuestos aplicables u otros. Si no sabes, escribe 0.", "opciones": [], "estado": estado}
    if paso == "costos":
        costos = numero(consulta)
        if costos is None or costos < 0:
            return {"mensaje": "Escribe los costos estimados como un número o 0.", "opciones": [], "estado": estado}
        pedido = estado["precio_pedido"]
        entrada = estado["precio_negociado"]
        reventa = estado["precio_reventa"]
        moneda = estado["moneda"]
        descuento = pedido - entrada
        pct_desc = (descuento / pedido * 100) if pedido else 0
        inversion = entrada + costos
        detalle = [
            f"Precio pedido: {moneda_texto(pedido, moneda)}.",
            f"Precio negociado: {moneda_texto(entrada, moneda)}.",
            f"Descuento frente al precio pedido: {moneda_texto(descuento, moneda)} ({pct_desc:.1f}%).",
            f"Inversión estimada incluyendo costos declarados: {moneda_texto(inversion, moneda)}.",
        ]
        if reventa > 0:
            ganancia = reventa - inversion
            roi = (ganancia / inversion * 100) if inversion else 0
            margen = (ganancia / reventa * 100) if reventa else 0
            detalle += [
                f"Precio de salida usado para el escenario: {moneda_texto(reventa, moneda)}.",
                f"Resultado potencial antes de costos no incluidos: {moneda_texto(ganancia, moneda)}.",
                f"ROI estimado del escenario: {roi:.1f}%.",
                f"Margen sobre la venta estimada: {margen:.1f}%.",
            ]
        else:
            detalle.append("Aún no podemos calcular ganancia ni ROI porque falta validar un precio realista de salida.")
        detalle += [
            f"Compradores que podrías investigar: {compradores(estado.get('tipo','otro'))}.",
            "Antes de invertir: valida documentación, estado del activo, demanda real, liquidez, costos omitidos y precios comparables. Un precio publicado no equivale necesariamente a un precio real de venta.",
        ]
        return {
            "mensaje": "Diagnóstico preliminar de la oportunidad:",
            "detalle": detalle,
            "opciones": ["Analizar otra inversión", "Analizar un problema público", "Tengo otro problema"],
            "estado": {},
        }
    return iniciar_inversion()


# -------------------- CIUDADANÍA Y ASUNTOS PÚBLICOS --------------------

def es_problema_publico(t):
    t = t.lower()
    claves = [
        "problema público", "problema publico", "fiscalizar", "fiscalización", "fiscalizacion",
        "autoridad", "municipalidad", "ministerio", "entidad pública", "entidad publica",
        "funcionario", "servidor público", "servidor publico", "trámite", "tramite",
        "servicio público", "servicio publico", "obra pública", "obra publica", "ciudadano"
    ]
    return any(k in t for k in claves)


def iniciar_publico():
    return {
        "mensaje": "Analicemos el problema público como ciudadano. Primero necesito entender los hechos. ¿Qué ocurrió? Describe el problema de forma concreta.",
        "opciones": [],
        "estado": {"flujo": "publico", "paso": "hecho"},
    }


def flujo_publico(consulta, estado):
    paso = estado.get("paso", "hecho")
    if paso == "hecho":
        estado.update(hecho=consulta, paso="desde_cuando")
        return {"mensaje": "¿Desde cuándo ocurre y con qué frecuencia pasa? Si conoces fechas aproximadas, inclúyelas.", "opciones": [], "estado": estado}
    if paso == "desde_cuando":
        estado.update(desde_cuando=consulta, paso="entidad")
        return {"mensaje": "¿Qué entidad, autoridad, oficina o servicio público está relacionado con el problema?", "opciones": [], "estado": estado}
    if paso == "entidad":
        estado.update(entidad=consulta, paso="afectados")
        return {"mensaje": "¿A quiénes afecta y qué consecuencia genera? Por ejemplo: demora, gasto, riesgo, falta de atención, perjuicio al barrio o uso ineficiente de recursos.", "opciones": [], "estado": estado}
    if paso == "afectados":
        estado.update(afectados=consulta, paso="evidencia")
        return {"mensaje": "¿Qué evidencia tienes o podrías conseguir? Ejemplos: fotos, videos, documentos, cargos, resoluciones, correos, recibos, respuestas oficiales, fechas, testimonios o enlaces públicos.", "opciones": ["Tengo documentos", "Tengo fotos o videos", "Solo tengo lo observado", "Tengo varias evidencias"], "estado": estado}
    if paso == "evidencia":
        estado.update(evidencia=consulta, paso="gestion_previa")
        return {"mensaje": "¿Ya presentaste una solicitud, reclamo, pedido de información o comunicación ante alguna entidad? Cuéntame qué hiciste y qué respuesta recibiste. Si no hiciste nada, escribe: todavía no.", "opciones": [], "estado": estado}
    if paso == "gestion_previa":
        estado.update(gestion_previa=consulta, paso="resultado")
        detalle = [
            "1. HECHO: redactar qué ocurrió sin opiniones innecesarias, indicando lugar y situación.",
            f"2. TIEMPO: registrar desde cuándo ocurre: {estado.get('desde_cuando','por precisar')}.",
            f"3. ENTIDAD RELACIONADA: {estado.get('entidad','por identificar')}.",
            f"4. AFECTACIÓN: {estado.get('afectados','por precisar')}.",
            f"5. EVIDENCIA DISPONIBLE: {estado.get('evidencia','por ordenar')}.",
            f"6. GESTIONES PREVIAS: {estado.get('gestion_previa','por precisar')}.",
            "7. SIGUIENTE PASO: verificar qué entidad tiene competencia, ordenar la evidencia por fecha y elegir el canal institucional apropiado (solicitud, acceso a información, reclamo, denuncia u otro mecanismo, según corresponda).",
            "8. SEGUIMIENTO: guardar cargo, número de expediente, fecha de presentación, plazo de respuesta y resultado.",
        ]
        return {
            "mensaje": "Con lo que me has contado, BizSoft puede organizar el caso en una ficha de vigilancia ciudadana:",
            "detalle": detalle,
            "opciones": ["Quiero ordenar mis evidencias", "Quiero preparar el seguimiento", "Analizar una inversión", "Tengo otro problema"],
            "estado": {"flujo": "publico", "paso": "resultado", **estado},
        }
    if paso == "resultado":
        q = consulta.lower()
        if "ordenar" in q and "evid" in q:
            return {
                "mensaje": "Ordena cada evidencia con una ficha simple. Así después será más fácil preparar una solicitud o sustentar el seguimiento.",
                "detalle": [
                    "Fecha y hora.", "Lugar.", "Qué ocurrió.", "Entidad o autoridad relacionada.",
                    "Tipo de evidencia (foto, video, documento, correo, cargo, respuesta, enlace).",
                    "Nombre del archivo o número de documento.", "Qué demuestra esa evidencia.",
                    "Estado: pendiente, presentado, respondido o cerrado."
                ],
                "opciones": ["Quiero preparar el seguimiento", "Analizar otro problema público", "Analizar una inversión"],
                "estado": estado,
            }
        if "seguimiento" in q:
            return {
                "mensaje": "Para el seguimiento, crea una línea de tiempo y evita perder trazabilidad del caso.",
                "detalle": [
                    "Fecha del hecho u observación.", "Fecha de cada presentación.", "Entidad y oficina receptora.",
                    "Número de expediente o cargo.", "Plazo informado o aplicable.", "Respuesta recibida.",
                    "Pendiente siguiente y fecha de control."
                ],
                "opciones": ["Quiero ordenar mis evidencias", "Analizar otro problema público", "Analizar una inversión"],
                "estado": estado,
            }
        if "otro problema público" in q or "otro problema publico" in q:
            return iniciar_publico()
    return iniciar_publico()


# -------------------- DIAGNÓSTICO GENERAL --------------------

def categoria_problema(t):
    t = t.lower()
    grupos = [
        ("ventas", ["venta", "ventas", "cliente", "clientes", "lead", "vender", "competencia", "cotiza"]),
        ("procesos", ["automatizar", "automatización", "proceso", "procesos", "manual", "demora", "tiempo", "repetitiv"]),
        ("publico", ["municipalidad", "entidad pública", "entidad publica", "estado", "ciudadano", "trámite", "tramite", "servicio público", "servicio publico"]),
        ("seguridad", ["ciber", "seguridad", "phishing", "ataque", "vulnerabilidad", "fraude"]),
        ("personal", ["personal", "equipo", "capacitación", "capacitacion", "productividad"]),
    ]
    for nombre, palabras in grupos:
        if any(p in t for p in palabras):
            return nombre
    return "general"


def diagnostico(t):
    cat = categoria_problema(t)
    data = {
        "ventas": ("Baja captación o conversión de clientes", "El cliente puede tener dificultad para descubrir, comparar, cotizar o dar seguimiento a la compra.", ["Catálogo/web orientado a conversión", "Captación y clasificación de leads", "Cotizador o calculadora digital", "Seguimiento comercial automatizado"], "Medir consultas, cotizaciones y ventas antes y después del piloto."),
        "procesos": ("Trabajo lento, manual o repetitivo", "Hay tareas que consumen tiempo y pueden contener duplicidad, esperas o errores.", ["Mapeo del trabajo", "Automatización de tareas", "Integración de información", "Panel de seguimiento"], "Medir tiempo por operación, errores y horas ahorradas."),
        "publico": ("Problema relacionado con una entidad o servicio público", "Puede tratarse de una oportunidad de mejora institucional o de un caso que un ciudadano necesita documentar y seguir.", ["Diagnóstico de gestión", "Digitalización y tecnología", "Indicadores", "Capacitación del personal", "Organización de evidencia ciudadana", "Seguimiento institucional"], "Medir atención, tiempos, incidencias, respuesta institucional y resultado."),
        "seguridad": ("Riesgo de ciberseguridad", "Primero hay que identificar activos, amenazas, vulnerabilidades y controles existentes.", ["Evaluación de riesgos", "Revisión de vulnerabilidades", "Medidas preventivas", "Capacitación"], "Priorizar riesgos por impacto y verificar reducción de exposición."),
        "personal": ("Brecha de productividad o capacidad", "Puede existir una combinación de organización deficiente, herramienta inadecuada o necesidad de capacitación.", ["Diagnóstico de tareas", "Capacitación focalizada", "Herramientas de productividad", "Indicadores"], "Comparar productividad y calidad antes y después."),
        "general": ("Problema por diagnosticar", "Necesitamos conocer quién lo sufre, dónde ocurre, con qué frecuencia y qué impacto genera.", ["Observar el problema", "Recoger evidencia", "Identificar causas", "Diseñar una solución mínima"], "Definir un indicador sencillo para saber si la solución funciona."),
    }
    nombre, causa, soluciones, medida = data[cat]
    return {
        "mensaje": f"Diagnóstico inicial: {nombre}.",
        "detalle": [f"Hipótesis: {causa}", "Posibles líneas de solución: " + "; ".join(soluciones) + ".", f"Cómo validarlo: {medida}"],
        "opciones": ["Quiero profundizar", "Analizar un problema público", "Analizar una inversión", "Tengo otro problema"],
        "estado": {"flujo": "diagnostico", "paso": "contexto", "categoria": cat},
    }


def responder(consulta, estado=None):
    consulta = (consulta or "").strip()
    estado = estado or {}
    if not consulta:
        return {"mensaje": "Cuéntame el problema, la inversión o el asunto público que quieres analizar.", "opciones": ["Analizar una inversión", "Analizar un problema público"], "estado": {}}

    q = consulta.lower()

    if estado.get("flujo") == "inversion":
        return flujo_inversion(consulta, estado)
    if estado.get("flujo") == "publico":
        return flujo_publico(consulta, estado)

    if es_inversion(consulta) or "analizar otra inversión" in q or "analizar otra inversion" in q:
        return iniciar_inversion()
    if es_problema_publico(consulta) or "analizar un problema público" in q or "analizar un problema publico" in q:
        return iniciar_publico()

    if estado.get("flujo") == "diagnostico" and estado.get("paso") == "contexto":
        if "otro problema" in q:
            return {"mensaje": "Describe el nuevo problema: qué ocurre, a quién afecta y dónde lo observaste.", "opciones": ["Analizar un problema público", "Analizar una inversión"], "estado": {}}
        if "hablar con bizsoft" in q:
            return {"mensaje": "Baja a Contacto y déjanos tu nombre y un medio de contacto junto con el problema.", "opciones": [], "estado": estado}
        return {"mensaje": "Para profundizar: ¿a quién afecta, dónde ocurre y qué consecuencia genera (ventas, tiempo, dinero, quejas u otro impacto)?", "opciones": [], "estado": {"flujo": "diagnostico", "paso": "evidencia", "categoria": estado.get("categoria", "general")}}

    if estado.get("flujo") == "diagnostico" and estado.get("paso") == "evidencia":
        return {
            "mensaje": "Buen punto de partida. Primero validaríamos el problema con evidencia y un piloto pequeño.",
            "detalle": ["1. Observar y registrar casos reales.", "2. Entrevistar a las personas afectadas.", "3. Identificar la causa principal.", "4. Diseñar una solución mínima.", "5. Medir si mejora ventas, tiempo, costo o servicio."],
            "opciones": ["Quiero hablar con BizSoft", "Analizar un problema público", "Analizar una inversión", "Tengo otro problema"],
            "estado": {"flujo": "diagnostico", "paso": "contexto", "categoria": estado.get("categoria", "general")},
        }

    return diagnostico(consulta)
