from django import forms

from crm.forms.forms_clients import _CHECK, _INPUT


class ServiceTypeForm(forms.Form):
    name = forms.CharField(label='Nome', max_length=100, required=True, widget=_INPUT)
    code = forms.CharField(label='Código', max_length=50, required=False, widget=_INPUT)
    is_active = forms.BooleanField(label='Ativo', required=False, widget=_CHECK, initial=True)

    def cleaned_payload(self):
        data = self.cleaned_data
        payload = {'name': data['name'].strip(), 'is_active': bool(data.get('is_active'))}
        if data.get('code'):
            payload['code'] = data['code'].strip()
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
