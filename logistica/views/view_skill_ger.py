from django.contrib.auth.models import User
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render


def skill_ger(request):
    user_q = request.GET.get("user_q", "")

    usuarios_qs = User.objects.filter(
        username__startswith="ARC"
    ).select_related(
        "perfil", "designacao__informacao_adicional"
    ).prefetch_related("groups").distinct()

    if user_q:
        usuarios_qs = usuarios_qs.filter(
            Q(username__icontains=user_q) |
            Q(first_name__icontains=user_q) |
            Q(last_name__icontains=user_q) |
            Q(email__icontains=user_q) |
            Q(perfil__cpf__icontains=user_q)
        )

    usuarios_qs = usuarios_qs.order_by("username")

    paginator = Paginator(usuarios_qs, 10)
    page_number = request.GET.get("page")
    usuarios = paginator.get_page(page_number)

    return render(request, "logistica/skill_ger.html", {
        "usuarios": usuarios,
        "user_q": user_q,
    })
