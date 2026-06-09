from django import forms


PROFILE_CHOICES = [
    ('', '— Selecione —'),
    ('prospect', 'Prospect'),
    ('customer', 'Cliente'),
    ('partner', 'Parceiro'),
]


_INPUT = forms.TextInput(attrs={'class': 'crm-input'})
_SELECT = forms.Select(attrs={'class': 'crm-input'})
_CHECK = forms.CheckboxInput(attrs={'class': 'crm-checkbox'})


class ClientForm(forms.Form):
    gai_id = forms.ChoiceField(
        label='GAI / Cliente',
        required=False,
        widget=_SELECT,
        help_text='Obrigatório na criação. Vincula o registro CRM ao GAI do Arancia.',
    )
    razao_social = forms.CharField(
        label='Razão social',
        max_length=200,
        required=True,
        widget=_INPUT,
    )
    nome = forms.CharField(
        label='Nome fantasia',
        max_length=200,
        required=False,
        widget=_INPUT,
    )
    cnpj = forms.CharField(
        label='CNPJ',
        max_length=20,
        required=False,
        widget=_INPUT,
    )
    email = forms.EmailField(
        label='E-mail',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'crm-input'}),
    )
    telefone1 = forms.CharField(
        label='Telefone',
        max_length=20,
        required=False,
        widget=_INPUT,
    )
    profile = forms.ChoiceField(
        label='Perfil',
        choices=PROFILE_CHOICES,
        required=False,
        widget=_SELECT,
    )

    def __init__(self, *args, gai_choices=None, lock_gai=False, **kwargs):
        super().__init__(*args, **kwargs)
        choices = list(gai_choices or [])
        if not lock_gai:
            choices = [('', '— Selecione o GAI —')] + choices
        self.fields['gai_id'].choices = choices
        if lock_gai:
            self.fields['gai_id'].widget.attrs['readonly'] = True
            self.fields['gai_id'].disabled = True

    def cleaned_payload(self):
        """Retorna dict pronto para POST/PATCH na API (omite vazios)."""
        data = self.cleaned_data
        payload = {
            'razao_social': data['razao_social'].strip(),
        }
        gai_id = data.get('gai_id')
        if gai_id:
            payload['gai_id'] = int(gai_id)
        for field in ('nome', 'cnpj', 'email', 'telefone1', 'profile'):
            value = data.get(field)
            if value not in (None, ''):
                payload[field] = value
        return payload


class ClientContactForm(forms.Form):
    name = forms.CharField(label='Nome', max_length=120, required=True, widget=_INPUT)
    email = forms.EmailField(
        label='E-mail',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'crm-input'}),
    )
    phone = forms.CharField(label='Telefone', max_length=20, required=False, widget=_INPUT)
    role = forms.CharField(label='Função', max_length=80, required=False, widget=_INPUT)
    is_primary = forms.BooleanField(label='Contato principal', required=False, widget=_CHECK)

    def cleaned_payload(self):
        data = self.cleaned_data
        payload = {'name': data['name'].strip()}
        if data.get('email'):
            payload['email'] = data['email']
        if data.get('phone'):
            payload['phone'] = data['phone']
        if data.get('role'):
            payload['role'] = data['role']
        payload['is_primary'] = bool(data.get('is_primary'))
        return payload


class ClientAddressForm(forms.Form):
    label = forms.CharField(label='Identificação', max_length=80, required=False, widget=_INPUT)
    street = forms.CharField(label='Logradouro', max_length=255, required=True, widget=_INPUT)
    number = forms.CharField(label='Número', max_length=20, required=False, widget=_INPUT)
    complement = forms.CharField(label='Complemento', max_length=100, required=False, widget=_INPUT)
    district = forms.CharField(label='Bairro', max_length=100, required=False, widget=_INPUT)
    city = forms.CharField(label='Cidade', max_length=100, required=False, widget=_INPUT)
    state = forms.CharField(label='UF', max_length=2, required=False, widget=_INPUT)
    zip_code = forms.CharField(label='CEP', max_length=10, required=False, widget=_INPUT)
    is_primary = forms.BooleanField(label='Endereço principal', required=False, widget=_CHECK)

    def cleaned_payload(self):
        data = self.cleaned_data
        payload = {'street': data['street'].strip()}
        for field in (
            'label', 'number', 'complement', 'district',
            'city', 'state', 'zip_code',
        ):
            value = data.get(field)
            if value not in (None, ''):
                payload[field] = value
        payload['is_primary'] = bool(data.get('is_primary'))
        return payload
