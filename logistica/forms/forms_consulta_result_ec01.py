from django import forms


class ConsultaResultEC01Form(forms.Form):
    nome_formulario = 'SAP - Consulta Resultados EC'
    gtec = forms.CharField(label='Pedido', max_length=20,
                           widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    serial = forms.CharField(label='Serial', max_length=50, required=False,
                             widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    tp_reg = forms.ChoiceField(label='Tipo de Registro', choices=[
        ('', ''),
        ('1', 'Saída de Campo'),
        ('2', 'Estorno Saída de Campo'),
    ],
        required=True
    )
