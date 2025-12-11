from .func_visao_detalhada import func_visao_detalhada


def func_visao_resumida(request, form, sales_channels_map):

    itens, totais, produtos = func_visao_detalhada(
        request, form, sales_channels_map
    )

    resumo = []
    for produto, qtd in totais["por_produto"].items():
        resumo.append({
            "produto": produto,
            "quantidade": qtd
        })

    return resumo, totais, produtos
