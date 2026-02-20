from ...forms import ConsultaOStranspForm
from django.shortcuts import render


def consulta_os_transp(request):
    titulo = 'Consulta OS'
    form = ConsultaOStranspForm(request.GET or None, nome_form=titulo)

    return render(request, 'transportes/transportes/consulta_os_transp.html', {
        "form": form,
    })
