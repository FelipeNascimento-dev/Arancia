from django import forms


class ConsultaOStranspForm(forms.Form):
    client = forms.ChoiceField(
        label="Cliente", choices=[], required=False)

    status = forms.ChoiceField(
        label="Status da OS", choices=[
            ("TODOS", "Todos os status"),
            ("TODOS_FINALIZADORES", "Todos Finalizadores"),
            ("TODOS_NAO_FINALIZADORES", "Todos Não Finalizadores"),
        ], required=False)

    numero_os = forms.CharField(
        label="Insira o número da OS")

    tipo_os = forms.ChoiceField(
        label="Consultar por",
        choices=[
            ("IN", "OS Interna"),
            ("EX", "OS Externa"),
        ],
        widget=forms.RadioSelect,
        initial="IN",
        required=True,
    )

    def __init__(self, *args, nome_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Consulta de OS"
