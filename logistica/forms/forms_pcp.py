from django import forms

class PcpForm(forms.Form):
    nome_formulario = 'PCP'
    pedido = forms.CharField(label='Pedido', max_length=20)