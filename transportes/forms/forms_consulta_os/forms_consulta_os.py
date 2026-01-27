from django import forms


class ConsultaOSForm(forms.Form):
    TAG_CHOICES = [
        ("Pendente", "Pendente"),
        ("Finalizado", "Finalizado"),
        ("Em rota", "Em rota"),
    ]

    base = forms.ChoiceField(
        label="Selecione a Base",
        choices=[],
        widget=forms.Select(
            attrs={
                "onchange": "if (this.value) this.form.submit();"
            }
        )
    )

    tecnico = forms.ChoiceField(
        label="Selecione o Técnico",
        choices=[],
        required=False
    )

    tag = forms.ChoiceField(
        label="Status do Chamado",
        choices=TAG_CHOICES,
        required=False,
        initial="Pendente"
    )

    data_inicial = forms.DateField(
        label="Data Inicial",
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control date-with-icon"
            }
        )
    )

    data_final = forms.DateField(
        label="Data Final",
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control date-with-icon"
            }
        )
    )

    def __init__(self, *args, nome_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Consulta de OS"

    def clean_tecnico(self):
        if not self.fields["tecnico"].choices:
            return None
        return self.cleaned_data.get("tecnico")
