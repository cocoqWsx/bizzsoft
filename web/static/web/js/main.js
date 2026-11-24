// BizzSoft: la web presenta los servicios; la atención conversacional ocurre en WhatsApp.
const WHATSAPP_NUMBER = "51978778434";
const WHATSAPP_BASE = `https://wa.me/${WHATSAPP_NUMBER}`;

function abrirWhatsApp(mensaje) {
    const texto = encodeURIComponent(mensaje || "Hola BizzSoft, quisiera información sobre sus soluciones.");
    window.open(`${WHATSAPP_BASE}?text=${texto}`, "_blank", "noopener,noreferrer");
}

// Los botones de sectores y demostraciones llevan la consulta directamente al único asistente: WhatsApp.
document.querySelectorAll("[data-pregunta]").forEach((elemento) => {
    elemento.addEventListener("click", () => abrirWhatsApp(elemento.dataset.pregunta));
});

// El formulario tradicional sigue disponible como alternativa de contacto.
const leadForm = document.getElementById("leadForm");
const leadEstado = document.getElementById("leadEstado");

function obtenerCookie(nombre) {
    const cookies = document.cookie ? document.cookie.split(";") : [];
    for (const cookie of cookies) {
        const item = cookie.trim();
        if (item.startsWith(nombre + "=")) return decodeURIComponent(item.substring(nombre.length + 1));
    }
    return "";
}

if (leadForm) {
    leadForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        leadEstado.textContent = "Enviando...";
        const payload = Object.fromEntries(new FormData(leadForm).entries());
        try {
            const respuesta = await fetch("/api/lead/", {
                method: "POST",
                credentials: "same-origin",
                headers: { "Content-Type": "application/json", "X-CSRFToken": obtenerCookie("csrftoken") },
                body: JSON.stringify(payload)
            });
            const data = await respuesta.json();
            if (!respuesta.ok) throw new Error(data.error || "No se pudo enviar.");
            leadEstado.textContent = data.mensaje;
            leadForm.reset();
        } catch (error) {
            leadEstado.textContent = error.message;
        }
    });
}

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
 contacto.addEventListener('click',close);
})();
