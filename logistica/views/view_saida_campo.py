from ..forms import SaidaCampoForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required

@login_required(login_url='logistica:login')
@permission_required('logistica.pode_visualizar_telas', raise_exception=True)
def saida_campo(request):
    if request.method == 'POST':
        form = SaidaCampoForm(request.POST)
        if form.is_valid():
            print('x'*100)
            serial = form.cleaned_data.get('serial')
            gtec = form.cleaned_data.get('gtec')
            centro = form.cleaned_data.get('centro')
            deposito = form.cleaned_data.get('deposito')
            request.session['serial'] = serial
            request.session['gtec'] = gtec
            request.session['centro'] = centro
            request.session['deposito'] = deposito
            print('-'*100)
            return redirect('logistica:consulta_result_ec', tp_reg='84')
    else:
        form = SaidaCampoForm()
    
    return render(request, 'logistica/saida_campo.html', {
        'form': form,
        'etapa_ativa': 'saida_campo',
        })
