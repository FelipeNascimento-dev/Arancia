import re
import unicodedata

from django import forms

from crm.forms.forms_clients import _CHECK, _INPUT, _SELECT


def _slugify_project_code(name):
    normalized = unicodedata.normalize('NFKD', (name or '').strip())
    ascii_text = normalized.encode('ascii', 'ignore').decode('ascii')
    code = re.sub(r'[^a-zA-Z0-9]+', '-', ascii_text.lower()).strip('-')
    return (code[:50] if code else 'projeto')


class ProjectForm(forms.Form):
    name = forms.CharField(label='Nome', max_length=200, required=True, widget=_INPUT)
    code = forms.CharField(
        label='Código',
        max_length=50,
        required=False,
        widget=_INPUT,
        help_text='Gerado automaticamente a partir do nome se deixado em branco.',
    )
    description = forms.CharField(
        label='Descrição',
        required=False,
        widget=forms.Textarea(attrs={'class': 'crm-input', 'rows': 3}),
    )
    customer_gai_id = forms.ChoiceField(label='Cliente (GAI)', required=False, widget=_SELECT)
    is_active = forms.BooleanField(label='Ativo', required=False, widget=_CHECK, initial=True)

    def __init__(self, *args, customer_choices=None, lock_customer=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock_customer = lock_customer
        customers = [('', '— Nenhum —')] + list(customer_choices or [])
        self.fields['customer_gai_id'].choices = customers
        if lock_customer:
            self.fields['customer_gai_id'].disabled = True

    def cleaned_payload(self, *, for_update=False):
        data = self.cleaned_data
        payload = {}
        if data.get('name'):
            payload['name'] = data['name'].strip()
        code = (data.get('code') or '').strip()
        if not code and data.get('name'):
            code = _slugify_project_code(data['name'])
        if code and not for_update:
            payload['code'] = code
        elif for_update and 'code' in self.fields and code:
            payload['code'] = code
        if data.get('description'):
            payload['description'] = data['description']
        elif for_update and data.get('description') == '':
            payload['description'] = None
        if not self.lock_customer:
            if data.get('customer_gai_id'):
                payload['customer_gai_id'] = int(data['customer_gai_id'])
            elif (
                for_update
                and 'customer_gai_id' in self.fields
                and 'customer_gai_id' in self.data
                and not self.data.get('customer_gai_id')
            ):
                payload['customer_gai_id'] = None
        elif not for_update and data.get('customer_gai_id'):
            payload['customer_gai_id'] = int(data['customer_gai_id'])
        if 'is_active' in self.fields:
            payload['is_active'] = bool(data.get('is_active'))
        return payload


class ProjectMemberForm(forms.Form):
    user_id = forms.ChoiceField(label='Usuário', required=False, widget=_SELECT)
    designation_id = forms.ChoiceField(label='Designação', required=False, widget=_SELECT)
    team_gai_id = forms.ChoiceField(label='Equipe (GAI)', required=False, widget=_SELECT)
    role = forms.CharField(label='Papel', max_length=100, required=False, widget=_INPUT)

    def __init__(
        self,
        *args,
        user_choices=None,
        designation_choices=None,
        team_gai_choices=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.fields['user_id'].choices = [('', '— Nenhum —')] + list(user_choices or [])
        self.fields['designation_id'].choices = [('', '— Nenhuma —')] + list(designation_choices or [])
        self.fields['team_gai_id'].choices = [('', '— Nenhuma —')] + list(team_gai_choices or [])

    def clean(self):
        cleaned = super().clean()
        keys = ('user_id', 'designation_id', 'team_gai_id')
        filled = [k for k in keys if cleaned.get(k)]
        if len(filled) != 1:
            raise forms.ValidationError(
                'Informe exatamente um membro: usuário, designação ou equipe (GAI).'
            )
        return cleaned

    def cleaned_payload(self):
        data = self.cleaned_data
        payload = {}
        if data.get('user_id'):
            payload['user_id'] = int(data['user_id'])
        if data.get('designation_id'):
            payload['designation_id'] = int(data['designation_id'])
        if data.get('team_gai_id'):
            payload['team_gai_id'] = int(data['team_gai_id'])
        if data.get('role'):
            payload['role'] = data['role'].strip()
        return payload
