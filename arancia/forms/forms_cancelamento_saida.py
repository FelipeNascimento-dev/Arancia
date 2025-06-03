from django import forms

class CancelamentoSaidaCampoForm(forms.Form):
    nome_formulario = 'Cancelamento Saída para Campo'
    serial = forms.CharField(label='Serial', max_length=50)
    gtec = forms.CharField(label='GTec', max_length=50)