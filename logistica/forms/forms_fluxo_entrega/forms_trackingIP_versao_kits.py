from django import forms


class trackingIPForm(forms.Form):
    pedido = forms.CharField(
        label='Pedido',
        max_length=20,
        widget=forms.TextInput(attrs={'autocomplete': 'off'})
    )

    serial = forms.CharField(
        label='Serial',
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'autocomplete': 'off'})
    )

    def __init__(
        self,
        *args,
        nome_form=None,
        show_serial=True,
        modo_insercao=None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.nome_formulario = nome_form or "Definir nome do formulário"

        if modo_insercao == "kit":
            self.fields.pop("serial", None)

        if not show_serial:
            self.fields.pop("serial", None)
