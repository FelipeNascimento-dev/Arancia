from django import forms

_PLACEHOLDER = [(" ", " ")]


class RecebimentoRemessaForm(forms.Form):
    order_number = forms.CharField(
        label='Pedido', max_length=25, required=False, widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    volume_number = forms.IntegerField(
        label='Volume', min_value=1, required=True)
    from_location = forms.ChoiceField(
        label='Origem', choices=[], required=True)
    to_location = forms.ChoiceField(
        label='Destino', choices=[], required=True)
    box_codes = forms.CharField(
        label='Códigos de Barra', max_length=4000, required=False, widget=forms.TextInput(attrs={'autocomplete': 'off'})
    )

    def __init__(
        self, *args, nome_form=None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Pré-Recebimento"
        self.fields['volume_number'].initial = 1
