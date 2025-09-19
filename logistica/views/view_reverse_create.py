from django.shortcuts import render, redirect
from django.contrib import messages
from ..forms import ReverseCreateForm


def reverse_create(request):
    titulo = 'Reversa de Equipamento'

    # tenta pegar o sales_channel do usuário logado (via UserDesignation -> GroupAditionalInformation)
    user_sales_channel = None
    try:
        if request.user.is_authenticated and hasattr(request.user, "designacao") and request.user.designacao.informacao_adicional:
            user_sales_channel = (
                request.user.designacao.informacao_adicional.sales_channel or "").strip()
    except Exception:
        user_sales_channel = None

    # passe o user_sales_channel na construção do form
    form = ReverseCreateForm(
        request.POST or None,
        nome_form=titulo,
        user_sales_channel=user_sales_channel,
    )

    # ---------------- sua lógica dos volumes (inalterada) ----------------
    if "volumes" not in request.session:
        request.session["volumes"] = []

    volumes = request.session["volumes"]

    if request.method == "POST" and form.is_valid():
        serial = form.cleaned_data.get("serial")

        if serial:
            if len(volumes) == 0:
                volumes.append({"number": 1, "kits": []})

            ultimo_volume = volumes[-1]

            if len(ultimo_volume["kits"]) >= 10:
                if len(volumes) >= 25:
                    messages.error(
                        request, "Limite máximo de 25 volumes atingido!")
                    return redirect("logistica:reverse_create")
                else:
                    novo_numero = ultimo_volume["number"] + 1
                    volumes.append({"number": novo_numero, "kits": []})
                    ultimo_volume = volumes[-1]

            kit_number = len(ultimo_volume["kits"]) + 1
            ultimo_volume["kits"].append({
                "number": kit_number,
                "serial": serial,
            })

            request.session["volumes"] = volumes
            request.session.modified = True

            if ultimo_volume["number"] == 25 and len(ultimo_volume["kits"]) == 10:
                messages.warning(
                    request, "Você atingiu o limite de 25 volumes com 10 kits cada!")

            return redirect("logistica:reverse_create")

    context = {
        "form": form,
        "botao_texto": "Inserir",
        "site_title": "Reversa",
        "volumes": volumes,
    }
    return render(request, "logistica/reverse_create.html", context)
