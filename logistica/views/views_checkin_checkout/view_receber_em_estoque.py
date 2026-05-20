from django.shortcuts import render
from ...forms import ReceberEmEstoqueForm


def receber_em_estoque(request):
    titulo = "Receber em Estoque"

    form = ReceberEmEstoqueForm(
        request.POST or None,
        nome_form=titulo
    )

    itens_romaneio = []
    numero_romaneio = None

    if request.method == "POST":
        numero_romaneio = request.POST.get("numero_romaneio")

        if numero_romaneio:
            itens_romaneio = [
                {
                    "serial": "ABC123",
                    "descricao": "Terminal POS",
                    "ck": False,
                },
                {
                    "serial": "DEF456",
                    "descricao": "Terminal POS",
                    "ck": False,
                },
                {
                    "serial": "GHI789",
                    "descricao": "Chip SIM Card",
                    "ck": False,
                },
                {
                    "serial": "JKL321",
                    "descricao": "Fonte de energia",
                    "ck": False,
                },
                {
                    "serial": "MNO654",
                    "descricao": "Bobina",
                    "ck": False,
                },
            ]

    return render(
        request,
        'logistica/templates_checkin_checkout/receber_em_estoque.html',
        {
            'form': form,
            'site_title': titulo,
            'botao_texto': 'Consultar Romaneio',
            'itens_romaneio': itens_romaneio,
            'numero_romaneio': numero_romaneio,
        }
    )
