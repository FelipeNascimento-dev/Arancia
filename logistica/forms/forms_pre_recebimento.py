from django import forms

_PLACEHOLDER = [("", "")]

class PreRecebimentoForm(forms.Form):
    id = forms.CharField(label='ID', max_length=20, required=True)

    centro_origem   = forms.ChoiceField(label='Centro (Origem)', choices=_PLACEHOLDER, required=True)
    deposito_origem = forms.ChoiceField(label='Depósito (Origem)', choices=_PLACEHOLDER, required=True)

    qtde_vol = forms.IntegerField(label='Qtde de Volumes', min_value=1, required=True)
    
    centro_destino   = forms.ChoiceField(label='Centro (Destino)', choices=_PLACEHOLDER, required=True)
    deposito_destino = forms.ChoiceField(label='Depósito (Destino)', choices=_PLACEHOLDER, required=True)

    def __init__(
        self, *args, nome_form=None,
        centro_choices=None,
        deposito_choices_origem=None,
        deposito_choices_destino=None,
        depositos_by_centro=None,  # para validar
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Pré-Recebimento"

        self.fields["centro_origem"].choices   = _PLACEHOLDER + list(centro_choices or [])
        self.fields["centro_destino"].choices  = _PLACEHOLDER + list(centro_choices or [])
        self.fields["deposito_origem"].choices = _PLACEHOLDER + list(deposito_choices_origem or [])
        self.fields["deposito_destino"].choices= _PLACEHOLDER + list(deposito_choices_destino or [])

        self._depositos_by_centro = depositos_by_centro or {}

    def clean(self):
        cleaned = super().clean()
        for par in (("centro_origem","deposito_origem"), ("centro_destino","deposito_destino")):
            c = cleaned.get(par[0]); d = cleaned.get(par[1])
            if c and d and self._depositos_by_centro:
                valid = {code for code, _ in self._depositos_by_centro.get(c, [])}
                if d not in valid:
                    self.add_error(par[1], "Depósito não pertence ao centro selecionado.")
        return cleaned