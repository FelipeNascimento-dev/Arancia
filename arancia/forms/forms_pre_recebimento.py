from django import forms

class PreRecebimentoForm(forms.Form):
    nome_formulario = 'Pré-Recebimento'
    id = forms.CharField(label='ID', max_length=20)
    volume = forms.IntegerField(label='Volume', min_value=1, initial=1)
    centro_origem = forms.ChoiceField(label='Centro de Origem', choices=[(1, ''), (2, 'FLEX'), (3, 'CTRD')])
    deposito_origem = forms.ChoiceField(label='Depósito de Origem', choices=[(1, ''), (2, '0001'), (3, '989A')])
    centro_destino = forms.ChoiceField(label='Centro de Destino', choices=[(1, ''), (2, 'CTRD'), (3, 'FLEX')])
    deposito_destino = forms.ChoiceField(label='Depósito de Destino', choices=[(1, ''), (2, '989A'), (3, '0001')])
