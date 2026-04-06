from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
def senhas_privilegiadas(request):
    return render(request, 'global/senhas_privilegiadas.html', {
        'site_title': 'Home',
        'current_parent_menu': 'seguranca_informacao',
        'current_menu': 'senhas_privilegiadas'
    })
