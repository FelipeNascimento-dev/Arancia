from django import forms
from django.contrib.auth.models import Group


class CreateGAIForm(forms.Form):
    group = forms.ModelChoiceField(
        label="Grupo",
        queryset=Group.objects.none(),
        required=True,
        empty_label="Selecione um grupo"
    )

    razao_social = forms.CharField(
        label="Razão Social", max_length=100, required=True)
    nome = forms.CharField(label="Nome", max_length=100, required=True)
    responsavel = forms.CharField(
        label="Responsável", max_length=100, required=True)
    cod_iata = forms.CharField(
        label="Código IATA", max_length=10, required=True)
    sales_channel = forms.CharField(
        label="Canal de Vendas", max_length=100, required=False)
    cod_center = forms.CharField(
        label="Código Centro", max_length=100, required=False)
    deposito = forms.CharField(
        label="Depósito SAP", max_length=100, required=False)
    cnpj = forms.CharField(
        label="CNPJ", max_length=30, required=False)
    inscricao_estadual = forms.CharField(
        label="Inscrição Estadual", max_length=20, required=False)
    CEP = forms.CharField(label="CEP", max_length=20, required=True)
    logradouro = forms.CharField(
        label="Logradouro", max_length=150, required=True)
    numero = forms.CharField(label="Número", max_length=20, required=True)
    complemento = forms.CharField(
        label="Complemento", max_length=100, required=False)
    bairro = forms.CharField(label="Bairro", max_length=100, required=True)
    cidade = forms.CharField(label="Cidade", max_length=100, required=True)
    UF = forms.CharField(label="UF", max_length=50, required=True)
    codigo_ibge = forms.CharField(
        label="Código IBGE", max_length=50, required=True)
    telefone1 = forms.CharField(
        label="Telefone 1", max_length=20, required=True)
    telefone2 = forms.CharField(
        label="Telefone 2", max_length=20, required=False)
    email = forms.EmailField(label="E-mail", required=True)

    def __init__(self, *args, **kwargs):
        grupos_disponiveis = kwargs.pop("grupos_disponiveis", None)

        super().__init__(*args, **kwargs)

        if grupos_disponiveis is not None:
            self.fields["group"].queryset = grupos_disponiveis
        else:
            self.fields["group"].queryset = Group.objects.all().order_by(
                "name")

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

            if field.required:
                field.label = f"{field.label} (*)"
                field.widget.attrs["required"] = "required"
