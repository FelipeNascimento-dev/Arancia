from django import forms


class ClientCheckInForm(forms.Form):
    pedido = forms.CharField(label='Pedido', max_length=100,
                             widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    serial = forms.CharField(label='Serial', max_length=100,
                             widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    product = forms.CharField(label='Material', max_length=100,
                              widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    from_location = forms.ChoiceField(label='Origem', choices=[])
    to_location = forms.ChoiceField(label='Destino', choices=[])

    def __init__(self, *args, nome_form=None, **kwargs):
        self.nome_formulario = nome_form or "Definir nome do formulário"
        super().__init__(*args, **kwargs)
