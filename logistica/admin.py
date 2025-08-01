from django.contrib import admin
from django import forms
from .models import PontoAtendimentoInfo, GroupAditionalInformation

class PontoAtendimentoInfoAdminForm(forms.ModelForm):
    limite_opcoes = [
        (50, "50 bipagens"),
        (100, "100 bipagens"),
        (150, "150 bipagens"),
        (300, "300 bipagens"),
        (500, "500 bipagens"),
        (1000, "1000 bipagens"),
    ]
    limite = forms.ChoiceField(choices=limite_opcoes, label="Limite de bipagens")

    class Meta:
        model = PontoAtendimentoInfo
        fields = '__all__'

@admin.register(PontoAtendimentoInfo)
class PontoAtendimentoInfoAdmin(admin.ModelAdmin):
    form = PontoAtendimentoInfoAdminForm
    list_display = ('group', 'endereco', 'limite', 'liberado')
    list_editable = ('liberado',)
    search_fields = ('group__name', 'endereco')

@admin.register(GroupAditionalInformation)
class GroupAditionalInformationAdmin(admin.ModelAdmin):
    list_display = ('group', 'cidade', 'estado', 'email', 'telefone1')
    search_fields = ('group__name', 'cidade', 'estado', 'email', 'responsavel')