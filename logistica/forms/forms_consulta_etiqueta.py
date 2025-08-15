from django import forms

class EtiquetasForm(forms.Form):
    nome_formulario = 'Consulta de Etiquetas'
    pedido = forms.CharField(label='Pedido', max_length=20)
    qtde_vol = forms.IntegerField(label='Qtde de Volumes', min_value=1, required=True)

    def __init__(self, *args, nome_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['qtde_vol'].initial = 1