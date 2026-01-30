from django.shortcuts import render
from ...forms import CheckoutReverseCreateForm


def checkout_reverse_create(request, rom):
    numero_romaneio = rom
    titulo = f'Romaneio {numero_romaneio}'
    form = CheckoutReverseCreateForm(request.POST, nome_form=titulo)

    return render(
        request,
        'logistica/templates_checkin_checkout/checkout_reverse_create.html', {
            'form': form,
            'botao_texto': 'Consultar'
        }
    )
