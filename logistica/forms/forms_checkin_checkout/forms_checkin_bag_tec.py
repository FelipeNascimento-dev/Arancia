from django import forms


class CheckInBagTecForm(forms.Form):
    TIPO_FILTRO_CHOICES = [
        ("ambos", "Ambos"),
        ("TO_BE_DELIVERED", "Suprimento de entrega"),
        ("COLLECTED", "Coletados"),
    ]

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

    tecnico = forms.CharField(
        label="Selecione o Técnico",
        required=False,
        widget=forms.Select(
            choices=[("", "Selecione o técnico")],
        ),
    )

    tipo_filtro = forms.ChoiceField(
        label="Tipo de item",
        choices=TIPO_FILTRO_CHOICES,
        initial="ambos",
        required=False,
    )

    def __init__(self, *args, nome_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Check-In de Bag Tec"
