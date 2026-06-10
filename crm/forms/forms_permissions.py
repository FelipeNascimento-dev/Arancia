from django import forms

from crm.forms.forms_clients import _SELECT
from crm.services.permissions import (
    LEVEL_CHOICES,
    PRESET_PROFILES,
    SETTINGS_LEVEL_CHOICES,
)


class UserCrmPermissionsForm(forms.Form):
    preset = forms.ChoiceField(
        label='Perfil rápido',
        required=False,
        widget=_SELECT,
        choices=[('', '— Personalizado —')] + [
            (key, spec['label']) for key, spec in PRESET_PROFILES.items()
        ],
    )
    commercial = forms.ChoiceField(
        label='CRM Comercial',
        choices=LEVEL_CHOICES,
        widget=_SELECT,
    )
    projects = forms.ChoiceField(
        label='Projetos, tarefas e boards',
        choices=LEVEL_CHOICES,
        widget=_SELECT,
    )
    settings = forms.ChoiceField(
        label='Configurações CRM',
        choices=SETTINGS_LEVEL_CHOICES,
        widget=_SELECT,
    )
    admin_scheduler = forms.BooleanField(
        label='Agendador de tarefas recorrentes',
        required=False,
    )
    use_pilot_group = forms.BooleanField(
        label='Atribuir grupo piloto correspondente ao perfil',
        required=False,
        initial=True,
    )

    def cleaned_profile(self):
        data = self.cleaned_data
        preset_key = data.get('preset') or ''
        preset = PRESET_PROFILES.get(preset_key)
        if preset:
            return {
                'commercial': preset['commercial'],
                'projects': preset['projects'],
                'settings': preset['settings'],
                'admin_scheduler': preset['admin_scheduler'],
                'pilot_group': preset['pilot_group'] if data.get('use_pilot_group') else None,
            }
        pilot_group = None
        if data.get('use_pilot_group'):
            for key, spec in PRESET_PROFILES.items():
                if (
                    spec['commercial'] == data['commercial']
                    and spec['projects'] == data['projects']
                    and spec['settings'] == data['settings']
                    and spec['admin_scheduler'] == bool(data.get('admin_scheduler'))
                    and spec.get('pilot_group')
                ):
                    pilot_group = spec['pilot_group']
                    break
        return {
            'commercial': data['commercial'],
            'projects': data['projects'],
            'settings': data['settings'],
            'admin_scheduler': bool(data.get('admin_scheduler')),
            'pilot_group': pilot_group,
        }
