from django import forms


class OrderConsultForm(forms.Form):
    form_title = 'Consultar Pedido'
    order = forms.CharField(label='Pedido', max_length=20, required=False)

    def __init__(self, *args, nome_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Consultar Pedido"
