from django import forms


class CadastrarSerialForm(forms.Form):
    
    serial_number = forms.CharField(label="Serial", max_length=150)
    product_model = forms.CharField(label="Modelo", max_length=150)
    order_origin = forms.CharField(label="Origem", max_length=150)
    product_type = forms.CharField(label="Tipo de Produto", max_length=150)
    service_type = forms.CharField(label="Tipo de Serviço", max_length=150)
    extra_information = forms.CharField(
        label="Informações Extras (JSON)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 4})
    )

    def clean_extra_information(self):
        value = self.cleaned_data.get("extra_information")
        if not value:
            return {}
        import json
        try:
            return json.loads(value)
        except Exception:
            raise forms.ValidationError("O campo deve ser um JSON válido.")