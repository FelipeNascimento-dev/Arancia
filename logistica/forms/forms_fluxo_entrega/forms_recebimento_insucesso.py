from django import forms


class RecebimentoInsucessoForm(forms.Form):
    pedido = forms.CharField(label='Pedido', max_length=100, required=True)

    def __init__(self, *args, nome_form=None, **kwargs):
        self.nome_formulario = nome_form or "Definir nome do formulário"
        super().__init__(*args, **kwargs)
