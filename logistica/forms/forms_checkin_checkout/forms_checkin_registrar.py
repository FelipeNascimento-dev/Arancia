from django import forms


class ClientCheckInForm(forms.Form):
    pedido = forms.CharField(
        label='Romaneio',
        max_length=100,
        widget=forms.TextInput(attrs={'autocomplete': 'off'})
    )
    serial = forms.CharField(
        label='Serial',
        max_length=100,
        widget=forms.TextInput(attrs={'autocomplete': 'off'})
    )
    product = forms.ChoiceField(
        label="Produto",
        required=True,
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    volume = forms.IntegerField(
        label='Volume (opcional)',
        min_value=1,
        required=False,
        initial=1
    )
    kit = forms.IntegerField(
        label='Kit (opcional)',
        min_value=1,
        required=False,
        initial=1
    )
    pedido_atrelado = forms.CharField(
        label='Pedido Atrelado (opcional)',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'autocomplete': 'off'})
    )
    from_location = forms.ChoiceField(
        label='Origem',
        required=False,
        choices=[]
    )
    to_location = forms.ChoiceField(
        label='Destino',
        choices=[]
    )

    def __init__(self, *args, **kwargs):
        from_choices = kwargs.pop('from_choices', None)
        product_choices = kwargs.pop('product_choices', None)
        nome_form = kwargs.pop('nome_form', None)

        self.nome_formulario = nome_form or "Definir nome do formulário"
        super().__init__(*args, **kwargs)

        if from_choices:
            self.fields['from_location'].choices = [
                ("", "Selecione a origem")] + from_choices

        if product_choices:
            self.fields['product'].choices = product_choices
