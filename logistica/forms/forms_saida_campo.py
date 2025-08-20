from django import forms

class SaidaCampoForm(forms.Form):
    gtec = forms.CharField(label='Pedido', max_length=50)
    serial = forms.CharField(label='Serial', max_length=50, required=False)
    origem_os = forms.ChoiceField(label='Origem Os', choices=[(1, ''), ('intelipost', 'Intelipost'), ('gtec', 'Gtec')])

    def __init__(self, *args, nome_form=None, **kwargs):
        self.nome_formulario = nome_form or "Definir nome do formulário"
        super().__init__(*args, **kwargs)