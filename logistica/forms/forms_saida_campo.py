from django import forms

class SaidaCampoForm(forms.Form):
    serial = forms.CharField(label='Serial', max_length=50)
    gtec = forms.CharField(label='GTec', max_length=50)
    centro = forms.ChoiceField(label='Centro de Custos', choices=[(1, ''), ('WIN', 'WIN')])
    deposito = forms.ChoiceField(label='Deposito', choices=[(1, ''), ('989A', '989A')])
    origem_os = forms.ChoiceField(label='Origem Os', choices=[(1, ''), ('intelipost', 'Intelipost'), ('gtec', 'Gtec')])

    def __init__(self, *args, nome_form=None, **kwargs):
        self.nome_formulario = nome_form or "Definir nome do formulário"
        super().__init__(*args, **kwargs)