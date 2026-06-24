"""Patch consulta_os_transp.html for static assets, view_mode, lazy-load."""
from pathlib import Path
import re

path = Path(__file__).resolve().parents[1] / "templates/transportes/transportes/consulta_os_transp.html"
text = path.read_text(encoding="utf-8")

text = re.sub(
    r"{% block content %}\s*<style>.*?</style>",
    """{% load static %}
{% block content %}
<link rel="stylesheet" href="{% static 'transportes/css/transportes_lists_common.css' %}">
<link rel="stylesheet" href="{% static 'transportes/css/consulta_os_transp.css' %}">""",
    text,
    count=1,
    flags=re.S,
)

old_toggle = """        <div class="view-toggle-group">
            <button type="button" class="btn-view-mode active" id="viewCards" title="Visão em Cards">
                <i class="fa-solid fa-grip"></i>
            </button>
            <button type="button" class="btn-view-mode" id="viewTable" title="Visão em Tabela">
                <i class="fa-solid fa-list"></i>
            </button>
        </div>"""

new_toggle = """        <div class="view-toggle-group">
            <a href="?{% if base_qs_no_view %}{{ base_qs_no_view }}{% endif %}"
               class="btn-view-mode{% if view_mode != 'table' %} active{% endif %}" title="Visão em Cards">
                <i class="fa-solid fa-grip"></i>
            </a>
            <a href="?{% if base_qs_no_view %}{{ base_qs_no_view }}&{% endif %}view_mode=table"
               class="btn-view-mode{% if view_mode == 'table' %} active{% endif %}" title="Visão em Tabela">
                <i class="fa-solid fa-list"></i>
            </a>
        </div>"""

text = text.replace(old_toggle, new_toggle)

text = text.replace(
    '    <main class="results-area">',
    """    <main class="results-area">
        <div class="results-loading-overlay{% if consultando and not orders %} is-active{% endif %}" id="resultsLoadingOverlay">
            <div class="results-loading">
                <div class="spinner"></div>
                <span>Consultando ordens de serviço...</span>
            </div>
        </div>""",
)

text = text.replace(
    '        {% if orders %}\n            <div class="cards-container" id="cardsContainer">',
    '        {% if orders %}\n            {% if view_mode != "table" %}\n            <div class="cards-container" id="cardsContainer">',
)

text = text.replace(
    '            </div>\n\n            <div class="table-container" id="tableContainer">',
    '            </div>\n            {% endif %}\n\n            {% if view_mode == "table" %}\n            <div class="table-container" id="tableContainer">',
)

text = text.replace(
    '                </table>\n            </div>\n\n            {% if pagination.has_prev',
    '                </table>\n            </div>\n            {% endif %}\n\n            {% if pagination.has_prev',
)

text = re.sub(r'\s*data-travels=\'[^\']*\'', "", text)

text = text.replace(
    '<form method="GET" id="consultaOsForm">',
    '<form method="GET" id="consultaOsForm">',
)
# Add id to filter form if missing
if 'id="consultaOsForm"' not in text:
    text = text.replace('<form method="GET">', '<form method="GET" id="consultaOsForm">', 1)

# Remove scripts, keep travel modal
idx = text.find('<div class="modal-overlay" id="travelModal">')
if idx == -1:
    raise SystemExit("travel modal not found")
endblock = text.rfind("{% endblock %}")
modal_section = text[idx:endblock]
modal_clean = re.sub(r"<script>.*?</script>\s*", "", modal_section, flags=re.S)

config_block = """
{{ consulta_os_js_config|json_script:"consulta-os-config" }}
<script src="{% static 'transportes/js/consulta_os_transp.js' %}"></script>
"""

text = text[:idx] + modal_clean + config_block + "\n{% endblock %}\n"
path.write_text(text, encoding="utf-8")
print(f"Patched {path}")
