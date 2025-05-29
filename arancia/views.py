from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Romaneio, ItemRomaneio
import json
from .forms import RomaneioForm, RevisarForm, DespachoForm, RastreioForm, \
EntregaPaecForm, EntregaPicpacForm, EstornoPaecForm, EstornoPicpacForm, EstornoRomaneioForm, \
ConsultaForm, PreRecebimentoForm

from django.shortcuts import render

def index(request):
    return render(request, 'global/base.html')

def romaneio(request):
    form = RomaneioForm()
    qtd_campos = len(form.fields)
    mod = qtd_campos % 2
    impar = (mod == 1)
    primeiro_nome = next(iter(form.fields))
    primeiro_campo = form[primeiro_nome] 

    context = {
        'form': form,
        'impar': impar,
        'primeiro_campo': primeiro_campo
    }   
    return render(request, 'arancia/romaneio.html', context)


def revisar(request):
    form = RevisarForm()
    context = {
        'form': form
    }
    return render(request, 'arancia/revisar.html', context)

def rastreio(request):
    form = RastreioForm()
    context = {
        'form': form
    }
    return render(request, 'arancia/rastreio.html', context)

def despacho(request):
    form = DespachoForm()
    context = {
        'form': form
    }
    return render(request, 'arancia/despacho.html', context)

def entrega_paec(request):
    form = EntregaPaecForm()
    context = {
        'form': form
    }
    return render(request, 'arancia/EntregaPAEC.html', context)

def entrega_picpac(request):
    form = EntregaPicpacForm()
    context = {
        'form': form
    }
    return render(request, 'arancia/EntregaPicPac.html', context)

def estorno_paec(request):
    form = EstornoPaecForm()
    context = {
        'form': form
    }
    return render(request, 'arancia/EstornoPAEC.html', context)

def estorno_picpac(request):
    form = EstornoPicpacForm()
    context = {
        'form': form
    }
    return render(request, 'arancia/EstornoPICPAC.html', context)

def estorno_rom(request):
    form = EstornoRomaneioForm()
    context = {
        'form': form
    }
    return render(request, 'arancia/EstornoROM.html', context)


def consulta_id(request):
    form = ConsultaForm()
    tabela_dados = None
    exibir_formulario = True

    if request.method == 'POST':
        form = ConsultaForm(request.POST)
        if form.is_valid():
            exibir_formulario = False
            tabela_dados = [
                {"matnr": "000000000000604825",
                "gernr": "000000000005305833",
                "serge": "6G612662",
                # "zser_pr": None,
                "ztipo": "G2",
                "zver_ap": "CD16PS92040",
                "zsta_eq": "RPA",
                "nr_lcr_un": "00019AA2525766",
                # "nr_lcr_mast": None,
                # "nr_cd_br_cx": None,
                "stat_div_rec": "00",
                "id_lote": "030000431485",
                }
            ]

    context = {
        'form': form,
        'tabela_dados': tabela_dados,
        'exibir_formulario': exibir_formulario
    }
    return render(request, 'arancia/consulta_id.html', context)

def pre_recebimento(request):
    form = PreRecebimentoForm()
    context = {
        'form': form
    }
    return render(request, 'arancia/pre_recebimento.html', context)


@csrf_exempt
def registrar_romaneio(request):
    if request.method == 'POST':
        dados = json.loads(request.body)

        numero = dados.get('romaneio')
        romaneio, _ = Romaneio.objects.get_or_create(numero=numero)

        ItemRomaneio.objects.create(
            romaneio=romaneio,
            serial=dados.get('serial', ''),
            chamado=dados.get('chamado', ''),
            data=dados.get('data', ''),
            hora=dados.get('hora', ''),
            usuario=dados.get('usuario', ''),
            filial=dados.get('filial', ''),
            destino=dados.get('destino', '')
        )

        return JsonResponse({'status': 'ok'})