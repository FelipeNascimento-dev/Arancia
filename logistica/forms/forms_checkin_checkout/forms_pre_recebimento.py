from django import forms


class PreRecebimentoForm(forms.Form):
    numero_pedido = forms.CharField(
        label="Número do Pedido",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    seriais = forms.CharField(
        label="Seriais",
        max_length=200,
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    def __init__(self, *args, nome_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Definir nome do formulário"
