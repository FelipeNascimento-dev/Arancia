# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.db import transaction

from ..models import (
    UserProfile,
    GroupAditionalInformation,
    UserDesignation,
)


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(label="Primeiro nome", max_length=30)
    last_name = forms.CharField(label="Último nome", max_length=30)
    email = forms.EmailField(label="E-mail")
    cpf = forms.CharField(label="CPF", max_length=14)

    grupo = forms.ModelChoiceField(
        queryset=Group.objects.filter(name__startswith="arancia_"),
        required=True,
        empty_label="Selecione a Skill do usuário",
        help_text="Cuidado, o setor é usado para definir as permissões do usuário",
    )

    aditionalinformation = forms.ModelChoiceField(
        label="Informação Adicional (Grupo)",
        queryset=GroupAditionalInformation.objects.all(),
        required=True,
        empty_label="Selecione o Setor/PA",
        help_text="Selecione para definir o Setor/PA do usuário",
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        grupo_id = None
        if self.data.get("grupo"):  # POST
            grupo_id = self.data.get("grupo")
        elif self.initial.get("grupo"):  # initial
            g = self.initial.get("grupo")
            grupo_id = g.id if hasattr(g, "id") else g

        if grupo_id:
            self.fields["aditionalinformation"].queryset = GroupAditionalInformation.objects.filter(
                group_id=grupo_id)
        else:
            self.fields["aditionalinformation"].queryset = GroupAditionalInformation.objects.all()

    def clean_cpf(self):
        cpf = self.cleaned_data["cpf"]
        if UserProfile.objects.filter(cpf=cpf).exists():
            raise forms.ValidationError("CPF já cadastrado.")
        return cpf

    def clean(self):
        cleaned = super().clean()
        grupo = cleaned.get("grupo")
        gai = cleaned.get("aditionalinformation")
        if grupo and gai and gai.group_id != grupo.id:
            self.add_error("aditionalinformation",
                           "A informação adicional selecionada não pertence ao grupo escolhido.")
        return cleaned

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)

        ultimo = User.objects.filter(
            username__startswith="ARC").order_by("-id").first()
        if ultimo and ultimo.username.startswith("ARC") and ultimo.username[3:].isdigit():
            numero = int(ultimo.username[3:]) + 1
        else:
            numero = 1
        user.username = f"ARC{numero:04d}"
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

            grupo = self.cleaned_data["grupo"]
            user.groups.add(grupo)

            UserProfile.objects.update_or_create(
                user=user, defaults={"cpf": self.cleaned_data["cpf"]}
            )

            gai = self.cleaned_data["aditionalinformation"]
            UserDesignation.objects.update_or_create(
                user=user,
                defaults={"informacao_adicional": gai},
            )

        return user
