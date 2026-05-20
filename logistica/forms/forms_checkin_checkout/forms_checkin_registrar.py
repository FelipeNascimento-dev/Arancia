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
        required=False,
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
        required=False,
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

        self.can_view_product = self.pode_visualizar_produto(user)

        if not self.can_view_product:
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

        if not informacao_adicional:
            return False

        nome_gai = (informacao_adicional.nome or "").strip().lower()

        if nome_gai == "pa ctb tatuapé".lower():
            return True

        return False

    def clean(self):
        cleaned_data = super().clean()

        if "product" not in self.fields:
            cleaned_data.pop("product", None)

        return cleaned_data
