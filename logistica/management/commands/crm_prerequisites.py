"""
Fase 0 — pré-requisitos da integração CRM.

Valida permissões crm.* no banco compartilhado (seed Alembic da API),
confirma configuração de URLs/secret e cria grupos piloto no Django Admin.

Uso:
    python manage.py crm_prerequisites
    python manage.py crm_prerequisites --skip-groups
    python manage.py crm_prerequisites --check-api
"""

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

# Permissões esperadas pelo plano de integração (41 codenames do seed Alembic).
EXPECTED_CRM_PERMISSIONS = frozenset({
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

CRM_PILOT_GROUPS = {
    'crm_pilot_viewer': {
        'description': 'Leitura em todos os módulos CRM (usuários piloto)',
        'codenames': {
            c for c in EXPECTED_CRM_PERMISSIONS if c.startswith('view_')
        },
    },
    'crm_pilot_operator': {
        'description': (
            'Operação diária: leitura + criação/edição de clientes, contratos, '
            'faturamento, tasks, projetos e boards; mover/atribuir tasks'
        ),
        'codenames': {
            c for c in EXPECTED_CRM_PERMISSIONS if c.startswith('view_')
        } | {
            'add_client', 'change_client', 'add_contract', 'change_contract',
            'upload_contract_file', 'add_billing', 'change_billing',
            'add_task', 'change_task', 'move_task', 'assign_task',
            'add_project', 'change_project', 'add_board', 'change_board',
        },
    },
    'crm_pilot_admin': {
        'description': 'Acesso total CRM (gestores piloto)',
        'codenames': set(EXPECTED_CRM_PERMISSIONS),
    },
}


class Command(BaseCommand):
    help = (
        'Valida pré-requisitos da integração CRM: config, permissões crm.* '
        'e grupos piloto no Admin.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-groups',
            action='store_true',
            help='Apenas validar config e permissões; não criar/atualizar grupos.',
        )
        parser.add_argument(
            '--check-api',
            action='store_true',
            help='Tentar GET na raiz da API CRM (health).',
        )

    def handle(self, *args, **options):
        ok = True
        ok &= self._check_config()
        ok &= self._check_permissions()
        if options['check_api']:
            ok &= self._check_api_health()
        if not options['skip_groups']:
            self._ensure_pilot_groups()
        if ok:
            self.stdout.write(self.style.SUCCESS('Pré-requisitos CRM: OK'))
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Pré-requisitos CRM: pendências encontradas (ver mensagens acima).'
                )
            )

    def _check_config(self):
        self.stdout.write('--- Configuração CRM ---')
        base_url = getattr(settings, 'CRM_API_BASE_URL', '')
        secret = getattr(settings, 'CRM_INTERNAL_API_SECRET', '')
        v1 = getattr(settings, 'CRM_API_V1_STR', '/api/v1')

        self.stdout.write(f'  CRM_API_BASE_URL: {base_url or "(vazio)"}')
        self.stdout.write(f'  CRM_API_V1_STR: {v1}')
        self.stdout.write(
            f'  CRM_INTERNAL_API_SECRET: {"(configurado)" if secret else "(vazio — definir CRM_INTERNAL_API_SECRET)"}'
        )
        self.stdout.write(f'  URL API completa: {base_url}{v1}')

        if not base_url:
            self.stdout.write(self.style.ERROR('  CRM_API_BASE_URL não configurada.'))
            return False
        if not secret:
            self.stdout.write(
                self.style.WARNING(
                    '  Secret não configurado. Obter com infra e definir '
                    'CRM_INTERNAL_API_SECRET no ambiente ou local_settings.'
                )
            )
        return True

    def _check_permissions(self):
        self.stdout.write('--- Permissões crm.* (auth_permission) ---')
        db_codenames = set(
            Permission.objects.filter(content_type__app_label='crm')
            .values_list('codename', flat=True)
        )
        missing = EXPECTED_CRM_PERMISSIONS - db_codenames
        extra = db_codenames - EXPECTED_CRM_PERMISSIONS

        self.stdout.write(f'  Encontradas: {len(db_codenames)}')
        if missing:
            self.stdout.write(
                self.style.ERROR(f'  Faltando ({len(missing)}): {sorted(missing)}')
            )
        else:
            self.stdout.write(self.style.SUCCESS('  Todas as 41 permissões esperadas presentes.'))

        if extra:
            self.stdout.write(
                self.style.WARNING(f'  Extras no banco ({len(extra)}): {sorted(extra)}')
            )

        content_types = (
            Permission.objects.filter(content_type__app_label='crm')
            .values_list('content_type__model', flat=True)
            .distinct()
        )
        self.stdout.write(f'  Content types: {sorted(set(content_types))}')
        return not missing

    def _check_api_health(self):
        self.stdout.write('--- Health API CRM ---')
        base_url = getattr(settings, 'CRM_API_BASE_URL', '').rstrip('/')
        if not base_url:
            self.stdout.write(self.style.ERROR('  URL não configurada; pulando health check.'))
            return False
        try:
            import httpx
        except ImportError:
            self.stdout.write(self.style.WARNING('  httpx não instalado; pulando health check.'))
            return True

        timeout = getattr(settings, 'CRM_API_TIMEOUT', 30)
        verify = getattr(settings, 'CRM_API_VERIFY_SSL', True)
        try:
            response = httpx.get(f'{base_url}/', timeout=timeout, verify=verify)
            self.stdout.write(f'  GET {base_url}/ -> HTTP {response.status_code}')
            if response.status_code < 400:
                return True
            self.stdout.write(
                self.style.WARNING(
                    '  Servidor acessivel, mas resposta nao-2xx — confirmar path '
                    'de health e deploy da API com infra.'
                )
            )
            return False
        except httpx.RequestError as exc:
            self.stdout.write(
                self.style.WARNING(f'  Não foi possível conectar: {exc}')
            )
            return False

    def _ensure_pilot_groups(self):
        self.stdout.write('--- Grupos piloto Django Admin ---')
        all_crm_perms = {
            p.codename: p
            for p in Permission.objects.filter(content_type__app_label='crm')
        }

        for group_name, spec in CRM_PILOT_GROUPS.items():
            group, created = Group.objects.get_or_create(name=group_name)
            perms = [
                all_crm_perms[c]
                for c in spec['codenames']
                if c in all_crm_perms
            ]
            group.permissions.set(perms)
            action = 'Criado' if created else 'Atualizado'
            self.stdout.write(
                f'  {action}: {group_name} ({len(perms)} permissões) — {spec["description"]}'
            )
            self.stdout.write(
                self.style.SUCCESS(
                    '    Atribua este grupo a usuários piloto no Admin '
                    '(além do grupo skill arancia_* com logistica.acesso_arancia).'
                )
            )
