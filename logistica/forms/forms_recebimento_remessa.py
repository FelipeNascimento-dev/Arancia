from django import forms

_PLACEHOLDER = [(" ", " ")]


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
        depositos_by_centro=None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Pré-Recebimento"
        self.fields['volume_number'].initial = 1

        dc = list(distribution_center_choices or [])
        self.fields["distribution_center"].choices = _PLACEHOLDER + dc

        self.fields["ware_house_code"].choices = list(_PLACEHOLDER)

        self._depositos_by_centro = depositos_by_centro or {}
