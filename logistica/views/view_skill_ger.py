from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from logistica.models import GroupAditionalInformation
import json
from django.core.serializers.json import DjangoJSONEncoder


def skill_ger(request):
    user_q = request.GET.get("user_q", "")

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        cpf = request.POST.get("cpf")
        groups_ids = request.POST.getlist("groups")
        additional_info_id = request.POST.get("additional_info")

        user = get_object_or_404(User, id=user_id)

        if full_name:
            parts = full_name.strip().split(" ", 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ""
        user.email = email
        user.save()

        if hasattr(user, "perfil"):
            user.perfil.cpf = cpf
            user.perfil.save()

        if groups_ids:
            user.groups.set(Group.objects.filter(id__in=groups_ids))
        else:
            user.groups.clear()

        if hasattr(user, "designacao"):
            if additional_info_id:
                try:
                    info = GroupAditionalInformation.objects.get(
                        id=additional_info_id)
                    user.designacao.informacao_adicional = info
                except GroupAditionalInformation.DoesNotExist:
                    user.designacao.informacao_adicional = None
            else:
                user.designacao.informacao_adicional = None
            user.designacao.save()

        messages.success(request, "Usuário atualizado com sucesso!")
        return redirect("logistica:skill_ger")

    usuarios_qs = (
        User.objects.filter(username__startswith="ARC")
        .select_related("perfil", "designacao__informacao_adicional")
        .prefetch_related("groups")
        .distinct()
    )
    if user_q:
        usuarios_qs = usuarios_qs.filter(
            Q(username__icontains=user_q)
            | Q(first_name__icontains=user_q)
            | Q(last_name__icontains=user_q)
            | Q(email__icontains=user_q)
            | Q(perfil__cpf__icontains=user_q)
        )

    usuarios_qs = usuarios_qs.order_by("username")

    paginator = Paginator(usuarios_qs, 10)
    page_number = request.GET.get("page")
    usuarios = paginator.get_page(page_number)

    all_groups = Group.objects.all().order_by("name")
    additional_infos = GroupAditionalInformation.objects.all().order_by("nome")

    usuarios_data = []
    for u in usuarios:
        usuarios_data.append({
            "id": u.id,
            "username": u.username,
            "full_name": f"{u.first_name} {u.last_name}".strip(),
            "email": u.email,
            "cpf": getattr(u.perfil, "cpf", ""),
            "groups": list(u.groups.values_list("id", flat=True)),
            "additional_info": getattr(u.designacao.informacao_adicional, "id", None)
            if hasattr(u, "designacao") and u.designacao.informacao_adicional else None,
        })

    return render(
        request,
        "logistica/skill_ger.html",
        {
            "usuarios": usuarios,
            "user_q": user_q,
            "all_groups": all_groups,
            "site_title": "Gerenciamento de Skills",
            "additional_infos": additional_infos,
            "usuarios_json": json.dumps(usuarios_data, cls=DjangoJSONEncoder),
        },
    )
