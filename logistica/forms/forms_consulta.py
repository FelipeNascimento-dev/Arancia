from django import forms

class ConsultaForm(forms.Form):
    nome_formulario = 'Consulta de ID'
    id = forms.CharField(label='Insira o ID:', max_length=20)
