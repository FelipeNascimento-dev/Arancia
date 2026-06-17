# CRM BFF — roadmap de implementação

Status: `pendente` | `em teste` | `ok`

| Fase | Entrega | Status |
| ---- | ------- | ------ |
| 0 | Auth `api_key_basic` (session, client, Celery) | em teste |
| 1 | Dashboard + context processor `/me/context` | em teste |
| 2 | Clientes (listagem, CRUD, contatos/endereços POST, delete AJAX) | em teste |
| 3 | Contratos + Alertas | em teste |
| 4 | Faturamento | em teste |
| 5 | Tasks (listagens) | em teste |
| 6 | Formulário unificado + Recorrências + scheduler one-shot Bearer | ok |
| 7 | Detalhe de Task + AJAX (edit, links, watchers, can_comment) | ok |
| 8 | Projetos (edit route, membros polimórficos, demandantes, lookups) | ok |
| 9 | Boards e Kanban (access/me, move, colunas, customer_gai) | ok |
| 10 | Configurações (service types int id, campos spec) | ok |
| 11 | Celery hardening + codenames + README | ok |

## Gaps API (não implementar no Django)

- DELETE contrato / faturamento
- PATCH/DELETE contato/endereço individual
- CRUD `/teams/*`
- Dashboard endpoint dedicado

## Codenames Django vs API

Gates de template e `@crm_permission_required` usam codenames do seed Alembic com `app_label=crm` (modelo dummy `CrmPermissions`). Exemplos confirmados:

| Django (BFF) | API `/me/context` (pode divergir) |
| ------------ | --------------------------------- |
| `crm.view_contract` | `view_contracts` (plural) |
| `crm.view_task` | `view_tasks` (plural) |

O menu lateral e botões seguem **Django** (`{% if perms.crm.view_task %}`). `permission_codenames` de `/me/context` serve para atalhos dinâmicos no context processor — não substituir gates existentes sem alinhar seed.
