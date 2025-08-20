from django import forms

class ExtracaoForm(forms.Form):
    nome_formulario = 'Extração de Pedidos'
    # sales_channel = forms.ChoiceField(label='Canal de Vendas', choices=[
    #     ('', ''), 
    #     ('all', 'All'), 
    #     ],
    #     required=True
    # )