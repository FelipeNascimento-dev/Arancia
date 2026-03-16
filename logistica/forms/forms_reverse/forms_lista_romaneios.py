from django import forms


class ListaRomaneiosForm(forms.Form):

    status_rom = forms.ChoiceField(
        label="Status do Romaneio",
        choices=[
            ('', 'Selecione o status do romaneio'),
            ('ABERTO', 'Aberto'),
            ('PRONTO', 'Pronto'),
            ('EM PROCESSAMENTO', 'Em Processamento'),
            ('FECHADO', 'Fechado'),
            ('CANCELADO', 'Cancelado'),
        ],
        required=False,)

    def __init__(self, *args, nome_form=None, **kwargs):
        self.nome_formulario = nome_form or "Definir nome do formulário"
        super().__init__(*args, **kwargs)
