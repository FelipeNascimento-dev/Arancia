from django import forms
from django.core.exceptions import ValidationError


class ClientSelectForm(forms.Form):
    client = forms.ChoiceField(
        label="Selecione o Cliente",
        choices=[]
    )

    order = forms.CharField(
        label="Número do Pedido (opcional)",
        required=False, widget=forms.TextInput(attrs={'autocomplete': 'off'})
    )

    def __init__(self, *args, nome_form=None, client_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Definir nome do formulário"
        if client_choices:
            self.fields['client'].choices = client_choices or [("", "")]

    def clean(self):
        cleaned_data = super().clean()
        client = cleaned_data.get('client')
        order = cleaned_data.get('order')

        if client and client.lower() == "cielo" and not order:
            self.add_error('order', ValidationError(
                "O número do pedido é obrigatório para o cliente Cielo."))
        return cleaned_data
