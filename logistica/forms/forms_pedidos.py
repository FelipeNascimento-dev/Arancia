from django import forms


class Order(forms.Form):
    form_title = 'Número do Pedido'
    nome_formulario = form_title
    order_number = forms.HiddenInput()
    simcard_priority = forms.CharField(
        label='simcard_priority', max_length=50, required=True, disabled=True)
    maquinetas_key = forms.CharField(
        label='maquinetas_key', max_length=50, required=True, disabled=True)
    model = forms.CharField(
        label='model', max_length=50, required=True, disabled=True)
    matnr = forms.CharField(
        label='matnr', max_length=50, required=True, disabled=True)
    category = forms.CharField(
        label='category', max_length=50, required=True, disabled=True)
    quantity = forms.IntegerField(
        label='quantity', required=True, disabled=True)
    ultima_tracking = forms.CharField(
        label='ultima_tracking', max_length=50, required=True, disabled=True)
    volume_number = forms.IntegerField(
        label='volume_number', required=True, disabled=True)
    volume_name = forms.CharField(
        label='volume_name', max_length=50, required=True, disabled=True)
    volume_state = forms.CharField(
        label='volume_state', max_length=50, required=True, disabled=True)
    logistic_provider_name = forms.CharField(
        label='logistic_provider_name', max_length=50, required=True, disabled=True)
    sales_channel = forms.CharField(
        label='sales_channel', max_length=50, required=True, disabled=True)
    origin_name = forms.CharField(
        label='origin_name', max_length=50, required=True, disabled=True)
    origin_quarter = forms.CharField(
        label='origin_quarter', max_length=50, required=True, disabled=True)
    origin_city = forms.CharField(
        label='origin_city', max_length=50, required=True, disabled=True)
    origin_state_code = forms.CharField(
        label='origin_state_code', max_length=50, required=True, disabled=True)
    end_customer_id = forms.CharField(
        label='end_customer_id', max_length=50, required=True, disabled=True)
    delivery_stage = forms.CharField(
        label='delivery_stage', max_length=50, required=True, disabled=True)
    terminal_logical_numbers = forms.CharField(
        label='terminal_logical_numbers', max_length=50, required=True, disabled=True)
    shipment_order_type = forms.CharField(
        label='shipment_order_type', max_length=50, required=True, disabled=True)
    created_at = forms.CharField(
        label='created_at', max_length=50, required=True, disabled=True)
    updated_at = forms.CharField(
        label='updated_at', max_length=50, required=True, disabled=True)

    def __init__(self, *args, form_title='order_number', dados: dict = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_title = f"Número do Pedido: {dados['order_number']}"
        self.nome_formulario = self.form_title
        if dados:
            for field_name, value in dados.items():
                if field_name in self.fields:
                    self.fields[field_name].initial = value
