from django import forms


class ConsultaEntradaPedForm(forms.Form):
    form_title = 'Consultar Pedido Entrada'
    order = forms.CharField(label='Pedido', max_length=20, required=False)
