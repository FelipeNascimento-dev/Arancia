import base64
from django.contrib import messages
from django.shortcuts import render, redirect
import requests
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
from backoffice.forms.forms_import import ImportacaoForm
from backoffice.utils.excel_export import gerar_excel_retorno
from setup.local_settings import API_BASE, TOKEN
from transportes.forms.form_script import ScriptingForm


API_SCRIPT = f"{API_BASE}/v3/rota/expo-processar-fluxo-completo"


@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('transportes.controle_campo', raise_exception=True)
def scripting_view(request):
    contexto = {
        "form": ScriptingForm(),
        "current_parent_menu": "transportes",
        "current_menu": "controle_campo",
        "current_submenu": "rotas",
        "current_subsubmenu": "roteirizacao",
    }

    if request.method == "POST":
        form = ScriptingForm(request.POST, request.FILES)
        if form.is_valid():
            arquivo = form.cleaned_data["arquivo"]

            try:
                arquivo.seek(0)

                headers = {
                    "access_token": TOKEN,
                    "accept": "application/json",
                }

                files = {
                    "arquivo": (
                        arquivo.name,
                        arquivo,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                }

                response = requests.post(
                    API_SCRIPT, headers=headers, files=files)
                response.raise_for_status()

            except Exception as e:
                contexto["erro"] = f"Erro ao enviar para API: {e}"
                return render(request, "transportes/tools/scripting.html", contexto)

            # 🔥 API RETORNOU DOWNLOAD
            content_type = response.headers.get("Content-Type", "")

            if "application" in content_type or "octet-stream" in content_type:
                filename = (
                    response.headers.get("Content-Disposition", "")
                    .replace("attachment; filename=", "")
                    .replace('"', "")
                ) or "retorno.xlsx"

                # 🔥 Converte o arquivo em Base64
                file_base64 = base64.b64encode(
                    response.content).decode('utf-8')

                # 🔥 Envia para o template mostrar o botão
                contexto["download_ready"] = True
                contexto["file_base64"] = file_base64
                contexto["filename"] = filename

                return render(request, "transportes/tools/scripting.html", contexto)

            # 🔥 Se não for arquivo, tenta JSON
            try:
                result = response.json()
            except ValueError:
                contexto["erro"] = (
                    "A API respondeu, mas não retornou JSON válido.\n"
                    f"Resposta: {response.text[:500]}..."
                )
                return render(request, "transportes/tools/scripting.html", contexto)

            if response.status_code != 200:
                contexto["erro"] = result.get(
                    "error", "Erro ao processar o arquivo.")
            else:
                contexto["mensagem"] = (
                    f"Importação concluída: "
                    f"{result.get('registros_inseridos', 0)} inseridos, "
                    f"{result.get('registros_duplicados_ignorados', 0)} ignorados."
                )

    return render(request, "transportes/tools/scripting.html", contexto)
