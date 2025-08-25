# forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class ConfiguracaoUserForm(forms.ModelForm):
    username = forms.CharField(
        label="Username", max_length=30, required=False, disabled=True)
    email = forms.EmailField(label="E-mail", required=True)
    first_name = forms.CharField(
        label="Primeiro nome", max_length=30, required=False)
    last_name = forms.CharField(
        label="Último nome", max_length=30, required=False)

    senha_atual = forms.CharField(
        label="Senha atual",
        required=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "off"}),
    )
    nova_senha1 = forms.CharField(
        label="Nova senha",
        required=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    nova_senha2 = forms.CharField(
        label="Confirmar nova senha",
        required=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    foto_perfil = forms.ImageField(label="Foto do perfil", required=False)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        qs = User.objects.filter(
            email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Este e-mail já está em uso.")
        return email

    def clean(self):
        cleaned = super().clean()
        senha_atual = cleaned.get("senha_atual") or ""
        nova1 = cleaned.get("nova_senha1") or ""
        nova2 = cleaned.get("nova_senha2") or ""

        if not any([senha_atual, nova1, nova2]):
            return cleaned

        if not senha_atual:
            self.add_error("senha_atual", "Informe a senha atual.")
        if not nova1:
            self.add_error("nova_senha1", "Informe a nova senha.")
        if not nova2:
            self.add_error("nova_senha2", "Confirme a nova senha.")
        if self.errors:
            return cleaned

        if not self.instance.check_password(senha_atual):
            self.add_error("senha_atual", "Senha atual incorreta.")
            return cleaned

        if nova1 != nova2:
            self.add_error(
                "nova_senha2", "A confirmação não coincide com a nova senha.")
            return cleaned

        if senha_atual == nova1:
            self.add_error(
                "nova_senha1", "A nova senha não pode ser igual à atual.")
            return cleaned

        try:
            validate_password(nova1, self.instance)
        except forms.ValidationError as e:
            self.add_error("nova_senha1", e.messages)

        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        nova1 = self.cleaned_data.get("nova_senha1") or ""
        senha_atual = self.cleaned_data.get("senha_atual") or ""
        self._password_changed = False

        if nova1 and senha_atual and not self.errors:
            user.set_password(nova1)
            self._password_changed = True

        if commit:
            user.save()
        return user

    def password_changed(self) -> bool:
        return getattr(self, "_password_changed", False)
