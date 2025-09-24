from django import forms
from django.db.models.functions import Lower
from ..models import GroupAditionalInformation, Group


class ReverseCreateForm(forms.Form):
    romaneio = forms.CharField(
        label='Romaneio',
        max_length=50,
        required=False
    )

    serial = forms.CharField(
        label='Serial',
        max_length=50,
        required=False
    )

    sales_channel = forms.ChoiceField(
        label='CD de Origem',
        required=False,
        choices=()
    )

    group_aditional_information = forms.ChoiceField(
        label='CD de Destino',
        required=False,
        choices=()
    )

    def __init__(self, *args, nome_form=None, user_sales_channel: str | None = None, romaneio_num=None, **kwargs):
        self.nome_formulario = nome_form or "Definir nome do formulário"
        super().__init__(*args, **kwargs)

        if romaneio_num:
            self.fields["romaneio"].initial = romaneio_num
            self.fields["romaneio"].disabled = True

        sc_qs = (
            GroupAditionalInformation.objects
            .exclude(sales_channel__isnull=True)
            .exclude(sales_channel__exact="")
            .annotate(sc_lower=Lower("sales_channel"))
            .order_by("sc_lower")
            .values_list("sales_channel", flat=True)
            .distinct()
        )

        sc_values = list(sc_qs)
        if user_sales_channel and user_sales_channel not in sc_values:
            sc_values.insert(0, user_sales_channel)

        sc_choices = [("", "")] + [(v, v) for v in sc_values]
        self.fields["sales_channel"].choices = sc_choices

        if user_sales_channel:
            self.fields["sales_channel"].initial = user_sales_channel
            if user_sales_channel.lower() != "all":
                self.fields["sales_channel"].disabled = True

        try:
            grupo_cd = Group.objects.get(name="arancia_CD")
            gi_qs = (
                GroupAditionalInformation.objects
                .filter(group=grupo_cd)
                .annotate(nome_lower=Lower("nome"))
                .order_by("nome_lower")
                .values_list("id", "nome")
            )
        except Group.DoesNotExist:
            gi_qs = []

        self.fields["group_aditional_information"].choices = [
            ("", "")] + list(gi_qs)
