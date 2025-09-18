from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('transportes.CC_admin', raise_exception=True)
def ver_usuario_view(request):
    pass

    return (request, "transportes/ferramentas/see_user.html")
