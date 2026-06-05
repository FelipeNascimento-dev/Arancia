from django import forms


class AtrelarMotoboyForm(forms.Form):
    base = forms.CharField(
        label="Selecione a Base",
        required=False,
        widget=forms.Select(
            choices=[("", "Selecione a base")],
            attrs={
                "onchange": "if (this.value) this.form.submit();",
            },
        ),
    )

    motoboy = forms.CharField(
        label="Selecione o Motoboy",
        required=False,
        widget=forms.Select(
            choices=[("", "Selecione o motoboy")],
        ),
    )

    serial = forms.CharField(
        label="Serial",
        required=False,
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
    )

    order_number = forms.CharField(
        label="Número do Pedido (Opcional)",
        required=False,
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
    )

    def __init__(self, *args, nome_form=None, **kwargs):
        self.nome_formulario = nome_form or "Atrelar Motoboy"
        super().__init__(*args, **kwargs)
