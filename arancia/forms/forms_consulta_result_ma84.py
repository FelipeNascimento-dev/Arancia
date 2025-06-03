from django import forms

class ConsultaResultMA84Form(forms.Form):
    nome_formulario = 'Consulta Resultados MA84'
    id = forms.CharField(label='ID', max_length=20)
    tp_reg = forms.ChoiceField(label='Tipo de Registro', choices=[
        ('', ''), 
        ('84', 'Reserva de Equipamento'), 
        ('85', 'Estorno Reserva de Equipamento'), 
        ],
        required=True
    )
    serial = forms.CharField(label='Serial', max_length=50,required=False)