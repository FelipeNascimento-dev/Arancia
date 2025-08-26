from django import forms
from ..models import GroupAditionalInformation


class ConsultaPedForm(forms.Form):
    nome_formulario = 'Consulta de Pedidos'

    sales_channel = forms.ChoiceField(
        label='Tipo de Registro',
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        sales_channels = (
            GroupAditionalInformation.objects
            .exclude(sales_channel__isnull=True)
            .exclude(sales_channel__exact="")
            .values_list("sales_channel", flat=True)
            .distinct()
        )

        self.fields["sales_channel"].choices = [
            ("", "Selecione...")] + [(sc, sc) for sc in sales_channels]
