from ..forms import ConsultaForm
from django.shortcuts import render, redirect

def consulta_id_form(request):
    form = ConsultaForm()
    exibir_formulario = True
    if request.method == 'POST':
        form = ConsultaForm(request.POST)
        if form.is_valid():
            id = form.cleaned_data['id']
            # Salva os dados na sessão para usar na view da tabela
            request.session['tabela_dados'] = [
                {
                    "matnr": "000000000000604825",
                    "gernr": "000000000005305833",
                    "serge": "6G612662",
                    "ztipo": "G2",
                    "zver_ap": "CD16PS92040",
                    "zsta_eq": "RPA",
                    "nr_lcr_un": "00019AA2525766",
                    "stat_div_rec": "00",
                    "id_lote": "030000431485",
                }
            ]
            # Redireciona para a página da tabela após o POST (limpa o form)
            return redirect('arancia:consulta_id_table', id=id)
    context = {
        'form': form,
        'exibir_formulario': exibir_formulario,
    }
    return render(request, 'arancia/consulta_id_form.html', context)


def consulta_id_table(request, id):
    tabela_dados = request.session.get('tabela_dados')
    exibir_formulario = False

    if not tabela_dados:
        # Se não tiver dados, redireciona para o formulário
        return redirect('arancia:consulta_id_form')

    context = {
        'tabela_dados': tabela_dados,
        'exibir_formulario': exibir_formulario,
    }
    # Opcional: Limpa os dados da sessão após mostrar a tabela (se quiser)
    # del request.session['tabela_dados']

    return render(request, 'arancia/consulta_id_table.html', context)
