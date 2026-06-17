# Decisões Confirmadas

Use este arquivo para registrar decisões de negócio confirmadas pelo usuário ou time.

| Data | Módulo | Decisão | Impacto |
| ---- | ------ | ------- | ------- |
| 2026-06-01 | Identidade | Não existem usuários válidos sem GAI. `UserDesignation.informacao_adicional` deve estar sempre preenchido para usuários operacionais. | Views podem assumir `user.designacao.informacao_adicional`; usuário sem GAI é configuração inválida. |
| 2026-06-01 | Identidade | `sales_channel == 'all'` e `gestao_total` são ambas flags de “visualizar tudo”, usadas em contextos diferentes em momentos diferentes do projeto. | Não unificar nem refatorar essas flags; respeitar o padrão já existente em cada tela. |
| 2026-06-01 | Logística | Reversa V1 e V2 coexistem em produção — partes de cada versão estão ativas. | Não depreciar nem migrar V1→V2 sem solicitação explícita; tratar ambos como válidos. |
| 2026-06-01 | Mural | Gerenciamento do mural lista itens **criados pelo usuário** (`by-created-by/?created_by_id=`). Comportamento **correto** — não alterar. | Manter filtro por autor em `gerenciamento_mural.py`. |
| 2026-06-01 | Mural | **Manter** comportamento atual de `view_mural.py`: create/edit/disable no feed consumidor **sem** checagem `ger_mural` no servidor (só UI). | Não adicionar `has_perm("mural.ger_mural")` em POST handlers de `view_mural.py` salvo solicitação explícita. |
| 2026-06-01 | Geral | Criar rules permanentes `2xx-business-*-auto.mdc` a partir das descobertas confirmadas. | Rules `201`–`205` em `.cursor/rules/`. |
| 2026-06-17 | CRM | Auth BFF migrada para `api_key_basic` (Basic + `X-API-Key`); senha Fernet na sessão; scheduler Celery usa Bearer | `crm_api/session_credentials.py`; remover headers `X-CRM-*`; jobs: scheduler Bearer, alerts Basic+key |
| 2026-06-17 | CRM | Fases 6–11: form RRULE + scheduler one-shot, edit task/projeto, AJAX links/watchers, board access_level, service types legados | Rotas edit; payloads `rrule`; `BoardAccessCreate` com `subject_type`/`access_level` |
| 2026-06-17 | CRM | App `crm/` reintroduzido como BFF Django → FastAPI (`crm_api/`). Sem migrations para tabelas `crm_*`; permissões via seed Alembic (`crm.*`). | Menu CRM visível apenas com `crm_context.has_any_access`; telas exigem `acesso_arancia` + permissão de domínio. |
