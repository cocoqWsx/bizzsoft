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



# -------------------- BIZSOFT ANTIFRAUDE --------------------

def es_posible_fraude(t):
    t = t.lower()
    claves = [
        "posible fraude", "fraude digital", "me quieren estafar", "me estafaron",
        "estafa", "phishing", "página falsa", "pagina falsa", "suplantación",
        "suplantacion", "anuncio falso", "publicidad engañosa", "inversión falsa",
        "inversion falsa", "venta falsa", "compra falsa", "perfil falso"
    ]
    return any(k in t for k in claves)


def iniciar_antifraude():
    return {
        "mensaje": "Analicemos el posible fraude sin interactuar con el sospechoso ni acceder a sistemas ajenos. ¿Qué ocurrió o qué te hizo desconfiar?",
        "opciones": ["Página o enlace sospechoso", "Anuncio o Marketplace", "Suplantación de identidad", "Inversión sospechosa", "Mensaje o correo sospechoso"],
        "estado": {"flujo": "antifraude", "paso": "hecho"},
    }


def flujo_antifraude(consulta, estado):
    paso = estado.get("paso", "hecho")
    if paso == "hecho":
        estado.update(hecho=consulta, paso="canal")
        return {
            "mensaje": "¿Dónde ocurrió o por qué canal llegó? Por ejemplo: Facebook Marketplace, WhatsApp, Instagram, correo, web, llamada u otro.",
            "opciones": ["Facebook Marketplace", "WhatsApp", "Instagram", "Correo", "Página web", "Otro"],
            "estado": estado,
        }
    if paso == "canal":
        estado.update(canal=consulta, paso="evidencia")
        return {
            "mensaje": "¿Qué evidencia tienes disponible? No compartas contraseñas, códigos de verificación ni datos bancarios completos.",
            "opciones": ["URL o dominio", "Capturas", "Número o perfil", "Comprobante de pago", "Correos o mensajes", "Varias evidencias"],
            "estado": estado,
        }
    if paso == "evidencia":
        estado.update(evidencia=consulta, paso="pago")
        return {
            "mensaje": "¿Llegaste a enviar dinero, datos personales, credenciales o códigos de verificación? Describe solo lo necesario y evita publicar información sensible.",
            "opciones": ["No envié nada", "Envié dinero", "Compartí datos", "Compartí una credencial o código", "No estoy seguro"],
            "estado": estado,
        }
    if paso == "pago":
        estado.update(pago=consulta, paso="resultado")
        detalle = [
            f"1. HECHO REPORTADO: {estado.get('hecho','por precisar')}.",
            f"2. CANAL: {estado.get('canal','por precisar')}.",
            f"3. EVIDENCIA DISPONIBLE: {estado.get('evidencia','por ordenar')}.",
            f"4. EXPOSICIÓN DECLARADA: {estado.get('pago','por precisar')}.",
            "5. PRESERVAR: guarda capturas completas, URL exacta, fecha/hora, nombre del perfil o comercio, correos, comprobantes y cualquier identificador visible. No alteres los archivos originales si pueden servir como evidencia.",
            "6. VERIFICAR: contrasta dominio, identidad del vendedor/empresa, canales oficiales, reputación y consistencia de la oferta sin intentar entrar a cuentas o sistemas ajenos.",
            "7. CONTENER: si compartiste credenciales o códigos, cambia contraseñas desde el servicio oficial, activa autenticación en dos pasos y contacta al proveedor o banco cuando corresponda.",
            "8. REPORTAR: usa los mecanismos de la plataforma, entidad financiera y autoridades competentes según el caso. Conserva los números de reporte o denuncia.",
        ]
        return {
            "mensaje": "Diagnóstico defensivo inicial del posible fraude:",
            "detalle": detalle,
            "opciones": ["Quiero ordenar mis evidencias", "Analizar otro posible fraude", "Quiero mejorar mi ciberseguridad", "Tengo otro problema"],
            "estado": {"flujo": "antifraude", "paso": "resultado", **estado},
        }
    if paso == "resultado":
        q = consulta.lower()
        if "ordenar" in q and "evid" in q:
            return {
                "mensaje": "Organiza la evidencia en una línea de tiempo para que sea útil al reportar el caso.",
                "detalle": [
                    "Fecha y hora del contacto o anuncio.",
                    "Canal y URL/perfil/teléfono involucrado.",
                    "Qué ofrecían o solicitaban.",
                    "Capturas y archivos originales.",
                    "Comprobantes o movimientos relacionados, ocultando datos sensibles al compartir copias.",
                    "Acciones tomadas: bloqueo, reporte, contacto con banco/plataforma o denuncia.",
                    "Número de reporte, expediente o constancia si existe."
                ],
                "opciones": ["Analizar otro posible fraude", "Analizar un problema público", "Analizar una inversión"],
                "estado": estado,
            }
        if "otro posible fraude" in q:
            return iniciar_antifraude()
    return iniciar_antifraude()


# -------------------- DIAGNÓSTICO EMPRESARIAL --------------------

def categoria_problema(t):
    t = t.lower()
    grupos = [
        ("ventas", ["venta", "cliente", "cotiza", "pedido", "marketing", "leads", "vender"]),
        ("inventario", ["inventario", "stock", "almacén", "almacen", "existencia", "mercadería"]),
        ("atencion", ["atención", "atencion", "whatsapp", "reserva", "cita", "consulta", "respuesta"]),
        ("procesos", ["demora", "tiempo", "manual", "excel", "repetitiv", "proceso", "automatiz"]),
        ("seguridad", ["ciber", "seguridad", "phishing", "hackeo", "vulnerabilidad"]),
        ("personal", ["personal", "empleado", "trabajador", "capacitación", "capacitacion"]),
    ]
    for categoria, claves in grupos:
        if any(clave in t for clave in claves):
            return categoria
    return "general"


SOLUCIONES = {
    "ventas": ("Pérdida de oportunidades comerciales o demoras en las ventas", "Un CRM sencillo con registro de consultas, cotizador digital y seguimiento automático de oportunidades.", "Consultas atendidas, tiempo de cotización y porcentaje de cotizaciones convertidas en ventas."),
    "inventario": ("Dificultades para controlar productos o existencias", "Un sistema de inventario con entradas, salidas, alertas de reposición y reportes por producto.", "Diferencias de inventario, quiebres de stock y tiempo para ubicar productos."),
    "atencion": ("Demoras o falta de seguimiento en la atención", "Una plataforma de atención con bandeja de solicitudes, estados, recordatorios y respuestas asistidas.", "Tiempo de primera respuesta, solicitudes pendientes y satisfacción del cliente."),
    "procesos": ("Tareas manuales o lentas", "Una aplicación web o móvil que centralice datos, genere documentos y automatice las tareas repetitivas.", "Minutos por operación, errores y tareas completadas por día."),
    "seguridad": ("Posibles riesgos de seguridad digital", "Una evaluación autorizada de riesgos, controles de acceso, copias de seguridad y capacitación preventiva.", "Incidentes, accesos no autorizados y cumplimiento de controles básicos."),
    "personal": ("Problemas de coordinación o productividad del equipo", "Un sistema de asignación y seguimiento de tareas, con indicadores y capacitación focalizada.", "Tareas terminadas a tiempo, retrabajos y calidad del servicio."),
    "general": ("Necesidad empresarial pendiente de precisar", "Un diagnóstico de procesos para decidir si conviene desarrollar una app, sistema web o automatización.", "Un indicador relacionado con el problema real, medido antes y después del piloto."),
}


def iniciar_diagnostico(consulta):
    return {
        "mensaje": "Para recomendarte una solución útil, primero quiero entender tu negocio. ¿A qué se dedica tu empresa y qué productos o servicios ofrece?",
        "opciones": [],
        "estado": {"flujo": "diagnostico", "paso": "negocio", "solicitud_inicial": consulta[:500]},
    }


def flujo_diagnostico(consulta, estado):
    paso = estado.get("paso", "negocio")
    consulta = consulta.strip()
    if len(consulta) < 3:
        return {"mensaje": "¿Puedes darme un poco más de detalle? Así evitaré recomendarte algo que no necesitas.", "opciones": [], "estado": estado}

    if paso == "negocio":
        estado["negocio"] = consulta[:500]
        estado["paso"] = "problema"
        return {"mensaje": "¿Qué problema concreto quieres resolver en ese negocio? Cuéntame qué ocurre hoy; por ejemplo, cotizaciones lentas, clientes sin seguimiento o inventario desordenado.", "opciones": [], "estado": estado}

    if paso == "problema":
        estado["problema"] = consulta[:800]
        estado["categoria"] = categoria_problema(consulta + " " + estado.get("solicitud_inicial", ""))
        estado["paso"] = "actual"
        return {"mensaje": "¿Cómo realizan actualmente esa tarea o proceso? ¿Usan Excel, WhatsApp, papel o algún sistema?", "opciones": [], "estado": estado}

    if paso == "actual":
        estado["proceso_actual"] = consulta[:500]
        estado["paso"] = "impacto"
        return {"mensaje": "¿Con qué frecuencia ocurre y qué consecuencia tiene? Si puedes, indica cuántos casos atienden al día o cuánto tiempo/dinero les cuesta. Si no lo sabes, puedes decir 'no tengo el dato'.", "opciones": [], "estado": estado}

    if paso == "impacto":
        estado["impacto"] = consulta[:500]
        estado["paso"] = "resultado"
        cat = estado.get("categoria", "general")
        problema, solucion, indicador = SOLUCIONES.get(cat, SOLUCIONES["general"])
        detalle = [
            "Negocio: " + estado.get("negocio", "Por precisar"),
            "Problema descrito: " + estado.get("problema", "Por precisar"),
            "Situación actual: " + estado.get("proceso_actual", "Por precisar"),
            "Impacto declarado: " + estado["impacto"],
            "Problema preliminar identificado: " + problema + ".",
            "Posible solución tecnológica: " + solucion,
            "Cómo comprobar su utilidad: " + indicador,
            "Propuesta preliminar: BizSoft puede revisar el proceso contigo, definir un alcance mínimo y preparar una propuesta de desarrollo. El costo y los resultados se determinan tras la evaluación.",
        ]
        return {
            "mensaje": "Este es tu diagnóstico preliminar. ¿Te gustaría que BizSoft evalúe y desarrolle esta solución? Usa el botón 'Quiero hablar con BizSoft' o 'Solicitar implementación' para dejarnos tus datos.",
            "detalle": detalle,
            "opciones": ["Quiero hablar con BizSoft", "Tengo otro problema", "Analizar una inversión", "Analizar un problema público"],
            "estado": estado,
        }

    if paso == "resultado":
        return {"mensaje": "Podemos convertir este diagnóstico en una propuesta de desarrollo. Haz clic en 'Solicitar implementación' o ve a Contacto y déjanos tu nombre y correo o teléfono. Si quieres otro diagnóstico, selecciona 'Tengo otro problema'.", "opciones": ["Tengo otro problema", "Analizar una inversión", "Analizar un problema público"], "estado": estado}
    return iniciar_diagnostico(consulta)


def responder(consulta, estado=None):
    consulta = (consulta or "").strip()[:1200]
    estado = dict(estado or {})
    if not consulta:
        return {"mensaje": "Cuéntame qué problema quieres resolver en tu negocio.", "opciones": ["Analizar una inversión", "Analizar un problema público", "Analizar posible fraude"], "estado": {}}

    q = consulta.lower()
    if "otro problema" in q:
        return iniciar_diagnostico("")
    if "hablar con bizsoft" in q or "solicitar implementación" in q:
        return {"mensaje": "Para que podamos contactarte, pulsa 'Solicitar implementación' o baja a la sección Contacto. Déjanos tu nombre, correo o teléfono y el resumen de tu necesidad.", "opciones": ["Tengo otro problema"], "estado": estado}

    if estado.get("flujo") == "inversion":
        return flujo_inversion(consulta, estado)
    if estado.get("flujo") == "publico":
        return flujo_publico(consulta, estado)
    if estado.get("flujo") == "antifraude":
        return flujo_antifraude(consulta, estado)
    if estado.get("flujo") == "diagnostico":
        return flujo_diagnostico(consulta, estado)

    if es_posible_fraude(consulta) or "analizar otro posible fraude" in q:
        return iniciar_antifraude()
    if es_inversion(consulta) or "analizar otra inversión" in q or "analizar otra inversion" in q:
        return iniciar_inversion()
    if es_problema_publico(consulta) or "analizar un problema público" in q or "analizar un problema publico" in q:
        return iniciar_publico()
    return iniciar_diagnostico(consulta)
