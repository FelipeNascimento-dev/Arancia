from django import forms


class UnsuccessfulInsertForm(forms.Form):
    pedido = forms.CharField(
        label='Pedido', max_length=50, widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    serial = forms.CharField(
        label='Serial', max_length=50, required=False, widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    material = forms.ChoiceField(label='Status do Material', choices=[
        ('', ''),
        ('EC21', 'GOOD'),
        ('EC22', 'BAD'),
    ])

    def __init__(self, *args, nome_form=None, **kwargs):
        self.nome_formulario = nome_form or "Definir nome do formulário"
        super().__init__(*args, **kwargs)
