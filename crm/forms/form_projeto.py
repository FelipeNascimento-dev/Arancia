from django import forms

from crm.helpers.lookup_choices import build_select_choices, build_user_choices


class ProjectForm(forms.Form):
    name = forms.CharField(
        label="Nome",
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    description = forms.CharField(
        label="Descrição",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )
    customer_gai_id = forms.IntegerField(
        label="Cliente (GAI)",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    is_active = forms.BooleanField(
        label="Ativo",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    def __init__(self, *args, lookups=None, nome_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Novo Projeto"
        lookups = lookups or {}
        self.fields["customer_gai_id"].widget = forms.Select(
            choices=build_select_choices(
                lookups.get("gais", []),
                id_keys=("id", "gai_id", "customer_gai_id"),
                label_keys=("nome", "name", "razao_social"),
            ),
            attrs={"class": "form-control"},
        )


class ProjectMemberForm(forms.Form):
    member_type = forms.ChoiceField(
        label="Tipo de membro",
        choices=[
            ("user", "Usuário"),
            ("designation", "Designação"),
            ("team_gai", "Equipe (GAI)"),
        ],
        widget=forms.Select(attrs={"class": "form-control", "id": "member_type"}),
    )
    user_id = forms.IntegerField(
        label="Usuário",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    designation_id = forms.IntegerField(
        label="Designação",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    team_gai_id = forms.IntegerField(
        label="Equipe (GAI)",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    role = forms.CharField(
        label="Papel",
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, lookups=None, **kwargs):
        super().__init__(*args, **kwargs)
        lookups = lookups or {}
        self.fields["user_id"].widget = forms.Select(
            choices=build_user_choices(lookups.get("users", [])),
            attrs={"class": "form-control"},
        )
        self.fields["designation_id"].widget = forms.Select(
            choices=build_select_choices(
                lookups.get("designations", []),
                id_keys=("id", "designation_id", "user_designation_id"),
                label_keys=("label", "username", "name", "nome"),
            ),
            attrs={"class": "form-control"},
        )
        self.fields["team_gai_id"].widget = forms.Select(
            choices=build_select_choices(
                lookups.get("team_gais", []),
                id_keys=("id", "gai_id", "team_gai_id"),
                label_keys=("nome", "name"),
            ),
            attrs={"class": "form-control"},
        )

    def clean(self):
        cleaned = super().clean()
        member_type = cleaned.get("member_type")
        if member_type == "user" and not cleaned.get("user_id"):
            self.add_error("user_id", "Selecione um usuário.")
        elif member_type == "designation" and not cleaned.get("designation_id"):
            self.add_error("designation_id", "Selecione uma designação.")
        elif member_type == "team_gai" and not cleaned.get("team_gai_id"):
            self.add_error("team_gai_id", "Selecione uma equipe.")
        return cleaned
