import asyncio
from django.shortcuts import render
from setup.local_settings import API_RESUMO, API_TECNICOS,status_labels, status_style, TOKEN 
from transportes.models import  fetch_json, initials, now_str


async def dashboard_view(request):
    resumo_data, tecnicos = await asyncio.gather(
        fetch_json(API_RESUMO, default={}),
        fetch_json(API_TECNICOS, default=[]),
    )

    contadores_geral = resumo_data.get("geral", {}).get("status", {})
    por_uid = resumo_data.get("por_uid", {})

    uid_to_name = {
        str(t.get("uid") or t.get("id") or t.get("user_id") or "").strip():
        t.get("nome") or t.get("name") or t.get("tecnico") or f"Técnico {t.get('uid')}"
        for t in tecnicos
    }

    def sort_key(item):
        s = item[1].get("status", {})
        return (-(s.get("atrasado", 0) or 0), -(s.get("no_limite", 0) or 0),
                -(s.get("no_tempo", 0) or 0), -(s.get("concluido", 0) or 0))

    tecnicos_list = []
    for uid, tec_data in sorted(por_uid.items(), key=sort_key):
        tecnicos_list.append({
            "uid": uid,
            "nome": uid_to_name.get(str(uid), f"Técnico {uid}"),
            "total": tec_data.get("total", 0),
            "status_counts": tec_data.get("status", {}),
            "iniciais": initials(uid_to_name.get(str(uid), "")),
        })

    context = {
        "status_labels": status_labels,
        "status_style": status_style,
        "contadores_geral": contadores_geral,
        "tecnicos": tecnicos_list,
        "last_update": now_str(),
    }

    return render(request, "CLR/technical_panel.html", context)
