from django import forms
from ..models import GroupAditionalInformation


class ReverseCreateForm(forms.Form):
    serial = forms.CharField(
        label='Serial',
        max_length=50,
        required=False
    )

    sales_channel = forms.ChoiceField(
        label='Escolha o Canal de Vendas',
        required=False,
        choices=()
    )

    group_aditional_information = forms.ChoiceField(
        label='Informação Adicional do Grupo',
        required=False,
        choices=()
    )

    def __init__(self, *args, nome_form=None, **kwargs):
        self.nome_formulario = nome_form or "Definir nome do formulário"
        super().__init__(*args, **kwargs)

        sales_channel_choices = (
            GroupAditionalInformation.objects
            .exclude(sales_channel__isnull=True)
            .exclude(sales_channel__exact="")
            .values_list("sales_channel", "sales_channel")
            .distinct()
        )
        self.fields['sales_channel'].choices = [
            ("", "")] + list(sales_channel_choices)

        group_choices = (
            GroupAditionalInformation.objects
            .values_list("id", "nome")
        )
        self.fields['group_aditional_information'].choices = [
            ("", "")] + list(group_choices)
