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
        label='PA de Origem',
        required=True,
        choices=()
    )

    group_aditional_information = forms.ChoiceField(
        label='CD de Destino',
        required=True,
        choices=()
    )

    def __init__(self, *args, nome_form=None, user_sales_channel: str | None = None, romaneio_num=None, **kwargs):
        self.nome_formulario = nome_form or "Definir nome do formulário"
        super().__init__(*args, **kwargs)

        if romaneio_num:
            self.fields["romaneio"].initial = romaneio_num
            self.fields["romaneio"].disabled = True
        grupo_pa = Group.objects.get(name="arancia_PA")
        sc_qs = (
            GroupAditionalInformation.objects
            .filter(group=grupo_pa)
            .annotate(nome_lower=Lower("nome"))
            .order_by("nome_lower")
            .values_list("id", "nome")
        )
        sc_values = list(sc_qs.values_list("id", "nome")
                         )

        sc_choices = [("", "")]
        if user_sales_channel == 'all':
            sc_values.insert(0, ("all", "all"))

        for v in sc_values:
            if isinstance(v, tuple):
                sc_choices.append(v)
            else:
                sc_choices.append((v, v))

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
