from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.shortcuts import render


@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
def visu_pedido(request, order: str):
    dados = None

    return render(request, "logistica/visu_pedidos.html", {
        "dados": dados,
        "botao_texto": "Consultar",
        "site_title": "Consultar Pedido Entrada",
        "nome_form": "Consultar Pedido Entrada",
    })
