# views.py
import json
from collections import defaultdict
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from ..forms import PreRecebimentoForm, RecebimentoForm
from utils.request import RequestClient

API_URL = "http://192.168.0.214/IntegrationXmlAPI/api/v2/centros_e_deps/O"

def _fetch_api_rows():
    client = RequestClient(url=API_URL, method="GET", headers={"Accept": "application/json"})
    resp = client.send_api_request_no_json(stream=False)
    data = resp.json() if hasattr(resp, "json") else []
    return data if isinstance(data, list) else []

def _build_choices(rows):
    centro_label = {}
    depositos_map = defaultdict(set)
    for r in rows:
        cod_c = (r.get("cod_centro") or "").strip()
        nome_c = (r.get("nome_centro") or "").strip()
        cod_d = (r.get("cod_deposito") or "").strip()
        nome_d = (r.get("nome_deposito") or "").strip()
        if not cod_c:
            continue
        if cod_c not in centro_label:
            centro_label[cod_c] = f"{cod_c} — {nome_c}" if nome_c else cod_c
        if cod_d:
            label = f"{cod_d} — {nome_d}" if nome_d else cod_d
            depositos_map[cod_c].add((cod_d, label))
    centro_choices = sorted(centro_label.items(), key=lambda kv: kv[1])
    depositos_by_centro = {k: sorted(list(v), key=lambda t: t[1]) for k, v in depositos_map.items()}
    return centro_choices, depositos_by_centro


@login_required(login_url='logistica:login')
@permission_required('logistica.usuario_de_TI', raise_exception=True)
@permission_required('logistica.usuario_credenciado', raise_exception=True)
def pre_recebimento(request, tp_reg):
    titulo = 'SAP - Pré-Recebimento' if tp_reg == '13' else 'SAP - Estorno de Pré-Recebimento'
    try:
        rows = _fetch_api_rows()
    except Exception as e:
        rows = []
        messages.error(request, f"Falha ao carregar centros/depósitos: {e}")

    centro_choices, depositos_by_centro = _build_choices(rows)

    sel_c_origem  = request.POST.get("centro_origem")  or request.GET.get("centro_origem")  or ""
    sel_c_destino = request.POST.get("centro_destino") or request.GET.get("centro_destino") or ""
    deps_origem   = depositos_by_centro.get(sel_c_origem, [])
    deps_destino  = depositos_by_centro.get(sel_c_destino, [])

    if request.method == 'POST':
        form = PreRecebimentoForm(
            request.POST, nome_form=titulo,
            centro_choices=centro_choices,
            deposito_choices_origem=deps_origem,
            deposito_choices_destino=deps_destino,
            depositos_by_centro=depositos_by_centro,
        )
        if form.is_valid():
            id_lote  = form.cleaned_data['id']
            qtde_vol = form.cleaned_data['qtde_vol']
            c_ori    = form.cleaned_data['centro_origem']
            d_ori    = form.cleaned_data['deposito_origem']
            c_des    = form.cleaned_data['centro_destino']
            d_des    = form.cleaned_data['deposito_destino']

            request.session['id_pre_recebido'] = id_lote
            request.session['origem'] = 'pre-recebimento'

            RequestClient(
                url=f'http://192.168.0.214/IntegrationXmlAPI/api/v2/clo/mo/{tp_reg}',
                method='POST',
                headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
                request_data={
                    "id_lote": id_lote,
                    "nr_controle_transp": id_lote,
                    "qtde_vol": qtde_vol,
                    "centro_origem": c_ori, "deposito_origem": d_ori,
                    "centro_destino": c_des, "deposito_destino": d_des
                }
            ).send_api_request()
            return redirect('logistica:consulta_resultados')
        else:
            messages.error(request, "Corrija os erros do formulário.")
    else:
        form = PreRecebimentoForm(
            nome_form=titulo,
            centro_choices=centro_choices,
            deposito_choices_origem=deps_origem,
            deposito_choices_destino=deps_destino,
            depositos_by_centro=depositos_by_centro,
        )

    return render(request, 'logistica/pre_recebimento.html', {
        'form': form,
        'botao_texto': 'Enviar',
        'depositos_map_json': json.dumps(depositos_by_centro),
    })


@login_required(login_url='logistica:login')
@permission_required('logistica.usuario_de_TI', raise_exception=True)
@permission_required('logistica.usuario_credenciado', raise_exception=True)
def recebimento(request, tp_reg):
    titulo = 'SAP - Recebimento' if tp_reg == '15' else 'SAP - Estorno de Recebimento'
    try:
        rows = _fetch_api_rows()
    except Exception as e:
        rows = []
        messages.error(request, f"Falha ao carregar centros/depósitos: {e}")

    centro_choices, depositos_by_centro = _build_choices(rows)

    sel_c_origem  = request.POST.get("centro_origem")  or request.GET.get("centro_origem")  or ""
    sel_c_destino = request.POST.get("centro_destino") or request.GET.get("centro_destino") or ""
    deps_origem   = depositos_by_centro.get(sel_c_origem, [])
    deps_destino  = depositos_by_centro.get(sel_c_destino, [])

    if request.method == 'POST':
        form = RecebimentoForm(
            request.POST, nome_form=titulo,
            centro_choices=centro_choices,
            deposito_choices_origem=deps_origem,
            deposito_choices_destino=deps_destino,
            depositos_by_centro=depositos_by_centro,
        )
        if form.is_valid():
            id_lote  = form.cleaned_data['id']
            serial   = form.cleaned_data['serial']
            qtde_vol = form.cleaned_data['qtde_vol']
            c_ori    = form.cleaned_data['centro_origem']
            d_ori    = form.cleaned_data['deposito_origem']
            c_des    = form.cleaned_data['centro_destino']
            d_des    = form.cleaned_data['deposito_destino']

            request.session['id_pre_recebido'] = id_lote
            request.session['origem'] = 'recebimento'
            request.session['serial_recebido'] = serial

            RequestClient(
                url=f'http://192.168.0.214/IntegrationXmlAPI/api/v2/clo/mo/{tp_reg}',
                method='POST',
                headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
                request_data={
                    "id_lote": id_lote,
                    "nr_controle_transp": id_lote,
                    "serge": serial,
                    "qtde_vol": qtde_vol,
                    "centro_origem": c_ori, "deposito_origem": d_ori,
                    "centro_destino": c_des, "deposito_destino": d_des
                }
            ).send_api_request()
            return redirect('logistica:consulta_resultados')
        else:
            messages.error(request, "Corrija os erros do formulário.")
    else:
        initial = {'id': request.session.get('id_pre_recebido') or ""}
        form = RecebimentoForm(
            initial=initial, nome_form=titulo,
            centro_choices=centro_choices,
            deposito_choices_origem=deps_origem,
            deposito_choices_destino=deps_destino,
            depositos_by_centro=depositos_by_centro,
        )

    return render(request, 'logistica/recebimento.html', {
        'form': form,
        'botao_texto': 'Enviar',
        'depositos_map_json': json.dumps(depositos_by_centro),
    })