from django import forms


class PreRecebimentoForm(forms.Form):
    id = forms.CharField(label='ID', max_length=20, required=True)

    qtde_vol = forms.IntegerField(
        label='Quantidade de volumes',
        min_value=1,
        initial=1,
        required=True
    )

    centro_origem = forms.ChoiceField(
        label='Centro de Origem',
        choices=[
            ('', ''),
            ('FLEX', 'FLEX'),
            ('WIN', 'WIN'),
        ],
        required=True
    )

    deposito_origem = forms.ChoiceField(
        label='Depósito de Origem',
        choices=[
            ('', ''),
            ('989A', '989A'),
            ('989B', '989B'),
            ('989C', '989C'),
            ('0001', '0001'),
        ],
        required=True
    )

    centro_destino = forms.ChoiceField(
        label='Centro de Destino',
        choices=[
            ('', ''),
            ('WIN', 'WIN'),
            ('FLEX', 'FLEX'),
        ],
        required=True
    )

    deposito_destino = forms.ChoiceField(
        label='Depósito de Destino',
        choices=[
            ('', ''),
            ('989A', '989A'),
            ('989B', '989B'),
            ('989C', '989C'),
            ('0001', '0001'),
        ],
        required=True
    )

    def __init__(self, *args, nome_form=None, **kwargs):
        self.nome_formulario = nome_form or "Definir nome do formulário"
        super().__init__(*args, **kwargs)