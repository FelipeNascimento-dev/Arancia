from django import forms

from crm.forms.forms_clients import _CHECK, _INPUT, _SELECT


class BoardAccessForm(forms.Form):
    user_id = forms.ChoiceField(label='Usuário', required=False, widget=_SELECT)
    designation_id = forms.ChoiceField(label='Designação', required=False, widget=_SELECT)
    team_gai_id = forms.ChoiceField(label='Equipe (GAI)', required=False, widget=_SELECT)
    can_view = forms.BooleanField(label='Visualizar', required=False, widget=_CHECK, initial=True)
    can_move_tasks = forms.BooleanField(label='Mover tarefas', required=False, widget=_CHECK)
    can_comment = forms.BooleanField(label='Comentar', required=False, widget=_CHECK)
    can_manage_columns = forms.BooleanField(label='Gerenciar colunas', required=False, widget=_CHECK)

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
                'Informe exatamente um alvo: usuário, designação ou equipe (GAI).'
            )
        return cleaned

    def cleaned_payload(self):
        data = self.cleaned_data
        payload = {
            'can_view': bool(data.get('can_view')),
            'can_move_tasks': bool(data.get('can_move_tasks')),
            'can_comment': bool(data.get('can_comment')),
            'can_manage_columns': bool(data.get('can_manage_columns')),
        }
        if data.get('user_id'):
            payload['user_id'] = int(data['user_id'])
        if data.get('designation_id'):
            payload['designation_id'] = int(data['designation_id'])
        if data.get('team_gai_id'):
            payload['team_gai_id'] = int(data['team_gai_id'])
        return payload


class BoardForm(forms.Form):
    name = forms.CharField(label='Nome', max_length=200, required=True, widget=_INPUT)
    description = forms.CharField(
        label='Descrição',
        required=False,
        widget=forms.Textarea(attrs={'class': 'crm-input', 'rows': 3}),
    )
    project_id = forms.ChoiceField(label='Projeto', required=False, widget=_SELECT)

    def __init__(self, *args, project_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project_id'].choices = [('', '— Nenhum —')] + list(project_choices or [])

    def cleaned_payload(self, *, for_update=False):
        data = self.cleaned_data
        payload = {'name': data['name'].strip()}
        if data.get('description'):
            payload['description'] = data['description']
        elif for_update:
            payload['description'] = data.get('description') or None
        if data.get('project_id'):
            payload['project_id'] = data['project_id']
        elif for_update and 'project_id' in self.data and not self.data.get('project_id'):
            payload['project_id'] = None
        return payload


class BoardColumnForm(forms.Form):
    name = forms.CharField(label='Nome da coluna', max_length=100, required=True, widget=_INPUT)
    status_id = forms.ChoiceField(label='Status', required=True, widget=_SELECT)
    column_template_id = forms.ChoiceField(label='Template (opcional)', required=False, widget=_SELECT)

    def __init__(self, *args, status_choices=None, template_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status_id'].choices = [('', '— Selecione —')] + list(status_choices or [])
        self.fields['column_template_id'].choices = [('', '— Nenhum —')] + list(template_choices or [])

    def cleaned_payload(self, *, for_update=False):
        data = self.cleaned_data
        payload = {}
        if data.get('name'):
            payload['name'] = data['name'].strip()
        if data.get('status_id'):
            payload['status_id'] = data['status_id']
        if data.get('column_template_id'):
            payload['column_template_id'] = data['column_template_id']
        elif for_update and 'column_template_id' in self.data and not self.data.get('column_template_id'):
            payload['column_template_id'] = None
        return payload


class BoardAccessUpdateForm(forms.Form):
    can_view = forms.BooleanField(label='Visualizar', required=False, widget=_CHECK)
    can_move_tasks = forms.BooleanField(label='Mover tarefas', required=False, widget=_CHECK)
    can_comment = forms.BooleanField(label='Comentar', required=False, widget=_CHECK)
    can_manage_columns = forms.BooleanField(label='Gerenciar colunas', required=False, widget=_CHECK)
    access_level = forms.ChoiceField(
        label='Nível de acesso',
        required=False,
        choices=[
            ('', '— Manter —'),
            ('viewer', 'Visualizador'),
            ('editor', 'Editor'),
            ('owner', 'Proprietário'),
        ],
        widget=_SELECT,
    )

    def cleaned_payload(self):
        data = self.cleaned_data
        payload = {
            'can_view': bool(data.get('can_view')),
            'can_move_tasks': bool(data.get('can_move_tasks')),
            'can_comment': bool(data.get('can_comment')),
            'can_manage_columns': bool(data.get('can_manage_columns')),
        }
        if data.get('access_level'):
            payload['access_level'] = data['access_level']
        return payload
