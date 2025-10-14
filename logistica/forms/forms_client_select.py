from django import forms


class ClientSelectForm(forms.Form):
    client = forms.ChoiceField(
        label="Selecione o Cliente",
        choices=[]
    )

    def __init__(self, *args, nome_form=None, client_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Definir nome do formulário"
        self.fields['client'].choices = client_choices or [("", "")]
