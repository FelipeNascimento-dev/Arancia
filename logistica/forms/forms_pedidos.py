from django import forms


class Order(forms.Form):
    form_title = 'Número do Pedido'
    nome_formulario = form_title

    GRUPO_1 = [
        "quantity", "ultima_tracking",
        "volume_number", "volume_name", "volume_state", "delivery_stage",
        "created_at", "updated_at", "shipment_order_type",
    ]
    GRUPO_2 = [
        "simcard_priority", "model", "matnr", "category",
        "terminal_logical_numbers",
    ]
    GRUPO_3 = [
        "logistic_provider_name", "origin_name", "origin_quarter",
        "origin_city", "origin_state_code", "end_customer_id", "maquinetas_key",
    ]

    order_number = forms.HiddenInput()
    simcard_priority = forms.CharField(
        label='Prioridade do Simcard', max_length=50, required=True, disabled=True)
    maquinetas_key = forms.CharField(
        label='Maquineta', max_length=50, required=True, disabled=True)
    model = forms.CharField(
        label='Modelo', max_length=50, required=True, disabled=True)
    matnr = forms.CharField(
        label='SKU (Código de Material)', max_length=50, required=True, disabled=True)
    category = forms.CharField(
        label='Categoria', max_length=50, required=True, disabled=True)
    quantity = forms.IntegerField(
        label='Quantidade', required=True, disabled=True)
    ultima_tracking = forms.CharField(
        label='Ultima Tracking', max_length=50, required=True, disabled=True)
    volume_number = forms.IntegerField(
        label='Número do Volume', required=True, disabled=True)
    volume_name = forms.CharField(
        label='Nome do Volume', max_length=50, required=True, disabled=True)
    volume_state = forms.CharField(
        label='Estado do Volume', max_length=50, required=True, disabled=True)
    logistic_provider_name = forms.CharField(
        label='Código Logistico', max_length=50, required=True, disabled=True)
    sales_channel = forms.CharField(
        label='Sales Channel', max_length=50, required=True, disabled=True)
    origin_name = forms.CharField(
        label='Origem', max_length=50, required=True, disabled=True)
    origin_quarter = forms.CharField(
        label='Bairro de Origem', max_length=50, required=True, disabled=True)
    origin_city = forms.CharField(
        label='Cidade de Origem', max_length=50, required=True, disabled=True)
    origin_state_code = forms.CharField(
        label='Código do Estado', max_length=50, required=True, disabled=True)
    end_customer_id = forms.CharField(
        label='ID', max_length=50, required=True, disabled=True)
    delivery_stage = forms.CharField(
        label='Projeto', max_length=50, required=True, disabled=True)
    terminal_logical_numbers = forms.CharField(
        label='Números Logicos', max_length=50, required=True, disabled=True)
    shipment_order_type = forms.CharField(
        label='Tipo do Pedido', max_length=50, required=True, disabled=True)
    created_at = forms.CharField(
        label='Criado em', max_length=50, required=True, disabled=True)
    updated_at = forms.CharField(
        label='Atualizado em', max_length=50, required=True, disabled=True)

    def __init__(self, *args, form_title='order_number', dados: dict = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_title = f"Número do Pedido: {dados['order_number']}"
        self.nome_formulario = self.form_title
        if dados:
            for field_name, value in dados.items():
                if field_name in self.fields:
                    self.fields[field_name].initial = value

        #     tipo = (dados.get("shipment_order_type") or "").lower()
        #     self.fields["operation"].initial = "ESTOQUE" if tipo == "return" else "INSUCESSO"
        #     self.botao_texto = "RECEBER ESTOQUE" if tipo == "return" else "RECEBER INSUCESSO"
        # else:
        #     self.botao_texto = "Enviar"
