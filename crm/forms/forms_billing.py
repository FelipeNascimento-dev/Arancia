from django import forms

from crm.forms.forms_clients import _INPUT, _SELECT

_TEXTAREA = forms.Textarea(attrs={'class': 'crm-input', 'rows': 3})


class BillingForm(forms.Form):
    customer_gai_id = forms.ChoiceField(
        label='Cliente (GAI)',
        required=False,
        widget=_SELECT,
    )
    contract_id = forms.ChoiceField(
        label='Contrato',
        required=False,
        widget=_SELECT,
    )
    period_start = forms.DateField(
        label='Início do período',
        required=False,
        widget=forms.DateInput(attrs={'class': 'crm-input', 'type': 'date'}),
    )
    period_end = forms.DateField(
        label='Fim do período',
        required=False,
        widget=forms.DateInput(attrs={'class': 'crm-input', 'type': 'date'}),
    )
    planned_amount = forms.DecimalField(
        label='Valor previsto',
        required=False,
        min_value=0,
        decimal_places=2,
        initial=0,
        widget=_INPUT,
    )
    actual_amount = forms.DecimalField(
        label='Valor realizado',
        required=False,
        min_value=0,
        decimal_places=2,
        initial=0,
        widget=_INPUT,
    )
    notes = forms.CharField(
        label='Observações',
        required=False,
        widget=_TEXTAREA,
    )

    def __init__(
        self,
        *args,
        customer_choices=None,
        contract_choices=None,
        lock_customer=False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        customers = list(customer_choices or [])
        if not lock_customer:
            customers = [('', '— Selecione o cliente —')] + customers
        self.fields['customer_gai_id'].choices = customers
        if lock_customer:
            del self.fields['customer_gai_id']
            del self.fields['contract_id']
        else:
            contracts = [('', '— Nenhum —')] + list(contract_choices or [])
            self.fields['contract_id'].choices = contracts

    def cleaned_payload(self, *, for_update=False):
        data = self.cleaned_data
        payload = {}

        if not for_update:
            gai_id = data.get('customer_gai_id')
            if gai_id:
                payload['customer_gai_id'] = int(gai_id)
            contract_id = data.get('contract_id')
            if contract_id:
                payload['contract_id'] = contract_id

        for date_field in ('period_start', 'period_end'):
            value = data.get(date_field)
            if value:
                payload[date_field] = value.isoformat()
            elif for_update:
                payload[date_field] = None

        for amount_field in ('planned_amount', 'actual_amount'):
            value = data.get(amount_field)
            if value is not None:
                payload[amount_field] = str(value)

        notes = data.get('notes')
        if notes:
            payload['notes'] = notes
        elif for_update:
            payload['notes'] = None

        return payload
