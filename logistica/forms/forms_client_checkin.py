from django import forms


class ClientCheckInForm(forms.Form):
    pedido = forms.CharField(label='Romaneio', max_length=100,
                             widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    serial = forms.CharField(label='Serial', max_length=100,
                             widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    product = forms.CharField(label='Material', max_length=100,
                              widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    volume = forms.IntegerField(
        label='Volume (opcional)', min_value=1, required=False)
    kit = forms.CharField(label='Kit (opcional)',
                          max_length=100, required=False,)
    pedido_atrelado = forms.CharField(label='Pedido Atrelado (opcional)',
                                      max_length=100, required=False,
                                      widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    from_location = forms.ChoiceField(
        label='Origem', required=False, choices=[])
    to_location = forms.ChoiceField(label='Destino', choices=[])

    def __init__(self, *args, nome_form=None, **kwargs):
        self.nome_formulario = nome_form or "Definir nome do formulário"
        super().__init__(*args, **kwargs)
