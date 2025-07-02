from django import forms

class EstornoForm(forms.Form):
    nome_formulario = 'Estornos'
    id = forms.CharField(label='ID', max_length=20)
    tp_reg = forms.ChoiceField(label='Tipo de Estorno', choices=[
        ('', ''), 
        ('14', 'Estorno Pré-Recebimento'), 
        ('16', 'Estorno Recebimento'),
        ],
        required=True
    )
    serial = forms.CharField(label='Serial', max_length=50,required=False)