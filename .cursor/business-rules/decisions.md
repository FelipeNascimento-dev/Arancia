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
| 2026-06-09 | CRM | URLs homolog/prod seguem padrão infra: homolog `http://192.168.0.214/hg-api-crm`, prod `http://192.168.0.215/api-crm`; local dev `http://localhost:8000` via env `CRM_API_BASE_URL`. | Config em `setup/local_settings.py` + defaults em `setup/settings.py`. |
| 2026-06-09 | CRM | `CRM_INTERNAL_API_SECRET` via variável de ambiente; nunca versionar valor real. | Celery e `CrmApiClient` (Fase 1) dependem do secret compartilhado com a API. |
| 2026-06-09 | CRM | Permissões `crm.*` (41 codenames) validadas no banco compartilhado via seed Alembic da API — sem migrations Django. | Grupos piloto: `crm_pilot_viewer`, `crm_pilot_operator`, `crm_pilot_admin` criados por `manage.py crm_prerequisites`. |
| 2026-06-10 | CRM | Demandantes GAI em tarefas de projeto: `requester_gai_ids[]` no payload; lookups via `GET /lookups/groups` e `GET /lookups/gais`; picker AJAX em `crm/ajax/lookups/gais/`. | Formulário unificado (`crm/tasks/new/`); detalhe exibe `task.requesters[]`. |
| 2026-06-10 | CRM | Gates GAI centralizados em `crm/services/gates.py`; task links usam `target_task_id` (não `linked_task_id`) no POST à API. | Views CRM importam `require_gai_or_render` / `ajax_require_gai`; templates preferem EntityRef aninhado com fallback flat. |
| 2026-06-10 | CRM | Checklist homologação §12: permissões por módulo, 403 PT-BR via `handle_crm_error`, token só em headers server-side, 100% via `CrmApiClient`, uploads multipart, Kanban move, board access, Celery idempotente. | Validado em testes unitários + padrão existente nas views; gaps API (§13) permanecem fora de escopo. |
