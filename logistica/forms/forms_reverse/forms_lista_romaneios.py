from django import forms


class ListaRomaneiosForm(forms.Form):

    status_rom = forms.ChoiceField(
        label="Status do Romaneio",
        choices=[
            ('', 'Selecione o status do romaneio'),
            ('STARTED', 'Aberto'),
            ('READY', 'Pronto'),
            ('AWAITING_COLLECTION', 'Aguardando Coleta'),
            ('DISPATCHED', 'Despachado'),
            ('PRE_RECEIVED', 'Pré-Recebido'),
            ('IN_PROCESSING', 'Em Processamento'),
            ('CANCELLED', 'Cancelado'),
        ],
        required=False,)

    def __init__(self, *args, nome_form=None, **kwargs):
        self.nome_formulario = nome_form or "Definir nome do formulário"
        super().__init__(*args, **kwargs)
