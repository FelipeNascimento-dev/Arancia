from turtle import title
from urllib import request
from django.shortcuts import redirect, render
from django.contrib import messages
from backoffice.forms import CadastrarSerialForm, BuscarOSForm
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
from utils.request import RequestClient
from setup.local_settings import API_BASE_BKO
from datetime import datetime
import json

JSON_CT = "application/json"
API_LISTA_EQUIPAMENTO = f"{API_BASE_BKO}v1/import/search"
API_CADASTRO_EQUIPAMENTO = f"{API_BASE_BKO}v1/import/create"


@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('backoffice.Importar', raise_exception=True)
def Create_equipament_view(request):
    
    os_consultada = request.session.get("ultima_os")

    # === CONFIGURAÇÕES INICIAIS === #
    titulo = "Consultar OS / Cadastrar Serial"
    equipamentos = []
    os_consultada = None
    consultado = bool(request.GET.get("enviar_evento"))

    form = BuscarOSForm(request.GET or None, nome_form=titulo)
    cadastrar_form = CadastrarSerialForm(request.POST or None)
    

    
    def __render():
        return render(
            request,
            "backoffice/cadastro_equipamento.html",
            {
                "site_title": title,
                "form": form,
                "botao_texto": "Consultar OS",
                "cadastrar_form": cadastrar_form,
                "equipamentos": equipamentos,
                "os_consultada": os_consultada,
                "consultado": consultado,
            },
        )
   
    # ======================== BUSCA OS ===================================
   
    if request.method == "GET" and request.GET.get("enviar_evento"):

        if form.is_valid():
            
            request.session["checkin_form_data"] = {
                "os_number": form.cleaned_data.get("os_number"),
            }
            
            if not os_consultada:
                os_consultada = form.cleaned_data["os_number"]

            try:
                url = f"{API_LISTA_EQUIPAMENTO}/{os_consultada}"
                res = RequestClient(url=url, method="GET", headers={"Accept": JSON_CT})
                resposta = res.send_api_request()

                if isinstance(resposta, list):
                    equipamentos = resposta
                else:
                    equipamentos = []
                    messages.warning(request, "Nenhum equipamento encontrado.")

                # === Formatando datas ===
                for eq in equipamentos:
                    dt_str = eq.get("service_deadline")
                    if dt_str:
                        try:
                            dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                            eq["service_deadline_fmt"] = dt.strftime("%d/%m/%Y - %Hh %Mmin")
                        except:
                            eq["service_deadline_fmt"] = dt_str

                if equipamentos:
                    messages.success(request, f"OS {os_consultada} carregada com sucesso!")
                else:
                    messages.info(request, "Nenhum equipamento encontrado para esta OS.")

            except Exception as e:
                messages.error(request, f"Erro ao consultar OS: {e}")
            return __render()
        

        else:
            messages.error(request, "Número da OS inválido.")

   
    # ======================== CADASTRAR SERIAL ===========================
    
    elif request.method == "POST" and request.POST.get("cadastrar_serial"):
        
        os_consultada =  request.POST.get("order_number")

        request.session["ultima_os"] = os_consultada
        
        if cadastrar_form.is_valid():
            dados = cadastrar_form.cleaned_data

            payload = {
                "order_number": os_consultada,
                "serial_number": dados["serial_number"],
                "order_origin": "Arancia",
                "product_model": dados["product_model"],
                "product_type": dados["product_type"],
                "service_type": dados["service_type"],
                "created_by": request.user.username,
                "status_id": 1,
                "extra_information": dados["extra_information"],
            }

            try:
                res = RequestClient(
                    url=API_CADASTRO_EQUIPAMENTO,
                    method="POST",
                    headers={"Content-Type": JSON_CT, "Accept": JSON_CT},
                    request_data=payload
                )
                api_result = res.send_api_request()

                messages.success(request, "Serial cadastrado com sucesso!")

                os_consultada = request.session.get("ultima_os")
                
                request.session["os_number"] = os_consultada

                return redirect('backoffice:equipamento_lista')

            except Exception as e:
                messages.error(request, f"Erro ao cadastrar serial: {e}")
            return __render()
        else:
            messages.error(request, "Erro ao validar o formulário de cadastro.")
            
    else:
        saved = request.session.pop("checkin_form_data", {})
            
    initial_data = {
        "os_number": saved.get("os_number", ""),
    }
    
    form = BuscarOSForm(
        request.GET or None, 
        nome_form=titulo,
        initial= initial_data
        )

    # ========================= RENDERIZAÇÃO ==============================
   
    return render(
        request,
        "backoffice/cadastro_equipamento.html",
        {
            "site_title": titulo,
            "form": form,
            "botao_texto": "Consultar OS",
            "cadastrar_form": cadastrar_form,
            "equipamentos": equipamentos,
            "os_consultada": os_consultada,
            "consultado": consultado,
        },
    )
