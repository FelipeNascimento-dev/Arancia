from django.shortcuts import redirect
from django.urls import reverse

from crm.decorators import crm_permission_required


@crm_permission_required("view_clients")
def detalhe_cliente(request, gai_id):
    return redirect(f"{reverse('crm:lista_clientes')}?client={gai_id}")
