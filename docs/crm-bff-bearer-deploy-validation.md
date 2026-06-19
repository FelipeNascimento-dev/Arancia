# Validação deploy homolog — Fase 1 Auth Bearer BFF

**Data:** 2026-06-19  
**Ambiente:** `http://192.168.0.214/hg-api-crm` (homolog)  
**Auth mode Django:** `CRM_BFF_AUTH_MODE=bearer` (default)  
**Usuário acting:** `ARC0000` (único usuário local com permissões `crm.*` confirmadas)

## Testes unitários

```text
python manage.py test crm.tests.test_crm_bff.BearerAuthTests \
  crm.tests.test_crm_bff.SessionCredentialsTests \
  crm.tests.test_crm_bff.ClientMaskTests \
  crm.tests.test_crm_bff.CeleryTaskTests
```

**Resultado:** 18 testes OK (Bearer, legacy rollback, service user, masking, Celery).

## Smoke tests (FastAPI homolog)

Script: [`scripts/validate_crm_bff_homolog.py`](../scripts/validate_crm_bff_homolog.py)

```bash
python scripts/validate_crm_bff_homolog.py --username ARC0000
```

| Check | HTTP | Latência (1ª call) |
|-------|------|--------------------|
| `GET /lookups/crm` | 200 | 544 ms (cold) |
| `GET /lookups/gais` | 200 | 40 ms |
| `GET /me/context` | 200 | 49 ms |
| `GET /boards/` | 200 | 23 ms |
| `POST /internal/scheduler/generate-due-tasks` | 200 | 143 ms |

**Summary:** 5/5 HTTP 2xx.

> Usuários sem registro na API CRM (ex.: `ARC0115`) retornam 401 em endpoints BFF mesmo com Bearer válido — comportamento esperado da validação de `X-Acting-User`.

## Probe de latência (Bearer, repeat=5)

| Endpoint | avg | p95 | Meta pacote |
|----------|-----|-----|-------------|
| `GET /lookups/crm` | **27 ms** | 48 ms | cold < 500 ms, warm < 100 ms |
| `GET /me/context` | **36 ms** | 42 ms | idem |

Comparação com baseline pré-Fase 1 (~1,6 s uniforme): **redução ~98%** no custo fixo de auth por request.

Comando equivalente:

```bash
python scripts/validate_crm_bff_homolog.py --username ARC0000 --repeat 5
```

Ou via management command (override homolog):

```python
from django.test.utils import override_settings
from django.core.management import call_command
with override_settings(CRM_API_BASE_URL='http://192.168.0.214/hg-api-crm'):
    call_command('measure_crm_api_latency', username='ARC0000', repeat=5)
```

## Logs FastAPI (`crm_auth_completed mode=internal_bff`)

Não verificável a partir do ambiente de desenvolvimento local (sem acesso SSH aos logs do host `hg-api-crm`).

**Evidência indireta:** latência warm < 50 ms nos endpoints autenticados confirma que o middleware de auth deixou de dominar o tempo de resposta (baseline ~1,5 s).

**Checklist manual no servidor FastAPI:**

```text
grep 'crm_auth_completed' /var/log/hg-api-crm/*.log | grep internal_bff
# Esperado: duration_ms < 10
```

## Rollback

Se 401 global após deploy Django homolog:

1. `CRM_BFF_AUTH_MODE=legacy_basic` em `local_settings.py` + restart
2. Manter `ALLOW_LEGACY_BASIC_AUTH=true` na FastAPI

## Próximos passos (pós 24–48 h estáveis)

- FastAPI: `ALLOW_LEGACY_BASIC_AUTH=false`
- Django: remover armazenamento Fernet de senha na sessão (fora Fase 1)
- Provisionar `CRM_SERVICE_USERNAME` na base CRM homolog/prod para Celery alerts
