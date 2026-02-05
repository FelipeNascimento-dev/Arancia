from django import forms
from django.db.models.functions import Lower
from ...models import GroupAditionalInformation, Group


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
        label='Destino (PA / CD)',
        required=True,
        choices=()
    )

    def __init__(
        self,
        *args,
        nome_form=None,
        user_sales_channel: str | None = None,
        romaneio_num=None,
        user=None,
        **kwargs
    ):
        self.nome_formulario = nome_form or "Definir nome do formulário"
        self.user = user
        super().__init__(*args, **kwargs)

        if romaneio_num:
            self.fields["romaneio"].initial = romaneio_num
            self.fields["romaneio"].disabled = True

        sc_choices = [("", "")]

        try:
            grupo_pa = Group.objects.get(name="arancia_PA")
            sc_qs = (
                GroupAditionalInformation.objects
                .filter(group=grupo_pa)
                .annotate(nome_lower=Lower("nome"))
                .order_by("nome_lower")
                .values_list("id", "nome")
            )
            sc_choices += list(sc_qs)
        except Group.DoesNotExist:
            pass

        if user_sales_channel == "all":
            sc_choices.insert(1, ("all", "all"))

        self.fields["sales_channel"].choices = sc_choices

        if (
            user_sales_channel
            and user_sales_channel.lower() != "all"
            and self.user
            and hasattr(self.user, "designacao")
            and self.user.designacao.informacao_adicional
        ):
            info = self.user.designacao.informacao_adicional

            self.fields["sales_channel"].choices = [
                (info.id, info.nome)
            ]
            self.fields["sales_channel"].initial = info.id
            # self.fields["sales_channel"].disabled = True

        destino_choices = [("", "")]

        if self.user and self.user.has_perm("logistica.reverse"):
            grupos = Group.objects.filter(
                name__in=["arancia_CD"]
            )

            # destinos = (
            #     GroupAditionalInformation.objects
            #     .filter(group__in=grupos)
            #     .select_related("group")
            #     .annotate(nome_lower=Lower("nome"))
            #     .order_by("group__name", "nome_lower")
            # )

            destinos = (
                GroupAditionalInformation.objects
                .filter(
                    group__in=grupos,
                    nome__istartswith="Flex"
                )
                .select_related("group")
                .annotate(nome_lower=Lower("nome"))
                .order_by("nome_lower")
            )

            for d in destinos:
                if d.group.name == "arancia_PA":
                    label = f"[PA] {d.nome}"
                elif d.group.name == "arancia_CD":
                    label = f"[CD] {d.nome}"
                else:
                    label = d.nome

                destino_choices.append((d.id, label))

        self.fields["group_aditional_information"].choices = destino_choices
