# Inventário de margin-left / width fixos — plano responsividade Fase 0.
# Uso: .\scripts\inventory_layout_overrides.ps1

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

$pattern = 'margin-left:\s*65px|margin-left:\s*90px|width:\s*1300px|min-width:\s*1100px|min-width:\s*1300px'

Write-Host "=== Arquivos com overrides de layout (excl. *.bundle.css) ===" -ForegroundColor Cyan
rg -l $pattern --glob '*.{html,css}' -g '!*.bundle.css' | Sort-Object

Write-Host "`n=== Contagem de ocorrências por arquivo ===" -ForegroundColor Cyan
rg $pattern --glob '*.{html,css}' -g '!*.bundle.css' --count-matches | Sort-Object
