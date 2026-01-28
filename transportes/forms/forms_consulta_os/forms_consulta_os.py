from django import forms


class ConsultaOSForm(forms.Form):
    ordem_servico = forms.CharField(label="Insira o numero da OS ")

    def __init__(self, *args, nome_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Consulta de OS"
