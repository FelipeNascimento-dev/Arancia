def build_cards(resumo_geral, ordens, ordens_os, ver_rota_uid, filtro_uid, filtro_flag, filtro_msg):
    if ordens_os:  # detalhadas por técnico
        base = ordens_os
    else:
        base = ordens

    if ver_rota_uid or filtro_uid == "sem" or filtro_flag or (filtro_msg and filtro_msg.upper() in ["CRITICO", "CRÍTICO"]):
        return {
            "total": len(base),
            "status": {
                "concluido": sum(1 for o in base if o["status_janela"] == "concluido"),
                "no_tempo": sum(1 for o in base if o["status_janela"] == "no_tempo"),
                "no_limite": sum(1 for o in base if o["status_janela"] == "no_limite"),
                "atrasado": sum(1 for o in base if o["status_janela"] == "atrasado"),
                "flag_azul": sum(1 for o in base if o.get("flag") == "AZUL"),
                "flag_vermelho": sum(1 for o in base if o.get("flag") == "VERMELHO"),
                "mensagem_critico": sum(1 for o in base if (o.get("mensagem") or "").upper() in ["CRITICO", "CRÍTICO"]),
                "sem_tecnico": sum(
    1 for o in base
    if not o.get("uid") or str(o.get("uid")).strip().lower() in ["", "none", "null"]
),

            },
        }
    return resumo_geral
