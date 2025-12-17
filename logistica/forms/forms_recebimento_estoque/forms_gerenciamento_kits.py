from django import forms


class GerenciamentoKitsForm(forms.Form):
    pedido = forms.CharField(
        label='Pedido',
        max_length=100,
        required=True
    )
    serial_number = forms.CharField(
        label='Serial',
        max_length=100,
        required=True
    )
    chip_number = forms.CharField(
        label='Chip',
        max_length=100,
        required=True
    )

    def __init__(self, *args, nome_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Gerenciamento de Kits"
