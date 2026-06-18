# Métricas de performance — API CRM FastAPI (`hg-api-crm`)

Documento para repasse ao time FastAPI. Consolidado a partir do plano de performance (Fase 5–6A) e medições reais coletadas em **18/Jun/2026**.

---

## 1. Resumo executivo

| Métrica | Valor observado | Conclusão |
|---------|-----------------|------------|
| Latência típica por GET simples | **~1,5–1,8 s** | Gargalo principal |
| Latência endpoints pesados | **3–10 s** | Crítico |
| Overhead Django BFF | **~100 ms** | Não é o problema |
| Calls CRM por navegação Kanban | **10 calls** (~14,5 s total) | Fan-out alto × latência alta |
| Auth | Basic + `X-API-Key` | Mesmo padrão em prod/homolog |

**Conclusão:** o tempo dominante está na **API CRM** (`http://192.168.0.214/hg-api-crm/api/v1`), não no Django BFF.

---

## 2. Ambiente de medição

| Item | Valor |
|------|-------|
| Base URL API | `http://192.168.0.214/hg-api-crm` |
| Prefixo v1 | `/api/v1` |
| Cliente | Django BFF (Arancia) — browser **nunca** chama a API diretamente |
| Autenticação | `Authorization: Basic` (username ARC + senha) + header `X-API-Key` |
| Data das medições | 18/Jun/2026 |
| Ambiente | Dev local → API em rede interna (`192.168.0.214`) |

---

## 3. Metodologia utilizada

### 3.1 Logs do client HTTP Django (`crm_api/client.py`)

Cada call registra tempo de resposta:

```text
CRM API GET http://192.168.0.214/hg-api-crm/api/v1/{endpoint}
CRM API response 200 ... ({elapsed_ms}ms)
```

### 3.2 Headers de instrumentação Django (quando `PERFORMANCE_INSTRUMENTATION=True`)

| Header | Significado |
|--------|-------------|
| `X-Request-Time-Ms` | Tempo total do request Django |
| `X-SQL-Queries` | Queries PostgreSQL no Django |
| `X-CRM-HTTP-Calls` | Quantidade de calls à API CRM |
| `X-CRM-HTTP-Time-Ms` | Soma do tempo gasto em calls CRM |

Ativar em `setup/local_settings.py`:

```python
PERFORMANCE_INSTRUMENTATION = True
```

### 3.3 Comando de baseline (Django → páginas completas)

```bash
python manage.py measure_performance_baseline --username SEU_ARC_USER --password SUA_SENHA --repeat 3
```

URLs medidas: `/`, `/consulta-id/`, `/crm/`, `/crm/comercial/`, `/crm/billing/`

### 3.4 Comando de latência direta (sem Django — ideal para o time FastAPI)

```bash
python manage.py measure_crm_api_latency --username SEU_ARC_USER --password SUA_SENHA --repeat 3 --board-id {ID}
```

Threshold interno: **500 ms** — acima disso é considerado lento.

Endpoints sondados por padrão:

- `health`
- `lookups/crm`
- `lookups/gais`
- `me/context`
- `boards/`

Com `--board-id`: também `boards/{id}`, `boards/{id}/columns`, `tasks/`, `boards/{id}/access/me`.

### 3.5 Teste isolado com curl (recomendado para o time FastAPI)

```bash
curl -w "time_total=%{time_total}\n" -o NUL -s \
  -H "Authorization: Basic ..." \
  -H "X-API-Key: ..." \
  "http://192.168.0.214/hg-api-crm/api/v1/lookups/crm"
```

---

## 4. Latência por endpoint — medições confirmadas

### 4.1 Navegação Kanban (1 request Django — 10 calls sequenciais)

Medição original via logs de rede (Fase 5 do plano de performance):

| # | Endpoint | Método | Tempo (ms) | HTTP |
|---|----------|--------|------------|------|
| 1 | `/boards/` | GET | **1793** | 200 |
| 2 | `/lookups/crm` | GET | **1627** | 200 |
| 3 | `/lookups/gais` | GET | **1551** | 200 |
| 4 | `/lookups/users` | GET | **6** | **404** |
| 5 | `/lookups/crm` *(duplicado)* | GET | **1616** | 200 |
| 6 | `/boards/{id}` | GET | **1590** | 200 |
| 7 | `/boards/{id}/columns` | GET | **1595** | 200 |
| 8 | `/tasks/?board_id={id}&limit=100` | GET | **1601** | 200 |
| 9 | `/boards/{id}/access/me` | GET | **1538** | 200 |
| 10 | `/me/context` | GET | **1583** | 200 |

**Total estimado:** ~**14,5 s** só de HTTP CRM (sequencial).

### 4.2 Endpoints medidos em sessão real (18/Jun/2026 — logs runserver)

| Endpoint | Tempo observado (ms) | HTTP | Observação |
|----------|----------------------|------|------------|
| `GET /billing/summary` | **9943** | 200 | Primeira visita (possível cold start ou query pesada) |
| `GET /billing/summary` | 1636, 1567, 1626 | 200 | Visitas subsequentes |
| `GET /billing/` | 1605, 1600 | 200 | Listagem faturamento |
| `GET /me/context` | 1635, 1686 | 200 | Menu/contexto CRM |
| `GET /clients/` | 1663 | 200 | Listagem clientes |
| `GET /alerts/` | **3139**, **3214** | 200 | Dashboard — mais lento que a média |
| `GET /tasks/my/?limit=50` | **4741**, **4867** | 200 | Dashboard — **endpoint mais lento** |

### 4.3 Metas de SLA propostas (para o time FastAPI)

| Endpoint | Hoje (ms) | Meta (ms) | Cacheável? |
|----------|-----------|-----------|------------|
| `/lookups/crm` | ~1627 | **< 100** | Sim (TTL 5 min) |
| `/lookups/gais` | ~1551 | **< 100** | Sim (TTL 5 min) |
| `/me/context` | ~1583 | **< 200** | Parcial (por usuário) |
| `/boards/{id}/columns` | ~1595 | **< 150** | Parcial |
| `/tasks/` (list, limit=100) | ~1601 | **< 300** | Não |
| `/tasks/my/` | ~4800 | **< 500** | Não |
| `/alerts/` | ~3200 | **< 500** | Não |
| `/billing/summary` | ~1600–9900 | **< 500** | Parcial |
| `/boards/` | ~1793 | **< 200** | Parcial |
| `/clients/` | ~1663 | **< 300** | Parcial |

**Threshold geral:** qualquer GET simples de lookup/catálogo deve responder em **< 500 ms** (usado no comando `measure_crm_api_latency`).

---

## 5. Fan-out — quantas calls a API recebe por tela Django

### 5.1 Dashboard (`GET /crm/`)

| Endpoint | Paralelo? |
|----------|-----------|
| `GET /billing/summary` | Sim (3 workers) |
| `GET /alerts/?limit=20` | Sim |
| `GET /tasks/my/?limit=50` | Sim |
| `GET /me/context` | Context processor (separado) |

**Tempo percebido:** ~**4,8 s** (limitado pelo endpoint mais lento: `/tasks/my/`).

### 5.2 Kanban comercial (`GET /crm/comercial/`)

Sequência típica (~10 calls):

1. `GET /boards/` (resolver board `crm_comercial`)
2. `GET /lookups/crm`
3. `GET /lookups/gais`
4. `GET /lookups/users` → **404**
5. `GET /lookups/crm` *(duplicado no mesmo request)*
6. `GET /boards/{id}`
7. `GET /boards/{id}/columns`
8. `GET /tasks/?board_id={id}&limit=100`
9. `GET /boards/{id}/access/me`
10. `GET /me/context`

Colunas + tasks + access já rodam em **paralelo** (3 workers) após o board carregar; lookups e board detail continuam sequenciais.

### 5.3 Faturamento (`GET /crm/billing/`)

| Endpoint | Quando |
|----------|--------|
| `GET /billing/summary` | Sempre (cards no topo) |
| `GET /billing/` | Sempre (tabela) |
| `GET /me/context` | Context processor |
| `GET /clients/?limit=200` | Só via AJAX (`ajax_billing_lookups`) — removido do SSR |

### 5.4 Lookups carregados em telas de board/task (via `load_board_lookups`)

Cadeia completa de endpoints potenciais:

| Endpoint | Uso |
|----------|-----|
| `GET /lookups/crm` | Catálogo CRM |
| `GET /lookups/gais` | GAIs ativos |
| `GET /lookups/users` | Usuários (404 hoje) |
| `GET /lookups/designations` | Designações |
| `GET /lookups/team-gais` | Team GAIs |
| `GET /lookups/groups` | Grupos |
| `GET /lookups/column-templates` | Templates de coluna |
| `GET /projects/?limit=200` | Projetos |
| `GET /boards/?limit=200` | Boards |

---

## 6. Problemas identificados para investigação no FastAPI

### 6.1 Latência uniforme ~1,6 s sugere

1. **Middleware de auth** — Basic + API key com query pesada em **todo** request
2. **Pool SQLAlchemy** — sem pool, pool esgotado ou conexão nova por request
3. **Proxy nginx → uvicorn** — buffer/timeout/upstream lento
4. **Queries sem índice** — full scan em lookups

### 6.2 Endpoints com latência desproporcional

| Endpoint | Tempo | Hipótese |
|----------|-------|----------|
| `/tasks/my/` | ~4,8 s | N+1, join pesado, falta de índice em `assignees`/`status` |
| `/alerts/` | ~3,2 s | Join contrato + cliente sem índice |
| `/billing/summary` | ~9,9 s (1ª vez) | Agregação sem cache; possível cold start |
| `/lookups/users` | 404 em 6 ms | Endpoint inexistente — BFF tenta fallback |

### 6.3 Tabelas/entidades suspeitas (checklist)

- `status_tasks`
- `boards`
- `tasks` (+ assignees, watchers)
- `designations`
- `alerts` (+ contratos, clientes)
- `billing`

---

## 7. Melhorias sugeridas na API (prioridade para o time FastAPI)

### P0 — Reduzir latência base (~1,6 s → < 200 ms)

1. Logar e otimizar queries SQL dos endpoints de lookup
2. Verificar custo do middleware de autenticação
3. Conferir pool de conexões e proxy nginx
4. Adicionar índices nas tabelas acima

### P1 — Cache na própria API

| Endpoint | TTL sugerido |
|----------|--------------|
| `/lookups/crm` | 5 min |
| `/lookups/gais` | 5 min |
| `/lookups/groups` | 5 min |
| `/lookups/column-templates` | 5 min |

### P2 — Endpoints agregados (reduz fan-out do BFF)

| Endpoint proposto | Substitui | Ganho estimado |
|-------------------|-----------|----------------|
| `GET /lookups/board-page` | crm + gais + users | −3 a −4 calls |
| `GET /boards/{id}/kanban` | board + columns + tasks + access | −3 calls |
| `GET /lookups/billing` | clients + contracts | −2 calls |
| `GET /dashboard/summary` | billing/summary + alerts + tasks/my | −2 calls (1 round-trip) |

### P3 — Corrigir/implementar

- `GET /lookups/users` — hoje retorna **404**; BFF faz fallback caro

---

## 8. Impacto no usuário final (metas de produto)

| Tela | TTFB hoje (estimado) | Meta após otimização API |
|------|----------------------|--------------------------|
| CRM Dashboard | ~5–7 s | **< 2 s** |
| Kanban comercial | ~14–15 s | **< 3 s** |
| Faturamento | ~3–12 s | **< 2 s** |
| Lookups (cache hit) | ~1,6 s/call | **< 100 ms** |

---

## 9. Como o time FastAPI pode reproduzir

```bash
# 1. Health check (sem auth)
curl -w "time_total=%{time_total}\n" -o NUL -s \
  "http://192.168.0.214/hg-api-crm/api/v1/health"

# 2. Endpoints críticos (com auth)
python manage.py measure_crm_api_latency \
  --username ARC_USER \
  --password SENHA \
  --repeat 5 \
  --board-id 1

# 3. Comparar com/sem cache (2ª execução imediata)
# Se 2ª execução continua ~1,6s → problema não é cold start
```

---

## 10. O que o Django BFF já faz (contexto)

Para o time FastAPI saber o que **não** precisa replicar:

- Cache Redis de lookups (TTL 5 min) — mitiga, mas não resolve latência base de ~1,6 s
- HTTP paralelo no dashboard e kanban (3 workers)
- Dedupe de `/lookups/crm` por request
- Keep-alive httpx por request

**Mesmo com essas mitigações**, a experiência continua lenta enquanto cada endpoint simples demorar ~1,6 s na API.

---

## Referências no repositório Arancia

| Arquivo | Descrição |
|---------|-----------|
| `logistica/management/commands/measure_crm_api_latency.py` | Probe direto na API CRM |
| `logistica/management/commands/measure_performance_baseline.py` | Baseline por página Django |
| `setup/middleware/request_timing.py` | Headers de instrumentação |
| `crm_api/client.py` | Logs de latência por call |
| `crm/helpers/lookup_cache.py` | Cache Redis BFF |
| `crm/views/kanban_helpers.py` | Fan-out Kanban |
| `crm/views/view_dashboard.py` | Fan-out Dashboard |
