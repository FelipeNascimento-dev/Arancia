from django import forms


class FallbackCheckForm(forms.Form):
    order = forms.CharField(label='Pedido', max_length=50, required=False)
    serial = forms.CharField(label='Serial', max_length=50, required=False)

    def __init__(self, *args, name_form=None, **kwargs):
        self.form_title = name_form or "Verificação de Fallback"
        self.nome_formulario = self.form_title
        super().__init__(*args, **kwargs)
