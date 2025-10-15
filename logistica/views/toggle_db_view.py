from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.decorators import login_required
import os
import re


@csrf_exempt
@login_required(login_url='logistica:login')
def toggle_db(request):
    try:
        file_path = os.path.join(
            settings.BASE_DIR, 'setup', 'local_settings.py')

        if not os.path.exists(file_path):
            return JsonResponse({'status': 'erro', 'msg': f'Arquivo não encontrado: {file_path}'})

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        match_host = re.search(r"DB_HOST\s*=\s*'([^']+)'", content)
        if not match_host:
            return JsonResponse({'status': 'erro', 'msg': 'Linha DB_HOST não encontrada no local_settings.py'})

        current_host = match_host.group(1).strip()

        if current_host == '192.168.0.219':
            new_host = '192.168.0.220'
            ambiente = 'Produção'
        else:
            new_host = '192.168.0.219'
            ambiente = 'Homologação'

        content = re.sub(
            r"DB_HOST\s*=\s*'[^']+'",
            f"DB_HOST = '{new_host}'",
            content
        )

        match_debug = re.search(r"LOCAL_DEBUG\s*=\s*(True|False)", content)
        if match_debug:
            current_debug = match_debug.group(1) == 'True'
            new_debug = not current_debug
            content = re.sub(
                r"LOCAL_DEBUG\s*=\s*(True|False)",
                f"LOCAL_DEBUG = {str(new_debug)}",
                content
            )
        else:
            content += f"\nLOCAL_DEBUG = False\n"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return JsonResponse({
            'status': 'ok',
            'ambiente': ambiente,
            'db_host': new_host,
            'local_debug': new_debug if match_debug else False
        })

    except Exception as e:
        return JsonResponse({'status': 'erro', 'msg': str(e)})
