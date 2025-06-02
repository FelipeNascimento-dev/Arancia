from django import forms

class SaidaCampoForm(forms.Form):
    nome_formulario = 'Saída para Campo'
    id = forms.CharField(label='ID', max_length=20)
    volume = forms.IntegerField(label='Volume', min_value=1, initial=1)