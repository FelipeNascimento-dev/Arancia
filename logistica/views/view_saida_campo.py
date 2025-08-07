from ..forms import SaidaCampoForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required

@login_required(login_url='logistica:login')
@permission_required('logistica.usuario_de_TI', raise_exception=True)
@permission_required('logistica.usuario_credenciado', raise_exception=True)
def saida_campo(request, tp_reg):
    titulo = 'Saida para Campo' if tp_reg == '1' else 'Cancelamento de Saida para Campo'
    if request.method == 'POST':
        form = SaidaCampoForm(request.POST, nome_form=titulo)
        if form.is_valid():
            serial = form.cleaned_data.get('serial')
            gtec = form.cleaned_data.get('gtec')
            centro = form.cleaned_data.get('centro')
            deposito = form.cleaned_data.get('deposito')
            request.session['serial'] = serial
            request.session['gtec'] = gtec
            request.session['centro'] = centro
            request.session['deposito'] = deposito
            return redirect('logistica:consulta_result_ec', tp_reg=tp_reg)
    else:
        form = SaidaCampoForm(nome_form=titulo)
    
    return render(request, 'logistica/saida_campo.html', {
        'form': form,
        'etapa_ativa': 'saida_campo',
        })
