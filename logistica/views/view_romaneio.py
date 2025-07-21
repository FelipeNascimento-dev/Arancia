from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from ..models import Romaneio, ItemRomaneio

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
