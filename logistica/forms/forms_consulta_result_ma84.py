from django import forms

class ConsultaResultMA84Form(forms.Form):
    nome_formulario = 'SAP - Consulta Resultados MA'
    pedido = forms.CharField(label='Pedido', max_length=50, required=False)
    tp_reg = forms.ChoiceField(label='Tipo de Registro', choices=[
        ('', ''), 
        ('84', 'Reserva de Equipamento'), 
        ('85', 'Estorno Reserva de Equipamento'), 
        ],
        required=True
    )
    serial = forms.CharField(label='Serial', max_length=50,required=False)