const input = document.getElementById("consulta");
const boton = document.getElementById("btnBuscar");
const salida = document.getElementById("resultadoIA");

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

async function buscarSolucion() {
    const consulta = input.value.trim();
    if (!consulta) return;

    boton.disabled = true;
    boton.textContent = "Analizando...";

    try {
        const respuesta = await fetch("/api/recomendar/", {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": obtenerCookie("csrftoken")
            },
            body: JSON.stringify({consulta})
        });

        if (!respuesta.ok) throw new Error(`Error HTTP ${respuesta.status}`);

        const data = await respuesta.json();

        salida.innerHTML = `
            <div class="respuesta">
                <h3>${data.titulo}</h3>
                <ul>${data.soluciones.map(s => `<li>${s}</li>`).join("")}</ul>
            </div>
        `;
    } catch (e) {
        salida.innerHTML = `
            <div class="respuesta">
                <h3>No pudimos procesar la consulta</h3>
                <p>${e.message}</p>
            </div>
        `;
    } finally {
        boton.disabled = false;
        boton.textContent = "Buscar";
    }
}

boton.addEventListener("click", buscarSolucion);
input.addEventListener("keydown", e => {
    if (e.key === "Enter") buscarSolucion();
});
