import re

IDEAS = {
    "bajo": [
        {"titulo":"Servicio digital para pequeños negocios","por_que":"Puede empezar con poca inversión y resolver problemas concretos.","validacion":"Habla con 10 negocios y registra qué problema se repite."},
        {"titulo":"Reventa especializada por internet","por_que":"Permite probar demanda sin abrir un local grande.","validacion":"Publica una muestra antes de comprar inventario amplio."},
        {"titulo":"Generación de leads para empresas","por_que":"Muchas empresas necesitan nuevos prospectos.","validacion":"Escoge un rubro y prepara una pequeña muestra de prospectos."},
    ],
    "medio": [
        {"titulo":"Distribución B2B especializada","por_que":"Puede generar ventas recurrentes si resuelve una necesidad de abastecimiento.","validacion":"Entrevista compradores antes de comprar stock."},
        {"titulo":"Comercio electrónico de nicho","por_que":"Combina inventario controlado y captación digital.","validacion":"Mide consultas antes de ampliar inventario."},
        {"titulo":"Automatización para MYPE","por_que":"Reduce tiempo y costos en problemas repetitivos.","validacion":"Ofrece un piloto y mide el ahorro generado."},
    ],
    "alto": [
        {"titulo":"Negocio físico con apoyo digital","por_que":"Combina presencia local, inventario y captación online.","validacion":"Estudia zona, competencia y punto de equilibrio."},
        {"titulo":"Distribución y comercialización B2B","por_que":"Permite manejar stock y contratos mayores.","validacion":"Consigue pedidos piloto antes de invertir fuerte."},
        {"titulo":"Plataforma tecnológica especializada","por_que":"Puede escalar si resuelve un problema frecuente de un nicho.","validacion":"Construye un MVP y consigue 3 clientes piloto."},
    ],
}

def capital_nivel(texto):
    nums = re.findall(r"(?:s/\.?\s*)?(\d[\d,.]*)", texto.lower())
    if not nums: return None
    try: n = float(nums[0].replace(",", ""))
    except ValueError: return None
    return "bajo" if n < 3000 else "medio" if n < 15000 else "alto"

def es_emprender(t):
    t=t.lower(); claves=["no se que negocio","no sé qué negocio","quiero emprender","poner un negocio","iniciar un negocio","idea de negocio","negocio me recomiendas"]
    return any(k in t for k in claves)

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
        return {"mensaje":"Cuéntame un problema que hayas visto en tu negocio, organización, entidad o en la calle. BizSoft te ayuda a convertirlo en una solución.","opciones":["Mi negocio no vende lo suficiente","Tengo un proceso que demora mucho","Quiero iniciar un negocio"],"estado":{}}

    if estado.get("flujo")=="diagnostico" and estado.get("paso")=="contexto":
        q=consulta.lower()
        if "otro problema" in q:
            return {"mensaje":"Perfecto. Describe el nuevo problema: qué ocurre, a quién afecta y dónde lo observaste.","opciones":[],"estado":{}}
        if "hablar con bizsoft" in q:
            return {"mensaje":"Excelente. Baja a la sección Contacto y déjanos tu nombre y un medio de contacto junto con el problema. Lo usaremos como punto de partida del diagnóstico.","opciones":[],"estado":estado}
        return {"mensaje":"Para profundizar: ¿a quién afecta el problema, dónde ocurre y qué consecuencia genera (pérdida de ventas, tiempo, dinero, quejas u otro impacto)?","opciones":[],"estado":{"flujo":"diagnostico","paso":"evidencia","categoria":estado.get("categoria","general")}}

    if estado.get("flujo")=="diagnostico" and estado.get("paso")=="evidencia":
        return {"mensaje":"Buen punto de partida. En BizSoft no construiríamos tecnología todavía: primero validaríamos el problema con evidencia y un piloto pequeño.","detalle":["1. Observar y registrar casos reales.","2. Entrevistar a las personas afectadas.","3. Identificar la causa principal.","4. Diseñar una solución mínima.","5. Medir si mejora ventas, tiempo, costo o servicio."],"opciones":["Quiero hablar con BizSoft","Tengo otro problema"],"estado":{"flujo":"diagnostico","paso":"contexto","categoria":estado.get("categoria","general")}}

    if estado.get("flujo")=="emprender":
        paso=estado.get("paso","capital")
        if paso=="capital":
            nivel=capital_nivel(consulta)
            if not nivel: return {"mensaje":"Dime aproximadamente cuánto capital podrías invertir.","opciones":["S/ 2,000","S/ 5,000","S/ 20,000"],"estado":{"flujo":"emprender","paso":"capital"}}
            return {"mensaje":"¿Qué prefieres: internet, vender a empresas, local físico o aún no tienes preferencia?","opciones":["Internet","Vender a empresas","Local físico","No tengo preferencia"],"estado":{"flujo":"emprender","paso":"modelo","nivel":nivel}}
        if paso=="modelo":
            estado.update(modelo=consulta,paso="tiempo")
            return {"mensaje":"¿Cuánto tiempo podrías dedicarle?","opciones":["Tiempo completo","Medio tiempo","Solo fines de semana"],"estado":estado}
        if paso=="tiempo":
            ideas=IDEAS[estado.get("nivel","medio")]
            return {"mensaje":"Estas son tres oportunidades para validar, no promesas de éxito:","detalle":[f"{i+1}. {x['titulo']} — {x['por_que']} Validación: {x['validacion']}" for i,x in enumerate(ideas)],"opciones":["Quiero hablar con BizSoft","Tengo otro problema"],"estado":{}}

    if es_emprender(consulta):
        return {"mensaje":"Empecemos por tu situación. ¿Con cuánto capital aproximado cuentas?","opciones":["S/ 2,000","S/ 5,000","S/ 20,000"],"estado":{"flujo":"emprender","paso":"capital"}}

    return diagnostico(consulta)
