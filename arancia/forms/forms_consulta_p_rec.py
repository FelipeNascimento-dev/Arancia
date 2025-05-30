from django import forms

class ConsultaPreRecebimentoForm(forms.Form):
    nome_formulario = 'Consulta Pré-Recebimento'
    id = forms.CharField(label='ID', max_length=20)
    tp_reg = forms.CharField(label='Tipo de Registro', max_length=50)