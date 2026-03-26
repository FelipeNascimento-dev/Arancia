from django import forms
from django.db.models import Q
from django.db.models.functions import Lower
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

    created_at = forms.DateField(
        label="Data de criação",
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

    def __init__(self, *args, nome_form=None, payload=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.nome_formulario = nome_form or "Consulta de OS"
        self.payload = payload or []

        self.fields["client"].choices = [("", "Selecione um cliente")]
        self.fields["order_type"].choices = []
        self.fields["status"].choices = []

        self.fields["client"].choices += [
            (str(c["id"]), c["nome"]) for c in self.payload
        ]

        pa_choices = [("", "Selecione uma PA")]
        pa_qs = (
            GroupAditionalInformation.objects
            .filter(
                Q(group__name="arancia_PA") |
                Q(group__name="arancia_TRANSPORT", nome="C-TRENDS")
            )
            .annotate(nome_lower=Lower("nome"))
            .order_by("nome_lower")
            .values_list("id", "nome")
            .distinct()
        )
        pa_choices += [(str(pa_id), nome) for pa_id, nome in pa_qs]
        self.fields["pa_selecionada"].choices = pa_choices

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
                    stype = st["type"]

                    if sid not in vistos:
                        vistos.add(sid)
                        status_unicos.append((sid, stype))

            self.fields["status"].choices = status_unicos

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.HiddenInput):
                continue

            css = "filter-input"
            if isinstance(field.widget, forms.Select):
                css = "filter-select"
            field.widget.attrs["class"] = css
