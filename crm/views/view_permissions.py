from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from crm.forms.forms_permissions import UserCrmPermissionsForm
from crm.services.permissions import (
    PRESET_PROFILES,
    apply_user_crm_permissions,
    get_user_direct_crm_codenames,
    get_user_effective_crm_codenames,
    get_user_group_crm_codenames,
    levels_from_codenames,
    summarize_user_access,
)

GERENCIAMENTO_MENU = {
    'current_parent_menu': 'gerenciamento',
    'current_menu': 'gestao_crm_permissions',
}


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
@permission_required('logistica.gestao_total', raise_exception=True)
def permissions_list(request):
    user_q = (request.GET.get('user_q') or '').strip()
    users_qs = (
        User.objects.filter(username__startswith='ARC', is_active=True)
        .select_related('designacao__informacao_adicional')
        .prefetch_related('groups', 'user_permissions')
        .order_by('username')
    )
    if user_q:
        users_qs = users_qs.filter(
            Q(username__icontains=user_q)
            | Q(first_name__icontains=user_q)
            | Q(last_name__icontains=user_q)
            | Q(email__icontains=user_q)
        )

    rows = []
    for user in users_qs:
        summary = summarize_user_access(user)
        rows.append({'user': user, 'summary': summary})

    paginator = Paginator(rows, 15)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'crm/settings/permissions_list.html', {
        'site_title': 'Gerenciamento — Permissões CRM',
        'page_rows': page,
        'user_q': user_q,
        'presets': PRESET_PROFILES,
        **GERENCIAMENTO_MENU,
    })


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
@permission_required('logistica.gestao_total', raise_exception=True)
def permissions_user(request, user_id):
    target_user = get_object_or_404(
        User.objects.prefetch_related('groups', 'user_permissions'),
        pk=user_id,
        username__startswith='ARC',
    )

    effective = get_user_effective_crm_codenames(target_user)
    initial_levels = levels_from_codenames(effective)

    if request.method == 'POST':
        form = UserCrmPermissionsForm(request.POST)
        if form.is_valid():
            profile = form.cleaned_profile()
            apply_user_crm_permissions(
                target_user,
                commercial=profile['commercial'],
                projects=profile['projects'],
                settings=profile['settings'],
                admin_scheduler=profile['admin_scheduler'],
                pilot_group=profile['pilot_group'],
                sync_direct=True,
            )
            messages.success(
                request,
                f'Permissões CRM de {target_user.username} atualizadas.',
            )
            return redirect('crm:permissions_user', user_id=target_user.pk)
        messages.error(request, 'Revise os campos do formulário.')
    else:
        form = UserCrmPermissionsForm(initial={
            'commercial': initial_levels['commercial'],
            'projects': initial_levels['projects'],
            'settings': initial_levels['settings'],
            'admin_scheduler': initial_levels['admin_scheduler'],
            'use_pilot_group': bool(summarize_user_access(target_user)['pilot_groups']),
        })

    return render(request, 'crm/settings/permissions_user.html', {
        'site_title': f'Permissões CRM — {target_user.username}',
        'target_user': target_user,
        'form': form,
        'presets': PRESET_PROFILES,
        'summary': summarize_user_access(target_user),
        'direct_codenames': sorted(get_user_direct_crm_codenames(target_user)),
        'group_codenames': sorted(get_user_group_crm_codenames(target_user)),
        'effective_codenames': sorted(effective),
        **GERENCIAMENTO_MENU,
    })
