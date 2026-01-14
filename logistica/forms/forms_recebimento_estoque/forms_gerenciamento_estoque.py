from django import forms


class GerenciamentoEstoqueForm(forms.Form):
    client = forms.ChoiceField(label="Selecione o Cliente", choices=[])
    cd_estoque = forms.MultipleChoiceField(
        label="Selecione as localidades",
        choices=[],
        widget=forms.SelectMultiple(attrs={"size": 6})
    )

    def __init__(self, *args, nome_form=None, client_choices=None, cd_choices=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.nome_formulario = nome_form or "Definir nome do formulário"

        if client_choices:
            self.fields['client'].choices = client_choices

        if cd_choices:
            self.fields['cd_estoque'].choices = cd_choices
