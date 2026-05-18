from django import forms


class ClientCheckInForm(forms.Form):
    pedido_atrelado = forms.CharField(
        label='Pedido',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'autocomplete': 'off'})
    )

    serial = forms.CharField(
        label='Serial',
        max_length=100,
        widget=forms.TextInput(attrs={'autocomplete': 'off'})
    )

    product = forms.ChoiceField(
        label="Produto",
        required=True,
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    from_location = forms.ChoiceField(
        label='Origem',
        required=False,
        choices=[]
    )

    to_location = forms.ChoiceField(
        label='Destino',
        choices=[]
    )

    def __init__(self, *args, **kwargs):
        from_choices = kwargs.pop('from_choices', None)
        product_choices = kwargs.pop('product_choices', None)
        nome_form = kwargs.pop('nome_form', None)
        user = kwargs.pop('user', None)

        self.nome_formulario = nome_form or "Definir nome do formulário"
        self.user = user

        super().__init__(*args, **kwargs)

        if from_choices:
            self.fields['from_location'].choices = [
                ("", "Selecione a origem")
            ] + from_choices

        if product_choices:
            self.fields['product'].choices = product_choices

        if not self.pode_visualizar_produto(user):
            self.fields.pop("product", None)

    def pode_visualizar_produto(self, user):
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        if user.has_perm("logistica.full_checkin"):
            return True

        informacao_adicional = getattr(
            getattr(user, "designacao", None),
            "informacao_adicional",
            None
        )

        if (
            informacao_adicional
            and informacao_adicional.nome
            and informacao_adicional.nome.strip().lower() == "tatuape"
        ):
            return True

        usuario_tem_grupo_tatuape = user.groups.filter(
            informacoes_adicionais__nome__iexact="PA CTB Tatuapé"
        ).exists()

        if usuario_tem_grupo_tatuape:
            return True

        return False

    def clean(self):
        cleaned_data = super().clean()

        if "product" not in self.fields:
            cleaned_data.pop("product", None)

        return cleaned_data
