from django import forms


class ConsultaOSForm(forms.Form):
    base = forms.ChoiceField(
        label="Selecione a Base",
        choices=[],
        widget=forms.Select(
            attrs={
                "onchange": "this.form.submit();"
            }
        )
    )

    tecnico = forms.ChoiceField(
        label="Selecione o Técnico",
        choices=[],
        required=False
    )

    def __init__(self, *args, nome_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Consulta de OS"

    def clean_tecnico(self):
        tecnico = self.cleaned_data.get("tecnico")

        if not self.fields["tecnico"].choices:
            return None

        return tecnico
