from django import forms


class BuscarOSForm(forms.Form):
    os_number = forms.CharField(
       
       label="Numero da OS",
       max_length=255,
       required=True,
       widget=forms.TextInput(attrs={"placeholder":"Digite a OS"})
   )
    def __init__(self, *args, nome_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nome_formulario = nome_form or "Definir nome do formulário"
   