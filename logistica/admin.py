from django.contrib import admin
from django import forms
from .models import PontoAtendimentoInfo, GroupAditionalInformation, UserDesignation, GroupAditionalInformationLegacy
from transportes.models import FiltroPadraoTela, FiltroFavoritoUsuario


class PontoAtendimentoInfoAdminForm(forms.ModelForm):
    limite_opcoes = [
        (50, "50 bipagens"),
        (100, "100 bipagens"),
        (150, "150 bipagens"),
        (300, "300 bipagens"),
        (500, "500 bipagens"),
        (1000, "1000 bipagens"),
    ]
    limite = forms.ChoiceField(
        choices=limite_opcoes, label="Limite de bipagens")

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
    list_display = ('group', 'nome', 'cidade', 'UF', 'email', 'telefone1')
    search_fields = ('group__name', 'cidade', 'UF', 'email', 'responsavel')


@admin.register(UserDesignation)
class UserDesignationAdmin(admin.ModelAdmin):
    list_display = ('user', 'informacao_adicional')
    search_fields = ('user__username', 'informacao_adicional__nome')
    autocomplete_fields = ('user', 'informacao_adicional')


@admin.register(GroupAditionalInformationLegacy)
class GroupAditionalInformationLegacyAdmin(admin.ModelAdmin):
    list_display = ('gaiid', 'cod_contato')
    search_fields = ('gaiid__nome', 'cod_contato')


@admin.register(FiltroPadraoTela)
class FiltroPadraoTelaAdmin(admin.ModelAdmin):
    list_display = ("chave_tela", "nome", "ativo", "atualizado_em")
    search_fields = ("chave_tela", "nome")
    list_filter = ("ativo",)


@admin.register(FiltroFavoritoUsuario)
class FiltroFavoritoUsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "chave_tela", "nome",
                    "favorito", "ativo", "atualizado_em")
    search_fields = ("usuario__username", "chave_tela", "nome")
    list_filter = ("favorito", "ativo", "chave_tela")
