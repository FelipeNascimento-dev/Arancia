# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from ..models import UserProfile


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(label="Primeiro nome", max_length=30)
    last_name = forms.CharField(label="Último nome", max_length=30)
    email = forms.EmailField(label="E-mail")
    cpf = forms.CharField(label="CPF", max_length=14)
    grupo = forms.ModelChoiceField(
        label="Setor",
        queryset=Group.objects.filter(name__startswith="arancia_NOVO_USER_EXT")
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',
                  'cpf', 'grupo', 'password1', 'password2')

    def clean_cpf(self):
        cpf = self.cleaned_data['cpf']
        if UserProfile.objects.filter(cpf=cpf).exists():
            raise forms.ValidationError("CPF já cadastrado.")
        return cpf

    def save(self, commit=True):
        user = super().save(commit=False)

        ultimo = User.objects.filter(
            username__startswith="ARC").order_by('-id').first()
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
                user=user, defaults={"cpf": self.cleaned_data["cpf"]})
        return user
