from django import forms

class RecebimentoForm(forms.Form):
    nome_formulario = 'Recebimento'
    serial = forms.CharField(label='Serial', max_length=50)
    id = forms.CharField(label='ID', max_length=20)
