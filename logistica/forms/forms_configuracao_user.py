from django import forms
from django.contrib.auth.models import User


class ConfiguracaoUserForm(forms.ModelForm):
    username = forms.CharField(
        label="Username", max_length=30, required=True)
    first_name = forms.CharField(
        label="Primeiro nome", max_length=30, required=False)
    last_name = forms.CharField(
        label="Último nome", max_length=30, required=False)
    email = forms.EmailField(label="E-mail", required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        qs = User.objects.filter(
            email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Este e-mail já está em uso.")
        return email
