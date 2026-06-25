# Matriz de testes — responsividade Arancia

Checklist obrigatório em cada PR das fases de responsividade (Fase 0+).

## Viewports

| Viewport | Uso | Baseline |
|----------|-----|----------|
| 1920×1080 | Desktop grande | **Não pode mudar** em relação ao visual atual |
| 1366×768 | Notebook comum | Sem scroll horizontal na home e forms principais |
| 1280×1024 | Desktop estreito | Shell e conteúdo cabem sem overflow lateral |
| 1080×1920 | Monitor vertical (portrait) | Sidebar colapsada; conteúdo legível |
| 2560×1440 | Monitor grande | Sem regressão; uso opcional de largura extra |

## Checklist por módulo

Marcar ✅ após validação visual e funcional em cada viewport relevante.

| Módulo | Tela de teste | 1920 | 1366 | 1280 | portrait | 2560 |
|--------|---------------|------|------|------|----------|------|
| Shell | Home (`base.html` welcome-banner) | | | | | |
| Forms | 1 formulário 2 colunas | | | | | |
| Forms | 1 formulário 3 colunas | | | | | |
| Admin | Gestão usuários (tabela) | | | | | |
| Logística | Consulta pedidos | | | | | |
| Transportes | Detalhe OS | | | | | |
| Mural | Feed principal | | | | | |
| Iframe | Acompanhamento / Arancia Message | | | | | |
| Auth | Login | | | | | |

## Critérios de aceite (Fases 0–1)

- Tokens carregam (`layout-tokens.css` antes dos forms em `style.css`).
- Em 1920×1080 o layout permanece idêntico ao baseline.
- Em 1280×1024 e 1080×1920 a home não apresenta scroll horizontal causado pelo shell.
- Sidebar: ≥1440px toggle manual; 1024–1439px e &lt;1024px colapsada por default; dropdowns expandem sidebar ao clicar.
- Top bar: breadcrumb truncado; busca com largura fluida.

## Como testar

1. DevTools → modo responsivo → definir dimensões da tabela acima.
2. Navegar logado com usuário operacional (GAI configurado).
3. Verificar scroll horizontal (`document.documentElement.scrollWidth > innerWidth`).
4. Após editar CSS globais: `python manage.py bundle_global_css`.
