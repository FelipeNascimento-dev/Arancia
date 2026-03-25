from django import forms


class ConsultaOStranspForm(forms.Form):
    client = forms.ChoiceField(label="Cliente", required=False)

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

    numero_os = forms.CharField(
        label="Insira o número da OS (Opcional)", required=False
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

    def __init__(self, *args, nome_form=None, payload=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.nome_formulario = nome_form or "Consulta de OS"
        self.payload = payload or []

        self.fields["client"].choices = [("", "Selecione um cliente")]
        self.fields["order_type"].choices = []
        self.fields["status"].choices = []

        self.fields["client"].choices += [
            (c["id"], c["nome"]) for c in self.payload
        ]

        if not self.is_bound:
            return

        selected_client = self.data.get("client")
        selected_types = self.data.getlist("order_type")

        if selected_client:
            cliente = next(
                (c for c in self.payload if str(
                    c["id"]) == str(selected_client)),
                None,
            )

            if cliente:
                order_types = cliente.get("OrderType", [])

                self.fields["order_type"].choices = [
                    (str(ot["id"]), ot["type"])
                    for ot in order_types
                ]

                status_choices = []
                for ot in order_types:
                    if str(ot["id"]) in [str(x) for x in selected_types]:
                        status_choices.extend([
                            (str(st["id"]), st["type"])
                            for st in ot.get("status", [])
                        ])

                # remove duplicados
                vistos = set()
                status_unicos = []
                for sid, stype in status_choices:
                    if sid not in vistos:
                        vistos.add(sid)
                        status_unicos.append((sid, stype))

                self.fields["status"].choices = status_unicos
