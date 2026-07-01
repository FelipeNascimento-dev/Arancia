# Matriz de testes — responsividade Arancia

Checklist obrigatório em cada PR de responsividade. Validar por **faixa de largura contínua**, não por resoluções isoladas.

## Faixas de largura (redimensionar o navegador de ponta a ponta)

| Faixa | Largura aproximada | O que verificar |
|-------|-------------------|-----------------|
| Estreito | 320px – 767px | Sem scroll horizontal no `body`; formulários empilham |
| Médio | 768px – 1279px | Shell usa tokens; tabelas com scroll interno se necessário |
| Largo | 1280px – 1919px | Conteúdo preenche faixa útil (`app-page--fluid`) |
| Ultrawide | ≥ 1920px | Sem faixa morta à direita; cap só via `min(token, --content-max-width-fluid)` |

## Critérios de aceite (todas as faixas)

1. `horizontalOverflow === false` — `document.documentElement.scrollWidth <= window.innerWidth + 1`
2. Wrapper principal usa tokens (`--content-offset`, `--content-gutter`, `--content-max-width-*`), não `65px`/`1300px` soltos
3. Telas wide (`app-page--fluid`, mural feed): conteúdo preenche faixa útil com tolerância de padding (~60px)
4. Formulários (`app-page--form`): cap de leitura sem espaço morto quando viewport é menor que o cap
5. Tabelas largas: `overflow-x: auto` no container, não no `body`

## Script de auditoria

Carregar ou colar no console (arquivo: `base_static/global/js/audit-layout.js`):

```javascript
// Uma tela
auditLayout('.app-page--fluid');

// Várias telas comuns
auditLayoutAll();
```

Retorno esperado para telas fluidas em viewport largo:

```javascript
{
  fillsSpace: true,
  horizontalOverflow: false,
  ok: true
}
```

### Bookmarklet (opcional)

```javascript
javascript:(function(){var s=document.createElement('script');s.src='/static/global/js/audit-layout.js';s.onload=function(){console.table(auditLayoutAll().results);alert(JSON.stringify(auditLayoutAll(),null,2));};document.head.appendChild(s);})();
```

Ajuste o caminho `/static/` se o deploy usar prefixo diferente.

## Checklist por módulo

Marcar após validação visual + `auditLayoutAll()` em estreito, médio, largo e ultrawide.

| Módulo | Tela de teste | Estreito | Médio | Largo | Ultrawide |
|--------|---------------|----------|-------|-------|-----------|
| Shell | Home (`welcome-banner`) | | | | |
| Forms | Formulário 2 colunas | | | | |
| Admin | Gestão usuários | | | | |
| Logística | Consulta produtos | | | | |
| Transportes | Lista viagens / detalhe OS | | | | |
| Mural | Feed principal | | | | |
| CRM | Lista tasks / dashboard | | | | |
| Backoffice | Importação | | | | |
| Iframe | Acompanhamento | | | | |

## Após editar CSS globais

```powershell
python manage.py bundle_global_css
```

## Tokens e shell

- `base_static/global/css/layout-tokens.css` — `--content-max-width-fluid`, `--content-max-width-form`
- `base_static/global/css/content-shell.css` — `.app-page`, `.app-page--fluid`, `.app-page--form`
