from django import forms

from crm.helpers.lookup_choices import build_select_choices, build_user_choices


_TASK_DESCRIPTION_WIDGET = forms.Textarea(
    attrs={
        "class": "form-control crm-task-description-input",
        "id": "taskCreateDescription",
        "rows": 5,
    },
)


class UnifiedTaskForm(forms.Form):
    title = forms.CharField(
        label="Título",
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    description = forms.CharField(
        label="Descrição",
        required=False,
        widget=_TASK_DESCRIPTION_WIDGET,
    )
    board_id = forms.IntegerField(
        label="Board",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    status_id = forms.IntegerField(
        label="Status",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    priority_id = forms.IntegerField(
        label="Prioridade",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    service_type_id = forms.IntegerField(
        label="Tipo de serviço",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    project_id = forms.IntegerField(
        label="Projeto",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    customer_gai_id = forms.IntegerField(
        label="Cliente (GAI)",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    scheduled_start_at = forms.DateTimeField(
        label="Início agendado",
        required=False,
        widget=forms.DateTimeInput(
            attrs={"class": "form-control", "type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"],
    )
    scheduled_end_at = forms.DateTimeField(
        label="Fim agendado",
        required=False,
        widget=forms.DateTimeInput(
            attrs={"class": "form-control", "type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"],
    )
    due_at = forms.DateTimeField(
        label="Prazo",
        required=False,
        widget=forms.DateTimeInput(
            attrs={"class": "form-control", "type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"],
    )
    is_recurring = forms.BooleanField(
        label="Task recorrente",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input", "id": "is_recurring"}),
    )
    recurrence_frequency = forms.ChoiceField(
        label="Frequência",
        required=False,
        choices=[
            ("", "---------"),
            ("daily", "Diária"),
            ("weekly", "Semanal"),
            ("monthly", "Mensal"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    recurrence_interval = forms.IntegerField(
        label="Intervalo",
        required=False,
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    recurrence_end_at = forms.DateTimeField(
        label="Fim da recorrência",
        required=False,
        widget=forms.DateTimeInput(
            attrs={"class": "form-control", "type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"],
    )
    requester_gai_ids = forms.MultipleChoiceField(
        label="Demandantes (GAI)",
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-control", "size": 4}),
    )

    def __init__(self, *args, lookups=None, nome_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Nova Task"
        lookups = lookups or {}
        self._set_choices("board_id", lookups.get("boards", []), "id", ("name", "nome", "title"))
        self._set_choices("status_id", lookups.get("status_tasks", []), "id", ("name", "nome", "label"))
        self._set_choices("priority_id", lookups.get("priorities", []), "id", ("name", "nome", "label"))
        self._set_choices("service_type_id", lookups.get("service_types", []), "id", ("description", "type", "name", "nome", "label"))
        self._set_choices("project_id", lookups.get("projects", []), "id", ("name", "nome", "title"))
        self._set_choices("customer_gai_id", lookups.get("gais", []), "id", ("nome", "name"))
        self.fields["requester_gai_ids"].choices = build_select_choices(
            lookups.get("gais", []),
            id_keys=("id", "gai_id", "customer_gai_id"),
            label_keys=("nome", "name"),
            as_str=True,
        )

    def _set_choices(self, field_name, items, id_key, label_keys):
        extra_id_keys = ("gai_id", "customer_gai_id") if "gai" in field_name else ()
        choices = build_select_choices(
            items,
            id_keys=(id_key, *extra_id_keys),
            label_keys=label_keys,
        )
        self.fields[field_name].widget = forms.Select(
            choices=choices,
            attrs={"class": "form-control"},
        )
        self.fields[field_name].required = field_name == "board_id"

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("is_recurring"):
            if not cleaned.get("recurrence_frequency"):
                self.add_error("recurrence_frequency", "Informe a frequência da recorrência.")
            if not cleaned.get("scheduled_start_at"):
                self.add_error("scheduled_start_at", "Informe o início para tasks recorrentes.")
            if not cleaned.get("status_id"):
                self.add_error("status_id", "Status é obrigatório para recorrências.")
            if not cleaned.get("priority_id"):
                self.add_error("priority_id", "Prioridade é obrigatória para recorrências.")
        requester_ids = cleaned.get("requester_gai_ids")
        if requester_ids:
            cleaned["requester_gai_ids"] = [int(x) for x in requester_ids]
        return cleaned


_SELECT_CLASS = "form-control"
_SEARCH_SELECT_CLASS = "form-control js-crm-search-select"


class TaskListModalForm(forms.Form):
    """Formulário modal na listagem de tasks (/crm/tasks/)."""

    title = forms.CharField(
        label="Título",
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
    )
    description = forms.CharField(
        label="Descrição",
        required=False,
        widget=_TASK_DESCRIPTION_WIDGET,
    )
    board_id = forms.ChoiceField(
        label="Board",
        choices=[("", "---------")],
        widget=forms.Select(attrs={"class": _SELECT_CLASS}),
    )
    status_id = forms.ChoiceField(
        label="Status",
        choices=[("", "---------")],
        widget=forms.Select(attrs={"class": _SELECT_CLASS}),
    )
    priority_id = forms.ChoiceField(
        label="Prioridade",
        required=False,
        choices=[("", "---------")],
        widget=forms.Select(attrs={"class": _SELECT_CLASS}),
    )
    service_type_id = forms.ChoiceField(
        label="Tipo de serviço",
        required=False,
        choices=[("", "---------")],
        widget=forms.Select(attrs={"class": _SELECT_CLASS}),
    )
    project_id = forms.ChoiceField(
        label="Projeto",
        required=False,
        choices=[("", "---------")],
        widget=forms.Select(attrs={"class": _SELECT_CLASS}),
    )
    customer_gai_id = forms.ChoiceField(
        label="Cliente (GAI)",
        required=False,
        choices=[("", "---------")],
        widget=forms.Select(attrs={"class": _SEARCH_SELECT_CLASS}),
    )
    assignee_user_id = forms.ChoiceField(
        label="Responsável (usuário)",
        required=False,
        choices=[("", "---------")],
        widget=forms.Select(attrs={"class": _SEARCH_SELECT_CLASS}),
    )
    assignee_customer_gai_id = forms.ChoiceField(
        label="Responsável (GAI)",
        required=False,
        choices=[("", "---------")],
        widget=forms.Select(attrs={"class": _SEARCH_SELECT_CLASS}),
    )
    due_at = forms.DateTimeField(
        label="Prazo",
        required=False,
        widget=forms.DateTimeInput(
            attrs={"class": "form-control", "type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"],
    )

    def __init__(self, *args, lookups=None, **kwargs):
        super().__init__(*args, **kwargs)
        lookups = lookups or {}
        self._set_choices("board_id", lookups.get("boards", []), "id", ("name", "nome", "title"))
        self._set_choices("status_id", lookups.get("status_tasks", []), "id", ("name", "nome", "label"))
        self._set_choices("priority_id", lookups.get("priorities", []), "id", ("name", "nome", "label"))
        self._set_choices(
            "service_type_id",
            lookups.get("service_types", []),
            "id",
            ("description", "type", "name", "nome", "label"),
        )
        self._set_choices("project_id", lookups.get("projects", []), "id", ("name", "nome", "title"))
        self._set_choices("customer_gai_id", lookups.get("gais", []), "id", ("nome", "name"))
        self._set_user_choices("assignee_user_id", lookups.get("users", []))
        self._set_choices(
            "assignee_customer_gai_id",
            lookups.get("gais", []),
            "id",
            ("nome", "name"),
        )
        self.fields["board_id"].required = True
        self.fields["status_id"].required = True

    def _set_user_choices(self, field_name, items):
        self.fields[field_name].choices = build_user_choices(items)

    def _set_choices(self, field_name, items, id_key, label_keys):
        extra_id_keys = ("gai_id",) if field_name.endswith("gai_id") or "gai" in field_name else ()
        self.fields[field_name].choices = build_select_choices(
            items,
            id_keys=(id_key, *extra_id_keys),
            label_keys=label_keys,
            as_str=True,
        )


class ComercialTaskModalForm(forms.Form):
    """Formulário enxuto para criação de task no Kanban comercial (modal)."""

    title = forms.CharField(
        label="Título",
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
    )
    description = forms.CharField(
        label="Descrição",
        required=False,
        widget=_TASK_DESCRIPTION_WIDGET,
    )
    status_id = forms.ChoiceField(
        label="Status",
        choices=[("", "---------")],
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    priority_id = forms.ChoiceField(
        label="Prioridade",
        required=False,
        choices=[("", "---------")],
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    customer_gai_id = forms.ChoiceField(
        label="Cliente (GAI)",
        required=False,
        choices=[("", "---------")],
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    due_at = forms.DateTimeField(
        label="Prazo",
        required=False,
        widget=forms.DateTimeInput(
            attrs={"class": "form-control", "type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"],
    )
    board_id = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, lookups=None, board_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        lookups = lookups or {}
        if board_id not in (None, ""):
            self.fields["board_id"].initial = board_id
        self._set_choices("status_id", lookups.get("status_tasks", []), "id", ("name", "nome", "label"))
        self._set_choices("priority_id", lookups.get("priorities", []), "id", ("name", "nome", "label"))
        self._set_choices("customer_gai_id", lookups.get("gais", []), "id", ("nome", "name"))
        self.fields["status_id"].required = True

    def _set_choices(self, field_name, items, id_key, label_keys):
        extra_id_keys = ("gai_id", "customer_gai_id") if "gai" in field_name else ()
        self.fields[field_name].choices = build_select_choices(
            items,
            id_keys=(id_key, *extra_id_keys),
            label_keys=label_keys,
            as_str=True,
        )


class TaskEditForm(forms.Form):
    title = forms.CharField(
        label="Título",
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    description = forms.CharField(
        label="Descrição",
        required=False,
        widget=_TASK_DESCRIPTION_WIDGET,
    )
    board_id = forms.IntegerField(
        label="Board",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    status_id = forms.IntegerField(
        label="Status",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    priority_id = forms.IntegerField(
        label="Prioridade",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    project_id = forms.IntegerField(
        label="Projeto",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    customer_gai_id = forms.IntegerField(
        label="Cliente (GAI)",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    scheduled_start_at = forms.DateTimeField(
        label="Início agendado",
        required=False,
        widget=forms.DateTimeInput(
            attrs={"class": "form-control", "type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"],
    )
    scheduled_end_at = forms.DateTimeField(
        label="Fim agendado",
        required=False,
        widget=forms.DateTimeInput(
            attrs={"class": "form-control", "type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"],
    )
    due_at = forms.DateTimeField(
        label="Prazo",
        required=False,
        widget=forms.DateTimeInput(
            attrs={"class": "form-control", "type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"],
    )
    requester_gai_ids = forms.MultipleChoiceField(
        label="Demandantes (GAI)",
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-control", "size": 4}),
    )

    def __init__(self, *args, lookups=None, nome_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Editar Task"
        lookups = lookups or {}
        self._set_choices("board_id", lookups.get("boards", []), "id", ("name", "nome", "title"))
        self._set_choices("status_id", lookups.get("status_tasks", []), "id", ("name", "nome", "label"))
        self._set_choices("priority_id", lookups.get("priorities", []), "id", ("name", "nome", "label"))
        self._set_choices("project_id", lookups.get("projects", []), "id", ("name", "nome", "title"))
        self._set_choices("customer_gai_id", lookups.get("gais", []), "id", ("nome", "name"))
        self.fields["requester_gai_ids"].choices = build_select_choices(
            lookups.get("gais", []),
            id_keys=("id", "gai_id", "customer_gai_id"),
            label_keys=("nome", "name"),
            as_str=True,
        )

    def _set_choices(self, field_name, items, id_key, label_keys):
        extra_id_keys = ("gai_id", "customer_gai_id") if "gai" in field_name else ()
        choices = build_select_choices(
            items,
            id_keys=(id_key, *extra_id_keys),
            label_keys=label_keys,
        )
        self.fields[field_name].widget = forms.Select(
            choices=choices,
            attrs={"class": "form-control"},
        )
        self.fields[field_name].required = field_name == "board_id"

    def clean(self):
        cleaned = super().clean()
        requester_ids = cleaned.get("requester_gai_ids")
        if requester_ids:
            cleaned["requester_gai_ids"] = [int(x) for x in requester_ids]
        return cleaned


class TaskCommentForm(forms.Form):
    body = forms.CharField(
        label="Comentário",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )


class TaskSubtaskForm(forms.Form):
    title = forms.CharField(
        label="Título",
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )


class TaskLinkForm(forms.Form):
    target_task_id = forms.IntegerField(
        label="Task vinculada (ID)",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    link_type = forms.ChoiceField(
        label="Tipo de vínculo",
        choices=[
            ("related", "Relacionada"),
            ("blocks", "Bloqueia"),
            ("blocked_by", "Bloqueada por"),
            ("duplicates", "Duplica"),
        ],
        initial="related",
        widget=forms.Select(attrs={"class": "form-control"}),
    )


class TaskAssigneeForm(forms.Form):
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

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("user_id") and not cleaned.get("designation_id"):
            raise forms.ValidationError("Informe usuário ou designação.")
        return cleaned
