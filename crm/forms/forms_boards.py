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
