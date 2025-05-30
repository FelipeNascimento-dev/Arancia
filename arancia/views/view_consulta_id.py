from django.shortcuts import render
from ..forms import ConsultaForm

def consulta_id(request):
    form = ConsultaForm()
    tabela_dados = None
    exibir_formulario = True

    if request.method == 'POST':
        form = ConsultaForm(request.POST)
        if form.is_valid():
            exibir_formulario = False
            tabela_dados = [
                {
                    "matnr": "000000000000604825",
                    "gernr": "000000000005305833",
                    "serge": "6G612662",
                    # "zser_pr": None,
                    "ztipo": "G2",
                    "zver_ap": "CD16PS92040",
                    "zsta_eq": "RPA",
                    "nr_lcr_un": "00019AA2525766",
                    # "nr_lcr_mast": None,
                    # "nr_cd_br_cx": None,
                    "stat_div_rec": "00",
                    "id_lote": "030000431485",
                }
            ]

    context = {
        'form': form,
        'tabela_dados': tabela_dados,
        'exibir_formulario': exibir_formulario
    }
    return render(request, 'arancia/consulta_id.html', context)
