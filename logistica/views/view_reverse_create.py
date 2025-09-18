from django.shortcuts import render, redirect
from ..forms import ReverseCreateForm


def reverse_create(request):
    titulo = 'Reversa de Equipamento'
    form = ReverseCreateForm(request.POST or None, nome_form=titulo)

    if "volumes" not in request.session:
        request.session["volumes"] = []

    volumes = request.session["volumes"]

    if request.method == "POST" and form.is_valid():
        serial = form.cleaned_data.get("serial")
        if serial:
            if not volumes:
                volumes.append({"number": 1, "kits": []})

            ultimo_volume = volumes[-1]

            if len(ultimo_volume["kits"]) >= 10:
                volumes.append({
                    "number": len(volumes) + 1,
                    "kits": []
                })
                ultimo_volume = volumes[-1]

            ultimo_volume["kits"].append({
                "number": len(ultimo_volume["kits"]) + 1,
                "serial": serial
            })

            request.session["volumes"] = volumes
            request.session.modified = True

        return redirect("logistica:reverse_create")

    context = {
        "form": form,
        "botao_texto": "Inserir",
        "site_title": "Reversa",
        "volumes": volumes,
    }
    return render(request, "logistica/reverse_create.html", context)
