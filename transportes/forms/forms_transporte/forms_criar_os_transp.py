from django import forms


class FormCriarOsTransp(forms.Form):

    numero_os = forms.CharField(label="Número da OS", max_length=100)

    ex_order_number = forms.CharField(
        label="Número do Pedido",
        max_length=100,
        required=False
    )

    cliente = forms.ChoiceField(label="Cliente", required=True)
    origem = forms.ChoiceField(label="Origem", required=True)
    destino = forms.ChoiceField(label="Destino", required=True)

    tipo_os = forms.ChoiceField(label="Tipo de Serviço", required=True)
    status_os = forms.ChoiceField(label="Status", required=True)

    def __init__(self, *args, nome_form=None, payload=None, **kwargs):

        super().__init__(*args, **kwargs)

        self.nome_formulario = nome_form or "Criar OS"
        self.payload = payload or []

        self.fields["cliente"].choices = [("", "Selecione um cliente")]
        self.fields["tipo_os"].choices = [("", "Selecione o tipo")]
        self.fields["status_os"].choices = [("", "Selecione o status")]

        self.fields["cliente"].choices += [
            (c["id"], c["nome"]) for c in self.payload
        ]

        if not self.is_bound:
            return

        data = self.data or {}

        selected_client = data.get("cliente")
        selected_type = data.get("tipo_os")

        if selected_client:

            cliente = next(
                (c for c in self.payload if str(c["id"]) == selected_client),
                None
            )

            if cliente:

                order_types = cliente.get("OrderType", [])

                self.fields["tipo_os"].choices += [
                    (ot["id"], ot["type"])
                    for ot in order_types
                ]

                if selected_type:

                    order_type = next(
                        (
                            ot for ot in order_types
                            if str(ot["id"]) == selected_type
                        ),
                        None
                    )

                    if order_type:

                        self.fields["status_os"].choices += [
                            (st["id"], st["type"])
                            for st in order_type.get("status", [])
                        ]
