from django import forms

class ImportacaoForm(forms.Form):
    arquivo = forms.FileField(
        label='Selecione o arquivo Excel',
        widget=forms.FileInput(attrs={'accept': '.xls,.xlsx'})
    )
