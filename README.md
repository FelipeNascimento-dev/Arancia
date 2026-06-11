# Arancia — C-Trends

Sistema web Django para operações logísticas da C-Trends: fulfillment/last mile, check-in/check-out, transportes, backoffice e mural operacional.

Prefixo de rotas: `/arancia/`.

## Stack

| Componente | Versão / uso |
| ---------- | ------------ |
| Python | 3.12+ (ambiente com `venv/`) |
| Django | 5.2 |
| Celery | 5.5 — tarefas agendadas (Redis como broker) |
| Banco | SQLite em dev (`setup/settings.py`); PostgreSQL via `setup/local_settings.py` em ambientes internos |
| Integrações externas | APIs de fulfillment, estoque, transportes, mural e Intelipost (URLs em `setup/local_settings.py`) |

Dependências completas: [`requirements.txt`](./requirements.txt).

## Apps Django

| App | Responsabilidade |
| --- | ---------------- |
| [`logistica/`](./logistica/) | Núcleo operacional: usuários, permissões, last mile, fulfillment, check-in/check-out, estoque, reversa, gerenciamento |
| [`transportes/`](./transportes/) | OS, viagens, motoristas, veículos, painel de campo e ferramentas de roteirização |
| [`backoffice/`](./backoffice/) | Importação Excel, cadastro e listagem de equipamentos |
| [`mural/`](./mural/) | Mural operacional (home) e gerenciamento de conteúdo |
| [`crm/`](./crm/) | CRM operacional (BFF): clientes, contratos, faturamento, tarefas, projetos, boards/Kanban — dados na API externa `api-crm` |

Configuração central: [`setup/`](./setup/) (`settings`, `urls`, middleware, Celery).

## Identidade, GAI e permissões

`User` e `Group` do Django **não** identificam sozinhos o cliente ou PA real do usuário. Escopo operacional segue:

```text
User → UserDesignation → GroupAditionalInformation (GAI) → dados filtrados
```

Modelos em [`logistica/models.py`](./logistica/models.py):

- `GroupAditionalInformation` — dados de cliente/PA (IATA, depósito, endereço, CNPJ etc.)
- `UserDesignation` — vínculo do usuário com um GAI
- `PermissaoUsuarioDummy` — permissões customizadas Django (`checkin_principal`, `lastmile_b2c`, `receber_checkin`, etc.)

Middleware de sessão e expiração de senha: [`setup/middleware/`](./setup/middleware/).

## Estrutura de pastas

```text
Arancia/
├── logistica/          # views/, forms/, templates/, tasks.py
├── transportes/
├── backoffice/
├── mural/
├── crm/                # BFF CRM (views, services, templates; sem models de negócio)
├── setup/              # settings, urls, celery, middleware
├── base_templates/     # templates globais
├── base_static/        # assets estáticos
├── media/
├── manage.py
├── requirements.txt
├── AGENTS.md
├── .cursorrules
└── .cursor/            # rules e regras de negócio para Cursor
```

Organização interna de `logistica/views/` por domínio: `views_checkin_checkout/`, `views_fluxo_entrega/`, `views_lastmile_consultas/`, `views_reverse/`, `views_recebimento_estoque/`, `views_gerenciamento/`, `views_user/`, entre outros.

## Execução local

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

Acesso: `http://127.0.0.1:8000/arancia/`.

**Configuração de ambiente:** copie/ajuste `setup/local_settings.py` (não versionar secrets). Define hosts, URLs de API, banco PostgreSQL e `PROJECT_BASE_PATH`.

**Celery** (Redis em `localhost:6379`):

```powershell
celery -A setup worker -l info
celery -A setup beat -l info
```

Tarefas agendadas: desativação diária de usuários inativos (`logistica.tasks.deactivate_inactive_users`, 03:00); alertas CRM vencidos (`crm.tasks.crm_fire_due_alerts`, 06:00); geração de tarefas recorrentes (`crm.tasks.crm_generate_recurring_tasks`, 06:30).

**Admin Django:** `/arancia/admin/`.

## Módulos principais (`logistica`)

| Área | Rotas (name) | Pasta |
| ---- | ------------- | ----- |
| Usuário / auth | login, register, settings, senhas privilegiadas | `views_user/` |
| Last mile / fulfillment | consulta pedidos, recebimento, estorno, reserva equip., saída campo, tracking IP | `views_fluxo_entrega/`, `view_fullfilment/` |
| Consultas last mile | extracao_pedidos, consulta_etiquetas, consulta_pedidos | `views_lastmile_consultas/` |
| Check-in / check-out | client_select, client_checkin, receber_em_estoque, pre_recebimento, checkout reverse | `views_checkin_checkout/` |
| Estoque / kits | gerenciamento_estoque, gerenciamento_kits, recebimento_remessa | `views_recebimento_estoque/` |
| Reversa | reverse_create(V2), lista_romaneios, consulta cotação | `views_reverse/` |
| Gerenciamento | user_ger, skill_ger | `views_gerenciamento/` |

Rotas completas: [`logistica/urls.py`](./logistica/urls.py), [`transportes/urls.py`](./transportes/urls.py), [`backoffice/urls.py`](./backoffice/urls.py), [`mural/urls.py`](./mural/urls.py), [`crm/urls.py`](./crm/urls.py).

### CRM (`/arancia/crm/`)

Integração BFF com API FastAPI CRM — **não** persiste tabelas `crm_*` no Django; permissões `crm.*` vêm do seed Alembic no banco compartilhado.

| Área | Rotas principais | Permissão UX típica |
| ---- | ---------------- | ------------------- |
| Dashboard | `crm/` | qualquer `crm.view_*` |
| Clientes | `crm/clients/` | `crm.view_clients` |
| Contratos / faturamento / alertas | `crm/contracts/`, `crm/billing/`, `crm/alerts/` | `crm.view_*` do módulo |
| Tarefas | `crm/tasks/`, links/watchers, AJAX assignees, demandantes GAI | `crm.view_tasks`, `crm.manage_watchers` |
| Recorrências | `crm/tasks/recurrences/` | `crm.view_task_recurrences` |
| Projetos | `crm/projects/`, `crm/projects/<id>/tasks/` | `crm.view_projects` |
| Boards / Kanban | `crm/boards/`, settings/colunas, acesso PATCH | `crm.view_boards`, `crm.manage_board_columns` |
| Configurações | `crm/settings/` + reorder status-tasks | `crm.view_settings`, `crm.manage_status_tasks` |

Variáveis: ver [`.env.example`](./.env.example) e `setup/local_settings.py` (não versionar secret): `CRM_API_BASE_URL`, `CRM_API_V1_STR`, `CRM_INTERNAL_API_SECRET`, `CRM_API_TIMEOUT`, `CRM_API_VERIFY_SSL`, `CRM_DEFAULT_LIMIT`, `CRM_ENABLE_DEBUG_LOGS`, `CRM_SERVICE_USER_ID`, `CRM_SERVICE_USERNAME`.

Pré-requisitos: `python manage.py crm_prerequisites`. Testes: `python manage.py test crm.tests`.

### Rotas AJAX internas (browser → Django → API)

| Rota BFF | API proxy | Uso |
| -------- | --------- | --- |
| `crm/ajax/lookups/crm/` | `GET /lookups/crm` | Filtro de service types por cliente |
| `crm/ajax/lookups/groups/` | `GET /lookups/groups` | Grupos para demandantes GAI |
| `crm/ajax/lookups/gais/` | `GET /lookups/gais` | Picker typeahead de GAIs demandantes |
| `crm/ajax/tasks/<id>/move/` | `PATCH /tasks/{id}/move` | Kanban drag-and-drop |
| `crm/ajax/health/` | health check | Diagnóstico |

Gates GAI centralizados em [`crm/services/gates.py`](./crm/services/gates.py) (`require_gai_or_render`, `ajax_require_gai`). Usuário sem `UserDesignation`/GAI recebe mensagem amigável sem chamar a API.

Tarefas de **projeto** aceitam `requester_gai_ids[]` no create/edit (formulário unificado em `crm/tasks/new/`). Vínculos entre tarefas enviam `target_task_id` para a API.

**EntityRef:** respostas da API incluem objetos aninhados (`customer`, `contract`, `status`, etc.). Exibição via `crm/services/refs.py` e filtros `crm_tags` (`crm_customer_label`, …); forms continuam enviando apenas `*_id`. Smoke homolog: `crm/ajax/health/`, `crm/diagnostic/validate-context/` (staff), cache `GET /me/context`.

## Documentação para desenvolvimento (Cursor)

- [Rules do projeto](./.cursor/rules/README.md)
- [Guia de aplicação das rules](./docs/cursor/README.md)
- [Prompts recomendados](./docs/cursor/PROMPTS.md)
- [Regras de negócio descobertas](./.cursor/business-rules/README.md)

## Alterações recentes

| Data | Tipo | Módulo/Pasta | Alteração | Impacto |
| ---- | ---- | ------------ | --------- | ------- |
| 2026-06-10 | Adicionado | `crm/` | EntityRef (`refs.py`, `crm_tags`), demandantes GAI, gates, smoke homolog | Listagens exibem nomes via refs; forms enviam `*_id`; testes BFF §12 |
| 2026-06-10 | Adicionado | `crm/` | Task links/watchers, boards CRUD/colunas, recorrências, reorder status, testes BFF | Usuários com permissões `crm.*` acessam telas colaborativas completas |
| 2026-06-09 | Adicionado | `crm/` | App CRM completo (fases 4–7): tarefas, projetos, Kanban, Celery, configurações | Usuários com permissões `crm.*` acessam módulo em `/arancia/crm/` via BFF |
| 2026-06-02 | Ajustado | `logistica/models` (GAI) | Campos obrigatórios ao criar novo GAI | Cadastro de cliente/PA exige preenchimento adicional |
| 2026-06-02 | Ajustado | `transportes/` | API de retenção | Integração de retenção atualizada |
| 2026-05-29 | Adicionado | `mural/` | Visualização em carrossel e em lista nos cards | Operadores alternam forma de exibição do mural |
| 2026-05-28 | Ajustado | `setup/settings` | Envio de e-mail | Fluxo de reset de senha passa a enviar corretamente |
| 2026-05-28 | Ajustado | `logistica/views_reverse` | Padrão de names em forms/rotas de romaneio | Consulta e criação de romaneios seguem nomenclatura unificada |
| 2026-05-27 | Adicionado | `logistica/views_fluxo_entrega` | Telas de estorno do retorno do picking (com e sem serial) | Usuários com permissão de fluxo de entrega estornam retorno de picking |
| 2026-05-26 | Ajustado | `transportes/` | Hora no envio de trackings (OS e viagem) | Trackings registram horário no envio |
| 2026-05-25 | Adicionado | `logistica/views_checkin_checkout` | Receber em estoque no menu (`receber_checkin`) | Perfil com permissão recebe check-ins em estoque |
| 2026-05-25 | Adicionado | `logistica/views_checkin_checkout` | Esboço da tela de pré-recebimento check-in | Início do fluxo de pré-recebimento no check-in |
