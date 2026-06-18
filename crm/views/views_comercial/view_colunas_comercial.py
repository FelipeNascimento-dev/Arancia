from django.shortcuts import redirect
from django.urls import reverse

from crm.decorators import crm_permission_required


@crm_permission_required("view_board")
def colunas_comercial(request):
    return redirect(f"{reverse('crm:kanban_comercial')}?manage_columns=1")
