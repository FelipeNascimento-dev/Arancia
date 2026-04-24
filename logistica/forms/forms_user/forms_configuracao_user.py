from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class ConfiguracaoUserForm(forms.ModelForm):
    username = forms.CharField(
        label="Username", max_length=30, required=False, disabled=True
    )
    email = forms.EmailField(
        label="E-mail", required=False, disabled=True
    )
    first_name = forms.CharField(
        label="Primeiro nome", max_length=30, required=False, disabled=True
    )
    last_name = forms.CharField(
        label="Último nome", max_length=30, required=False, disabled=True
    )

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

    foto_perfil = forms.URLField(label="Foto do perfil", required=False)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if not email:
            return email

        qs = User.objects.filter(
            email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Este e-mail já está em uso.")
        return email

    def clean(self):
        cleaned_data = super().clean()

        senha_atual = cleaned_data.get("senha_atual")
        nova_senha1 = cleaned_data.get("nova_senha1")
        nova_senha2 = cleaned_data.get("nova_senha2")

        quer_alterar_senha = bool(nova_senha1 or nova_senha2 or senha_atual)

        if self.password_required:
            quer_alterar_senha = True

        if quer_alterar_senha:
            if not self.allow_without_current_password:
                if not senha_atual:
                    self.add_error("senha_atual", "Informe a senha atual.")
                elif self.user and not self.user.check_password(senha_atual):
                    self.add_error("senha_atual", "Senha atual inválida.")

            if not nova_senha1:
                self.add_error("nova_senha1", "Informe a nova senha.")

            if not nova_senha2:
                self.add_error("nova_senha2", "Confirme a nova senha.")

            if nova_senha1 and nova_senha2 and nova_senha1 != nova_senha2:
                self.add_error("nova_senha2", "As senhas não conferem.")

            if nova_senha1:
                from django.contrib.auth import password_validation
                from django.core.exceptions import ValidationError

                try:
                    password_validation.validate_password(
                        nova_senha1, self.user)
                except ValidationError as e:
                    self.add_error("nova_senha1", e)

        return cleaned_data

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

    def password_changed(self):
        return bool(self.cleaned_data.get("nova_senha1"))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.password_required = kwargs.pop("password_required", False)
        self.allow_without_current_password = kwargs.pop(
            "allow_without_current_password",
            False
        )

        super().__init__(*args, **kwargs)
