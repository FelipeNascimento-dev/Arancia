from django import forms


class ConsultaQuoteForm(forms.Form):

    numero_romaneio = forms.CharField(
        label="Número do Romaneio",
        required=False,
    )

    def __init__(self, *args, nome_form=None, **kwargs):
        self.nome_formulario = nome_form or "Definir nome do formulário"
        super().__init__(*args, **kwargs)
