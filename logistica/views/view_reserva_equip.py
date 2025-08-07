from ..forms import ReservaEquipamentosForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required

@login_required(login_url='logistica:login')
@permission_required('logistica.usuario_de_TI', raise_exception=True)
@permission_required('logistica.usuario_credenciado', raise_exception=True)
def reserva_equip(request, tp_reg):
    titulo = 'Reserva de Equipamento' if tp_reg == '84' else 'Estorno Reserva de Equipamento'
    if request.method == 'POST':
        form = ReservaEquipamentosForm(request.POST, nome_form=titulo)
        if form.is_valid():
            centro = form.cleaned_data.get('centro')
            deposito = form.cleaned_data.get('deposito')
            request.session['centro'] = centro
            request.session['deposito'] = deposito
            return redirect('logistica:consulta_result_ma', tp_reg=tp_reg)
    else:
        form = ReservaEquipamentosForm(nome_form=titulo)
    
    return render(request, 'logistica/reserva_equip.html', {
        'form': form,
        'etapa_ativa': 'reserva'
        })