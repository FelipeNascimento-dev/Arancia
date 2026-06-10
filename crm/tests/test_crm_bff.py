"""Testes mínimos do módulo CRM BFF."""

from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase, override_settings

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from crm.services.context import build_crm_headers
from crm.services.exceptions import CrmApiError
from crm.services.lookups import (
    build_designation_choices,
    build_user_choices,
    fetch_member_lookups_django,
    resolve_member_lookups,
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
        from crm.views.view_tasks import _ajax_require_gai

        request = self.factory.post('/crm/ajax/tasks/x/move/')
        request.user = self.user
        with patch('crm.views.view_tasks.get_user_gai_id', return_value=None):
            response = _ajax_require_gai(request)
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'ok': False, 'error': 'Usuário sem GAI configurado.'})

    def test_ajax_require_gai_allows_user_with_gai(self):
        from crm.views.view_tasks import _ajax_require_gai

        request = self.factory.post('/crm/ajax/tasks/x/move/')
        request.user = self.user
        with patch('crm.views.view_tasks.get_user_gai_id', return_value=42):
            self.assertIsNone(_ajax_require_gai(request))


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


class CeleryCrmTasksTests(TestCase):
    @override_settings(CRM_API_BASE_URL='', CRM_INTERNAL_API_SECRET='')
    def test_fire_due_alerts_skips_when_crm_not_configured(self):
        result = crm_fire_due_alerts()
        self.assertEqual(result, 'CRM não configurado.')

    @override_settings(CRM_API_BASE_URL='', CRM_INTERNAL_API_SECRET='')
    def test_generate_recurring_tasks_skips_when_crm_not_configured(self):
        result = crm_generate_recurring_tasks()
        self.assertEqual(result, 'CRM não configurado.')

