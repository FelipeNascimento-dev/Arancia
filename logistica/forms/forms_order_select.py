from django import forms


class OrderSelectForm(forms.Form):
    order = forms.CharField(
        label="Insira o número do pedido", max_length=100, required=True)
    actions = forms.ChoiceField(label="Ações", choices=[], required=True)

    def __init__(self, *args, nome_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Definir nome do formulário"
