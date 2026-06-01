# Cursor Rules Django - C-Trends / Arancia

Repositório/pacote de rules para uso do Cursor em projetos Django da C-Trends, especialmente projetos legados ou semi-estruturados como o Arancia.

## Objetivo

Padronizar o uso do Cursor em projetos Django, ajudando o agente a:

- respeitar a arquitetura existente;
- evitar regras de negócio em locais errados;
- preservar compatibilidade com código legado;
- aplicar corretamente permissões, GAI e UserDesignation;
- documentar regras de negócio descobertas;
- criar novas rules específicas quando necessário.

## Estrutura

```text
.cursor/
├── rules/
│   ├── README.md
│   ├── 000-project-context-always.mdc
│   ├── 010-django-architecture-always.mdc
│   ├── 020-django-views-auto.mdc
│   ├── 030-django-models-auto.mdc
│   ├── 040-django-forms-auto.mdc
│   ├── 050-templates-static-auto.mdc
│   ├── 060-urls-routing-auto.mdc
│   ├── 070-services-utils-auto.mdc
│   ├── 080-auth-gai-userdesignation-always.mdc
│   ├── 090-tests-auto.mdc
│   ├── 100-security-settings-always.mdc
│   ├── 110-docs-readme-auto.mdc
│   ├── 115-reusable-core-abstractions-auto.mdc
│   └── 120-business-rules-discovery-manual.mdc
└── business-rules/
    ├── README.md
    ├── discovered-rules.md
    ├── pending-questions.md
    └── decisions.md

docs/
└── cursor/
    ├── README.md
    └── PROMPTS.md

AGENTS.md
.cursorrules
```

## Regra crítica do projeto

No Django existem `User` e `Group`, mas nos projetos Arancia/C-Trends também usamos:

- GAI (`GroupAdditionalInformation` / `GroupAditionalInformation`);
- `UserDesignation`.

Apenas atribuir o usuário a um grupo como `Arancia_Client` não identifica o cliente real dele. Quando a funcionalidade depender de cliente/PA/escopo operacional, o fluxo deve considerar:

```text
User -> UserDesignation -> GAI -> dados filtrados
```

## Documentação

- [Explicação de cada rule](./.cursor/rules/README.md)
- [Guia de aplicação em projetos existentes](./docs/cursor/README.md)
- [Prompts recomendados](./docs/cursor/PROMPTS.md)

## Uso recomendado

Copie para a raiz do projeto Django:

```text
.cursor/
AGENTS.md
.cursorrules
docs/cursor/
```

Depois abra o projeto no Cursor pela raiz.

## Observação

As rules foram pensadas para refatoração gradual. Elas não obrigam o projeto legado a mudar tudo de uma vez.
