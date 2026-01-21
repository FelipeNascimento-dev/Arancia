from django import forms


class ConsultaOSForm(forms.Form):
    os_number = forms.CharField(label='Numero da OS', required=True)

    def __init__(self, *args, nome_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Consulta de OS"
