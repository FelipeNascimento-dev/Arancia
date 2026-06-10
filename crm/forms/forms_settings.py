from django import forms

from crm.forms.forms_clients import _CHECK, _INPUT, _SELECT


DIRECTION_CHOICES = [
    ('', '— Selecione —'),
    ('normal', 'Normal'),
    ('reverse', 'Reversa'),
]


class ServiceTypeForm(forms.Form):
    type = forms.CharField(label='Tipo', max_length=50, required=True, widget=_INPUT)
    description = forms.CharField(
        label='Descrição',
        max_length=255,
        required=False,
        widget=forms.Textarea(attrs={'class': 'crm-input', 'rows': 2}),
    )
    status_initial_id = forms.ChoiceField(
        label='Status inicial',
        required=False,
        widget=_SELECT,
    )
    client_id = forms.ChoiceField(
        label='Cliente (GAI)',
        required=False,
        widget=_SELECT,
    )
    direction = forms.ChoiceField(
        label='Direção',
        choices=DIRECTION_CHOICES,
        required=False,
        widget=_SELECT,
    )

    def __init__(self, *args, status_choices=None, client_choices=None, default_client_id='', **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status_initial_id'].choices = [('', '— Nenhum —')] + list(status_choices or [])
        self.fields['client_id'].choices = [('', '— Nenhum —')] + list(client_choices or [])
        for field in ('client_id', 'status_initial_id'):
            if self.initial.get(field) is not None:
                self.initial[field] = str(self.initial[field])
        if default_client_id and not self.initial.get('client_id'):
            self.initial['client_id'] = str(default_client_id)
        if default_client_id:
            self.fields['client_id'].disabled = True

    def cleaned_payload(self):
        data = self.cleaned_data
        payload = {'type': data['type'].strip()}
        if data.get('description'):
            payload['description'] = data['description'].strip()
        if data.get('status_initial_id'):
            payload['status_initial_id'] = data['status_initial_id']
        client_id = data.get('client_id')
        if not client_id and self.fields['client_id'].disabled:
            client_id = self.initial.get('client_id')
        if client_id:
            payload['client_id'] = int(client_id)
        if data.get('direction'):
            payload['direction'] = data['direction']
        return payload


class PriorityForm(forms.Form):
    name = forms.CharField(label='Nome', max_length=100, required=True, widget=_INPUT)
    level = forms.IntegerField(label='Nível', required=False, min_value=0, widget=_INPUT)
    color = forms.CharField(label='Cor (hex)', max_length=20, required=False, widget=_INPUT)
    is_active = forms.BooleanField(label='Ativo', required=False, widget=_CHECK, initial=True)

    def cleaned_payload(self):
        data = self.cleaned_data
        payload = {'name': data['name'].strip(), 'is_active': bool(data.get('is_active'))}
        if data.get('level') is not None:
            payload['level'] = data['level']
        if data.get('color'):
            payload['color'] = data['color'].strip()
        return payload


class StatusTaskForm(forms.Form):
    name = forms.CharField(label='Nome', max_length=100, required=True, widget=_INPUT)
    code = forms.CharField(label='Código', max_length=50, required=False, widget=_INPUT)
    is_terminal = forms.BooleanField(label='Status final', required=False, widget=_CHECK)
    is_active = forms.BooleanField(label='Ativo', required=False, widget=_CHECK, initial=True)

    def cleaned_payload(self):
        data = self.cleaned_data
        payload = {
            'name': data['name'].strip(),
            'is_terminal': bool(data.get('is_terminal')),
            'is_active': bool(data.get('is_active')),
        }
        if data.get('code'):
            payload['code'] = data['code'].strip()
        return payload
