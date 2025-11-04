from django import forms


class ProductCreateForm(forms.Form):
    product_name = forms.CharField(label='Nome do Produto', max_length=100)

    def __init__(self, *args, nome_form=None, client_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Definir nome do formulário"
