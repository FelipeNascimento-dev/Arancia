from django import forms

class ConsultaPreRecebimentoForm(forms.Form):
    nome_formulario = 'Consulta Resultados SAP'
    id = forms.CharField(label='ID', max_length=20)
    tp_reg = forms.ChoiceField(label='Tipo de Registro', choices=[
        ('', ''), 
        ('13', 'Pré-Recebimento'), 
        ('14', 'Estorno Pré-Recebimento'), 
        ('15', 'Recebimento'), 
        ('16', 'Estorno Recebimento'),
        ],
        required=True
    )
    serial = forms.CharField(label='Serial', max_length=50,required=False)

