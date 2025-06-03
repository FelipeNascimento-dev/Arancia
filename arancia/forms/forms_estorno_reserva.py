from django import forms

class EstornoReservaForms(forms.Form):
    nome_formulario = 'Reserva de Equipamentos (Estorno)'
    serial = forms.CharField(label='Serial', max_length=50)
    centro = forms.ChoiceField(label='Centro de Custos', choices=[(1, ''), (2, 'WIN')])
    deposito = forms.ChoiceField(label='Deposito', choices=[(1, ''), (2, '989A')])