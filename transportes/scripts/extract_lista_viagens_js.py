"""One-off helper to extract lista_viagens inline JS to static file."""
from pathlib import Path
import re

template = Path(__file__).resolve().parents[1] / "templates/transportes/transportes/lista_viagens.html"
lines = template.read_text(encoding="utf-8").splitlines()

start = next(i for i, l in enumerate(lines) if i > 2400 and l.strip() == "<script>")
end = next(i for i, l in enumerate(lines) if l.strip() == "{% endblock %}")

script_chunks = []
i = start
while i < end:
    if lines[i].strip() == "<script>":
        j = i + 1
        while j < end and lines[j].strip() != "</script>":
            j += 1
        script_chunks.append("\n".join(lines[i + 1 : j]))
        i = j + 1
    else:
        i += 1

parts = []
for chunk in script_chunks:
    chunk = chunk.strip()
    if chunk.startswith('document.addEventListener("DOMContentLoaded"'):
        inner = re.sub(
            r'^document\.addEventListener\(["\']DOMContentLoaded["\'],\s*function\s*\(\)\s*\{',
            "",
            chunk,
        )
        inner = re.sub(r"\}\);\s*$", "", inner.strip())
        parts.append(inner)
    else:
        parts.append(chunk)

body = "\n\n".join(parts)
body = body.replace(
    '{{ pode_escolher_transportadora|yesno:"true,false" }}',
    "cfg.pode_escolher_transportadora",
)
body = body.replace('{{ pa_travada|yesno:"true,false" }}', "cfg.pa_travada")
body = body.replace("{{ filtros_ativos }}", "cfg.filtros_ativos")
body = re.sub(
    r'"\{% url \'transportes:buscar_motoristas_travels\' %\}" \+',
    "cfg.urls.buscar_motoristas +",
    body,
)
body = re.sub(
    r'"\{% url \'transportes:imprimir_os_viagens\' %\}"',
    "cfg.urls.imprimir_os",
    body,
)

old_events = """            const travelId = this.dataset.travelId;
            const targetId = this.dataset.eventsTarget;
            const jsonEl = document.getElementById(targetId);

            let events = [];

            console.log("travelId:", travelId);
            console.log("targetId:", targetId);
            console.log("jsonEl:", jsonEl);

            try {
                events = jsonEl ? JSON.parse(jsonEl.textContent.trim()) : [];
                console.log("Eventos carregados:", events);
            } catch (e) {
                console.error("Erro ao converter eventos:", e);
                events = [];
            }

            title.textContent = `Ocorrências da viagem ${travelId}`;

            if (!events.length) {
                content.innerHTML = `<div class="empty-events">Nenhuma ocorrência encontrada para esta viagem.</div>`;
            } else {
                content.innerHTML = `
                    <div class="occurrences-list">
                        ${events.map(buildOccurrence).join("")}
                    </div>
                `;
            }

            modal.classList.add("show");"""

new_events = """            const travelId = this.dataset.travelId;
            title.textContent = `Ocorrências da viagem ${travelId}`;
            content.innerHTML = '<div class="results-loading"><div class="spinner"></div><span>Carregando ocorrências...</span></div>';
            modal.classList.add("show");

            const eventsUrl = cfg.urls.travel_events_template.replace("/0/", `/${travelId}/`);
            fetch(eventsUrl, { headers: { Accept: "application/json" } })
                .then((r) => r.json())
                .then((data) => {
                    const events = data.events || [];
                    if (!events.length) {
                        content.innerHTML = '<div class="empty-events">Nenhuma ocorrência encontrada para esta viagem.</div>';
                    } else {
                        content.innerHTML = '<div class="occurrences-list">' + events.map(buildOccurrence).join("") + "</div>";
                    }
                })
                .catch(() => {
                    content.innerHTML = '<div class="empty-events">Erro ao carregar ocorrências.</div>';
                });"""

if old_events in body:
    body = body.replace(old_events, new_events)

view_mode_pattern = re.compile(
    r'const btnCards = document\.getElementById\("viewCards"\);.*?setViewMode\(savedMode\);\s*\}',
    re.S,
)
body = view_mode_pattern.sub("// view mode handled server-side", body)

header = """(function () {
    function getCfg() {
        const el = document.getElementById("lista-viagens-config");
        return el ? JSON.parse(el.textContent) : {};
    }
    const cfg = getCfg();

    function initListaViagens() {
"""
footer = """
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initListaViagens);
    } else {
        initListaViagens();
    }
})();
"""

out_path = Path(__file__).resolve().parents[1] / "static/transportes/js/lista_viagens.js"
out_path.write_text(header + body + footer, encoding="utf-8")
print(f"Wrote {out_path} ({out_path.stat().st_size} bytes)")
