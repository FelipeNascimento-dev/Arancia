from django import forms

class SaidaCampoForm(forms.Form):
    nome_formulario = 'Saída para Campo'
    serial = forms.CharField(label='Serial', max_length=50)
    gtec = forms.CharField(label='GTec', max_length=50)
    centro = forms.ChoiceField(label='Centro de Custos', choices=[(1, ''), (2, 'WIN')])
    deposito = forms.ChoiceField(label='Deposito', choices=[(1, ''), (2, '989A')])