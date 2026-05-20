from django import forms


class ReceberEmEstoqueForm(forms.Form):
    numero_romaneio = forms.CharField(
        label='Número do romaneio',
        required=False
    )

    serial = forms.CharField(
        label='Bipar serial',
        required=False
    )

    def __init__(self, *args, nome_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Definir nome do formulário"
