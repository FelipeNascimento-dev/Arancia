from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from ...models import Romaneio, ItemRomaneio
from django.contrib.auth.decorators import login_required, permission_required


@csrf_exempt
@login_required(login_url='logistica:login')
@permission_required('logistica.usuario_de_TI', raise_exception=True)
@permission_required('logistica.usuario_credenciado', raise_exception=True)
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
