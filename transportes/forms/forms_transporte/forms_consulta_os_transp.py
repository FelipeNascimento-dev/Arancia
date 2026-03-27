from django import forms
from django.db.models import Q
from logistica.models import GroupAditionalInformation


class ConsultaOStranspForm(forms.Form):
    client = forms.ChoiceField(label="Cliente", required=False)

    numero_os = forms.CharField(
        label="Insira o número da OS (Opcional)", required=False
    )

    order_type = forms.MultipleChoiceField(
        label="Tipo de OS",
        required=False,
        widget=forms.SelectMultiple
    )

    status = forms.MultipleChoiceField(
        label="Status da OS (Opcional)",
        required=False,
        widget=forms.SelectMultiple
    )

    data_inicial = forms.DateField(
        label="Data inicial",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    data_final = forms.DateField(
        label="Data final",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    tipo_os = forms.ChoiceField(
        label="Consultar por",
        choices=[("IN", "OS Interna"), ("EX", "OS Externa")],
        widget=forms.RadioSelect,
        required=False,
    )

    pa_selecionada = forms.ChoiceField(
        label="PA Responsável",
        choices=[],
        required=False
    )

    origem = forms.ChoiceField(
        label="Origem",
        choices=[],
        required=False
    )

    destino = forms.ChoiceField(
        label="Destino",
        choices=[],
        required=False
    )

    def __init__(self, *args, nome_form=None, payload=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.nome_formulario = nome_form or "Consulta de OS"
        self.payload = payload or []

        self.fields["client"].choices = [("", "Selecione um cliente")]
        self.fields["order_type"].choices = []
        self.fields["status"].choices = []
        self.fields["origem"].choices = [("", "Selecione a origem")]
        self.fields["destino"].choices = [("", "Selecione o destino")]

        self.fields["client"].choices += [
            (str(c["id"]), c["nome"]) for c in self.payload
        ]

        pa_qs = (
            GroupAditionalInformation.objects
            .filter(
                Q(group__name="arancia_PA") |
                Q(group__name="arancia_TRANSPORT", nome="C-TRENDS")
            )
            .select_related("group")
            .order_by("nome")
            .distinct()
        )

        pa_choices = [("", "Selecione uma PA")]
        pa_choices += [(str(pa.id), pa.nome) for pa in pa_qs]
        self.fields["pa_selecionada"].choices = pa_choices

        locais_qs = (
            GroupAditionalInformation.objects
            .filter(
                Q(group__name="arancia_PA") |
                Q(group__name="arancia_CD") |
                Q(group__name="arancia_CUSTOMER")
            )
            .select_related("group")
            .order_by("nome")
            .distinct()
        )

        def formatar_label(g):
            prefix = g.group.name.replace("arancia_", "")
            return f"[{prefix}] {g.nome}"

        base_choices = [(str(g.id), formatar_label(g))
                        for g in locais_qs[:100]]
        self.fields["origem"].choices += base_choices
        self.fields["destino"].choices += base_choices

        origem_id = None
        destino_id = None

        if self.is_bound:
            origem_id = self.data.get("origem")
            destino_id = self.data.get("destino")
        else:
            origem_id = self.initial.get("origem")
            destino_id = self.initial.get("destino")

        ids_extra = [x for x in [origem_id, destino_id] if x]

        if ids_extra:
            extras = (
                GroupAditionalInformation.objects
                .filter(id__in=ids_extra)
                .select_related("group")
            )

            extras_choices = [(str(g.id), formatar_label(g)) for g in extras]

            existentes_origem = {valor for valor,
                                 _ in self.fields["origem"].choices}
            existentes_destino = {valor for valor,
                                  _ in self.fields["destino"].choices}

            for valor, label in extras_choices:
                if valor not in existentes_origem:
                    self.fields["origem"].choices.append((valor, label))
                if valor not in existentes_destino:
                    self.fields["destino"].choices.append((valor, label))

        selected_client = None
        selected_client_id = None

        if self.is_bound:
            selected_client_id = self.data.get("client")
        else:
            selected_client_id = self.initial.get("client")

        if selected_client_id:
            selected_client = next(
                (c for c in self.payload if str(
                    c["id"]) == str(selected_client_id)),
                None
            )

        if selected_client:
            order_types = selected_client.get("OrderType", [])

            self.fields["order_type"].choices = [
                (str(ot["id"]), ot["type"])
                for ot in order_types
            ]

            status_unicos = []
            vistos = set()

            for ot in order_types:
                for st in ot.get("status", []):
                    sid = str(st["id"])
                    stype = (st.get("type") or "").strip()

                    if not stype:
                        continue

                    chave = stype.lower()
                    if chave not in vistos:
                        vistos.add(chave)
                        status_unicos.append((sid, stype))

            self.fields["status"].choices = status_unicos

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.HiddenInput):
                continue

            css = "filter-input"
            if isinstance(field.widget, forms.Select):
                css = "filter-select"
            field.widget.attrs["class"] = css
