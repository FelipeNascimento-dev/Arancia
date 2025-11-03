from django.contrib import messages
from django.shortcuts import render, redirect
import requests
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
from backoffice.forms.forms_import import ImportacaoForm
from backoffice.utils.excel_export import gerar_excel_retorno
from setup.local_settings import API_BASE_BKO


API_MOVER = f"{API_BASE_BKO}v1/import_equipaments/create"


@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('transportes.controle_campo', raise_exception=True)
def importar_excel_view(request):
    contexto = {"form": ImportacaoForm()}

    if request.method == "POST":
        form = ImportacaoForm(request.POST, request.FILES)
        if form.is_valid():
            arquivo = form.cleaned_data["arquivo"]

            try:
                arquivo.seek(0)
                files = {
                    'file': (arquivo.name, arquivo, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                }
                response = requests.post(API_MOVER, files=files)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                messages.error(request, f" Erro ao enviar para API: {e}")
                return redirect("backoffice:importar_excel")

            result = response.json()

            if "detalhes_duplicados" in result and result["detalhes_duplicados"]:
                request.session["duplicados"] = result["detalhes_duplicados"]
                messages.warning(
                    request,
                    f"Foram encontrados {len(result['detalhes_duplicados'])} registros duplicados. "
                    "Eles estão listados abaixo."
                )
                contexto["duplicados"] = result["detalhes_duplicados"]
            else:
                messages.success(
                    request,
                    f" Importação concluída com sucesso: {result.get('registros_inseridos', 0)} inseridos, "
                    f"{result.get('registros_duplicados_ignorados', 0)} ignorados."
                )
                contexto["duplicados"] = None

    return render(request, "backoffice/importacao.html", contexto)
