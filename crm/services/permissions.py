"""Catálogo e helpers de permissões Django ``crm.*`` (auth_permission compartilhado)."""

from django.contrib.auth.models import Permission

# Alinhado ao seed Alembic / ``crm_prerequisites``.
ALL_CRM_CODENAMES = frozenset({
    'add_billing', 'add_board', 'add_client', 'add_contract', 'add_project',
    'add_task', 'add_task_recurrence', 'assign_task', 'change_billing',
    'change_board', 'change_client', 'change_contract', 'change_project',
    'change_settings', 'change_task', 'change_task_recurrence', 'delete_board',
    'delete_client', 'delete_contract', 'delete_project', 'delete_task',
    'delete_task_recurrence', 'manage_board_access', 'manage_board_columns',
    'manage_priorities', 'manage_project_members', 'manage_service_types',
    'manage_status_tasks', 'manage_watchers', 'move_task', 'run_task_scheduler',
    'upload_contract_file', 'view_billing', 'view_boards', 'view_clients',
    'view_contracts', 'view_projects', 'view_settings', 'view_task_recurrences',
    'view_tasks', 'view_teams',
})

CRM_PILOT_GROUP_NAMES = frozenset({
    'crm_pilot_viewer',
    'crm_pilot_operator',
    'crm_pilot_admin',
})

MODULE_COMMERCIAL = frozenset({
    'view_clients', 'view_contracts', 'view_billing',
    'add_client', 'change_client', 'delete_client',
    'add_contract', 'change_contract', 'delete_contract', 'upload_contract_file',
    'add_billing', 'change_billing',
})

MODULE_PROJECTS = frozenset({
    'view_tasks', 'view_projects', 'view_boards', 'view_task_recurrences', 'view_teams',
    'add_task', 'change_task', 'delete_task', 'move_task', 'assign_task', 'manage_watchers',
    'add_project', 'change_project', 'delete_project', 'manage_project_members',
    'add_board', 'change_board', 'delete_board', 'manage_board_columns', 'manage_board_access',
    'add_task_recurrence', 'change_task_recurrence', 'delete_task_recurrence',
})

MODULE_SETTINGS = frozenset({
    'view_settings', 'change_settings',
    'manage_service_types', 'manage_priorities', 'manage_status_tasks',
})

MODULE_ADMIN = frozenset({'run_task_scheduler'})

LEVEL_CHOICES = (
    ('none', 'Sem acesso'),
    ('read', 'Leitura'),
    ('operate', 'Operação'),
    ('full', 'Completo'),
)

SETTINGS_LEVEL_CHOICES = (
    ('none', 'Sem acesso'),
    ('read', 'Leitura'),
    ('manage', 'Gerenciar catálogos'),
)

COMMERCIAL_LEVELS = {
    'none': set(),
    'read': {'view_clients', 'view_contracts', 'view_billing'},
    'operate': {
        'view_clients', 'view_contracts', 'view_billing',
        'add_client', 'change_client',
        'add_contract', 'change_contract', 'upload_contract_file',
        'add_billing', 'change_billing',
    },
    'full': set(MODULE_COMMERCIAL),
}

PROJECTS_LEVELS = {
    'none': set(),
    'read': {
        'view_tasks', 'view_projects', 'view_boards', 'view_task_recurrences', 'view_teams',
    },
    'operate': {
        'view_tasks', 'view_projects', 'view_boards', 'view_task_recurrences', 'view_teams',
        'add_task', 'change_task', 'move_task', 'assign_task', 'manage_watchers',
        'add_project', 'change_project', 'manage_project_members',
        'add_board', 'change_board',
        'add_task_recurrence', 'change_task_recurrence',
    },
    'full': set(MODULE_PROJECTS),
}

SETTINGS_LEVELS = {
    'none': set(),
    'read': {'view_settings'},
    'manage': set(MODULE_SETTINGS),
}

PRESET_PROFILES = {
    'none': {
        'label': 'Sem acesso CRM',
        'commercial': 'none',
        'projects': 'none',
        'settings': 'none',
        'admin_scheduler': False,
        'pilot_group': None,
    },
    'viewer': {
        'label': 'Leitor (todos os módulos)',
        'commercial': 'read',
        'projects': 'read',
        'settings': 'read',
        'admin_scheduler': False,
        'pilot_group': 'crm_pilot_viewer',
    },
    'crm_commercial': {
        'label': 'CRM Comercial (operador)',
        'commercial': 'operate',
        'projects': 'read',
        'settings': 'read',
        'admin_scheduler': False,
        'pilot_group': None,
    },
    'projetos': {
        'label': 'Projetos e Kanban (operador)',
        'commercial': 'read',
        'projects': 'operate',
        'settings': 'none',
        'admin_scheduler': False,
        'pilot_group': None,
    },
    'operator': {
        'label': 'Operador completo',
        'commercial': 'operate',
        'projects': 'operate',
        'settings': 'read',
        'admin_scheduler': False,
        'pilot_group': 'crm_pilot_operator',
    },
    'admin': {
        'label': 'Administrador CRM',
        'commercial': 'full',
        'projects': 'full',
        'settings': 'manage',
        'admin_scheduler': True,
        'pilot_group': 'crm_pilot_admin',
    },
}

PERMISSION_LABELS = {
    'view_clients': 'Ver clientes',
    'add_client': 'Criar clientes',
    'change_client': 'Editar clientes',
    'delete_client': 'Excluir clientes',
    'view_contracts': 'Ver contratos',
    'add_contract': 'Criar contratos',
    'change_contract': 'Editar contratos',
    'delete_contract': 'Excluir contratos',
    'upload_contract_file': 'Anexar arquivos em contratos',
    'view_billing': 'Ver faturamento',
    'add_billing': 'Lançar faturamento',
    'change_billing': 'Editar faturamento',
    'view_tasks': 'Ver tarefas',
    'add_task': 'Criar tarefas',
    'change_task': 'Editar tarefas',
    'delete_task': 'Excluir tarefas',
    'move_task': 'Mover tarefas no Kanban',
    'assign_task': 'Atribuir responsáveis',
    'manage_watchers': 'Gerenciar observadores',
    'view_projects': 'Ver projetos',
    'add_project': 'Criar projetos',
    'change_project': 'Editar projetos',
    'delete_project': 'Excluir projetos',
    'manage_project_members': 'Gerenciar membros de projeto',
    'view_boards': 'Ver boards / Kanban',
    'add_board': 'Criar boards',
    'change_board': 'Editar boards',
    'delete_board': 'Excluir boards',
    'manage_board_columns': 'Gerenciar colunas do board',
    'manage_board_access': 'Gerenciar acesso ao board',
    'view_task_recurrences': 'Ver recorrências',
    'add_task_recurrence': 'Criar recorrências',
    'change_task_recurrence': 'Editar recorrências',
    'delete_task_recurrence': 'Excluir recorrências',
    'view_teams': 'Ver equipes (lookups)',
    'view_settings': 'Ver configurações CRM',
    'change_settings': 'Alterar configurações',
    'manage_service_types': 'Gerenciar tipos de serviço',
    'manage_priorities': 'Gerenciar prioridades',
    'manage_status_tasks': 'Gerenciar status de tarefas',
    'run_task_scheduler': 'Executar agendador de tarefas',
}


def _crm_permission_queryset():
    return Permission.objects.filter(content_type__app_label='crm').select_related('content_type')


def get_permissions_by_codename():
    return {p.codename: p for p in _crm_permission_queryset()}


def codenames_from_levels(*, commercial, projects, settings, admin_scheduler=False):
    """Monta conjunto de codenames a partir dos níveis por módulo."""
    codenames = set()
    codenames |= COMMERCIAL_LEVELS.get(commercial, set())
    codenames |= PROJECTS_LEVELS.get(projects, set())
    codenames |= SETTINGS_LEVELS.get(settings, set())
    if admin_scheduler:
        codenames |= MODULE_ADMIN
    return codenames & ALL_CRM_CODENAMES


def levels_from_codenames(codenames):
    """Infere níveis de módulo a partir de codenames efetivos."""
    codes = set(codenames) & ALL_CRM_CODENAMES

    def _level(module_levels, module_codes):
        if not codes & module_codes:
            return 'none'
        if module_codes <= codes:
            return 'full'
        operate = module_levels.get('operate', set())
        if operate and operate <= codes:
            return 'operate'
        return 'read'

    return {
        'commercial': _level(COMMERCIAL_LEVELS, MODULE_COMMERCIAL),
        'projects': _level(PROJECTS_LEVELS, MODULE_PROJECTS),
        'settings': (
            'manage'
            if MODULE_SETTINGS <= codes
            else ('read' if 'view_settings' in codes else 'none')
        ),
        'admin_scheduler': 'run_task_scheduler' in codes,
    }


def get_user_direct_crm_codenames(user):
    return set(
        user.user_permissions.filter(content_type__app_label='crm')
        .values_list('codename', flat=True)
    )


def get_user_group_crm_codenames(user):
    return set(
        Permission.objects.filter(
            group__user=user,
            content_type__app_label='crm',
        ).values_list('codename', flat=True)
    )


def get_user_effective_crm_codenames(user):
    if user.is_superuser:
        return set(ALL_CRM_CODENAMES)
    return get_user_direct_crm_codenames(user) | get_user_group_crm_codenames(user)


def get_user_crm_pilot_groups(user):
    return list(
        user.groups.filter(name__in=CRM_PILOT_GROUP_NAMES).values_list('name', flat=True)
    )


def user_has_commercial_access(user):
    codes = get_user_effective_crm_codenames(user)
    return bool(codes & COMMERCIAL_LEVELS['read'])


def user_has_projects_access(user):
    codes = get_user_effective_crm_codenames(user)
    return bool(codes & PROJECTS_LEVELS['read'])


def apply_user_crm_permissions(
    user,
    *,
    commercial,
    projects,
    settings,
    admin_scheduler=False,
    pilot_group=None,
    sync_direct=True,
):
    """
    Atualiza grupos piloto CRM e permissões diretas do usuário.

    ``sync_direct=True``: grava permissões diretas espelhando os níveis escolhidos
    (útil quando o perfil não usa só grupo piloto).
    """
    target_codenames = codenames_from_levels(
        commercial=commercial,
        projects=projects,
        settings=settings,
        admin_scheduler=admin_scheduler,
    )
    perms_by_codename = get_permissions_by_codename()
    target_permissions = [
        perms_by_codename[c] for c in sorted(target_codenames) if c in perms_by_codename
    ]

    pilot_groups = user.groups.filter(name__in=CRM_PILOT_GROUP_NAMES)
    user.groups.remove(*pilot_groups)
    if pilot_group and pilot_group in CRM_PILOT_GROUP_NAMES:
        from django.contrib.auth.models import Group

        group = Group.objects.filter(name=pilot_group).first()
        if group:
            user.groups.add(group)

    if sync_direct:
        direct_crm = user.user_permissions.filter(content_type__app_label='crm')
        user.user_permissions.remove(*direct_crm)
        user.user_permissions.add(*target_permissions)

    return target_codenames


def summarize_user_access(user):
    effective = get_user_effective_crm_codenames(user)
    levels = levels_from_codenames(effective)
    return {
        'effective_count': len(effective),
        'commercial': levels['commercial'],
        'projects': levels['projects'],
        'settings': levels['settings'],
        'admin_scheduler': levels['admin_scheduler'],
        'pilot_groups': get_user_crm_pilot_groups(user),
        'has_commercial': user_has_commercial_access(user),
        'has_projects': user_has_projects_access(user),
    }
