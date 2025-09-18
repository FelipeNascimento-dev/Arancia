from django import forms


class ReverseCreateForm(forms.Form):
    serial = forms.CharField(label='Serial', max_length=50, required=False)
    sales_channel = forms.ChoiceField(
        label='Escolha o Canal de Vendas', required=False, choices=())

    def __init__(self, *args, nome_form=None, **kwargs):
        self.nome_formulario = nome_form or "Definir nome do formulário"
        choices = kwargs.pop('sales_channel_choices', None)
        super().__init__(*args, **kwargs)
        if choices is not None:
            self.fields['sales_channel'].choices = choices
