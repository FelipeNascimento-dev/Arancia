from django import forms


class ClientSelectForm(forms.Form):
    client = forms.ChoiceField(
        label="Selecione o Cliente",
        choices={
            "": "",
            "1": "Cielo",
            "2": "Claro",
            "3": "Escuro"
        }
    )

    def __init__(self, *args, nome_form=None, **kwargs):
        self.nome_formulario = nome_form or "Definir nome do formulário"
        super().__init__(*args, **kwargs)
