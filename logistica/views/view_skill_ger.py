from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render


def skill_ger(request):
    usuarios_qs = User.objects.filter(
        username__startswith="ARC"
    ).select_related(
        "perfil", "designacao__informacao_adicional"
    ).prefetch_related("groups").distinct().order_by("username")

    paginator = Paginator(usuarios_qs, 10)
    page_number = request.GET.get("page")
    usuarios = paginator.get_page(page_number)

    return render(request, "logistica/skill_ger.html", {"usuarios": usuarios})
