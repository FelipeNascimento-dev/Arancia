from django import forms


class CheckOutForm(forms.Form):
    numero_romaneio = forms.CharField(
        label='Digite o número do romaneio', required=False)

    def __init__(self, *args, nome_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Definir nome do formulário"
