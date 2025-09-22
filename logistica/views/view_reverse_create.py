from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from ..forms import ReverseCreateForm


def reverse_create(request):
    titulo = 'Reversa de Equipamento'

    payload = {
        "romaneio": "1",
        "status": "ABERTO",
        "volums": [
            {
                "volum_number": "1",
                "kits": [
                    {
                        "kit_number": "1",
                        "serial": "J9A503097285",
                        "order_number": "10195181023115",
                        "created_by": "ARC0001",
                        "created_at": "2025-09-18T16:53:25.503311"
                    },
                    {
                        "kit_number": "1",
                        "serial": "TESTEDAV3",
                        "order_number": "ORD2025000123",
                        "created_by": "ARC0001",
                        "created_at": "2025-09-18T16:54:02.333902"
                    },
                    {
                        "kit_number": "1",
                        "serial": "TESTEDAVI2",
                        "order_number": "ORD2025000123",
                        "created_by": "ARC0001",
                        "created_at": "2025-09-18T16:54:27.428307"
                    }
                ]
            },
            {
                "volum_number": "2",
                "kits": [
                    {
                        "kit_number": "1",
                        "serial": "TESTEDAVI",
                        "order_number": "ORD2025000123",
                        "created_by": "ARC0001",
                        "created_at": "2025-09-18T16:54:52.512093"
                    },
                    {
                        "kit_number": "2",
                        "serial": "6C671351",
                        "order_number": "10439131047510",
                        "created_by": "ARC0001",
                        "created_at": "2025-09-18T16:57:20.947043"
                    }
                ]
            },
            {
                "volum_number": "3",
                "kits": [
                    {
                        "kit_number": "1",
                        "serial": "6G001256",
                        "order_number": "10439211047518",
                        "created_by": "ARC0000",
                        "created_at": "2025-09-19T18:41:29.028077"
                    }
                ]
            }
        ]
    }

    user_sales_channel = None
    try:
        if (
            request.user.is_authenticated
            and hasattr(request.user, "designacao")
            and request.user.designacao.informacao_adicional
        ):
            user_sales_channel = (
                request.user.designacao.informacao_adicional.sales_channel or ""
            ).strip()
    except Exception:
        user_sales_channel = None

    romaneio_num = request.session.get("romaneio_num", None)

    form = ReverseCreateForm(
        request.POST or None,
        nome_form=titulo,
        user_sales_channel=user_sales_channel,
        romaneio_num=romaneio_num,
    )

    if "volums" not in request.session:
        request.session["volums"] = []

    volums = request.session["volums"]

    if request.method == "POST" and form.is_valid():
        serial = form.cleaned_data.get("serial")

        if serial:
            if len(volums) == 0:
                volums.append({"volum_number": 1, "kits": []})

            ultimo_volume = volums[-1]

            if len(ultimo_volume["kits"]) >= 10:
                if len(volums) >= 25:
                    messages.error(
                        request, "Limite máximo de 25 volumes atingido!")
                    return redirect("logistica:reverse_create")
                else:
                    novo_numero = int(ultimo_volume["volum_number"]) + 1
                    volums.append({"volum_number": novo_numero, "kits": []})
                    ultimo_volume = volums[-1]

            kit_number = len(ultimo_volume["kits"]) + 1
            ultimo_volume["kits"].append({
                "kit_number": kit_number,
                "serial": serial,
                "order_number": f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "created_by": request.user.username if request.user.is_authenticated else "SYSTEM",
                "created_at": datetime.now().isoformat()
            })

            request.session["volums"] = volums
            request.session.modified = True

            if int(ultimo_volume["volum_number"]) == 25 and len(ultimo_volume["kits"]) == 10:
                messages.warning(
                    request,
                    "Você atingiu o limite de 25 volumes com 10 kits cada!"
                )

            return redirect("logistica:reverse_create")

    context = {
        "form": form,
        "botao_texto": "Inserir",
        "site_title": "Reversa",
        "volums": volums,
        "payload": payload,
    }
    return render(request, "logistica/reverse_create.html", context)
