from django import forms

class ExtracaoForm(forms.Form):
    nome_formulario = 'Extração de Pedidos'
    tp_reg = forms.ChoiceField(label='Filtros', choices=[
        ('', ''), 
        ('All', 'All'), 
        ],
        required=True
    )