from django import forms

class trackingIPForm(forms.Form):
    pedido = forms.CharField(label='Pedido', max_length=20)
    serial = forms.CharField(label='Serial', max_length=50,required=False)

    def __init__(self, *args, nome_form=None, show_serial=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Definir nome do formulário"

        if not show_serial:
            self.fields.pop('serial', None)