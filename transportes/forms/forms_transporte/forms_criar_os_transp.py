from django import forms


class FormCriarOsTransp(forms.Form):
    numero_os = forms.CharField(label="Número da OS", max_length=100)
    ex_order_number = forms.CharField(
        label="Número do Pedido", max_length=100, required=False)
    cliente = forms.ChoiceField(label="Cliente", choices=[], required=False)
    origem = forms.ChoiceField(label="Origem", choices=[], required=False)
    destino = forms.ChoiceField(label="Destino", choices=[], required=False)
    tipo_os = forms.ChoiceField(
        label="Tipo de Serviço", choices=[], required=False)
    status_os = forms.ChoiceField(label="Status", choices=[], required=False)

    def __init__(self, *args, nome_form=None, **kwargs):
        self.nome_formulario = nome_form or "Definir nome do formulário"
        super().__init__(*args, **kwargs)
