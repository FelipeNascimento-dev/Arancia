from django import forms


class ClientCreateForm(forms.Form):
    """Criação de cliente = novo GAI no grupo arancia_client (sem seleção de GAI)."""

    razao_social = forms.CharField(
        label="Razão Social",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    nome = forms.CharField(
        label="Nome",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    responsavel = forms.CharField(
        label="Responsável",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    cod_iata = forms.CharField(
        label="Código IATA",
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    sales_channel = forms.CharField(
        label="Canal de Vendas",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    cod_center = forms.CharField(
        label="Código Centro",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    deposito = forms.CharField(
        label="Depósito SAP",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    cnpj = forms.CharField(
        label="CNPJ",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    inscricao_estadual = forms.CharField(
        label="Inscrição Estadual",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    CEP = forms.CharField(
        label="CEP",
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    logradouro = forms.CharField(
        label="Logradouro",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    numero = forms.CharField(
        label="Número",
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    complemento = forms.CharField(
        label="Complemento",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    bairro = forms.CharField(
        label="Bairro",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    cidade = forms.CharField(
        label="Cidade",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    UF = forms.CharField(
        label="UF",
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    codigo_ibge = forms.CharField(
        label="Código IBGE",
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    telefone1 = forms.CharField(
        label="Telefone 1",
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    telefone2 = forms.CharField(
        label="Telefone 2",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        label="E-mail",
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    notes = forms.CharField(
        label="Observações CRM",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.required:
                field.label = f"{field.label} (*)"
                field.widget.attrs["required"] = "required"


class ClientForm(forms.Form):
    nome = forms.CharField(
        label="Nome",
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    razao_social = forms.CharField(
        label="Razão Social",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    cnpj = forms.CharField(
        label="CNPJ",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        label="E-mail",
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    telefone = forms.CharField(
        label="Telefone",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    sales_channel = forms.CharField(
        label="Canal",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    cod_iata = forms.CharField(
        label="Código IATA",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    notes = forms.CharField(
        label="Observações",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )

    def __init__(self, *args, lookups=None, nome_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Cliente"
        for field in self.fields.values():
            if "class" not in field.widget.attrs:
                field.widget.attrs["class"] = "form-control"


class ClientContactForm(forms.Form):
    nome = forms.CharField(label="Nome", max_length=255, widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(label="E-mail", required=False, widget=forms.EmailInput(attrs={"class": "form-control"}))
    telefone = forms.CharField(label="Telefone", required=False, max_length=30, widget=forms.TextInput(attrs={"class": "form-control"}))
    cargo = forms.CharField(label="Cargo", required=False, max_length=100, widget=forms.TextInput(attrs={"class": "form-control"}))


class ClientAddressForm(forms.Form):
    logradouro = forms.CharField(label="Logradouro", max_length=255, widget=forms.TextInput(attrs={"class": "form-control"}))
    numero = forms.CharField(label="Número", required=False, max_length=20, widget=forms.TextInput(attrs={"class": "form-control"}))
    complemento = forms.CharField(label="Complemento", required=False, max_length=100, widget=forms.TextInput(attrs={"class": "form-control"}))
    bairro = forms.CharField(label="Bairro", required=False, max_length=100, widget=forms.TextInput(attrs={"class": "form-control"}))
    cidade = forms.CharField(label="Cidade", required=False, max_length=100, widget=forms.TextInput(attrs={"class": "form-control"}))
    uf = forms.CharField(label="UF", required=False, max_length=2, widget=forms.TextInput(attrs={"class": "form-control"}))
    cep = forms.CharField(label="CEP", required=False, max_length=10, widget=forms.TextInput(attrs={"class": "form-control"}))
