"""Testes mínimos do módulo CRM BFF."""

import json
from unittest.mock import MagicMock, patch
from uuid import UUID

from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, TestCase, override_settings
from django.utils import timezone

from crm.forms.forms_tasks import TaskForm, TaskLinkForm
from crm.services.calendar import tasks_to_calendar_events
from crm.services.context import build_crm_headers
from crm.services.exceptions import CrmApiError
from crm.services.lookups import (
    build_designation_choices,
    build_gai_requester_choices,
    build_group_choices,
    build_user_choices,
    extract_requester_gai_ids,
    fetch_member_lookups_django,
    normalize_lookup_list,
    resolve_member_lookups,
)
from crm.services.recurrences import (
    build_recurrence_create_payload,
    frequency_to_rrule,
    recurrence_start_is_due,
    run_scheduler_for_template,
    validate_board_can_create,
)
from crm.services.refs import (
    contract_ref_label,
    customer_ref_label,
    subject_ref_label,
    task_ref_label,
)
from crm.tasks import crm_fire_due_alerts, crm_generate_recurring_tasks
from logistica.models import GroupAditionalInformation, PermissaoUsuarioDummy, UserDesignation


class BuildCrmHeadersTests(TestCase):
    def test_headers_contain_user_context_without_raw_secret(self):
        user = User.objects.create_user(username='ARC_test', password='x')
        headers = build_crm_headers(user)
        self.assertTrue(headers['Authorization'].startswith('Bearer '))
        self.assertEqual(headers['X-CRM-User-ID'], str(user.id))
        self.assertEqual(headers['X-CRM-Username'], 'ARC_test')
        self.assertIn('X-CRM-Designation-IDs', headers)


class AjaxGaiGateTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='ARC_nogai', password='x')

    def test_ajax_require_gai_rejects_user_without_gai(self):
        from crm.services.gates import ajax_require_gai

        request = self.factory.post('/crm/ajax/tasks/x/move/')
        request.user = self.user
        with patch('crm.services.gates.get_user_gai_id', return_value=None):
            response = ajax_require_gai(request)
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'ok': False, 'error': 'Usuário sem GAI configurado.'})

    def test_ajax_require_gai_allows_user_with_gai(self):
        from crm.services.gates import ajax_require_gai

        request = self.factory.post('/crm/ajax/tasks/x/move/')
        request.user = self.user
        with patch('crm.services.gates.get_user_gai_id', return_value=42):
            self.assertIsNone(ajax_require_gai(request))

    def test_require_gai_or_render_blocks_html_view(self):
        from crm.services.gates import require_gai_or_render

        request = self.factory.get('/crm/tasks/')
        request.user = self.user
        with patch('crm.services.gates.get_user_gai_id', return_value=None):
            response = require_gai_or_render(
                request,
                'crm/tasks/list.html',
                site_title='CRM — Tarefas',
                menu_context={'current_menu': 'x'},
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'GAI', response.content)


class MemberLookupsFallbackTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.group = Group.objects.create(name='arancia_PA')
        cls.gai_a = GroupAditionalInformation.objects.create(
            group=cls.group,
            nome='PA Alpha',
            sales_channel='SC1',
        )
        cls.gai_b = GroupAditionalInformation.objects.create(
            group=cls.group,
            nome='PA Beta',
            sales_channel='SC2',
        )
        cls.requester = User.objects.create_user(username='ARC_req', password='x')
        UserDesignation.objects.create(user=cls.requester, informacao_adicional=cls.gai_a)
        cls.peer = User.objects.create_user(username='ARC_peer', password='x')
        UserDesignation.objects.create(user=cls.peer, informacao_adicional=cls.gai_a)
        cls.other_channel = User.objects.create(username='ARC_other', password='x')
        UserDesignation.objects.create(user=cls.other_channel, informacao_adicional=cls.gai_b)

    def test_django_fallback_lists_users_in_same_sales_channel(self):
        data = fetch_member_lookups_django(self.requester)
        user_ids = {item['id'] for item in data['users']}
        self.assertIn(self.requester.id, user_ids)
        self.assertIn(self.peer.id, user_ids)
        self.assertNotIn(self.other_channel.id, user_ids)

    def test_django_fallback_builds_choices(self):
        data = fetch_member_lookups_django(self.requester)
        choices = build_user_choices(data)
        self.assertTrue(any(value == str(self.peer.id) for value, _ in choices))
        des_choices = build_designation_choices(data)
        self.assertTrue(any('ARC_peer' in label for _, label in des_choices))

    def test_resolve_member_lookups_falls_back_when_api_fails(self):
        with patch('crm.services.lookups.fetch_member_lookups', side_effect=CrmApiError('404')):
            data = resolve_member_lookups(self.requester)
        self.assertIn(self.peer.id, {item['id'] for item in data['users']})

    def test_resolve_member_lookups_falls_back_when_api_returns_empty(self):
        with patch('crm.services.lookups.fetch_member_lookups', return_value={'users': [], 'designations': []}):
            data = resolve_member_lookups(self.requester)
        self.assertIn(self.peer.id, {item['id'] for item in data['users']})

    def test_gestao_total_sees_users_from_other_sales_channel(self):
        ct = ContentType.objects.get_for_model(PermissaoUsuarioDummy)
        perm = Permission.objects.get(codename='gestao_total', content_type=ct)
        manager = User.objects.create_user(username='ARC_mgr', password='x')
        UserDesignation.objects.create(user=manager, informacao_adicional=self.gai_a)
        manager.user_permissions.add(perm)

        data = fetch_member_lookups_django(manager)
        user_ids = {item['id'] for item in data['users']}
        self.assertIn(self.other_channel.id, user_ids)


class CalendarEventsTests(TestCase):
    def test_scheduled_task_becomes_calendar_event(self):
        tasks = [{
            'id': '11111111-1111-1111-1111-111111111111',
            'title': 'Reunião',
            'scheduled_at': '2026-06-10T14:00:00.000Z',
            'priority_name': 'Alta',
        }]
        events = tasks_to_calendar_events(tasks)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['title'], 'Reunião')
        self.assertIn('scheduled-11111111', events[0]['id'])
        self.assertEqual(events[0]['backgroundColor'], '#e74c3c')

    def test_due_only_task_when_include_due(self):
        tasks = [{
            'id': '22222222-2222-2222-2222-222222222222',
            'title': 'Entrega',
            'due_at': '2026-06-15T23:59:00.000Z',
        }]
        events = tasks_to_calendar_events(tasks, include_due=True)
        self.assertEqual(len(events), 1)
        self.assertTrue(events[0]['title'].startswith('Vence:'))
        self.assertTrue(events[0]['allDay'])


class RecurrenceServiceTests(TestCase):
    def test_frequency_to_rrule_weekly_with_interval(self):
        self.assertEqual(frequency_to_rrule('weekly', 2), 'FREQ=WEEKLY;INTERVAL=2')

    def test_build_recurrence_create_payload_uses_rrule_and_start_at(self):
        payload = build_recurrence_create_payload({
            'title': 'Checklist',
            'frequency': 'daily',
            'interval': 1,
            'recurrence_start': '2026-06-01',
            'board_id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
        })
        self.assertEqual(payload['rrule'], 'FREQ=DAILY')
        self.assertTrue(payload['start_at'].startswith('2026-06-01'))
        self.assertEqual(payload['board_id'], 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa')

    def test_recurrence_start_is_due_past_date(self):
        past = (timezone.now() - timezone.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
        self.assertTrue(recurrence_start_is_due(past))

    def test_run_scheduler_for_template_parses_results(self):
        template_id = UUID('11111111-1111-1111-1111-111111111111')
        task_id = UUID('22222222-2222-2222-2222-222222222222')
        client = MagicMock()
        client.post.return_value = {
            'results': [
                {'template_id': str(template_id), 'task_id': str(task_id)},
            ],
        }
        self.assertEqual(
            run_scheduler_for_template(template_id, client=client),
            str(task_id),
        )
        client.post.assert_called_once_with('/internal/scheduler/generate-due-tasks', json={})

    def test_validate_board_can_create_blocks_when_false(self):
        user = User.objects.create_user(username='ARC_board', password='x')
        with patch(
            'crm.services.recurrences.CrmApiClient',
        ) as mock_client_cls:
            mock_client_cls.return_value.get.return_value = {'can_create_tasks': False}
            self.assertEqual(
                validate_board_can_create(user, 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
                'Você não tem permissão para criar tarefas neste board.',
            )


class TaskNewUnifiedFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.group = Group.objects.create(name='arancia_PA')
        cls.gai = GroupAditionalInformation.objects.create(
            group=cls.group,
            nome='PA Test',
            sales_channel='SC1',
        )
        cls.user = User.objects.create_user(username='ARC_tasknew', password='x')
        UserDesignation.objects.create(user=cls.user, informacao_adicional=cls.gai)
        crm_ct, _ = ContentType.objects.get_or_create(app_label='crm', model='crmdummy')
        log_ct = ContentType.objects.get_for_model(PermissaoUsuarioDummy)

        def _perm(codename, ct, name):
            perm, _ = Permission.objects.get_or_create(
                codename=codename,
                content_type=ct,
                defaults={'name': name},
            )
            return perm

        cls.add_task_perm = _perm('add_task', crm_ct, 'Can add task')
        cls.add_recurrence_perm = _perm('add_task_recurrence', crm_ct, 'Can add task recurrence')
        cls.view_tasks_perm = _perm('view_tasks', crm_ct, 'Can view tasks')
        cls.acesso_perm = Permission.objects.get(codename='acesso_arancia', content_type=log_ct)

    def setUp(self):
        self.factory = RequestFactory()
        self.user.user_permissions.add(
            self.acesso_perm,
            self.view_tasks_perm,
            self.add_task_perm,
            self.add_recurrence_perm,
        )

    def _post_task_new(self, data, user=None):
        from crm.views.view_tasks import task_new

        request = self.factory.post('/crm/tasks/new/', data)
        request.user = user or self.user
        request.session = {}
        request._messages = MagicMock()
        return task_new(request)

    def test_task_new_without_create_permissions_raises_permission_denied(self):
        viewer = User.objects.create_user(username='ARC_viewer', password='x')
        UserDesignation.objects.create(user=viewer, informacao_adicional=self.gai)
        viewer.user_permissions.add(self.acesso_perm, self.view_tasks_perm)

        with self.assertRaises(PermissionDenied):
            self._post_task_new({'title': 'Sem permissão'}, user=viewer)

    def test_recurring_past_start_triggers_scheduler(self):
        template_id = '33333333-3333-3333-3333-333333333333'
        task_id = '44444444-4444-4444-4444-444444444444'
        past = (timezone.now() - timezone.timedelta(days=2)).strftime('%Y-%m-%d')

        data = {
            'task_kind': 'recurring',
            'title': 'Recorrente vencida',
            'frequency': 'daily',
            'recurrence_start': past,
            'interval': '1',
        }
        with patch('crm.views.view_tasks.fetch_crm_lookups', return_value={}), \
             patch('crm.views.view_tasks.validate_board_can_create', return_value=None), \
             patch('crm.views.view_tasks.run_scheduler_for_template', return_value=task_id) as mock_sched, \
             patch('crm.views.view_tasks.CrmApiClient') as mock_api_cls:
            mock_api = mock_api_cls.return_value
            mock_api.post.return_value = {'id': template_id}
            response = self._post_task_new(data)
            mock_sched.assert_called_once_with(template_id)
            self.assertEqual(response.status_code, 302)
            self.assertIn(task_id, response.url)


class TaskFormRecurrencePayloadTests(TestCase):
    def test_cleaned_recurrence_payload_delegates_to_service(self):
        form = TaskForm(
            data={
                'task_kind': 'recurring',
                'title': 'Semanal',
                'frequency': 'weekly',
                'interval': '2',
                'recurrence_start': '2026-06-10',
            },
            show_task_kind=True,
            board_choices=[],
            status_choices=[],
            priority_choices=[],
            project_choices=[],
            customer_choices=[],
        )
        self.assertTrue(form.is_valid(), form.errors)
        payload = form.cleaned_recurrence_payload()
        self.assertEqual(payload['rrule'], 'FREQ=WEEKLY;INTERVAL=2')
        self.assertIn('start_at', payload)


class TaskLinkFormTests(TestCase):
    def test_cleaned_payload_uses_target_task_id(self):
        form = TaskLinkForm(data={
            'target_task_id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
            'link_type': 'related',
        })
        self.assertTrue(form.is_valid(), form.errors)
        payload = form.cleaned_payload()
        self.assertEqual(payload['target_task_id'], 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa')
        self.assertNotIn('linked_task_id', payload)


class RequesterGaiLookupsTests(TestCase):
    def test_normalize_lookup_list_from_envelope(self):
        raw = {'items': [{'gai_id': 1, 'nome': 'PA A'}]}
        self.assertEqual(len(normalize_lookup_list(raw)), 1)

    def test_build_priority_choices_reads_prioritys_key(self):
        from crm.services.lookups import build_priority_choices

        lookups = {'prioritys': [{'id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'name': 'Alta'}]}
        choices = build_priority_choices(lookups)
        self.assertEqual(choices, [('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Alta')])

    def test_build_group_and_gai_choices(self):
        groups = build_group_choices([{'group_id': 27, 'group_name': 'arancia_client'}])
        self.assertEqual(groups, [('27', 'arancia_client')])
        groups_legacy = build_group_choices([{'id': 3, 'name': 'arancia_PA'}])
        self.assertEqual(groups_legacy, [('3', 'arancia_PA')])
        gais = build_gai_requester_choices([{'gai_id': 10, 'nome': 'Cliente X'}])
        self.assertEqual(gais, [('10', 'Cliente X')])

    def test_build_new_client_gai_choices_uses_arancia_client_group(self):
        from unittest.mock import patch

        from crm.services.lookups import build_new_client_gai_choices

        user = object()
        lookups = {'customers': [{'gai_id': 28, 'razao_social': 'CLARO'}]}
        with patch('crm.services.lookups.resolve_crm_client_group_id', return_value=27), patch(
            'crm.services.lookups.fetch_gais',
            return_value=[
                {'gai_id': 100, 'razao_social': 'Novo Corp', 'cnpj': '123'},
                {'gai_id': 28, 'nome': 'CLARO'},
            ],
        ) as mock_fetch:
            choices = build_new_client_gai_choices(user, lookups)
        mock_fetch.assert_called_once_with(user, group_id=27)
        self.assertEqual(choices, [('100', 'Novo Corp (123)')])

    def test_extract_requester_gai_ids_from_nested_response(self):
        task = {
            'requesters': [
                {'gai_id': 5},
                {'gai': {'id': 6, 'nome': 'Y'}},
            ],
        }
        self.assertEqual(extract_requester_gai_ids(task), ['5', '6'])


class TaskFormRequesterPayloadTests(TestCase):
    def test_cleaned_payload_includes_requester_gai_ids(self):
        form = TaskForm(
            data={
                'title': 'Projeto X',
                'project_id': '11111111-1111-1111-1111-111111111111',
                'requester_gai_ids': ['10', '20'],
            },
            board_choices=[],
            status_choices=[],
            priority_choices=[],
            project_choices=[('11111111-1111-1111-1111-111111111111', 'Projeto X')],
            customer_choices=[],
            show_requesters=True,
            group_choices=[],
            requester_gai_choices=[('10', 'GAI 10'), ('20', 'GAI 20')],
        )
        self.assertTrue(form.is_valid(), form.errors)
        payload = form.cleaned_payload()
        self.assertEqual(payload['requester_gai_ids'], [10, 20])

    def test_recurrence_payload_includes_requester_gai_ids(self):
        payload = build_recurrence_create_payload({
            'title': 'Checklist',
            'frequency': 'daily',
            'interval': 1,
            'recurrence_start': '2026-06-01',
            'requester_gai_ids': ['42'],
        })
        self.assertEqual(payload['requester_gai_ids'], [42])


class ProjectFormTests(TestCase):
    def test_cleaned_payload_generates_code_from_name(self):
        from crm.forms.forms_projects import ProjectForm

        form = ProjectForm(data={
            'name': 'Projetinho Felas',
            'customer_gai_id': '29',
            'is_active': True,
        }, customer_choices=[('29', 'Cliente')])
        self.assertTrue(form.is_valid(), form.errors)
        payload = form.cleaned_payload()
        self.assertEqual(payload['code'], 'projetinho-felas')
        self.assertEqual(payload['name'], 'Projetinho Felas')
        self.assertEqual(payload['customer_gai_id'], 29)


class TaskFieldNormalizationTests(TestCase):
    def test_normalize_maps_homolog_date_fields(self):
        from crm.services.tasks import enrich_task, normalize_task_fields

        raw = {
            'id': '11111111-1111-1111-1111-111111111111',
            'due_date': '2026-06-15',
            'scheduled_start_at': None,
        }
        normalized = normalize_task_fields(raw)
        self.assertEqual(normalized['due_at'], '2026-06-15')
        self.assertIsNone(normalized['scheduled_at'])

    def test_enrich_task_does_not_raise_on_missing_legacy_keys(self):
        from crm.services.tasks import enrich_task

        task = enrich_task({
            'id': '22222222-2222-2222-2222-222222222222',
            'title': 'Fake homolog',
            'due_date': None,
            'scheduled_start_at': None,
        })
        self.assertIn('due_at', task)
        self.assertIn('scheduled_at', task)


    def test_move_status_label_uses_nested_ref(self):
        from crm.services.refs import move_status_label, moved_by_label

        entry = {
            'from_status': {'name': 'A fazer'},
            'to_status': {'name': 'Em andamento'},
            'moved_by': {'username': 'ARC0007'},
        }
        self.assertEqual(move_status_label(entry, direction='from'), 'A fazer')
        self.assertEqual(move_status_label(entry, direction='to'), 'Em andamento')
        self.assertEqual(moved_by_label(entry), 'ARC0007')

    def test_enrich_move_history_adds_flat_fallbacks(self):
        from crm.services.tasks import enrich_move_history

        rows = enrich_move_history([{
            'from_status': {'name': 'A fazer'},
            'to_status': {'name': 'Em andamento'},
            'moved_by': {'username': 'ARC0007'},
        }])
        self.assertEqual(rows[0]['from_status_name'], 'A fazer')
        self.assertEqual(rows[0]['moved_by_username'], 'ARC0007')


class CeleryCrmTasksTests(TestCase):
    @override_settings(CRM_API_BASE_URL='', CRM_INTERNAL_API_SECRET='')
    def test_fire_due_alerts_skips_when_crm_not_configured(self):
        result = crm_fire_due_alerts()
        self.assertEqual(result, 'CRM não configurado.')

    @override_settings(CRM_API_BASE_URL='', CRM_INTERNAL_API_SECRET='')
    def test_generate_recurring_tasks_skips_when_crm_not_configured(self):
        result = crm_generate_recurring_tasks()
        self.assertEqual(result, 'CRM não configurado.')


class EntityRefLabelTests(TestCase):
    def test_customer_ref_label_prefers_nested_razao_social(self):
        record = {
            'customer': {'razao_social': 'Cliente Alpha', 'gai_id': 10},
            'customer_gai_id': 10,
        }
        self.assertEqual(customer_ref_label(record), 'Cliente Alpha')

    def test_customer_ref_label_falls_back_to_gai_id(self):
        record = {'customer_gai_id': 99}
        self.assertEqual(customer_ref_label(record), 'GAI 99')

    def test_contract_ref_label_uses_nested_title(self):
        record = {'contract': {'title': 'Contrato Anual'}, 'contract_id': 'abc'}
        self.assertEqual(contract_ref_label(record), 'Contrato Anual')

    def test_subject_ref_label_user_username(self):
        access = {'subject': {'username': 'ARC_user', 'subject_type': 'user'}}
        self.assertEqual(subject_ref_label(access), 'ARC_user')

    def test_subject_ref_label_customer_gai(self):
        access = {'subject': {'razao_social': 'PA Norte', 'subject_type': 'customer_gai'}}
        self.assertEqual(subject_ref_label(access), 'PA Norte')

    def test_task_ref_label_from_nested_task(self):
        run = {
            'task_id': '22222222-2222-2222-2222-222222222222',
            'task': {'title': 'Checklist diário', 'id': '22222222-2222-2222-2222-222222222222'},
        }
        self.assertEqual(task_ref_label(run), 'Checklist diário')


class CalendarRefTests(TestCase):
    def test_calendar_event_uses_status_ref(self):
        tasks = [{
            'id': '11111111-1111-1111-1111-111111111111',
            'title': 'Reunião',
            'scheduled_at': '2026-06-10T14:00:00.000Z',
            'status': {'name': 'Em andamento'},
            'priority': {'name': 'Alta', 'slug': 'alta'},
        }]
        events = tasks_to_calendar_events(tasks)
        self.assertEqual(events[0]['extendedProps']['status'], 'Em andamento')
        self.assertEqual(events[0]['extendedProps']['priority'], 'Alta')


class CrmHomologSmokeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.group = Group.objects.create(name='arancia_PA')
        cls.gai = GroupAditionalInformation.objects.create(
            group=cls.group,
            nome='PA Smoke',
            sales_channel='SC1',
        )
        cls.user = User.objects.create_user(username='ARC_smoke', password='x', is_staff=True)
        UserDesignation.objects.create(user=cls.user, informacao_adicional=cls.gai)
        log_ct = ContentType.objects.get_for_model(PermissaoUsuarioDummy)
        crm_ct, _ = ContentType.objects.get_or_create(app_label='crm', model='crmdummy')
        cls.acesso_perm = Permission.objects.get(codename='acesso_arancia', content_type=log_ct)
        cls.view_clients_perm, _ = Permission.objects.get_or_create(
            codename='view_clients',
            content_type=crm_ct,
            defaults={'name': 'Can view clients'},
        )
        cls.user.user_permissions.add(cls.acesso_perm, cls.view_clients_perm)

    def setUp(self):
        self.factory = RequestFactory()

    def test_ajax_health_proxies_api_root(self):
        from crm.views.view_dashboard import ajax_health

        request = self.factory.get('/crm/ajax/health/')
        request.user = self.user
        mock_response = MagicMock()
        mock_response.status_code = 200
        with patch('crm.views.view_dashboard.CrmApiClient') as mock_cls:
            mock_cls.return_value.health_check.return_value = mock_response
            response = ajax_health(request)
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertTrue(payload['ok'])

    def test_validate_context_calls_auth_endpoint(self):
        from crm.views.view_dashboard import validate_context

        request = self.factory.post('/crm/diagnostic/validate-context/')
        request.user = self.user
        request.session = {}
        request._messages = MagicMock()
        with patch('crm.views.view_dashboard.CrmApiClient') as mock_cls:
            mock_cls.return_value.post.return_value = {'valid': True, 'user_id': self.user.id}
            response = validate_context(request)
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertTrue(payload['ok'])
        mock_cls.return_value.post.assert_called_once_with('/auth/validate-context', json={})

    def test_me_context_cached_in_session(self):
        from crm.services.context import get_cached_me_context

        request = self.factory.get('/crm/')
        request.user = self.user
        request.session = {}
        me_context = {'accessible_boards': [{'id': 'aaa', 'name': 'Board A'}]}
        with patch('crm.services.context.CRM_CONTEXT_TTL_SECONDS', 300):
            result = get_cached_me_context(
                request,
                client_factory=lambda: MagicMock(get=MagicMock(return_value=me_context)),
            )
        self.assertEqual(result, me_context)
        self.assertEqual(request.session.get('crm_me_context'), me_context)

