from django import forms


class RomaneioConsultaForm(forms.Form):
    numero = forms.IntegerField(
        label="Número do Romaneio",
        required=True,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    def __init__(self, *args, nome_form=None, user_sales_channel: str | None = None, romaneio_num=None, **kwargs):
        self.nome_formulario = nome_form or "Definir nome do formulário"
        super().__init__(*args, **kwargs)
