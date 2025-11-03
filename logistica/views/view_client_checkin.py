from ..forms import ClientCheckInForm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
def client_checkin(request):
    client_data = request.session.get("selected_client", {})
    client_name = client_data.get("client_name", "Cliente não selecionado")

    titulo = f"Check-In {client_name}"

    # 🔹 Recupera o 'order' salvo anteriormente na sessão
    pedido_atrelado = request.session.get("order", "")

    if request.method == "POST":
        form = ClientCheckInForm(request.POST, nome_form=titulo)
    else:
        # 🔹 Define o valor inicial do campo 'pedido_atrelado'
        initial_data = {"pedido_atrelado": pedido_atrelado}
        form = ClientCheckInForm(nome_form=titulo, initial=initial_data)

    return render(
        request,
        "logistica/client_checkin.html",
        {
            "form": form,
            "site_title": titulo,
            "botao_texto": "Registrar Check-In",
        },
    )
