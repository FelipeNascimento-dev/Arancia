from ..forms import ReservaEquipamentosForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required

@login_required(login_url='logistica:login')
@permission_required('logistica.usuario_credenciado', raise_exception=True)
def reserva_equip(request):
    if request.method == 'POST':
        form = ReservaEquipamentosForm(request.POST)
        if form.is_valid():
            print('x'*100)
            centro = form.cleaned_data.get('centro')
            deposito = form.cleaned_data.get('deposito')
            request.session['centro'] = centro
            request.session['deposito'] = deposito
            print('-'*100)
            return redirect('logistica:consulta_result_ma', tp_reg='84')
        else:
            print('z'*100)
    else:
        form = ReservaEquipamentosForm()
    
    return render(request, 'logistica/reserva_equip.html', {
        'form': form,
        'etapa_ativa': 'reserva'
        })