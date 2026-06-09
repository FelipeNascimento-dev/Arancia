from django import forms

from crm.forms.forms_clients import _CHECK, _INPUT, _SELECT

CONTRACT_STATUS_CHOICES = [
    ('', '— Automático —'),
    ('draft', 'Rascunho'),
    ('active', 'Ativo'),
    ('suspended', 'Suspenso'),
    ('expired', 'Expirado'),
    ('cancelled', 'Cancelado'),
]


class ContractForm(forms.Form):
    customer_gai_id = forms.ChoiceField(
        label='Cliente (GAI)',
        required=False,
        widget=_SELECT,
    )
    service_type_id = forms.ChoiceField(
        label='Tipo de serviço',
        required=False,
        widget=_SELECT,
    )
    title = forms.CharField(
        label='Título',
        max_length=200,
        required=True,
        widget=_INPUT,
    )
    description = forms.CharField(
        label='Descrição',
        required=False,
        widget=forms.Textarea(attrs={'class': 'crm-input', 'rows': 3}),
    )
    start_date = forms.DateField(
        label='Início',
        required=False,
        widget=forms.DateInput(attrs={'class': 'crm-input', 'type': 'date'}),
    )
    end_date = forms.DateField(
        label='Término',
        required=False,
        widget=forms.DateInput(attrs={'class': 'crm-input', 'type': 'date'}),
    )
    renewal_notice_days = forms.IntegerField(
        label='Aviso de renovação (dias)',
        required=False,
        initial=30,
        min_value=0,
        widget=_INPUT,
    )
    status = forms.ChoiceField(
        label='Status',
        choices=CONTRACT_STATUS_CHOICES,
        required=False,
        widget=_SELECT,
    )
    is_active = forms.BooleanField(
        label='Ativo',
        required=False,
        widget=_CHECK,
    )

    def __init__(
        self,
        *args,
        customer_choices=None,
        service_type_choices=None,
        lock_customer=False,
        show_status_fields=False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        customers = list(customer_choices or [])
        if not lock_customer:
            customers = [('', '— Selecione o cliente —')] + customers
        self.fields['customer_gai_id'].choices = customers
        if lock_customer:
            self.fields['customer_gai_id'].disabled = True

        st_choices = [('', '— Nenhum —')] + list(service_type_choices or [])
        self.fields['service_type_id'].choices = st_choices

        if not show_status_fields:
            del self.fields['status']
            del self.fields['is_active']

    def cleaned_payload(self, *, for_update=False):
        data = self.cleaned_data
        payload = {}

        if not for_update:
            payload['title'] = data['title'].strip()
            gai_id = data.get('customer_gai_id')
            if gai_id:
                payload['customer_gai_id'] = int(gai_id)
        else:
            if data.get('title'):
                payload['title'] = data['title'].strip()

        if data.get('service_type_id'):
            payload['service_type_id'] = data['service_type_id']
        elif for_update and 'service_type_id' in self.fields:
            payload['service_type_id'] = None

        if data.get('description'):
            payload['description'] = data['description']
        elif for_update and data.get('description') == '':
            payload['description'] = None

        for date_field in ('start_date', 'end_date'):
            value = data.get(date_field)
            if value:
                payload[date_field] = value.isoformat()
            elif for_update and date_field in self.fields:
                payload[date_field] = None

        if data.get('renewal_notice_days') is not None:
            payload['renewal_notice_days'] = data['renewal_notice_days']

        if 'status' in self.fields and data.get('status'):
            payload['status'] = data['status']
        if 'is_active' in self.fields:
            payload['is_active'] = bool(data.get('is_active'))

        return payload


class ContractFileForm(forms.Form):
    file = forms.FileField(
        label='Arquivo do contrato',
        required=True,
        widget=forms.FileInput(attrs={'class': 'crm-input', 'accept': '.pdf,.doc,.docx,.xls,.xlsx,.png,.jpg,.jpeg'}),
    )
