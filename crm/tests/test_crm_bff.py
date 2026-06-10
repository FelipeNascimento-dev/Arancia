"""Testes mínimos do módulo CRM BFF."""

from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase, override_settings

from crm.services.context import build_crm_headers
from crm.tasks import crm_fire_due_alerts, crm_generate_recurring_tasks


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


class CeleryCrmTasksTests(TestCase):
    @override_settings(CRM_API_BASE_URL='', CRM_INTERNAL_API_SECRET='')
    def test_fire_due_alerts_skips_when_crm_not_configured(self):
        result = crm_fire_due_alerts()
        self.assertEqual(result, 'CRM não configurado.')

    @override_settings(CRM_API_BASE_URL='', CRM_INTERNAL_API_SECRET='')
    def test_generate_recurring_tasks_skips_when_crm_not_configured(self):
        result = crm_generate_recurring_tasks()
        self.assertEqual(result, 'CRM não configurado.')

