from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from ..models import GroupAditionalInformation, UserDesignation
from django.contrib.auth.decorators import login_required, permission_required


@login_required
@permission_required("logistica.gestao_total", raise_exception=True)
def skill_ger(request):
    grupos = GroupAditionalInformation.objects.all().order_by("nome")
    selected_group = None
    usuarios_vinculados = []
    all_users = User.objects.filter(
        username__startswith='ARC').order_by("username")

    group_id = request.GET.get("group_id")
    if group_id:
        selected_group = get_object_or_404(
            GroupAditionalInformation, id=group_id)
        usuarios_vinculados = User.objects.filter(
            designacao__informacao_adicional=selected_group)

    if request.method == "POST" and "edit_group" in request.POST:
        group_id = request.POST.get("group_id")
        grupo = get_object_or_404(GroupAditionalInformation, id=group_id)

        grupo.nome = request.POST.get("nome")
        grupo.cod_iata = request.POST.get("cod_iata")
        grupo.sales_channel = request.POST.get("sales_channel")
        grupo.deposito = request.POST.get("deposito")
        grupo.logradouro = request.POST.get("logradouro")
        grupo.numero = request.POST.get("numero")
        grupo.complemento = request.POST.get("complemento")
        grupo.bairro = request.POST.get("bairro")
        grupo.cidade = request.POST.get("cidade")
        grupo.estado = request.POST.get("estado")
        grupo.CEP = request.POST.get("cep")
        grupo.telefone1 = request.POST.get("telefone1")
        grupo.telefone2 = request.POST.get("telefone2")
        grupo.email = request.POST.get("email")
        grupo.responsavel = request.POST.get("responsavel")

        grupo.save()
        messages.success(
            request, f"Grupo {grupo.nome} atualizado com sucesso!")
        return redirect(f"{request.path}?group_id={grupo.id}")

    if request.method == "POST" and "add_user" in request.POST and selected_group:
        user_id = request.POST.get("user_id")
        user = get_object_or_404(User, id=user_id)

        designation, _ = UserDesignation.objects.get_or_create(user=user)
        designation.informacao_adicional = selected_group
        designation.save()

        messages.success(
            request, f"Usuário {user.username} vinculado a {selected_group.nome}")
        return redirect(f"{request.path}?group_id={selected_group.id}")

    context = {
        "grupos": grupos,
        "selected_group": selected_group,
        "usuarios_vinculados": usuarios_vinculados,
        "all_users": all_users,
        "site_title": 'Gerenciamento de Informações Adicionais'
    }
    return render(request, "logistica/skill_ger.html", context)
