from django.shortcuts import render
from ...forms import ConsultaOSForm
from django.contrib import messages


def consulta_os(request):
    titulo = 'Consulta de OS'
    form = ConsultaOSForm(request.POST, nome_form=titulo)

    if form.is_valid():
        messages.success(request, "Teste OK")
    else:
        messages.error(request, "Teste OK")

    return render(
        request, 'transportes/controle_chamados/consulta_os.html', {
            "form": form,
            "site_title": titulo,
            "botao_texto": "Consultar",
            "current_parent_menu": "transportes",
            "current_menu": "controle_chamados",
            "current_submenu": "consulta_os",
        },
    )
