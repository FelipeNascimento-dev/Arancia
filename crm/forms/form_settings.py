from django import forms

from crm.helpers.lookup_choices import build_select_choices


class RecurrenceEditForm(forms.Form):
    title = forms.CharField(
        label="Título",
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    description = forms.CharField(
        label="Descrição",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}),
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
        label="Início",
        required=False,
        widget=forms.DateTimeInput(
            attrs={"class": "form-control", "type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"],
    )
    recurrence_frequency = forms.ChoiceField(
        label="Frequência",
        choices=[
            ("daily", "Diária"),
            ("weekly", "Semanal"),
            ("monthly", "Mensal"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    recurrence_interval = forms.IntegerField(
        label="Intervalo",
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
    is_active = forms.BooleanField(
        label="Ativa",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    def __init__(self, *args, lookups=None, nome_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Editar recorrência"
        lookups = lookups or {}
        self._apply_select("board_id", lookups.get("boards", []), ("name", "nome"))
        self._apply_select("status_id", lookups.get("status_tasks", []), ("name", "nome"))
        self._apply_select("priority_id", lookups.get("priorities", []), ("name", "nome"))
        self._apply_select("service_type_id", lookups.get("service_types", []), ("description", "type", "name", "nome"))
        self._apply_select("project_id", lookups.get("projects", []), ("name", "nome"))
        self._apply_select("customer_gai_id", lookups.get("gais", []), ("nome", "name"))

    def _apply_select(self, field_name, items, label_keys):
        extra_id_keys = ("gai_id", "customer_gai_id") if "gai" in field_name or field_name == "client_id" else ()
        choices = build_select_choices(
            items,
            id_keys=("id", *extra_id_keys),
            label_keys=label_keys,
        )
        self.fields[field_name].widget = forms.Select(
            choices=choices,
            attrs={"class": "form-control"},
        )


class ServiceTypeForm(forms.Form):
    type = forms.CharField(
        label="Tipo (código)",
        max_length=64,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    description = forms.CharField(
        label="Descrição",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )
    status_initial_id = forms.IntegerField(
        label="Status inicial",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    client_id = forms.IntegerField(
        label="Cliente (GAI)",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    direction = forms.ChoiceField(
        label="Direção",
        required=False,
        choices=[
            ("", "---------"),
            ("inbound", "Entrada"),
            ("outbound", "Saída"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
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
        self.fields["status_initial_id"].widget = forms.Select(
            choices=status_choices,
            attrs={"class": "form-control"},
        )
        self.fields["client_id"].widget = forms.Select(
            choices=build_select_choices(
                lookups.get("gais", []),
                id_keys=("id", "gai_id", "customer_gai_id", "client_id"),
                label_keys=("nome", "name", "razao_social"),
            ),
            attrs={"class": "form-control"},
        )


class PriorityForm(forms.Form):
    name = forms.CharField(
        label="Nome",
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    color = forms.CharField(
        label="Cor (hex)",
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "#ff0000"}),
    )
    sort_order = forms.IntegerField(
        label="Ordem",
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    is_active = forms.BooleanField(
        label="Ativo",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )


class StatusTaskForm(forms.Form):
    name = forms.CharField(
        label="Nome",
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    color = forms.CharField(
        label="Cor (hex)",
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "#cccccc"}),
    )
    sort_order = forms.IntegerField(
        label="Ordem",
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    is_terminal = forms.BooleanField(
        label="Status final",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    is_active = forms.BooleanField(
        label="Ativo",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
