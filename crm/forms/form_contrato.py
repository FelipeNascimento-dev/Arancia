from django import forms

from crm.helpers.api_display import service_type_option_label


class ContractForm(forms.Form):
    client_gai_id = forms.IntegerField(
        label="Cliente (GAI)",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    titulo = forms.CharField(
        label="Título",
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    numero = forms.CharField(
        label="Número do contrato",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ex.: C-2024-001 ou referência interna",
            },
        ),
    )
    status = forms.CharField(
        label="Status",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    data_inicio = forms.DateField(
        label="Data início",
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
    data_fim = forms.DateField(
        label="Data fim",
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
    valor = forms.DecimalField(
        label="Valor",
        required=False,
        max_digits=14,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )
    service_type_id = forms.IntegerField(
        label="Tipo de serviço",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    descricao = forms.CharField(
        label="Descrição",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}),
    )

    def __init__(self, *args, lookups=None, nome_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Contrato"
        lookups = lookups or {}
        self._set_choices(
            "client_gai_id",
            lookups.get("clients", []),
            id_keys=("gai_id", "id"),
            label_keys=("nome", "name"),
        )
        self._set_service_type_choices(lookups.get("service_types", []))

    def _set_service_type_choices(self, items):
        choices = [("", "---------")]
        for item in items:
            if not isinstance(item, dict):
                continue
            item_id = item.get("id")
            if item_id is None:
                continue
            label = service_type_option_label(item)
            choices.append((item_id, label or str(item_id)))
        self.fields["service_type_id"].widget = forms.Select(
            choices=choices,
            attrs={"class": "form-control"},
        )

    def _set_choices(self, field_name, items, id_keys, label_keys):
        choices = [("", "---------")]
        for item in items:
            item_id = next((item.get(k) for k in id_keys if item.get(k) is not None), None)
            label = next((item.get(k) for k in label_keys if item.get(k)), None)
            if item_id is not None:
                choices.append((item_id, label or str(item_id)))
        self.fields[field_name].widget = forms.Select(
            choices=choices,
            attrs={"class": "form-control"},
        )


class ContractFileForm(forms.Form):
    arquivo = forms.FileField(label="Arquivo", widget=forms.FileInput(attrs={"class": "form-control"}))
