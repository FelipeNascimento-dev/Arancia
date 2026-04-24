from django import forms
from django.contrib.auth import authenticate, password_validation, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import check_password
from django.db.models import Q

from logistica.models import PasswordResetAccessCode, UserPasswordControl

User = get_user_model()


class LoginComCodigoForm(AuthenticationForm):
    username = forms.CharField(label="Usuário ou e-mail")

    def clean(self):
        print(">>> LoginComCodigoForm FOI CHAMADO")

        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        print(">>> username digitado:", username)
        print(">>> senha/codigo digitado:", password)

        if username is None or password is None:
            return self.cleaned_data

        username = str(username).strip()
        password = str(password).strip()

        user = authenticate(
            self.request,
            username=username,
            password=password
        )

        if user is not None:
            print(">>> Login normal OK")

            self.confirm_login_allowed(user)
            self.user_cache = user
            return self.cleaned_data

        print(">>> Login normal falhou. Tentando código único...")

        user_codigo = User.objects.filter(
            Q(username__iexact=username) | Q(email__iexact=username),
            is_active=True
        ).first()

        print(">>> usuário encontrado para código:", user_codigo)

        if user_codigo:
            codigo = PasswordResetAccessCode.objects.filter(
                user=user_codigo,
                used=False
            ).order_by("-created_at").first()

            print(">>> código encontrado:", codigo)

            if codigo:
                print(">>> código usado:", codigo.used)
                print(">>> código expirado:", codigo.is_expired())
                print(">>> código válido:", codigo.is_valid())
                print(">>> código confere:", check_password(
                    password, codigo.code_hash))

            if codigo and codigo.is_valid() and check_password(password, codigo.code_hash):
                print(">>> Código único OK")

                codigo.used = True
                codigo.save(update_fields=["used"])

                control, _ = UserPasswordControl.objects.get_or_create(
                    user=user_codigo
                )

                control.force_change_password = True
                control.save(update_fields=["force_change_password"])

                self.request.session["allow_password_change_without_current"] = True
                self.request.session.modified = True

                self.confirm_login_allowed(user_codigo)
                self.user_cache = user_codigo

                return self.cleaned_data

        print(">>> Código único falhou")

        raise self.get_invalid_login_error()


class UserProfilePasswordForm(forms.ModelForm):
    senha_atual = forms.CharField(
        label="Senha atual",
        required=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Senha atual"
        })
    )

    nova_senha1 = forms.CharField(
        label="Nova senha",
        required=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Nova senha"
        })
    )

    nova_senha2 = forms.CharField(
        label="Confirmar nova senha",
        required=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirmar nova senha"
        })
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
        ]

        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.password_required = kwargs.pop("password_required", False)
        self.allow_without_current_password = kwargs.pop(
            "allow_without_current_password",
            False
        )
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        senha_atual = cleaned_data.get("senha_atual")
        nova_senha1 = cleaned_data.get("nova_senha1")
        nova_senha2 = cleaned_data.get("nova_senha2")

        quer_alterar_senha = bool(senha_atual or nova_senha1 or nova_senha2)

        if self.password_required:
            quer_alterar_senha = True

        if quer_alterar_senha:
            if not self.allow_without_current_password:
                if not senha_atual:
                    self.add_error("senha_atual", "Informe sua senha atual.")

                elif self.user and not self.user.check_password(senha_atual):
                    self.add_error("senha_atual", "Senha atual inválida.")

            if not nova_senha1:
                self.add_error("nova_senha1", "Informe a nova senha.")

            if not nova_senha2:
                self.add_error("nova_senha2", "Confirme a nova senha.")

            if nova_senha1 and nova_senha2 and nova_senha1 != nova_senha2:
                self.add_error("nova_senha2", "As senhas não conferem.")

            if nova_senha1:
                try:
                    password_validation.validate_password(
                        nova_senha1, self.user)
                except forms.ValidationError as e:
                    self.add_error("nova_senha1", e)

        return cleaned_data
