from django import forms

class CheckInBagTecForm(forms.Form):
    
    nome_tecnico = forms.CharField(label='Nome do Técnico', max_length=100)
    serial = forms.CharField(label='Serial', max_length=100)

    def __init__(self, *args, nome_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Definir nome do formulário"