from django import forms


class CreateGAIForm(forms.Form):
    nome = forms.CharField(label="Nome", max_length=100, required=True)
    responsavel = forms.CharField(
        label="Responsável", max_length=100, required=False)
    cod_iata = forms.CharField(
        label="Código IATA", max_length=10, required=False)
    sales_channel = forms.CharField(
        label="Canal de Vendas", max_length=100, required=False)
    cod_center = forms.CharField(
        label="Código Centro", max_length=100, required=False)
    deposito = forms.CharField(
        label="Depósito SAP", max_length=100, required=False)
    CEP = forms.CharField(label="CEP", max_length=20, required=False)
    logradouro = forms.CharField(
        label="Logradouro", max_length=150, required=False)
    numero = forms.CharField(label="Número", max_length=20, required=False)
    complemento = forms.CharField(
        label="Complemento", max_length=100, required=False)
    bairro = forms.CharField(label="Bairro", max_length=100, required=False)
    cidade = forms.CharField(label="Cidade", max_length=100, required=False)
    estado = forms.CharField(label="Estado", max_length=50, required=False)
    telefone1 = forms.CharField(
        label="Telefone 1", max_length=20, required=False)
    telefone2 = forms.CharField(
        label="Telefone 2", max_length=20, required=False)
    email = forms.EmailField(label="E-mail", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})
