from django import forms

class EstornoReservaForms(forms.Form):
    nome_formulario = 'Reserva de Equipamentos (Estorno)'
    serial = forms.CharField(label='Serial', max_length=50)