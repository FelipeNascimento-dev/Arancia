"""Helpers para montar cards e dados de gráficos do dashboard CRM."""

SUMMARY_LABELS = {
    "total_records": "Total de registros",
    "total_value": "Valor total",
    "pending_count": "Pendentes",
    "pending_value": "Valor pendente",
    "paid_count": "Pagos",
    "paid_value": "Valor pago",
    "overdue_count": "Vencidos",
    "overdue_value": "Valor vencido",
    "planned_total": "Total planejado",
    "actual_total": "Total realizado",
    "gap": "Gap",
    "gap_pct": "Gap %",
}

PCT_KEYS = frozenset({"gap_pct"})
MONEY_KEYS = frozenset({
    "total_value",
    "pending_value",
    "paid_value",
    "overdue_value",
    "planned_total",
    "actual_total",
    "gap",
})

BILLING_CHART_SKIP_KEYS = frozenset({
    "items",
    "detail",
    "total_records",
    "total_value",
})


def _format_br_number(value, decimals=2):
    formatted = f"{value:,.{decimals}f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def format_card_value(key, value):
    if value in (None, ""):
        return "-"

    if key in PCT_KEYS:
        return f"{_format_br_number(_numeric(value), 2)}%"

    if key in MONEY_KEYS:
        return f"R$ {_format_br_number(_numeric(value), 2)}"

    if isinstance(value, bool):
        return "Sim" if value else "Não"

    if isinstance(value, (int, float)):
        num = float(value)
        if num == int(num):
            return str(int(num))
        return _format_br_number(num, 2)

    if isinstance(value, str):
        try:
            num = float(value.replace(",", "."))
        except ValueError:
            return value
        if key in PCT_KEYS:
            return f"{_format_br_number(num, 2)}%"
        if key in MONEY_KEYS:
            return f"R$ {_format_br_number(num, 2)}"
        if num == int(num):
            return str(int(num))
        return _format_br_number(num, 2)

    return str(value)


def build_summary_cards(billing_data):
    cards = []
    if not isinstance(billing_data, dict):
        return cards
    for key, value in billing_data.items():
        if key in BILLING_CHART_SKIP_KEYS:
            continue
        cards.append({
            "label": SUMMARY_LABELS.get(key, key.replace("_", " ").title()),
            "value": format_card_value(key, value),
            "title": str(value),
        })
    return cards


def _numeric(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _count_group(items, label_key, fallback="Outros"):
    counts = {}
    for item in items or []:
        if not isinstance(item, dict):
            continue
        label = item.get(label_key) or fallback
        counts[label] = counts.get(label, 0) + 1
    labels = list(counts.keys())
    return {
        "labels": labels,
        "values": [counts[label] for label in labels],
    }


def build_chart_data(billing_data, my_tasks, recent_alerts):
    billing = billing_data if isinstance(billing_data, dict) else {}

    billing_counts = {
        "labels": ["Pendentes", "Pagos", "Vencidos"],
        "values": [
            _numeric(billing.get("pending_count")),
            _numeric(billing.get("paid_count")),
            _numeric(billing.get("overdue_count")),
        ],
    }
    billing_values = {
        "labels": ["Pendente", "Pago", "Vencido"],
        "values": [
            _numeric(billing.get("pending_value")),
            _numeric(billing.get("paid_value")),
            _numeric(billing.get("overdue_value")),
        ],
    }

    tasks_by_status = _count_group(my_tasks, "display_status")
    alerts_by_status = _count_group(recent_alerts, "status")

    return {
        "billing_counts": billing_counts,
        "billing_values": billing_values,
        "tasks_by_status": tasks_by_status,
        "alerts_by_status": alerts_by_status,
    }
