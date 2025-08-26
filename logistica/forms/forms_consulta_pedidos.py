from django import forms


class ConsultaPedForm(forms.Form):
    nome_formulario = 'Consulta de Pedidos'
    sales_channel = forms.ChoiceField(
        label='Tipo de Registro', required=True, choices=())

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('sales_channel_choices', None)
        super().__init__(*args, **kwargs)
        if choices is not None:
            self.fields['sales_channel'].choices = choices
