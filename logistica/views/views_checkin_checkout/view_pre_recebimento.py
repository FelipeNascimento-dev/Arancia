from django.shortcuts import render
from ...forms import PreRecebimentoForm


def pre_recebimento(request):
    titulo = "Pré-Recebimento"
    form = PreRecebimentoForm(request.POST or None, nome_form=titulo)
    return render(
        request,
        'logistica/templates_checkin_checkout/pre_recebimento.html', {
            'form': form,
            'site_title': titulo,
            'botao_texto': 'Confirmar Pré-Recebimento',
        }
    )
