from django import forms


class ListaViagensForm(forms.Form):
    cliente = forms.ChoiceField(label='Cliente', choices=[], required=False)
    transportadora = forms.ChoiceField(
        label='Transportadora', choices=[], required=False)

    def __init__(self, *args, nome_form=None, clientes=None, transportadoras=None, **kwargs):
        self.nome_formulario = nome_form or "Definir nome do formulário"
        super().__init__(*args, **kwargs)

        clientes = clientes or []
        cliente_choices = [("", "Selecione um cliente")]

        for c in clientes:
            if not isinstance(c, dict):
                continue
            value = c.get("id") or c.get(
                "codigo") or c.get("value") or c.get("nome")
            label = c.get("nome") or c.get("label") or c.get(
                "razao_social") or str(value)

            if value is not None:
                cliente_choices.append((str(value), str(label)))

        self.fields["cliente"].choices = cliente_choices

        transportadoras = transportadoras or []
        transportadora_choices = [("", "Selecione uma transportadora")]

        for t in transportadoras:
            if not isinstance(t, dict):
                continue
            value = t.get("id") or t.get(
                "codigo") or t.get("value") or t.get("nome")
            label = t.get("nome") or t.get("label") or t.get(
                "razao_social") or str(value)

            if value is not None:
                transportadora_choices.append((str(value), str(label)))

        self.fields["transportadora"].choices = transportadora_choices
