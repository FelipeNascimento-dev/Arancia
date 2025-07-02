from ..forms import ConsultaForm
from django.shortcuts import render, redirect
from utils.request import RequestClient


def consulta_id_form(request):
    form = ConsultaForm()
    exibir_formulario = True
    if request.method == 'POST':
        form = ConsultaForm(request.POST)
        if form.is_valid():
            id = form.cleaned_data['id']
            request_api = RequestClient(
                headers={'Content-Type': 'application/json'},
                method='get',
                url=f'http://192.168.0.214/IntegrationXmlAPI/api/v2/clo/lm/{id}',
            )
            response = request_api.send_api_request()
            if not response:
                form.add_error(
                    None, 'Nenhum dado encontrado para o ID informado.')
                return render(request, 'arancia/consulta_id_form.html', {'form': form, 'exibir_formulario': exibir_formulario})

            tabela_dados = response.get('items', [])

            # Salva os dados na sessão para usar na view da tabela
            request.session['tabela_dados'] = tabela_dados

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
        return redirect('arancia:consulta_id_form')

    context = {
        'tabela_dados': tabela_dados,
        'exibir_formulario': exibir_formulario,
    }

    return render(request, 'arancia/consulta_id_table.html', context)
