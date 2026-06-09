from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, permission_required

from crm.services.context import invalidate_crm_session_cache


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
def logout_view(request):
    invalidate_crm_session_cache(request)
    logout(request)
    return redirect('logistica:login')
