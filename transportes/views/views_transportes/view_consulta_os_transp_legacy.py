from django.db.models import Q
from django.http import JsonResponse
from logistica.models import Group, GroupAditionalInformation


def buscar_locais(request):
    termo = request.GET.get("q", "").strip()

    if len(termo) < 2:
        return JsonResponse({"items": []})

    grupos_base = Group.objects.filter(
        Q(name="arancia_PA")
        | Q(name="arancia_CD")
        | Q(name="arancia_CUSTOMER")
    )

    locais = (
        GroupAditionalInformation.objects.filter(
            group__in=grupos_base, nome__icontains=termo
        )
        .select_related("group")
        .order_by("nome")[:10]
    )

    data = []
    for l in locais:
        prefix = ""
        if l.group.name == "arancia_PA":
            prefix = "[PA]"
        elif l.group.name == "arancia_CD":
            prefix = "[CD]"
        elif l.group.name == "arancia_CUSTOMER":
            prefix = "[CUSTOMER]"
        data.append({"id": l.id, "label": f"{prefix} {l.nome}"})

    return JsonResponse({"items": data})
