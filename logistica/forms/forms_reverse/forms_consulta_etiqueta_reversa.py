from django import forms


class ConsultaEtiquetaReversaForm(forms.Form):
    numero_rom = forms.CharField(
        label="Número do Romaneio",
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
    )

    def __init__(self, *args, nome_form=None, **kwargs):
        self.nome_formulario = nome_form or "Etiquetas de Reversa"
        super().__init__(*args, **kwargs)

    def clean_numero_rom(self):
        numero = (self.cleaned_data.get("numero_rom") or "").strip().upper()
        if not numero:
            raise forms.ValidationError("Informe o número do romaneio.")
        return numero
