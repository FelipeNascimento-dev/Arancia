from django import forms

from crm.forms.forms_clients import _CHECK, _INPUT, _SELECT
from crm.services.datetime_utils import format_datetime_to_api

FREQUENCY_CHOICES = [
    ('daily', 'Diária'),
    ('weekly', 'Semanal'),
    ('monthly', 'Mensal'),
]


class TaskRecurrenceForm(forms.Form):
    title = forms.CharField(label='Título', max_length=200, required=True, widget=_INPUT)
    description = forms.CharField(
        label='Descrição',
        required=False,
        widget=forms.Textarea(attrs={'class': 'crm-input', 'rows': 3}),
    )
    board_id = forms.ChoiceField(label='Board', required=False, widget=_SELECT)
    status_id = forms.ChoiceField(label='Status', required=False, widget=_SELECT)
    priority_id = forms.ChoiceField(label='Prioridade', required=False, widget=_SELECT)
    project_id = forms.ChoiceField(label='Projeto', required=False, widget=_SELECT)
    frequency = forms.ChoiceField(label='Frequência', choices=FREQUENCY_CHOICES, required=True, widget=_SELECT)
    interval = forms.IntegerField(label='Intervalo', required=False, min_value=1, initial=1, widget=_INPUT)
    start_date = forms.CharField(
        label='Início',
        required=False,
        widget=forms.DateInput(attrs={'class': 'crm-input', 'type': 'date'}),
    )
    end_date = forms.CharField(
        label='Fim',
        required=False,
        widget=forms.DateInput(attrs={'class': 'crm-input', 'type': 'date'}),
    )
    is_active = forms.BooleanField(label='Ativa', required=False, widget=_CHECK, initial=True)

    def __init__(
        self,
        *args,
        board_choices=None,
        status_choices=None,
        priority_choices=None,
        project_choices=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.fields['board_id'].choices = [('', '— Nenhum —')] + list(board_choices or [])
        self.fields['status_id'].choices = [('', '— Automático —')] + list(status_choices or [])
        self.fields['priority_id'].choices = [('', '— Nenhuma —')] + list(priority_choices or [])
        self.fields['project_id'].choices = [('', '— Nenhum —')] + list(project_choices or [])

    def cleaned_payload(self, *, for_update=False):
        data = self.cleaned_data
        payload = {
            'title': data['title'].strip(),
            'frequency': data['frequency'],
            'is_active': bool(data.get('is_active')),
        }
        if data.get('description'):
            payload['description'] = data['description']
        elif for_update:
            payload['description'] = data.get('description') or None

        for field, key in (
            ('board_id', 'board_id'),
            ('status_id', 'status_id'),
            ('priority_id', 'priority_id'),
            ('project_id', 'project_id'),
        ):
            if data.get(field):
                payload[key] = data[field]

        if data.get('interval'):
            payload['interval'] = data['interval']

        for field, key in (('start_date', 'start_date'), ('end_date', 'end_date')):
            raw = data.get(field)
            if raw:
                api_val = format_datetime_to_api(f'{raw}T00:00')
                if api_val:
                    payload[key] = api_val[:10]
            elif for_update and field in self.data and not self.data.get(field):
                payload[key] = None

        return payload
