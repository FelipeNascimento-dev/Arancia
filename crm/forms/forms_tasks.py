from django import forms

from crm.forms.forms_clients import _CHECK, _INPUT, _SELECT
from crm.services.datetime_utils import format_datetime_to_api

TASK_KIND_CHOICES = (
    ('normal', 'Tarefa única'),
    ('recurring', 'Tarefa recorrente'),
)

FREQUENCY_CHOICES = (
    ('daily', 'Diária'),
    ('weekly', 'Semanal'),
    ('monthly', 'Mensal'),
)


class TaskForm(forms.Form):
    task_kind = forms.ChoiceField(
        label='Tipo de tarefa',
        choices=TASK_KIND_CHOICES,
        initial='normal',
        widget=forms.RadioSelect(attrs={'class': 'crm-task-kind-radio'}),
    )
    title = forms.CharField(label='Título', max_length=200, required=True, widget=_INPUT)
    description = forms.CharField(
        label='Descrição',
        required=False,
        widget=forms.Textarea(attrs={'class': 'crm-input', 'id': 'taskDescription', 'rows': 8}),
    )
    board_id = forms.ChoiceField(label='Board', required=False, widget=_SELECT)
    status_id = forms.ChoiceField(label='Status', required=False, widget=_SELECT)
    priority_id = forms.ChoiceField(label='Prioridade', required=False, widget=_SELECT)
    project_id = forms.ChoiceField(label='Projeto', required=False, widget=_SELECT)
    customer_gai_id = forms.ChoiceField(label='Cliente (GAI)', required=False, widget=_SELECT)
    due_at = forms.CharField(
        label='Vencimento',
        required=False,
        widget=forms.DateTimeInput(attrs={'class': 'crm-input', 'type': 'datetime-local'}),
    )
    scheduled_at = forms.CharField(
        label='Agendamento',
        required=False,
        widget=forms.DateTimeInput(attrs={'class': 'crm-input', 'type': 'datetime-local'}),
    )
    frequency = forms.ChoiceField(
        label='Frequência',
        choices=[('', '— Selecione —')] + list(FREQUENCY_CHOICES),
        required=False,
        widget=_SELECT,
    )
    interval = forms.IntegerField(
        label='Intervalo',
        required=False,
        min_value=1,
        initial=1,
        widget=_INPUT,
        help_text='Ex.: a cada 2 semanas → frequência Semanal e intervalo 2.',
    )
    recurrence_start = forms.CharField(
        label='Início da recorrência',
        required=False,
        widget=forms.DateInput(attrs={'class': 'crm-input', 'type': 'date'}),
    )
    recurrence_end = forms.CharField(
        label='Fim da recorrência',
        required=False,
        widget=forms.DateInput(attrs={'class': 'crm-input', 'type': 'date'}),
    )
    is_active = forms.BooleanField(label='Ativa', required=False, widget=_CHECK)

    def __init__(
        self,
        *args,
        board_choices=None,
        status_choices=None,
        priority_choices=None,
        project_choices=None,
        customer_choices=None,
        lock_board=False,
        show_status=True,
        show_task_kind=False,
        recurrence_only=False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.show_task_kind = show_task_kind
        self.recurrence_only = recurrence_only

        if recurrence_only:
            self.show_task_kind = False
            if 'task_kind' in self.fields:
                del self.fields['task_kind']
        elif not show_task_kind:
            for name in ('task_kind', 'frequency', 'interval', 'recurrence_start', 'recurrence_end'):
                if name in self.fields:
                    del self.fields[name]
        self.lock_board = lock_board
        boards = [('', '— Nenhum —')] + list(board_choices or [])
        self.fields['board_id'].choices = boards
        if lock_board:
            self.fields['board_id'].disabled = True

        self.fields['status_id'].choices = [('', '— Automático —')] + list(status_choices or [])
        self.fields['priority_id'].choices = [('', '— Nenhuma —')] + list(priority_choices or [])
        self.fields['project_id'].choices = [('', '— Nenhum —')] + list(project_choices or [])
        self.fields['customer_gai_id'].choices = [('', '— Nenhum —')] + list(customer_choices or [])

        if not show_status:
            del self.fields['status_id']

    def clean(self):
        cleaned = super().clean()
        is_recurring = self.recurrence_only or (
            self.show_task_kind and cleaned.get('task_kind') == 'recurring'
        )
        if not is_recurring:
            return cleaned
        if not cleaned.get('frequency'):
            self.add_error('frequency', 'Informe a frequência da recorrência.')
        if not cleaned.get('recurrence_start'):
            self.add_error('recurrence_start', 'Informe a data de início da recorrência.')
        return cleaned

    def is_recurring(self):
        if self.recurrence_only:
            return True
        return self.show_task_kind and self.cleaned_data.get('task_kind') == 'recurring'

    def cleaned_payload(self, *, for_update=False):
        data = self.cleaned_data
        payload = {}

        if data.get('title'):
            payload['title'] = data['title'].strip()

        if data.get('description'):
            payload['description'] = data['description']
        elif for_update and data.get('description') == '':
            payload['description'] = None

        for field, key in (
            ('board_id', 'board_id'),
            ('status_id', 'status_id'),
            ('priority_id', 'priority_id'),
            ('project_id', 'project_id'),
        ):
            if field not in self.fields:
                continue
            if field == 'board_id' and self.lock_board:
                continue
            if data.get(field):
                payload[key] = data[field]

        if data.get('customer_gai_id'):
            payload['customer_gai_id'] = int(data['customer_gai_id'])
        elif (
            for_update
            and 'customer_gai_id' in self.fields
            and 'customer_gai_id' in self.data
            and not self.data.get('customer_gai_id')
        ):
            payload['customer_gai_id'] = None

        due_at = format_datetime_to_api(data.get('due_at'))
        if due_at:
            payload['due_at'] = due_at
        elif for_update and 'due_at' in self.fields:
            payload['due_at'] = None

        scheduled_at = format_datetime_to_api(data.get('scheduled_at'))
        if scheduled_at:
            payload['scheduled_at'] = scheduled_at
        elif for_update and 'scheduled_at' in self.fields:
            payload['scheduled_at'] = None

        if 'is_active' in self.fields:
            payload['is_active'] = bool(data.get('is_active'))

        return payload

    def cleaned_recurrence_payload(self):
        """Payload para POST /task-recurrences/ — gera template + primeira instância na API."""
        data = self.cleaned_data
        payload = {
            'title': data['title'].strip(),
            'frequency': data['frequency'],
            'is_active': True,
        }
        if data.get('description'):
            payload['description'] = data['description']

        for field, key in (
            ('board_id', 'board_id'),
            ('status_id', 'status_id'),
            ('priority_id', 'priority_id'),
            ('project_id', 'project_id'),
        ):
            if field in self.fields and data.get(field):
                payload[key] = data[field]

        if data.get('customer_gai_id'):
            payload['customer_gai_id'] = int(data['customer_gai_id'])

        if data.get('interval'):
            payload['interval'] = data['interval']

        for field, key in (('recurrence_start', 'start_date'), ('recurrence_end', 'end_date')):
            raw = data.get(field)
            if raw:
                api_val = format_datetime_to_api(f'{raw}T00:00')
                if api_val:
                    payload[key] = api_val[:10]

        scheduled_at = format_datetime_to_api(data.get('scheduled_at'))
        if scheduled_at and 'start_date' not in payload:
            payload['start_date'] = scheduled_at[:10]

        return payload


class SubtaskForm(forms.Form):
    title = forms.CharField(label='Título da subtarefa', max_length=200, required=True, widget=_INPUT)


class TaskCommentForm(forms.Form):
    content = forms.CharField(
        label='Comentário',
        required=True,
        widget=forms.Textarea(attrs={'class': 'crm-input', 'rows': 2}),
    )


class TaskAssigneeForm(forms.Form):
    user_id = forms.ChoiceField(label='Usuário', required=False, widget=_SELECT)
    designation_id = forms.ChoiceField(label='Designação', required=False, widget=_SELECT)
    is_primary = forms.BooleanField(label='Responsável principal', required=False, widget=_CHECK)

    def __init__(self, *args, user_choices=None, designation_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_id'].choices = [('', '— Nenhum —')] + list(user_choices or [])
        self.fields['designation_id'].choices = [('', '— Nenhuma —')] + list(designation_choices or [])

    def cleaned_payload(self):
        data = self.cleaned_data
        payload = {'is_primary': bool(data.get('is_primary'))}
        if data.get('user_id'):
            payload['user_id'] = int(data['user_id'])
        if data.get('designation_id'):
            payload['designation_id'] = int(data['designation_id'])
        return payload


class TaskAttachmentForm(forms.Form):
    file = forms.FileField(
        label='Anexo',
        required=True,
        widget=forms.FileInput(attrs={'class': 'crm-input'}),
    )


LINK_TYPE_CHOICES = [
    ('related', 'Relacionada'),
    ('blocks', 'Bloqueia'),
    ('blocked_by', 'Bloqueada por'),
    ('duplicates', 'Duplicata'),
]


class TaskLinkForm(forms.Form):
    linked_task_id = forms.CharField(label='ID da tarefa vinculada', max_length=36, required=True, widget=_INPUT)
    link_type = forms.ChoiceField(label='Tipo de vínculo', choices=LINK_TYPE_CHOICES, required=True, widget=_SELECT)

    def cleaned_payload(self):
        data = self.cleaned_data
        return {
            'linked_task_id': data['linked_task_id'].strip(),
            'link_type': data['link_type'],
        }


class TaskWatcherForm(forms.Form):
    user_id = forms.ChoiceField(label='Usuário', required=False, widget=_SELECT)
    designation_id = forms.ChoiceField(label='Designação', required=False, widget=_SELECT)

    def __init__(self, *args, user_choices=None, designation_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_id'].choices = [('', '— Nenhum —')] + list(user_choices or [])
        self.fields['designation_id'].choices = [('', '— Nenhuma —')] + list(designation_choices or [])

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('user_id') and not cleaned.get('designation_id'):
            raise forms.ValidationError('Informe usuário ou designação.')
        if cleaned.get('user_id') and cleaned.get('designation_id'):
            raise forms.ValidationError('Informe apenas um alvo: usuário ou designação.')
        return cleaned

    def cleaned_payload(self):
        data = self.cleaned_data
        payload = {}
        if data.get('user_id'):
            payload['user_id'] = int(data['user_id'])
        if data.get('designation_id'):
            payload['designation_id'] = int(data['designation_id'])
        return payload
