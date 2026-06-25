# Inventário de overrides — larguras e margens fixas

Base para Fases 4–5 (limpeza de `<style>` inline e overrides em templates).
Gerado na Fase 0; atualizar com o script abaixo antes de cada sprint de limpeza.

## Padrões rastreados

| Padrão | Significado legado |
|--------|-------------------|
| `margin-left: 65px` | Offset do conteúdo com sidebar colapsada |
| `margin-left: 90px` | Offset ampliado (home, kanban, algumas consultas) |
| `width: 1300px` / `max-width: 1300px` | Largura fixa de formulários e listas |
| `min-width: 1100px` | Tabelas / painéis que forçam scroll horizontal |

## CSS globais (substituir por tokens nas fases 2–3)

| Arquivo | Padrões |
|---------|---------|
| `base_static/global/css/form_1col.css` | 1300px, margin-left 65px |
| `base_static/global/css/form_2col.css` | 1300px, margin-left 65px |
| `base_static/global/css/form_3col.css` | 1300px, margin-left 65px |
| `base_static/global/css/form_card_2col.css` | 1300px, margin-left 65px |
| `base_static/global/css/user_ger.css` | 1300px, margin-left 65px |
| `base_static/global/css/skill_ger.css` | 1300px, margin-left 65px |
| `base_static/global/css/consulta_id.css` | margin-left 65px |
| `base_static/global/css/campo.css` | min-width 1100px, margin-left 65px |
| `base_static/global/css/style.css` | welcome-banner, kanban margin-left 90px |
| `base_static/global/css/detalhe_os.css` | max-width 1300px |

## Templates com override inline ou `<style>` (prioridade Fase 5)

### Logística

- `logistica/templates/logistica/templatesV2/criar_reversaV2.html` — 1300px, margin-left 65px (múltiplos)
- `logistica/templates/logistica/templates_reverse/criar_reversa.html`
- `logistica/templates/logistica/templates_checkin_checkout/checkout_reverse_create.html`
- `logistica/templates/logistica/templates_checkin_checkout/consulta_produtos.html` — 65px e 90px
- `logistica/templates/logistica/templates_checkin_checkout/consulta_clientes.html`
- `logistica/templates/logistica/templatesV2/lista_romaneios.html`
- `logistica/templates/logistica/templatesV2/consulta_romaneioV2.html`
- `logistica/templates/logistica/templatesV2/consulta_cotacao.html`
- `logistica/templates/logistica/templates_reverse/consulta_romaneio.html`
- `logistica/templates/logistica/templates_checkin_checkout/checkin_bag_tec.html`
- `logistica/templates/logistica/templates_recebimento_estoque/gerenciamento_kits.html`
- `logistica/templates/logistica/templates_lastmile_consultas/consultar_entrada_pedido.html`
- `logistica/templates/logistica/acompanhamento_iframe.html`

### Transportes

- `transportes/templates/transportes/controle_chamados/detalhe_os.html` — min-width 1300px
- `transportes/templates/transportes/controle_chamados/lista_tecnicos.html`

### Mural

- `mural/templates/mural/template_mural.html`
- `mural/templates/mural/gerenciamento_mural.html` — min-width 1100px

### Backoffice

- `backoffice/templates/backoffice/cadastro_equipamento.html` — 65px e 90px

### CRM / Projetos

- `crm/templates/crm/templates_dashboard/dashboard.html`
- `crm/templates/crm/templates_tasks/lista_tasks.html`
- `crm/templates/crm/templates_tasks/minhas_tasks.html`
- `crm/templates/crm/templates_tasks/calendario_tasks.html`
- `crm/templates/crm/templates_contratos/form_contrato.html`
- `crm/templates/crm/templates_projetos/membros_projeto.html`
- `crm/templates/crm/templates_projetos/tasks_projeto.html`
- `crm/templates/crm/templates_boards/colunas_board.html`
- `projetos/templates/projetos/templates_boards/acesso_board.html`
- `projetos/templates/projetos/templates_boards/colunas_board.html`
- `projetos/templates/projetos/templates_projetos/membros_projeto.html`
- `projetos/templates/projetos/templates_projetos/tasks_projeto.html`

### Partials globais

- `base_templates/global/partials/_nav_chevron_simpl.html` — margin-left 65px

## Script de atualização

```powershell
cd C:\Projetos\Arancia
rg -l "margin-left:\s*65px|margin-left:\s*90px|width:\s*1300px|min-width:\s*1100px|min-width:\s*1300px" --glob "*.{html,css}" -g "!*.bundle.css" | Sort-Object
```

Contagem rápida (excluindo bundles):

```powershell
rg "margin-left:\s*65px|margin-left:\s*90px|width:\s*1300px|min-width:\s*1100px|min-width:\s*1300px" --glob "*.{html,css}" -g "!*.bundle.css" --count-matches
```
