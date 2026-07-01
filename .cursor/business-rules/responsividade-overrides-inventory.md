# Inventário de overrides — larguras e margens fixas

Base para limpeza de `<style>` inline e overrides em templates.
Atualizar com o script abaixo antes de cada sprint.

## Padrões rastreados

| Padrão | Substituição |
|--------|--------------|
| `margin-left: 65px` | `var(--content-offset)` ou `.app-page` |
| `margin-left: 90px` | `var(--content-offset-wide)` ou `.app-section-header` |
| `width: 1300px` / `max-width: 1300px` | `var(--content-max-width-form)` |
| `max-width: 1350px` / `1550px` | `var(--content-max-width-fluid)` |
| `margin-top: 95px` | Remover — `form-card-2col` / `setcontainer` já usam `--topbar-height` |
| `min-width: 1100px` em shell | Scroll interno em `.table-responsive` |

## CSS globais — status

| Arquivo | Status |
|---------|--------|
| `layout-tokens.css` | ✅ tokens fluidos |
| `content-shell.css` | ✅ shell `.app-page` |
| `form_1col.css`, `form_2col.css`, `form_3col.css` | ✅ tokens |
| `form_card_2col.css` | ✅ tokens |
| `user_ger.css`, `skill_ger.css` | ✅ tokens |
| `consulta_id.css`, `campo.css` | ✅ tokens |
| `detalhe_os.css`, `detalhe_viagem.css` | ✅ fluido |
| `lista_viagens.css`, `consulta_os_transp.css` | ✅ fluido |
| `style.css` (kanban, CRM comercial) | ✅ tokens |

## Templates migrados

### Logística

- `consulta_produtos.html` — section-header com tokens
- `detalhe_pedidos.html` — margin-top token

### Transportes

- `tools/order_route.html`, `move_route.html`, `see_user.html`, `scripting.html` — removido `margin-top: 95px`

### CRM / Projetos

- Tasks: `lista_tasks`, `minhas_tasks`, `calendario_tasks` — `app-page app-page--fluid`
- Dashboard — margens KPI com tokens
- Boards, projetos, contratos, clientes, faturamento — `app-page-actions`, `app-page-breadcrumb-bar`
- Configurações — `_config_page_styles.html` com tokens

### Backoffice

- `importacao.html`, `cadastro_equipamento.html` — tokens / removido margin-top fixo

### Partials

- `_nav_chevron_simpl.html` — largura fluida

## Pendências conhecidas (baixa prioridade)

- Larguras de coluna em tabelas (`width: 90px`, `265px`) — não afetam shell
- Modais com `width: 600px` — intencional
- `crm/templates_comercial/acesso_comercial.html` — coluna de ações

## Script de atualização

```powershell
cd C:\Projetos\Arancia
rg -l "margin-left:\s*65px|margin-left:\s*90px|width:\s*1300px|min-width:\s*1100px|min-width:\s*1300px|margin-top:\s*95px" --glob "*.{html,css}" -g "!*.bundle.css" | Sort-Object
```

## Validação contínua

Ver `responsividade-test-matrix.md` e `base_static/global/js/audit-layout.js`.
