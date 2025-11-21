from django import forms

class ScriptingForm(forms.Form):
    arquivo = forms.FileField(
        label='Selecione o arquivo Excel',
        widget=forms.FileInput(attrs={'accept': '.xls,.xlsx'})
    )
