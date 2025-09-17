from django import forms


class ConsultaEntradaPedForm(forms.Form):
    form_title = 'Consultar Pedido Entrada'
    order = forms.CharField(label='Pedido', max_length=20, required=False)

    def __init__(self, *args, nome_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Consulta Entrada Pedido"
