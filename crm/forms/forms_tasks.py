from django import forms

from crm.forms.forms_clients import _CHECK, _INPUT, _SELECT
from crm.services.datetime_utils import format_datetime_to_api


class TaskForm(forms.Form):
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
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
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
