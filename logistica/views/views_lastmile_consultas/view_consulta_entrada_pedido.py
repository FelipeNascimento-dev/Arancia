from ...forms import OrderConsultForm
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages


@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
@permission_required('logistica.acesso_arancia', raise_exception=True)
def order_consult(request):
    form = OrderConsultForm(request.POST or None)
    titulo = 'Consultar Pedido Entrada'

    if request.method == "POST" and form.is_valid():
        order = (form.cleaned_data.get("order") or "").strip()
        if not order:
            messages.warning(request, "Informe o número do pedido.")
        else:
            return redirect('logistica:detalhe_pedido', order=order)

    return render(
        request,
        "logistica/templates_lastmile_consultas/consultar_pedido.html",
        {
            "form": form,
            "botao_texto": "Consultar",
            "site_title": "Consultar Pedido Entrada",
            "nome_form": titulo,
        },
    )
