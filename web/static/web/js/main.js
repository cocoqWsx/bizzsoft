const input = document.getElementById("consulta");
const boton = document.getElementById("btnBuscar");
const chat = document.getElementById("chat");
const chips = document.getElementById("chips");
const leadForm = document.getElementById("leadForm");
const leadEstado = document.getElementById("leadEstado");
const ctaImplementar = document.getElementById("ctaImplementar");
const btnImplementar = document.getElementById("btnImplementar");
const origenDiagnostico = document.getElementById("origenDiagnostico");
const necesidadLead = leadForm ? leadForm.querySelector('[name="necesidad"]') : null;

let historialDiagnostico = [];

let estadoAsistente = {};

function obtenerCookie(nombre) {
    const cookies = document.cookie ? document.cookie.split(";") : [];
    for (const cookie of cookies) {
        const item = cookie.trim();
        if (item.startsWith(nombre + "=")) {
            return decodeURIComponent(item.substring(nombre.length + 1));
        }
    }
    return "";
}

function agregarMensaje(tipo, html) {
    const div = document.createElement("div");
    div.className = `mensaje ${tipo}`;
    div.innerHTML = html;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

function pintarOpciones(opciones = []) {
    chips.innerHTML = "";
    opciones.forEach(opcion => {
        const b = document.createElement("button");
        b.type = "button";
        b.textContent = opcion;
        b.addEventListener("click", () => enviarConsulta(opcion));
        chips.appendChild(b);
    });
}

async function enviarConsulta(textoManual = null) {
    const consulta = (textoManual ?? input.value).trim();
    if (!consulta) return;

    agregarMensaje("user", `<strong>Tú:</strong> ${consulta}`);
    historialDiagnostico.push(`Usuario: ${consulta}`);
    input.value = "";
    boton.disabled = true;
    boton.textContent = "Analizando...";

    try {
        const respuesta = await fetch("/api/asistente/", {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": obtenerCookie("csrftoken")
            },
            body: JSON.stringify({consulta, estado: estadoAsistente})
        });

        if (!respuesta.ok) throw new Error(`Error HTTP ${respuesta.status}`);
        const data = await respuesta.json();
        estadoAsistente = data.estado || {};

        let html = `<strong>BizSoft:</strong> ${data.mensaje || ""}`;
        if (data.detalle && data.detalle.length) {
            html += `<ul>${data.detalle.map(x => `<li>${x}</li>`).join("")}</ul>`;
        }
        agregarMensaje("bot", html);
        const resumenBot = [data.mensaje || "", ...(data.detalle || [])].filter(Boolean).join(" | ");
        if (resumenBot) historialDiagnostico.push(`BizSoft: ${resumenBot}`);
        pintarOpciones(data.opciones || []);
        if (ctaImplementar) ctaImplementar.hidden = false;
    } catch (e) {
        agregarMensaje("bot", `<strong>BizSoft:</strong> No pude procesar la consulta. ${e.message}`);
    } finally {
        boton.disabled = false;
        boton.textContent = "Preguntar";
    }
}

boton.addEventListener("click", () => enviarConsulta());
input.addEventListener("keydown", e => {
    if (e.key === "Enter") enviarConsulta();
});

document.querySelectorAll("[data-texto]").forEach(b => {
    b.addEventListener("click", () => enviarConsulta(b.dataset.texto));
});

document.querySelectorAll("[data-pregunta]").forEach(b => {
    b.addEventListener("click", () => {
        document.getElementById("inicio").scrollIntoView({behavior: "smooth"});
        setTimeout(() => enviarConsulta(b.dataset.pregunta), 400);
    });
});

if (btnImplementar) {
    btnImplementar.addEventListener("click", () => {
        const resumen = historialDiagnostico.slice(-10).join("\n");
        if (necesidadLead && resumen) {
            necesidadLead.value = `Quiero implementar la solución analizada con el Asistente BizSoft.\n\nResumen del diagnóstico:\n${resumen}`;
        }
        if (origenDiagnostico) origenDiagnostico.hidden = false;
        document.getElementById("contacto").scrollIntoView({behavior: "smooth"});
        setTimeout(() => {
            const nombre = leadForm.querySelector('[name="nombre"]');
            if (nombre) nombre.focus();
        }, 500);
    });
}

leadForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    leadEstado.textContent = "Enviando...";
    const payload = Object.fromEntries(new FormData(leadForm).entries());

    try {
        const respuesta = await fetch("/api/lead/", {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": obtenerCookie("csrftoken")
            },
            body: JSON.stringify(payload)
        });

        const data = await respuesta.json();
        if (!respuesta.ok) throw new Error(data.error || "No se pudo enviar.");

        leadEstado.textContent = data.mensaje;
        leadForm.reset();
    } catch (e) {
        leadEstado.textContent = e.message;
    }
});

// BizSoft v9: demo local de predictor de ventas (tendencia lineal)
(() => {
 const abrir=document.getElementById('abrir-predictor'), modal=document.getElementById('predictor-modal');
 const cerrar=document.getElementById('predictor-cerrar'), calcular=document.getElementById('calcular-prediccion');
 const resultado=document.getElementById('predictor-resultado'), contacto=document.getElementById('predictor-contacto');
 if(!abrir||!modal) return;
 const close=()=>{modal.hidden=true;document.body.style.overflow=''};
 abrir.addEventListener('click',()=>{modal.hidden=false;document.body.style.overflow='hidden'});
 cerrar.addEventListener('click',close); modal.addEventListener('click',e=>{if(e.target===modal) close()});
 calcular.addEventListener('click',()=>{
   const y=[...modal.querySelectorAll('.venta-mes')].map(i=>Number(i.value));
   if(y.some(v=>!Number.isFinite(v)||v<=0)){resultado.hidden=false;resultado.textContent='Completa los 6 meses con valores mayores que cero.';return;}
   const n=y.length, xm=(n-1)/2, ym=y.reduce((a,b)=>a+b,0)/n;
   let num=0,den=0; y.forEach((v,i)=>{num+=(i-xm)*(v-ym);den+=(i-xm)**2});
   const slope=num/den, pred=Math.max(0,ym+slope*((n)-xm));
   const pct=ym?((pred-y[n-1])/y[n-1])*100:0;
   resultado.hidden=false;
   resultado.innerHTML=`Estimación orientativa del próximo mes:<br><strong>${pred.toLocaleString('es-PE',{maximumFractionDigits:2})}</strong><br>Tendencia frente al último mes: ${pct>=0?'+':''}${pct.toFixed(1)}%. <small>Demo basada únicamente en tendencia histórica; un proyecto real incorporaría variables relevantes y evaluación del modelo.</small>`;
 });
 contacto.addEventListener('click',()=>{close(); const n=document.querySelector('[name="necesidad"]'); if(n) n.value='Quiero implementar un sistema predictivo de ventas adaptado a los datos de mi empresa.';});
})();
