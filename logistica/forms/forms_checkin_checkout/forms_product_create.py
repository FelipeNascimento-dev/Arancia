from django import forms


class ProductCreateForm(forms.Form):
    client = forms.ChoiceField(
        label="Selecione o Cliente",
        choices=[]
    )

    def __init__(self, *args, nome_form=None, client_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Definir nome do formulário"
        if client_choices:
            self.fields['client'].choices = client_choices or [("", "")]
