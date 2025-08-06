from ..forms.forms_estorno import EstornoForm
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, permission_required

@login_required(login_url='logistica:login')
@permission_required('logistica.usuario_de_TI', raise_exception=True)
@permission_required('logistica.usuario_credenciado', raise_exception=True)
def buscar_dados_estorno(form):
    return [
        {
            "nr_arq": "00000019",
            "mensagem": "Erro no processamento",
            "status": "3",
            "data": "2025-05-27",
            "hora": "17:13:32",
        }
    ]

@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('logistica.usuario_de_TI', raise_exception=True)
@permission_required('logistica.usuario_credenciado', raise_exception=True)
def estorno_result(request):
    id_pre_recebido = request.session.pop('id_pre_recebido', None)
    serial_inserido = request.session.pop('serial_recebido', None)
    origem = request.session.pop('origem', None)
    mostrar_tabela = request.session.pop('mostrar_tabela', False)

    if request.method == 'POST':
        form = EstornoForm(request.POST)

        if form.data.get('tp_reg') == '16' and form.data.get('serial') == '':
            form.add_error('serial', 'O serial não pode ser vazio para essa mensagem.')
            return render(request, 'logistica/estorno.html', {'form': form})

        if form.is_valid():
            request.session['dados_estorno'] = form.cleaned_data

            request.session['origem'] = 'estorno_result'
            request.session['mostrar_tabela'] = True

            

            return redirect('logistica:consulta_resultados', tp_reg='16')

    else:
        form = EstornoForm()

    return render(request, 'logistica/estorno.html', {
        'form': form
    })
