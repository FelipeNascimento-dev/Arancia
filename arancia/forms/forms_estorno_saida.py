from django import forms

class EstornoSaidaCampoForm(forms.Form):
    nome_formulario = 'Saída para Campo (Estorno)'
    serial = forms.CharField(label='Serial', max_length=50)
    gtec = forms.CharField(label='GTec', max_length=50)
    centro = forms.CharField(label='Centro', max_length=50)
    deposito = forms.CharField(label='Depósito', max_length=50)