import base64
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings

from crm_api.context import (
    build_basic_token,
    build_crm_headers,
    build_crm_headers_from_request,
    build_scheduler_headers,
)
from crm_api.exceptions import CrmAuthError
from crm_api.payloads import (
    board_access_payload,
    build_rrule,
    parse_rrule,
    recurrence_payload,
    service_type_payload,
    task_payload,
)
from crm_api.session_credentials import (
    clear_password_from_session,
    get_password_from_session,
    store_password_in_session,
)
from crm.views.views_tasks._helpers import can_comment_on_board


class BuildCrmHeadersTests(SimpleTestCase):
    @override_settings(CRM_API_KEY="test-key")
    def test_build_crm_headers_includes_basic_and_api_key(self):
        user = Mock(is_authenticated=True, username="joao")
        headers = build_crm_headers(user=user, password="secret")
        self.assertEqual(headers["X-API-Key"], "test-key")
        self.assertTrue(headers["Authorization"].startswith("Basic "))
        token = headers["Authorization"].split(" ", 1)[1]
        decoded = base64.b64decode(token).decode("utf-8")
        self.assertEqual(decoded, "joao:secret")

    def test_build_basic_token(self):
        token = build_basic_token("user", "pass")
        self.assertEqual(base64.b64decode(token).decode("utf-8"), "user:pass")

    @override_settings(CRM_INTERNAL_API_SECRET="scheduler-secret")
    def test_build_scheduler_headers(self):
        headers = build_scheduler_headers()
        self.assertEqual(headers["Authorization"], "Bearer scheduler-secret")


class SessionCredentialsTests(TestCase):
    @override_settings(
        SECRET_KEY="test-secret-key-for-fernet-derivation",
        CRM_API_KEY="test-key",
    )
    def test_session_password_roundtrip(self):
        request = RequestFactory().get("/")
        request.session = self.client.session
        store_password_in_session(request, "my-password")
        self.assertEqual(get_password_from_session(request), "my-password")
        clear_password_from_session(request)
        self.assertIsNone(get_password_from_session(request))

    @override_settings(CRM_API_KEY="test-key")
    def test_build_crm_headers_from_request_without_session_raises(self):
        user = User(username="joao", is_active=True)
        request = RequestFactory().get("/")
        request.user = user
        request.session = {}
        with self.assertRaises(CrmAuthError):
            build_crm_headers_from_request(request)


class ClientMaskTests(SimpleTestCase):
    def test_crm_client_masks_basic_in_logs(self):
        from crm_api.client import _mask_headers

        masked = _mask_headers({
            "Authorization": "Basic abc123",
            "X-API-Key": "real-key",
        })
        self.assertEqual(masked["Authorization"], "Basic ***")
        self.assertEqual(masked["X-API-Key"], "***")


class PayloadTests(SimpleTestCase):
    def test_build_and_parse_rrule(self):
        rrule = build_rrule("weekly", 2)
        self.assertEqual(rrule, "FREQ=WEEKLY;INTERVAL=2")
        freq, interval = parse_rrule(rrule)
        self.assertEqual(freq, "weekly")
        self.assertEqual(interval, 2)

    def test_recurrence_payload_includes_rrule(self):
        from datetime import datetime

        cleaned = {
            "title": "T",
            "board_id": 1,
            "status_id": 2,
            "priority_id": 3,
            "recurrence_frequency": "daily",
            "recurrence_interval": 1,
            "scheduled_start_at": datetime(2026, 6, 17, 10, 0),
        }
        payload = recurrence_payload(cleaned)
        self.assertIn("rrule", payload)
        self.assertEqual(payload["rrule"], "FREQ=DAILY")
        self.assertIn("start_at", payload)

    def test_task_payload_requester_gai_ids_only_with_project(self):
        cleaned = {
            "title": "T",
            "board_id": 1,
            "requester_gai_ids": [10, 20],
        }
        without_project = task_payload(cleaned)
        self.assertNotIn("requester_gai_ids", without_project)
        cleaned["project_id"] = 5
        with_project = task_payload(cleaned)
        self.assertEqual(with_project["requester_gai_ids"], [10, 20])

    def test_board_access_payload_customer_gai(self):
        payload = board_access_payload({
            "grant_type": "customer_gai",
            "customer_gai_id": 42,
            "access_level": "editor",
        })
        self.assertEqual(payload["subject_type"], "customer_gai")
        self.assertEqual(payload["subject_id"], 42)
        self.assertEqual(payload["access_level"], "editor")

    def test_service_type_payload_fields(self):
        payload = service_type_payload({
            "type": "support",
            "description": "Suporte",
            "status_initial_id": 1,
            "client_id": 99,
            "direction": "inbound",
        })
        self.assertEqual(payload["type"], "support")
        self.assertEqual(payload["direction"], "inbound")
        self.assertNotIn("name", payload)
        self.assertNotIn("code", payload)


class SchedulerTests(SimpleTestCase):
    @patch("crm_api.services.recurrences.generate_due_tasks")
    @patch("crm_api.services.recurrences.CrmApiClient")
    def test_run_scheduler_for_template_returns_task_id(self, mock_client_cls, mock_gen):
        from crm_api.services.recurrences import run_scheduler_for_template

        mock_gen.return_value = {"results": [{"template_id": 7, "task_id": 100}]}
        task_id = run_scheduler_for_template(7)
        mock_client_cls.assert_called_once_with(scheduler=True)
        self.assertEqual(task_id, 100)


class CeleryTaskTests(SimpleTestCase):
    @patch("crm.tasks.CrmApiClient")
    @patch("crm.tasks.recurrences_service.generate_due_tasks")
    def test_generate_recurring_tasks_uses_scheduler_client(self, mock_gen, mock_client_cls):
        from crm.tasks import generate_recurring_tasks

        mock_gen.return_value = {"ok": True}
        result = generate_recurring_tasks()
        mock_client_cls.assert_called_once_with(scheduler=True)
        self.assertIn("sucesso", result.lower())

    @patch("crm.tasks.CrmApiClient")
    @patch("crm.tasks.alerts_service.fire_alert")
    @patch("crm.tasks.alerts_service.list_alerts")
    def test_fire_contract_alerts_skips_fired(self, mock_list, mock_fire, mock_client_cls):
        from crm.tasks import fire_contract_alerts

        mock_list.return_value = (
            [{"id": 1, "status": "pending"}, {"id": 2, "status": "fired"}],
            2,
        )
        result = fire_contract_alerts()
        mock_client_cls.assert_called_once_with(service_user=True)
        self.assertEqual(mock_fire.call_count, 1)
        self.assertIn("1 alertas", result)


class CanCommentTests(SimpleTestCase):
    def test_can_comment_requires_view_task_and_board_flag(self):
        user = Mock()
        user.has_perm = lambda codename: codename == "crm.view_task"
        request = Mock(user=user)
        self.assertTrue(can_comment_on_board(request, {"can_comment": True}))
        self.assertFalse(can_comment_on_board(request, {"can_comment": False}))
        user.has_perm = lambda codename: False
        self.assertFalse(can_comment_on_board(request, {"can_comment": True}))
