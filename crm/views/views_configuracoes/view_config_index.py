from crm.decorators import crm_permission_required
from crm.views.views_tasks._helpers import menu_context
from django.shortcuts import render


@crm_permission_required("view_settings")
def config_index(request):
    return render(
        request,
        "crm/templates_configuracoes/index.html",
        {
            "site_title": "CRM — Configurações",
            **menu_context("projetos_config"),
        },
    )
