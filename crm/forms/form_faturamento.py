from django import forms

from crm.views.views_contratos._helpers import (
    contract_option_label,
    filter_contracts_for_gai,
)


class BillingForm(forms.Form):
    client_gai_id = forms.IntegerField(
        label="Cliente (GAI)",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    contract_id = forms.CharField(
        label="Contrato",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    referencia = forms.CharField(
        label="Referência",
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    valor = forms.DecimalField(
        label="Valor",
        max_digits=14,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )
    data_vencimento = forms.DateField(
        label="Vencimento",
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
    status = forms.CharField(
        label="Status",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    observacoes = forms.CharField(
        label="Observações",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )

    def __init__(self, *args, lookups=None, nome_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Faturamento"
        lookups = lookups or {}
        client_choices = [("", "---------")]
        for client in lookups.get("clients", []):
            gai_id = client.get("gai_id") or client.get("id")
            label = client.get("nome") or client.get("name") or str(gai_id)
            if gai_id is not None:
                client_choices.append((gai_id, label))
        self.fields["client_gai_id"].widget = forms.Select(
            choices=client_choices,
            attrs={"class": "form-control"},
        )

        client_gai_id = None
        if self.initial.get("client_gai_id") not in (None, ""):
            client_gai_id = self.initial.get("client_gai_id")
        elif self.data.get("client_gai_id") not in (None, ""):
            client_gai_id = self.data.get("client_gai_id")

        contract_choices = [("", "---------")]
        for contract in filter_contracts_for_gai(lookups.get("contracts", []), client_gai_id):
            contract_id = contract.get("id")
            label = contract_option_label(contract)
            if contract_id is not None:
                contract_choices.append((str(contract_id), label))
        self.fields["contract_id"].widget = forms.Select(
            choices=contract_choices,
            attrs={"class": "form-control"},
        )


class BillingFilterForm(forms.Form):
    q = forms.CharField(
        label="Buscar",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Referência, cliente..."}),
    )
    status = forms.CharField(
        label="Status",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, nome_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Consulta de Faturamento"
