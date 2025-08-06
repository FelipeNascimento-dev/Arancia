from django import forms

class RecebimentoForm(forms.Form):

    serial = forms.CharField(label='Serial', max_length=50)
    id = forms.CharField(label='ID', max_length=20)

    def __init__(self, *args, nome_form=None, **kwargs):
        self.nome_formulario = nome_form or "Definir nome do formulário"
        super().__init__(*args, **kwargs)