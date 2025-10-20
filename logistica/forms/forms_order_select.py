from django import forms


class OrderSelectForm(forms.Form):
    order = forms.CharField(
        label="Insira o número do pedido", max_length=100, required=True)
    actions = forms.ChoiceField(label="Ações", choices=[
        ("", ""),
        ("checkin", "Check-in do Pedido"),
        ("desinstalar", "Desinstalar Pedido"),
        ("retirada", "Retirar Pedido"),
        ("entrega", "Entregar Pedido"),
    ], required=True)

    def __init__(self, *args, nome_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Definir nome do formulário"

    def clean(self):
        cleaned_data = super().clean()
        order = cleaned_data.get("order")

        cleaned_data["order"] = order.strip() if order else order

        return cleaned_data
