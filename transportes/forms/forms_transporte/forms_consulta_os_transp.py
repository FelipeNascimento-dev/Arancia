from django import forms


class ConsultaOStranspForm(forms.Form):
    client = forms.ChoiceField(label="Cliente", required=False)
    order_type = forms.ChoiceField(label="Tipo de OS", required=False)
    status = forms.ChoiceField(label="Status da OS", required=False)
    numero_os = forms.CharField(
        label="Insira o número da OS (Opcional)", required=False)

    tipo_os = forms.ChoiceField(
        label="Consultar por",
        choices=[("IN", "OS Interna"), ("EX", "OS Externa")],
        widget=forms.RadioSelect,
        initial="IN",
        required=False,
    )

    def __init__(self, *args, nome_form=None, payload=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.nome_formulario = nome_form or "Consulta de OS"
        self.payload = payload or []

        self.fields["client"].choices = [("", "Selecione um cliente")]
        self.fields["order_type"].choices = [("", "Selecione o tipo")]
        self.fields["status"].choices = [("", "Selecione o status")]

        self.fields["client"].choices += [
            (c["id"], c["nome"]) for c in self.payload
        ]

        if not self.is_bound:
            return

        selected_client = self.data.get("client")
        selected_type = self.data.get("order_type")

        if selected_client:
            cliente = next(
                (c for c in self.payload if str(c["id"]) == selected_client),
                None,
            )

            if cliente:
                order_types = cliente.get("OrderType", [])

                self.fields["order_type"].choices += [
                    (ot["id"], ot["type"])
                    for ot in order_types
                ]

                if selected_type:
                    order_type = next(
                        (
                            ot for ot in order_types
                            if str(ot["id"]) == selected_type
                        ),
                        None,
                    )

                    if order_type:
                        self.fields["status"].choices += [
                            (st["id"], st["type"])
                            for st in order_type.get("status", [])
                        ]
