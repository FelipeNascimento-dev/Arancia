"""Gera CSS/JS estáticos de transportes a partir do template legado (29dc94d)."""
import re
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parents[2] / "base_static" / "transportes"
REV = "29dc94d"


def git_show(path: str) -> str:
    return subprocess.check_output(
        ["git", "show", f"{REV}:{path}"],
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def extract_style(html: str) -> str:
    match = re.search(r"<style>(.*?)</style>", html, re.S)
    return match.group(1).strip() if match else ""


def extract_scripts(html: str) -> list[str]:
    blocks = []
    for match in re.finditer(r"<script(?![^>]*type=)([^>]*)>(.*?)</script>", html, re.S):
        body = match.group(2).strip()
        if len(body) > 200:
            blocks.append(body)
    return blocks


def main() -> None:
    (BASE / "css").mkdir(parents=True, exist_ok=True)
    (BASE / "js").mkdir(parents=True, exist_ok=True)

    lv_html = git_show("transportes/templates/transportes/transportes/lista_viagens.html")
    (BASE / "css" / "lista_viagens.css").write_text(
        extract_style(lv_html) + "\n", encoding="utf-8"
    )

    co_html = git_show("transportes/templates/transportes/transportes/consulta_os_transp.html")
    (BASE / "css" / "consulta_os_transp.css").write_text(
        extract_style(co_html) + "\n", encoding="utf-8"
    )

    common = """/* Estilos compartilhados — listagens transportes */
.page-layout { display: flex; gap: 16px; align-items: flex-start; }
.results-area { flex: 1; min-width: 0; position: relative; }
.results-loading-overlay {
  display: none;
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.75);
  z-index: 20;
  align-items: center;
  justify-content: center;
}
.results-loading-overlay.is-active { display: flex; }
.results-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  color: #475569;
}
.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e2e8f0;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: transp-spin 0.8s linear infinite;
}
@keyframes transp-spin { to { transform: rotate(360deg); } }
"""
    (BASE / "css" / "transportes_lists_common.css").write_text(common, encoding="utf-8")

    parts = []
    for chunk in extract_scripts(lv_html):
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
    body = re.sub(
        r'"\{% url \'transportes:buscar_motoristas_travels\' %\}" \+',
        "cfg.urls.buscar_motoristas +",
        body,
    )
    body = re.sub(
        r'"\{% url \'transportes:buscar_motoristas_travels\' %\}\?nome=" \+',
        'cfg.urls.buscar_motoristas + "?nome=" +',
        body,
    )

    view_mode_pattern = re.compile(
        r"const btnCards = document\.getElementById\(\"viewCards\"\);.*?if \(savedMode\) setViewMode\(savedMode\);\s*",
        re.S,
    )
    body = view_mode_pattern.sub(
        "// Visão cards/tabela: alternância server-side (view_mode na URL).\n\n",
        body,
    )

    lv_js = (
        "(function () {\n"
        "    function getCfg() {\n"
        '        var el = document.getElementById("lista-viagens-config");\n'
        "        return el ? JSON.parse(el.textContent) : {};\n"
        "    }\n"
        "    var cfg = getCfg();\n"
        "    function initListaViagens() {\n"
        f"{body}\n"
        "    }\n"
        '    if (document.readyState === "loading") {\n'
        '        document.addEventListener("DOMContentLoaded", initListaViagens);\n'
        "    } else {\n"
        "        initListaViagens();\n"
        "    }\n"
        "})();\n"
    )
    (BASE / "js" / "lista_viagens.js").write_text(lv_js, encoding="utf-8")

    co_js = """(function () {
    function getCfg() {
        var el = document.getElementById("consulta-os-config");
        return el ? JSON.parse(el.textContent) : {};
    }
    var cfg = getCfg();
    function initConsultaOsExtras() {
        document.querySelectorAll(".btn-show-travels").forEach(function (btn) {
            btn.addEventListener("click", function () {
                var orderNumber = btn.getAttribute("data-order-number") || "-";
                var modal = document.getElementById("travelModal");
                var modalTitle = document.getElementById("travelModalTitle");
                var modalList = document.getElementById("travelModalList");
                if (!modal || !modalList) return;
                modalTitle.textContent = "Viagens da OS " + orderNumber;
                modalList.innerHTML = '<div class="results-loading"><div class="spinner"></div><span>Carregando viagens...</span></div>';
                modal.classList.add("show");
                var base = cfg.urls && cfg.urls.order_travels ? cfg.urls.order_travels : "";
                fetch(base + "?order_number=" + encodeURIComponent(orderNumber), {
                    headers: { Accept: "application/json" },
                })
                    .then(function (r) { return r.json(); })
                    .then(function (data) {
                        var travels = data.travels || [];
                        modalList.innerHTML = "";
                        if (!travels.length) {
                            modalList.innerHTML = '<div class="travel-empty">Nenhuma viagem encontrada para esta OS.</div>';
                            return;
                        }
                        travels.forEach(function (travel) {
                            var row = document.createElement("div");
                            row.className = "travel-row";
                            row.innerHTML =
                                '<span class="travel-id">ID: ' + (travel.id || "-") +
                                '</span><span class="travel-status">' + (travel.status || "-") + "</span>";
                            modalList.appendChild(row);
                        });
                    })
                    .catch(function () {
                        modalList.innerHTML = '<div class="travel-empty">Erro ao carregar viagens.</div>';
                    });
            });
        });
        var closeBtn = document.getElementById("closeTravelModal");
        var travelModal = document.getElementById("travelModal");
        if (closeBtn && travelModal) {
            closeBtn.addEventListener("click", function () { travelModal.classList.remove("show"); });
        }
    }
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initConsultaOsExtras);
    } else {
        initConsultaOsExtras();
    }
})();
"""
    (BASE / "js" / "consulta_os_transp.js").write_text(co_js, encoding="utf-8")
    print(f"Static files written under {BASE}")


if __name__ == "__main__":
    main()
