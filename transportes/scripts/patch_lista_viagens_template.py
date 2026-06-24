"""Patch lista_viagens.html for static assets, view_mode, lazy-load."""
from pathlib import Path
import re

path = Path(__file__).resolve().parents[1] / "templates/transportes/transportes/lista_viagens.html"
text = path.read_text(encoding="utf-8")

# 1. Replace style block with static CSS
text = re.sub(
    r"{% block content %}\s*<style>.*?</style>",
    """{% load static %}
{% block content %}
<link rel="stylesheet" href="{% static 'transportes/css/transportes_lists_common.css' %}">
<link rel="stylesheet" href="{% static 'transportes/css/lista_viagens.css' %}">""",
    text,
    count=1,
    flags=re.S,
)

# 2. View toggle links
old_toggle = """    <div class="view-toggle-group">
        <button type="button" class="btn-view-mode active" id="viewCards" title="Visão em Cards">
            <i class="fa-solid fa-grip"></i>
        </button>
        <button type="button" class="btn-view-mode" id="viewTable" title="Visão em Tabela">
            <i class="fa-solid fa-list"></i>
        </button>"""

new_toggle = """    <div class="view-toggle-group">
        <a href="?{% if base_qs_no_view %}{{ base_qs_no_view }}{% endif %}"
           class="btn-view-mode{% if view_mode != 'table' %} active{% endif %}" title="Visão em Cards">
            <i class="fa-solid fa-grip"></i>
        </a>
        <a href="?{% if base_qs_no_view %}{{ base_qs_no_view }}&{% endif %}view_mode=table"
           class="btn-view-mode{% if view_mode == 'table' %} active{% endif %}" title="Visão em Tabela">
            <i class="fa-solid fa-list"></i>
        </a>"""

text = text.replace(old_toggle, new_toggle)

# 3. Export button formaction
text = text.replace(
    '<button type="submit" name="extrair_travels" value="1" class="btn-main btn-main--export">',
    '<button type="submit" formaction="{% url \'transportes:lista_viagens_export\' %}" class="btn-main btn-main--export">',
)

# 4. Bulk criar eventos formaction
text = text.replace(
    '<button type="submit" name="criar_eventos_cards" value="1" class="btn-bulk btn-bulk--primary">',
    '<button type="submit" formaction="{% url \'transportes:lista_viagens_preparar_eventos\' %}" class="btn-bulk btn-bulk--primary">',
)

# 5. Results area loading overlay
text = text.replace(
    "    <main class=\"results-area\">",
    """    <main class="results-area">
        <div class="results-loading-overlay{% if consultando and not travels %} is-active{% endif %}" id="resultsLoadingOverlay">
            <div class="results-loading">
                <div class="spinner"></div>
                <span>Consultando viagens...</span>
            </div>
        </div>""",
)

# 6. Wrap cards container
text = text.replace(
    '            <div class="cards-container" id="cardsContainer">',
    '            {% if view_mode != "table" %}\n            <div class="cards-container" id="cardsContainer">',
)
text = text.replace(
    '            </div>\n\n            <div class="table-container" id="tableContainer">',
    '            </div>\n            {% endif %}\n\n            {% if view_mode == "table" %}\n            <div class="table-container" id="tableContainer">',
)
text = text.replace(
    '            </div>\n        </form>\n        {% endif %}',
    '            </div>\n            {% endif %}\n        </form>\n        {% endif %}',
    1,
)

# 7. Remove inline event JSON and simplify buttons
text = re.sub(
    r'\s*data-events-target="[^"]*"',
    "",
    text,
)
text = re.sub(
    r'\s*<script type="application/json" id="travel-events-[^"]*">\s*\{\{ item\.travel_events_json\|safe \}\}\s*</script>',
    "",
    text,
)

# 8. Show events button when detailed mode (count only, lazy load)
text = text.replace(
    "{% if response_mode == \"detailed\" and item.travel_events %}",
    "{% if response_mode == \"detailed\" and item.travel_events_count %}",
)

# 9. Driver form action
text = text.replace(
    '<form method="post" id="driverAssignForm">',
    '<form method="post" id="driverAssignForm" action="{% url \'transportes:lista_viagens_atrelar_motorista\' %}">',
)
text = text.replace(
    '                            name="atrelar_motorista_lote"\n                            value="1">',
    '                            >',
)

# 10. Event modal form action
text = text.replace(
    '            <form method="post">\n                {% csrf_token %}\n\n                {% for selected_id in selected_travel_ids %}',
    '            <form method="post" action="{% url \'transportes:lista_viagens_criar_evento_lote\' %}">\n                {% csrf_token %}\n\n                {% for selected_id in selected_travel_ids %}',
)
text = text.replace(
    '                            name="criar_evento_travel_lote"\n                            value="1">',
    '                            >',
)

# 11. Filter form loading state id
text = text.replace(
    '<form method="POST">',
    '<form method="POST" id="listaViagensFilterForm">',
    1,
)

# 12. Remove all inline scripts after travel events modal, add config + static js
idx = text.find('<div class="os-modal-overlay" id="travelEventsDetailModal">')
if idx == -1:
    raise SystemExit("modal not found")
# Keep modals HTML, remove scripts until endblock
endblock = text.rfind("{% endblock %}")
modals_and_rest = text[idx:endblock]

# Strip scripts from modals section
modals_clean = re.sub(r"<script>.*?</script>\s*", "", modals_and_rest, flags=re.S)

config_block = """
{{ lista_viagens_js_config|json_script:"lista-viagens-config" }}
<script src="{% static 'transportes/js/lista_viagens.js' %}"></script>
"""

text = text[:idx] + modals_clean + config_block + "\n{% endblock %}\n"

path.write_text(text, encoding="utf-8")
print(f"Patched {path}")
