from django import forms


class RomaneioConsultaForm(forms.Form):
    numero = forms.IntegerField(
        label="Número do Romaneio",
        required=True,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
