from django import forms

class UsuarioForm(forms.Form):
    username = forms.CharField(label="Usuário", max_length=150, required=True)
    name = forms.CharField(label="Nome", max_length=150, required=True)
    pwd = forms.CharField(label="Senha", widget=forms.PasswordInput, required=True)
    pwd_confirm = forms.CharField(label="Confirmar Senha", widget=forms.PasswordInput, required=True)
    phone = forms.CharField(label="Telefone", max_length=20, required=False)
    email = forms.EmailField(label="E-mail", required=True)
    cod_base = forms.CharField(label="Código Base", required=True)
    nome_unidade = forms.CharField(label="Unidade", required=False)
    documento = forms.CharField(label="Documento", required=True)
    profile = forms.CharField(label="Projeto", required=False)

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get("pwd")
        pwd_confirm = cleaned_data.get("pwd_confirm")

        if pwd and pwd_confirm and pwd != pwd_confirm:
            self.add_error("pwd_confirm", "As senhas não coincidem.")

        return cleaned_data
