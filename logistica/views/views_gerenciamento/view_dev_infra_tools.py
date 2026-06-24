from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

from logistica.services.dev_infra_catalog import get_dev_infra_apps, get_dev_infra_categories
from logistica.utils.dev_access import require_arancia_dev


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
def dev_infra_tools(request):
    require_arancia_dev(request.user)

    apps = get_dev_infra_apps()

    return render(
        request,
        'logistica/templates_gerenciamento/dev_infra_tools.html',
        {
            'site_title': 'Ferramentas de Infraestrutura',
            'dev_infra_apps': apps,
            'dev_infra_categories': get_dev_infra_categories(apps),
            'dev_infra_total': len(apps),
            'current_parent_menu': 'gerenciamento',
            'current_menu': 'dev_infra_tools',
        },
    )
