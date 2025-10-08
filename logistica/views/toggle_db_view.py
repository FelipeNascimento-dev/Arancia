from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
import re


@csrf_exempt
def toggle_db(request):
    try:
        file_path = os.path.join(
            settings.BASE_DIR, 'setup', 'local_settings.py')

        if not os.path.exists(file_path):
            return JsonResponse({'status': 'erro', 'msg': f'Arquivo não encontrado: {file_path}'})

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        match = re.search(r"DB_HOST\s*=\s*'([^']+)'", content)
        if not match:
            return JsonResponse({'status': 'erro', 'msg': 'Linha DB_HOST não encontrada no local_settings.py'})

        current_host = match.group(1).strip()

        if current_host == '192.168.0.219':
            new_host = '192.168.0.220'
            ambiente = 'Produção'
        else:
            new_host = '192.168.0.219'
            ambiente = 'Homologação'

        new_content = re.sub(
            r"DB_HOST\s*=\s*'[^']+'",
            f"DB_HOST = '{new_host}'",
            content
        )

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return JsonResponse({'status': 'ok', 'ambiente': ambiente, 'db_host': new_host})

    except Exception as e:
        re
