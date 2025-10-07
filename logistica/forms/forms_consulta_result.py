from django import forms


class ConsultaPreRecebimentoForm(forms.Form):
    nome_formulario = 'SAP - Consulta Resultados'
    id = forms.CharField(label='ID', max_length=20,
                         widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    tp_reg = forms.ChoiceField(label='Tipo de Registro', choices=[
        ('', ''),
        ('13', 'Pré-Recebimento'),
        ('14', 'Estorno Pré-Recebimento'),
        ('15', 'Recebimento'),
        ('16', 'Estorno Recebimento'),
    ],
        required=True
    )
    serial = forms.CharField(label='Serial', max_length=50, required=False,
                             widget=forms.TextInput(attrs={'autocomplete': 'off'}))
