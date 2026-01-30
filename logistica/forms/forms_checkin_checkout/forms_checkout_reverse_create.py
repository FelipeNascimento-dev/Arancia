from django import forms


class CheckoutReverseCreateForm(forms.Form):
    serial = forms.CharField(
        label='Serial',
        required=False,
        widget=forms.TextInput(attrs={
            'autocomplete': 'off',
            'autofocus': True
        })
    )

    def __init__(self, *args, nome_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Definir nome do formulário"
