from django import forms

class ConsultaResultEC01Form(forms.Form):
    nome_formulario = 'Consulta Resultados EC01'
    id = forms.CharField(label='ID', max_length=20)
    tp_reg = forms.ChoiceField(label='Tipo de Registro', choices=[
        ('', ''), 
        ('1', 'Saída de Campo'), 
        ('2', 'Estorno Saída de Campo'), 
        ],
        required=True
    )
    serial = forms.CharField(label='Serial', max_length=50,required=False)