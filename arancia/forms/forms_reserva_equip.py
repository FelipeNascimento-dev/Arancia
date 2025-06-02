from django import forms

class ReservaEquipamentosForm(forms.Form):
    nome_formulario = 'Reserva de Equipamentos'
    id = forms.CharField(label='ID', max_length=20)
    volume = forms.IntegerField(label='Volume', min_value=1, initial=1)