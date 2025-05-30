from ..forms.forms_consulta_result import ConsultaPreRecebimentoForm
from django.shortcuts import render

def consulta_result(request, tp_reg: str):
    if request.method == 'POST':
        # Usa o formulário adequado com base no tp_reg
        form = ConsultaPreRecebimentoForm(request.POST)
        if form.data.get('tp_reg') in ('15', '16') and form.data.get('serial') =='':
            form.add_error('serial', 'O serial não pode ser vazio para essa mensagem.')
            return render(request, 'arancia/consulta_result.html', {'form': form})
        
        if form.is_valid():
            return render(request, 'arancia/consulta_result.html', {'form': form})
    else:
        form = ConsultaPreRecebimentoForm()
        form.data = {'tp_reg': tp_reg}


    return render(request, 'arancia/consulta_result.html', {'form': form})


def btn_voltar(request):
    return render(request, 'arancia/consulta_result.html')