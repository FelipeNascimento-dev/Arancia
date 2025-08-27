from django import forms


_PLACEHOLDER = [
    ("", "")
]


class RecebimentoRemessaForm(forms.Form):
    order_number = forms.CharField(
        label='Pedido', max_length=25, required=False)
    volume_number = forms.IntegerField(
        label='Volume', min_value=1, required=True)
    distribution_center = forms.ChoiceField(
        label='Centro', choices=_PLACEHOLDER, required=True)
    ware_house_code = forms.ChoiceField(
        label='Depósito', choices=_PLACEHOLDER, required=True)

    def __init__(
        self, *args, nome_form=None,
        distribution_center_choices=None,
        ware_house_code_choices=None,

        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Recebimento por Remessa"
        self.fields['volume_number'].initial = 1
        self.fields["distribution_center"].choices = _PLACEHOLDER + \
            list(distribution_center_choices or [])
        self.fields["ware_house_code"].choices = _PLACEHOLDER + \
            list(ware_house_code_choices or [])
