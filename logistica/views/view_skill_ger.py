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
    all_users = User.objects.all().order_by("username")

    if request.method == "POST" and "create_group" in request.POST:
        nome = request.POST.get("nome")
        cod_iata = request.POST.get("cod_iata")
        sales_channel = request.POST.get("sales_channel")
        grupo = GroupAditionalInformation.objects.create(
            nome=nome,
            cod_iata=cod_iata,
            sales_channel=sales_channel,
        )
        messages.success(request, f"Grupo {grupo.nome} criado com sucesso!")
        return redirect("logistica:group_additional_manager")

    group_id = request.GET.get("group_id")
    if group_id:
        selected_group = get_object_or_404(
            GroupAditionalInformation, id=group_id)
        usuarios_vinculados = User.objects.filter(
            designacao__informacao_adicional=selected_group)

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
    }
    return render(request, "logistica/skill_ger.html", context)
