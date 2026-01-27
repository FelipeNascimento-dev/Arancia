from django import forms


class ListaTecnicoForm(forms.Form):
    base = forms.ChoiceField(
        label="Selecione a Base",
        choices=[],
    )

    def __init__(self, *args, nome_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Consulta de OS"
