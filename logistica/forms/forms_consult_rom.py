import re
from django import forms


class RomaneioConsultaForm(forms.Form):
    numero = forms.CharField(
        label="Número do Romaneio",
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    def clean_numero(self):
        numero = self.cleaned_data["numero"]
        try:
            numero_int = int(numero)
        except ValueError:
            raise forms.ValidationError("Informe apenas números.")

        return str(numero_int).zfill(10)

    def __init__(self, *args, nome_form=None, user_sales_channel: str | None = None, romaneio_num=None, **kwargs):
        self.nome_formulario = nome_form or "Definir nome do formulário"
        super().__init__(*args, **kwargs)
