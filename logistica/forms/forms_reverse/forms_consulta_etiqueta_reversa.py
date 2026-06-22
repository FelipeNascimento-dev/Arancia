from django import forms


class ConsultaEtiquetaReversaForm(forms.Form):
    numero_rom = forms.CharField(
        label="Número do Romaneio",
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
    )
    qtde_vol = forms.IntegerField(
        label="Quantidade de Volumes",
        min_value=1,
        max_value=999,
        required=True,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 1}),
    )

    def __init__(self, *args, nome_form=None, **kwargs):
        self.nome_formulario = nome_form or "Etiquetas de Reversa"
        super().__init__(*args, **kwargs)
        self.fields["qtde_vol"].initial = 1

    def clean_numero_rom(self):
        numero = (self.cleaned_data.get("numero_rom") or "").strip().upper()
        if not numero:
            raise forms.ValidationError("Informe o número do romaneio.")
        return numero
