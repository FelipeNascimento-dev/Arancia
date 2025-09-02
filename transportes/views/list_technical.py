import asyncio
from django.shortcuts import render
from setup.local_settings import API_RESUMO, API_TECNICOS, status_labels
from transportes.models import fetch_json, initials, now_str


def _sum_counts(counts: dict) -> int:
    return sum(int(counts.get(k, 0) or 0) for k in status_labels.keys())


def dashboard_view(request):
    async def fetch_all():
        return await asyncio.gather(
            fetch_json(API_RESUMO, default={}),
            fetch_json(API_TECNICOS, default=[]),
        )

    resumo_data, tecnicos = asyncio.run(fetch_all())

    contadores_geral = resumo_data.get("geral", {}).get("status", {})
    por_uid = resumo_data.get("por_uid", {})

    total_geral = _sum_counts(contadores_geral) or 1

    # monta lista de status já com cores e %
    status_data = [
        {
            "key": "concluido",
            "label": "Concluído",
            "style": "bg-concluido",
            "value": f"{contadores_geral.get('concluido', 0)} ({(contadores_geral.get('concluido', 0)/total_geral)*100:.0f}%)"
        },
        {
            "key": "no_tempo",
            "label": "No Tempo",
            "style": "bg-no-tempo",
            "value": f"{contadores_geral.get('no_tempo', 0)} ({(contadores_geral.get('no_tempo', 0)/total_geral)*100:.0f}%)"
        },
        {
            "key": "no_limite",
            "label": "No Limite",
            "style": "bg-no-limite",
            "value": f"{contadores_geral.get('no_limite', 0)} ({(contadores_geral.get('no_limite', 0)/total_geral)*100:.0f}%)"
        },
        {
            "key": "atrasado",
            "label": "Atrasado",
            "style": "bg-atrasado",
            "value": f"{contadores_geral.get('atrasado', 0)} ({(contadores_geral.get('atrasado', 0)/total_geral)*100:.0f}%)"
        },
        {
            "key": "sem_horario_definido",
            "label": "Sem Horário",
            "style": "bg-sem-horario",
            "value": f"{contadores_geral.get('sem_horario_definido', 0)} ({(contadores_geral.get('sem_horario_definido', 0)/total_geral)*100:.0f}%)"
        },
    ]

    # tecnicos
    uid_to_name = {
        str(t.get("uid") or t.get("id") or t.get("user_id") or "").strip():
        t.get("nome") or t.get("name") or t.get("tecnico") or f"Técnico {t.get('uid')}"
        for t in tecnicos
    }

    def sort_key(item):
        s = item[1].get("status", {})
        return (-(s.get("atrasado", 0) or 0),
                -(s.get("no_limite", 0) or 0),
                -(s.get("no_tempo", 0) or 0),
                -(s.get("concluido", 0) or 0))

    tecnicos_list = []
    for uid, tec_data in sorted(por_uid.items(), key=sort_key):
        status_counts = tec_data.get("status", {}) or {}

        status_list = [
            {"key": "concluido", "style": "bg-concluido", "value": f"{status_counts.get('concluido', 0)}"},
            {"key": "no_tempo", "style": "bg-no-tempo", "value": f"{status_counts.get('no_tempo', 0)}"},
            {"key": "no_limite", "style": "bg-no-limite", "value": f"{status_counts.get('no_limite', 0)}"},
            {"key": "atrasado", "style": "bg-atrasado", "value": f"{status_counts.get('atrasado', 0)}"},
            {"key": "sem_horario_definido", "style": "bg-sem-horario", "value": f"{status_counts.get('sem_horario_definido', 0)}"},
        ]

        tecnicos_list.append({
            "uid": uid,
            "nome": uid_to_name.get(str(uid), f"Técnico {uid}"),
            "total": tec_data.get("total", 0),
            "iniciais": initials(uid_to_name.get(str(uid), "")),
            "status_counts": status_list,
        })

    context = {
        "status_data": status_data,
        "contadores_geral_total": _sum_counts(contadores_geral),
        "tecnicos": tecnicos_list,
        "site_title":'Gerenciamento',
        "last_update": now_str(),
    }

    return render(request, "transportes/controle_campo/technical_panel.html", context)
