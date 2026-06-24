"""Extract consulta_os_transp inline JS to static file."""
from pathlib import Path
import re

template = Path(__file__).resolve().parents[1] / "templates/transportes/transportes/consulta_os_transp.html"
lines = template.read_text(encoding="utf-8").splitlines()

start = next(i for i, l in enumerate(lines) if l.strip() == "<script>")
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
    if chunk.startswith("document.addEventListener"):
        inner = re.sub(
            r"^document\.addEventListener\([\"']DOMContentLoaded[\"'],\s*function\s*\(\)\s*\{",
            "",
            chunk,
        )
        inner = re.sub(r"\}\);\s*$", "", inner.strip())
        parts.append(inner)
    elif chunk.startswith("function makeSearchable"):
        parts.append(chunk)
    else:
        parts.append(chunk)

body = "\n\n".join(parts)
body = body.replace("{{ filtros_ativos|default:0 }}", "cfg.filtros_ativos")

old_travel = """                const orderNumber = this.getAttribute("data-order-number") || "-";
                const travelsRaw = this.getAttribute("data-travels") || "[]";

                let travels = [];

                try {
                    travels = JSON.parse(travelsRaw);
                } catch (e) {
                    travels = [];
                }

                modalTitle.textContent = `Viagens da OS ${orderNumber}`;
                modalList.innerHTML = "";

                if (!travels.length) {
                    modalList.innerHTML = '<div class="travel-empty">Nenhuma viagem encontrada para esta OS.</div>';
                    openModal();
                    return;
                }

                travels.forEach(travel => {
                    const row = document.createElement("div");
                    row.className = "travel-row";
                    row.innerHTML = `
                        <span class="travel-id">ID: ${travel.id || "-"}</span>
                        <span class="travel-status">${travel.status || "-"}</span>
                    `;
                    modalList.appendChild(row);
                });

                openModal();"""

new_travel = """                const orderNumber = this.getAttribute("data-order-number") || "-";
                modalTitle.textContent = `Viagens da OS ${orderNumber}`;
                modalList.innerHTML = '<div class="results-loading"><div class="spinner"></div><span>Carregando viagens...</span></div>';
                openModal();

                const url = cfg.urls.order_travels + "?order_number=" + encodeURIComponent(orderNumber);
                fetch(url, { headers: { Accept: "application/json" } })
                    .then((r) => r.json())
                    .then((data) => {
                        const travels = data.travels || [];
                        modalList.innerHTML = "";
                        if (!travels.length) {
                            modalList.innerHTML = '<div class="travel-empty">Nenhuma viagem encontrada para esta OS.</div>';
                            return;
                        }
                        travels.forEach((travel) => {
                            const row = document.createElement("div");
                            row.className = "travel-row";
                            row.innerHTML = `
                                <span class="travel-id">ID: ${travel.id || "-"}</span>
                                <span class="travel-status">${travel.status || "-"}</span>
                            `;
                            modalList.appendChild(row);
                        });
                    })
                    .catch(() => {
                        modalList.innerHTML = '<div class="travel-empty">Erro ao carregar viagens.</div>';
                    });"""

if old_travel in body:
    body = body.replace(old_travel, new_travel)

view_mode_pattern = re.compile(
    r"const btnCards = document\.getElementById\(\"viewCards\"\);.*?setViewMode\(savedMode\);\s*\}",
    re.S,
)
body = view_mode_pattern.sub("// view mode handled server-side", body)

header = """(function () {
    function getCfg() {
        const el = document.getElementById("consulta-os-config");
        return el ? JSON.parse(el.textContent) : {};
    }
    const cfg = getCfg();

    function initConsultaOs() {
"""
footer = """
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initConsultaOs);
    } else {
        initConsultaOs();
    }
})();
"""

out_path = Path(__file__).resolve().parents[1] / "static/transportes/js/consulta_os_transp.js"
out_path.write_text(header + body + footer, encoding="utf-8")
print(f"Wrote {out_path} ({out_path.stat().st_size} bytes)")
