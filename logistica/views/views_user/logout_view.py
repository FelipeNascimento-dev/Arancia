from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, permission_required

from crm.context_processors import clear_crm_context_cache
from crm_api.session_credentials import clear_password_from_session
from setup.middleware.password_expiration_session import clear_password_expiration_session


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
def logout_view(request):
    clear_password_from_session(request)
    clear_crm_context_cache(request)
    clear_password_expiration_session(request)
    logout(request)
    return redirect('logistica:login')
