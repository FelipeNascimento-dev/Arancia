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
| Integrações externas | APIs de fulfillment, estoque, transportes, mural, CRM e Intelipost (URLs em `setup/local_settings.py` / `setup/environments.py`) |

Dependências completas: [`requirements.txt`](./requirements.txt).

## Apps Django

| App | Responsabilidade |
| --- | ---------------- |
| [`logistica/`](./logistica/) | Núcleo operacional: usuários, permissões, last mile, fulfillment, check-in/check-out, estoque, reversa, gerenciamento |
| [`transportes/`](./transportes/) | OS, viagens, motoristas, veículos, painel de campo e ferramentas de roteirização |
| [`backoffice/`](./backoffice/) | Importação Excel, cadastro e listagem de equipamentos |
| [`mural/`](./mural/) | Mural operacional (home) e gerenciamento de conteúdo |
| [`crm/`](./crm/) | CRM BFF: clientes, contratos, faturamento, tasks, boards, projetos, recorrências, configurações e alertas via API FastAPI (`crm_api/`) |

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
├── crm/                # BFF CRM (views, forms, templates)
├── crm_api/            # Client HTTP e services da API CRM
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

Tarefas agendadas: desativação diária de usuários inativos (`logistica.tasks.deactivate_inactive_users`, 03:00); geração de tasks recorrentes CRM (`crm.tasks.generate_recurring_tasks`, a cada 15 min); disparo de alertas de contrato (`crm.tasks.fire_contract_alerts`, 08:00).

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

### CRM (BFF)

Browser → Django (`/arancia/crm/...`) → FastAPI (`CRM_API_BASE_URL` + `/api/v1`). Auth BFF (padrão): `Bearer {CRM_INTERNAL_API_SECRET}` + `X-Acting-User` (username logado ou `CRM_SERVICE_USERNAME` em jobs Celery) — montados server-side em `crm_api/context.py`. Rollback: `CRM_BFF_AUTH_MODE=legacy_basic` (Basic + `X-API-Key` + senha na sessão). Scheduler: Bearer only (`CrmApiClient(scheduler=True)`).

**Endpoints agregados** (`CRM_USE_AGGREGATED_ENDPOINTS=true`, default): `/lookups/board-page`, `/boards/{id}/kanban`, `/dashboard/summary`, `/lookups/billing` — reduzem fan-out do Kanban (~10 → 2–3 calls). Rollback: `CRM_USE_AGGREGATED_ENDPOINTS=false`.

**Probe e validação homolog:**

```bash
# Latência direta na API (Bearer)
python manage.py measure_crm_api_latency --username ARC0000 --include-aggregates --board-id {UUID}

# Smoke + SLA bundles (Kanban <3 s, dashboard <2 s, cache MISS após write)
python scripts/validate_crm_bff_homolog.py --username ARC0000
```

Variáveis em [`.env.example`](./.env.example) — não versionar valores reais.

Rotas principais: dashboard, clientes, contratos, faturamento, alertas, tasks (lista/minhas/calendário/novo/edit/detalhe), recorrências, projetos (detalhe/edit/membros/tasks), boards (Kanban + acesso/colunas), configurações (tipos de serviço, prioridades, status). AJAX interno em `/crm/ajax/` (move task, assign/watch/comment/link/subtask, reorder colunas, health).

Documentação Cursor: [`.cursor/rules/220-business-crm-auto.mdc`](./.cursor/rules/220-business-crm-auto.mdc).

## Documentação para desenvolvimento (Cursor)

- [Rules do projeto](./.cursor/rules/README.md)
- [Guia de aplicação das rules](./docs/cursor/README.md)
- [Prompts recomendados](./docs/cursor/PROMPTS.md)
- [Regras de negócio descobertas](./.cursor/business-rules/README.md)

## Alterações recentes

| Data | Tipo | Módulo/Pasta | Alteração | Impacto |
| ---- | ---- | ------------ | --------- | ------- |
| 2026-06-19 | Ajustado | `crm/`, `crm_api/` | Fase 6: probe agregados, SLA homolog, bundles + gates Django | Kanban/dashboard via bundles; `measure_crm_api_latency --include-aggregates` |
| 2026-06-19 | Ajustado | `crm_api/` | Fase 1 auth Bearer BFF → API (`CRM_BFF_AUTH_MODE=bearer`) | Elimina ~1,5 s de latência fixa por request; rollback via `legacy_basic` |
| 2026-06-17 | Adicionado | `crm/` | Fases 1–2: dashboard enriquecido, clientes com soft delete AJAX | Dashboard acessível com qualquer perm CRM; `DELETE /clients/{id}` via ajax |
| 2026-06-17 | Adicionado | `crm/`, `crm_api/` | Módulo CRM BFF reintroduzido (fases 1–3: fundação, clientes, contratos/faturamento/alertas) | Rotas `/arancia/crm/`; menu lateral condicionado a `crm.*`; depende da API FastAPI CRM |
| 2026-06-17 | Removido | `crm/` | App CRM e integrações removidos do Django | Superseded pela reintrodução BFF na mesma data |
| 2026-06-02 | Ajustado | `logistica/models` (GAI) | Campos obrigatórios ao criar novo GAI | Cadastro de cliente/PA exige preenchimento adicional |
| 2026-06-02 | Ajustado | `transportes/` | API de retenção | Integração de retenção atualizada |
| 2026-05-29 | Adicionado | `mural/` | Visualização em carrossel e em lista nos cards | Operadores alternam forma de exibição do mural |
| 2026-05-28 | Ajustado | `setup/settings` | Envio de e-mail | Fluxo de reset de senha passa a enviar corretamente |
| 2026-05-28 | Ajustado | `logistica/views_reverse` | Padrão de names em forms/rotas de romaneio | Consulta e criação de romaneios seguem nomenclatura unificada |
| 2026-05-27 | Adicionado | `logistica/views_fluxo_entrega` | Telas de estorno do retorno do picking (com e sem serial) | Usuários com permissão de fluxo de entrega estornam retorno de picking |
| 2026-05-26 | Ajustado | `transportes/` | Hora no envio de trackings (OS e viagem) | Trackings registram horário no envio |
| 2026-05-25 | Adicionado | `logistica/views_checkin_checkout` | Receber em estoque no menu (`receber_checkin`) | Perfil com permissão recebe check-ins em estoque |
| 2026-05-25 | Adicionado | `logistica/views_checkin_checkout` | Esboço da tela de pré-recebimento check-in | Início do fluxo de pré-recebimento no check-in |
