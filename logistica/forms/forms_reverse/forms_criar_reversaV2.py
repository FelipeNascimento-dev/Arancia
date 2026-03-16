from django import forms
from django.db.models.functions import Lower
from ...models import GroupAditionalInformation, Group


class ReverseCreateV2Form(forms.Form):
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

    def __init__(
        self,
        *args,
        nome_form=None,
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
