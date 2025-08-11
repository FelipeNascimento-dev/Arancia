from django import forms

class PcpForm(forms.Form):
    nome_formulario = 'PCP'
    id = forms.CharField(label='ID', max_length=20)
    serial = forms.CharField(label='Serial', max_length=50,required=False)