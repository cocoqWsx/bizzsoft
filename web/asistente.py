import re


def numero(texto):
    """Extrae un importe escrito como 35000, 35,000, 35.000 o S/ 35000."""
    m = re.search(r"(-?\d[\d.,]*)", (texto or "").replace(" ", ""))
    if not m:
        return None
    raw = m.group(1)
    # Para este asistente, separadores con 3 dígitos finales se interpretan como miles.
    if re.fullmatch(r"-?\d{1,3}([.,]\d{3})+", raw):
        raw = raw.replace(",", "").replace(".", "")
    elif "," in raw and "." in raw:
        # toma el último separador como decimal
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


def es_inversion(t):
    t = t.lower()
    claves = ["quiero invertir", "analizar una inversión", "analizar una inversion",
              "me conviene comprar", "quiero comprar para vender", "oportunidad de inversión",
              "oportunidad de inversion", "regatear", "negociar precio", "reventa"]
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
        "mensaje": "Empecemos el diagnóstico. ¿Qué estás pensando comprar o financiar?",
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
        return {"mensaje": "¿Cuál es el precio que pide actualmente el vendedor? Escribe solo un importe aproximado.", "opciones": [], "estado": estado}
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
        return {"mensaje": "¿Cuál sería un precio de venta REALISTA según operaciones o anuncios comparables? Si aún no lo sabes, escribe 0 y BizSoft te indicará que debes investigarlo.", "opciones": [], "estado": estado}
    if paso == "referencia":
        n = numero(consulta)
        if n is None or n < 0:
            return {"mensaje": "Escribe un importe de referencia o 0 si todavía no lo conoces.", "opciones": [], "estado": estado}
        estado.update(precio_reventa=n, paso="costos")
        return {"mensaje": "¿Cuánto estimas en costos adicionales totales? Incluye mejoras, trámites, transporte, comisiones, publicidad, impuestos aplicables u otros. Si por ahora no sabes, escribe 0.", "opciones": [], "estado": estado}
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
            "Antes de invertir: valida propiedad/documentación, estado del activo, demanda real, liquidez, costos omitidos y precios comparables. No confundas precio publicado con precio efectivamente vendido.",
        ]
        return {
            "mensaje": "Diagnóstico preliminar de la oportunidad:",
            "detalle": detalle,
            "opciones": ["Analizar otra inversión", "Quiero hablar con BizSoft", "Tengo otro problema"],
            "estado": {},
        }
    return iniciar_inversion()


def categoria_problema(t):
    t=t.lower()
    grupos=[
      ("ventas",["venta","ventas","cliente","clientes","lead","vender","competencia","cotiza"]),
      ("procesos",["automatizar","automatización","proceso","procesos","manual","demora","tiempo","repetitiv"]),
      ("publico",["municipalidad","entidad pública","estado","ciudadano","trámite","tramite","servicio público"]),
      ("seguridad",["ciber","seguridad","phishing","ataque","vulnerabilidad","fraude"]),
      ("personal",["personal","equipo","capacitación","capacitacion","productividad"]),
    ]
    for nombre,palabras in grupos:
        if any(p in t for p in palabras): return nombre
    return "general"


def diagnostico(t):
    cat=categoria_problema(t)
    data={
      "ventas":("Baja captación o conversión de clientes", "El cliente puede tener dificultad para descubrir, comparar, cotizar o dar seguimiento a la compra.", ["Catálogo/web orientado a conversión", "Captación y clasificación de leads", "Cotizador o calculadora digital", "Seguimiento comercial automatizado"], "Medir consultas, cotizaciones y ventas antes y después del piloto."),
      "procesos":("Proceso lento, manual o repetitivo", "Hay tareas que consumen tiempo y pueden contener duplicidad, esperas o errores.", ["Mapeo del proceso", "Automatización de tareas", "Integración de información", "Panel de seguimiento"], "Medir tiempo por operación, errores y horas ahorradas."),
      "publico":("Problema de proceso o servicio al ciudadano", "La causa puede estar en pasos innecesarios, información dispersa, demoras o falta de indicadores.", ["Diagnóstico del recorrido del ciudadano", "Simplificación y digitalización", "Indicadores de gestión", "Capacitación del personal"], "Medir tiempo de atención, incidencias y satisfacción."),
      "seguridad":("Riesgo de ciberseguridad", "Primero hay que identificar activos, amenazas, vulnerabilidades y controles existentes.", ["Evaluación de riesgos", "Revisión de vulnerabilidades", "Medidas preventivas", "Capacitación"], "Priorizar riesgos por impacto y verificar reducción de exposición."),
      "personal":("Brecha de productividad o capacidad", "Puede existir una combinación de proceso deficiente, herramienta inadecuada o necesidad de capacitación.", ["Diagnóstico de tareas", "Capacitación focalizada", "Herramientas de productividad", "Indicadores"], "Comparar productividad y calidad antes y después."),
      "general":("Problema por diagnosticar", "Necesitamos conocer quién lo sufre, dónde ocurre, con qué frecuencia y qué impacto genera.", ["Observar el problema", "Recoger evidencia", "Identificar causas", "Diseñar y probar una solución pequeña"], "Definir un indicador concreto antes de construir la solución."),
    }[cat]
    problema,causa,soluciones,medicion=data
    return {"mensaje":f"Problema detectado: {problema}.", "detalle":[f"Posible causa: {causa}", "Soluciones que podríamos evaluar: " + "; ".join(soluciones), f"Validación: {medicion}"], "opciones":["Quiero profundizar el diagnóstico","Quiero hablar con BizSoft","Tengo otro problema"], "estado":{"flujo":"diagnostico","paso":"contexto","categoria":cat}}


def responder(texto, estado=None):
    estado=estado or {}; consulta=(texto or "").strip()
    if not consulta:
        return {"mensaje":"Cuéntame un problema u oportunidad. BizSoft te ayuda a analizarlo antes de construir o invertir.","opciones":["Mi negocio no vende lo suficiente","Tengo un proceso que demora mucho","Quiero analizar una inversión"],"estado":{}}

    if estado.get("flujo") == "inversion":
        return flujo_inversion(consulta, estado)
    if es_inversion(consulta) or "analizar otra inversión" in consulta.lower() or "analizar otra inversion" in consulta.lower():
        return iniciar_inversion()

    if estado.get("flujo")=="diagnostico" and estado.get("paso")=="contexto":
        q=consulta.lower()
        if "otro problema" in q:
            return {"mensaje":"Describe el nuevo problema: qué ocurre, a quién afecta y dónde lo observaste.","opciones":[],"estado":{}}
        if "hablar con bizsoft" in q:
            return {"mensaje":"Baja a Contacto y déjanos tu nombre y un medio de contacto junto con el problema.","opciones":[],"estado":estado}
        return {"mensaje":"Para profundizar: ¿a quién afecta, dónde ocurre y qué consecuencia genera (ventas, tiempo, dinero, quejas u otro impacto)?","opciones":[],"estado":{"flujo":"diagnostico","paso":"evidencia","categoria":estado.get("categoria","general")}}
    if estado.get("flujo")=="diagnostico" and estado.get("paso")=="evidencia":
        return {"mensaje":"Buen punto de partida. Primero validaríamos el problema con evidencia y un piloto pequeño.","detalle":["1. Observar y registrar casos reales.","2. Entrevistar a las personas afectadas.","3. Identificar la causa principal.","4. Diseñar una solución mínima.","5. Medir si mejora ventas, tiempo, costo o servicio."],"opciones":["Quiero hablar con BizSoft","Tengo otro problema"],"estado":{"flujo":"diagnostico","paso":"contexto","categoria":estado.get("categoria","general")}}

    return diagnostico(consulta)
