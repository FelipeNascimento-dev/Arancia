from django import forms


_PLACEHOLDER = [
    ("", ""),
    ("opcao2", "opcao2")
]


class RecebimentoRemessaForm(forms.Form):
    order_number = forms.CharField(
        label='Pedido', max_length=25, required=False)
    volume_number = forms.IntegerField(
        label='Volume', min_value=1, required=True)
    distribution_center = forms.ChoiceField(
        label='Centro de Distribuição', choices=_PLACEHOLDER, required=True)
    ware_house_code = forms.ChoiceField(
        label='Depósito', choices=_PLACEHOLDER, required=True)
