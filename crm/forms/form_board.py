from django import forms


class BoardForm(forms.Form):
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
    column_template_id = forms.IntegerField(
        label="Template de colunas",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    is_active = forms.BooleanField(
        label="Ativo",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    def __init__(self, *args, lookups=None, nome_form=None, initial_data=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Board"
        lookups = lookups or {}
        template_choices = [("", "---------")]
        for tpl in lookups.get("column_templates", []):
            tpl_id = tpl.get("id")
            label = tpl.get("name") or tpl.get("nome") or str(tpl_id)
            if tpl_id is not None:
                template_choices.append((tpl_id, label))
        self.fields["column_template_id"].widget = forms.Select(
            choices=template_choices,
            attrs={"class": "form-control"},
        )
        if initial_data:
            for key, value in initial_data.items():
                if key in self.fields and value is not None:
                    self.fields[key].initial = value


class BoardAccessForm(forms.Form):
    grant_type = forms.ChoiceField(
        label="Tipo de acesso",
        choices=[
            ("user", "Usuário"),
            ("designation", "Designação"),
            ("customer_gai", "Cliente (GAI)"),
            ("group", "Grupo Django"),
        ],
        widget=forms.Select(attrs={"class": "form-control", "id": "grant_type"}),
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
    customer_gai_id = forms.IntegerField(
        label="Cliente (GAI)",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    group_id = forms.IntegerField(
        label="Grupo",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    access_level = forms.ChoiceField(
        label="Nível de acesso",
        choices=[
            ("viewer", "Visualizador"),
            ("commenter", "Comentarista"),
            ("editor", "Editor"),
            ("manager", "Gerente"),
            ("owner", "Proprietário"),
        ],
        initial="viewer",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, lookups=None, **kwargs):
        super().__init__(*args, **kwargs)
        lookups = lookups or {}
        self.fields["user_id"].widget = forms.Select(
            choices=self._choices_from(lookups.get("users", []), "id", ("username", "name")),
            attrs={"class": "form-control"},
        )
        self.fields["designation_id"].widget = forms.Select(
            choices=self._choices_from(lookups.get("designations", []), "id", ("label", "username")),
            attrs={"class": "form-control"},
        )
        self.fields["customer_gai_id"].widget = forms.Select(
            choices=self._choices_from(lookups.get("gais", []), "id", ("nome", "name")),
            attrs={"class": "form-control"},
        )
        self.fields["group_id"].widget = forms.Select(
            choices=self._choices_from(lookups.get("groups", []), "id", ("name",)),
            attrs={"class": "form-control"},
        )

    def _choices_from(self, items, id_key, label_keys):
        choices = [("", "---------")]
        for item in items:
            item_id = item.get(id_key)
            label = next((item.get(k) for k in label_keys if item.get(k)), None)
            if item_id is not None:
                choices.append((item_id, label or str(item_id)))
        return choices

    def clean(self):
        cleaned = super().clean()
        grant_type = cleaned.get("grant_type")
        field_map = {
            "user": "user_id",
            "designation": "designation_id",
            "customer_gai": "customer_gai_id",
            "group": "group_id",
        }
        required_field = field_map.get(grant_type)
        if required_field and not cleaned.get(required_field):
            self.add_error(required_field, "Selecione um valor.")
        return cleaned


class BoardColumnForm(forms.Form):
    name = forms.CharField(
        label="Nome da coluna",
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    status_task_id = forms.IntegerField(
        label="Status",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    position = forms.IntegerField(
        label="Posição",
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, lookups=None, **kwargs):
        super().__init__(*args, **kwargs)
        lookups = lookups or {}
        status_choices = [("", "---------")]
        for st in lookups.get("status_tasks", []):
            st_id = st.get("id")
            label = st.get("name") or st.get("nome") or str(st_id)
            if st_id is not None:
                status_choices.append((st_id, label))
        self.fields["status_task_id"].widget = forms.Select(
            choices=status_choices,
            attrs={"class": "form-control"},
        )
