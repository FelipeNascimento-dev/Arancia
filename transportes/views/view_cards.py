def build_cards(resumo_geral, ordens, ordens_os, ver_rota_uid, filtro_uid, filtro_flag, filtro_msg):
    base = ordens_os if ordens_os else ordens

    if ver_rota_uid or filtro_uid == "sem" or filtro_flag or (filtro_msg and filtro_msg.upper() in ["CRITICO", "CRÍTICO"]):
        return {
            "total": len(base),
            "status": {
                "concluido": sum(1 for o in base if o.get("status_janela") == "CONCLUIDO"),
                "no_tempo": sum(1 for o in base if o.get("status_janela") == "NO TEMPO"),
                "no_limite": sum(1 for o in base if o.get("status_janela") == "NO LIMITE"),
                "atrasado": sum(1 for o in base if o.get("status_janela") == "ATRASADO"),
                "flag_azul": sum(1 for o in base if o.get("flag") == "AZUL"),
                "flag_vermelho": sum(1 for o in base if o.get("flag") == "VERMELHO"),
                "mensagem_critico": sum(
                    1 for o in base if (o.get("mensagem") or "").upper() in ["CRITICO", "CRÍTICO"]
                ),
                "sem_tecnico": sum(
                    1 for o in base
                    if not o.get("uid") or str(o.get("uid")).strip().lower() in ["", "none", "null", "0"]
                ),
            },
        }

    return resumo_geral
