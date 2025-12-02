from django import forms


class RomaneioConsultaForm(forms.Form):
    numero = forms.CharField(
        label="Número do Romaneio",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    # def clean_numero(self):
    #     numero = self.cleaned_data["numero"].strip().upper()
    #     if not numero:
    #         raise forms.ValidationError("Informe um número de romaneio.")
    #     return numero.zfill(10) if numero.isdigit() else numero

    def __init__(self, *args, nome_form=None, user_sales_channel: str | None = None, romaneio_num=None, **kwargs):
        self.nome_formulario = nome_form or "Definir nome do formulário"
        super().__init__(*args, **kwargs)
