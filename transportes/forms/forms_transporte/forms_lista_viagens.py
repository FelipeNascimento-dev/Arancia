from django import forms
from django.db.models.functions import Lower
from logistica.models import GroupAditionalInformation, Group


BOOL_CHOICES = [
    ("", "Selecione"),
    ("true", "Sim"),
    ("false", "Não"),
]


class ListaViagensForm(forms.Form):
    travel_id = forms.CharField(label="ID da Viagem", required=False)
    cliente = forms.ChoiceField(label="Cliente", choices=[], required=False)
    transportadora = forms.ChoiceField(
        label="Transportadora", choices=[], required=False)
    pa_selecionada = forms.ChoiceField(
        label="PA Responsável", choices=[], required=False)

    tipo_servico = forms.CharField(
        label="Tipo de Serviço",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Ex: Tipo1,Tipo2,Tipo3"})
    )
    driver_id = forms.CharField(label="Motorista", required=False)
    status_id = forms.CharField(label="Status ID", required=False)
    sem_motorista = forms.ChoiceField(
        label="Sem motorista",
        required=False,
        choices=BOOL_CHOICES
    )

    status_list = forms.CharField(
        label="Lista de Status",
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Ex: status1,status2,status3"})
    )
    cep_origin = forms.CharField(
        label="CEP Origem",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Ex: cep1,cep2"})
    )
    cep_destin = forms.CharField(
        label="CEP Destino",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Ex: cep1,cep2"})
    )
    offset = forms.CharField(label="Offset", required=False)
    limit = forms.CharField(label="Limite", required=False)
    created_at = forms.DateField(
        label="Criado em",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"})
    )
    designation_id = forms.CharField(label="Designation ID", required=False)

    def __init__(
        self,
        *args,
        nome_form=None,
        clientes=None,
        transportadoras=None,
        user=None,
        **kwargs
    ):
        self.nome_formulario = nome_form or "Definir nome do formulário"
        self.user = user
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

        pa_choices = [("", "Selecione uma PA")]

        try:
            grupo_pa = Group.objects.get(name="arancia_PA")
            pa_qs = (
                GroupAditionalInformation.objects
                .filter(group=grupo_pa)
                .annotate(nome_lower=Lower("nome"))
                .order_by("nome_lower")
                .values_list("id", "nome")
            )
            pa_choices += [(str(pa_id), nome) for pa_id, nome in pa_qs]
        except Group.DoesNotExist:
            pass

        self.fields["pa_selecionada"].choices = pa_choices

        for field_name, field in self.fields.items():
            css = "filter-input"
            if isinstance(field.widget, forms.Select):
                css = "filter-select"
            field.widget.attrs["class"] = css
