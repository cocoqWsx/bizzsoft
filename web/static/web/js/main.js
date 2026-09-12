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
