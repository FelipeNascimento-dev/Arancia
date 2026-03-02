from django import forms


class ListaViagensForm(forms.Form):
    travel_number = forms.CharField(
        label='ID da Viagem', max_length=100, required=False)

    def __init__(self, *args, nome_form=None, **kwargs):
        self.nome_formulario = nome_form or "Definir nome do formulário"
        super().__init__(*args, **kwargs)
