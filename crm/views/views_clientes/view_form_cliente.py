from django.shortcuts import redirect
from django.urls import reverse

from crm.decorators import crm_permission_required


@crm_permission_required("view_clients")
def form_cliente(request, gai_id=None):
    if gai_id:
        return redirect(f"{reverse('crm:lista_clientes')}?edit={gai_id}")
    return redirect("crm:lista_clientes")
