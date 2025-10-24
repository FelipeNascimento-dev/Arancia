from ..forms import ConsultaForm
from django.shortcuts import render, redirect
from utils.request import RequestClient
from django.contrib.auth.decorators import login_required, permission_required


@login_required(login_url='logistica:login')
@permission_required('logistica.entrada_flfm', raise_exception=True)
def consulta_id_form(request):
    form = ConsultaForm()
    tabela_dados = None

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
            else:
                tabela_dados = response.get('items', []) or []
                request.session['tabela_dados'] = tabela_dados

    context = {
        'form': form,
        'exibir_formulario': True,
        'botao_texto': 'Consultar',
        'site_title': 'SAP - Consulta de ID',
        'tabela_dados': tabela_dados,
    }
    return render(request, 'logistica/consulta_id_form.html', context)


@login_required(login_url='logistica:login')
@permission_required('logistica.usuario_de_TI', raise_exception=True)
@permission_required('logistica.usuario_credenciado', raise_exception=True)
def consulta_id_table(request, id):
    tabela_dados = request.session.get('tabela_dados')
    exibir_formulario = False

    if not tabela_dados:
        return redirect('logistica:consulta_id_form')

    context = {
        'tabela_dados': tabela_dados,
        'exibir_formulario': exibir_formulario,
    }

    return render(request, 'logistica/consulta_id_table.html', context)
