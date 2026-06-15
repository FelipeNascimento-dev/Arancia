from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from setup.services.environment_switch import toggle_environment


@require_POST
@login_required(login_url='logistica:login')
@permission_required('logistica.ti_interno', raise_exception=True)
def toggle_db(request):
    try:
        result = toggle_environment()
        return JsonResponse({'status': 'ok', **result})
    except FileNotFoundError as exc:
        return JsonResponse({'status': 'erro', 'msg': str(exc)}, status=404)
    except ValueError as exc:
        return JsonResponse({'status': 'erro', 'msg': str(exc)}, status=400)
    except Exception as exc:
        return JsonResponse({'status': 'erro', 'msg': str(exc)}, status=500)
