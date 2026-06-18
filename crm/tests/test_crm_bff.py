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
    board_column_payload,
    billing_payload,
    billing_api_payload,
    build_rrule,
    contract_payload,
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
from crm.helpers.api_display import billing_to_json, enrich_billing, enrich_billing_with_lookups
from crm.helpers.date_format import format_date_br, format_datetime_br, format_period_br
from crm.helpers.dashboard import build_summary_cards
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

    def test_board_column_payload_includes_code(self):
        payload = board_column_payload({
            "name": "coluninhaaaaaa",
            "status_task_id": "0cf4a088-89ca-4e08-b057-9fa74055d80d",
            "position": 5,
        })
        self.assertEqual(payload["name"], "coluninhaaaaaa")
        self.assertEqual(payload["code"], "coluninhaaaaaa")
        self.assertEqual(payload["status_task_id"], "0cf4a088-89ca-4e08-b057-9fa74055d80d")
        self.assertEqual(payload["position"], 5)

    def test_board_column_payload_slugifies_name(self):
        payload = board_column_payload({
            "name": "Em Andamento",
            "status_task_id": "abc-123",
        })
        self.assertEqual(payload["code"], "em_andamento")

    def test_board_column_payload_preserves_explicit_code(self):
        payload = board_column_payload({
            "name": "Qualquer",
            "code": "custom_code",
        })
        self.assertEqual(payload["code"], "custom_code")

    def test_column_reorder_payload_maps_ids_to_items(self):
        from crm_api.services.boards import column_reorder_payload

        payload = column_reorder_payload({
            "column_ids": ["aaa-111", "bbb-222", "ccc-333"],
        })
        self.assertEqual(payload["items"], [
            {"id": "aaa-111", "kanban_position": 0},
            {"id": "bbb-222", "kanban_position": 1},
            {"id": "ccc-333", "kanban_position": 2},
        ])

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

    def test_contract_payload_serializes_dates_and_decimal(self):
        from datetime import date
        from decimal import Decimal

        payload = contract_payload({
            "client_gai_id": 10,
            "titulo": "Contrato teste",
            "numero": "81",
            "data_inicio": date(2026, 6, 17),
            "data_fim": date(2026, 12, 31),
            "valor": Decimal("1500.50"),
            "descricao": "Observação",
        })
        self.assertEqual(payload["customer_gai_id"], 10)
        self.assertEqual(payload["title"], "Contrato teste")
        self.assertEqual(payload["number"], "81")
        self.assertEqual(payload["start_date"], "2026-06-17")
        self.assertEqual(payload["end_date"], "2026-12-31")
        self.assertEqual(payload["value"], "1500.50")
        self.assertEqual(payload["description"], "Observação")
        self.assertNotIn("titulo", payload)
        self.assertNotIn("data_inicio", payload)

    def test_billing_payload_serializes_dates_and_decimal(self):
        from datetime import date
        from decimal import Decimal

        payload = billing_payload({
            "client_gai_id": 10,
            "contract_id": 5,
            "referencia": "REF-2026-01",
            "valor": Decimal("2500.00"),
            "data_vencimento": date(2026, 7, 15),
            "status": "pending",
            "observacoes": "Nota teste",
        })
        self.assertEqual(payload["customer_gai_id"], 10)
        self.assertEqual(payload["contract_id"], 5)
        self.assertEqual(payload["reference"], "REF-2026-01")
        self.assertEqual(payload["value"], "2500.00")
        self.assertEqual(payload["due_date"], "2026-07-15")
        self.assertEqual(payload["status"], "pending")
        self.assertEqual(payload["notes"], "Nota teste")

    def test_billing_api_payload_adds_planned_amount_and_period(self):
        from datetime import date
        from decimal import Decimal

        payload = billing_api_payload(
            {
                "client_gai_id": 10,
                "contract_id": "abc-123",
                "referencia": "REF-2026-01",
                "valor": Decimal("2500.00"),
                "data_vencimento": date(2026, 7, 15),
            },
            contract={
                "id": "abc-123",
                "start_date": "2026-01-01",
                "end_date": "2026-12-31",
            },
        )
        self.assertEqual(payload["value"], 2500.0)
        self.assertEqual(payload["planned_amount"], 2500.0)
        self.assertEqual(payload["period_start"], "2026-01-01")
        self.assertEqual(payload["period_end"], "2026-12-31")


class DateFormatTests(SimpleTestCase):
    def test_format_date_br_from_iso_string(self):
        self.assertEqual(format_date_br("2026-07-15"), "15/07/2026")

    def test_format_datetime_br_from_iso_string(self):
        self.assertEqual(format_datetime_br("2026-06-17T10:30:00"), "17/06/2026 10:30")

    def test_format_period_br(self):
        self.assertEqual(format_period_br("2026-01-01", "2026-12-31"), "01/01/2026 — 31/12/2026")


class EnrichBillingTests(SimpleTestCase):
    def test_enrich_billing_maps_all_api_fields(self):
        record = {
            "id": 42,
            "reference": "REF-01",
            "value": "1500.00",
            "planned_amount": "1600.00",
            "actual_amount": "1500.00",
            "due_date": "2026-07-15",
            "period_start": "2026-07-01",
            "period_end": "2026-07-31",
            "status": "pending",
            "notes": "Observação da API",
            "contract_id": 7,
            "customer": {"name": "Cliente Teste"},
            "contract": {"title": "Contrato Alpha", "number": "C-7"},
        }
        enriched = enrich_billing(record)

        self.assertEqual(enriched["display_referencia"], "REF-01")
        self.assertEqual(enriched["display_customer"], "Cliente Teste")
        self.assertEqual(enriched["display_contract"], "Contrato Alpha")
        self.assertEqual(enriched["display_contract_id"], 7)
        self.assertEqual(enriched["display_period_start"], "01/07/2026")
        self.assertEqual(enriched["display_period_end"], "31/07/2026")
        self.assertEqual(enriched["display_period"], "01/07/2026 — 31/07/2026")
        self.assertEqual(enriched["display_planned_amount"], "R$ 1.600,00")
        self.assertEqual(enriched["display_actual_amount"], "R$ 1.500,00")
        self.assertEqual(enriched["display_valor"], "R$ 1.500,00")
        self.assertEqual(enriched["display_vencimento"], "15/07/2026")
        self.assertEqual(enriched["display_status"], "pending")
        self.assertEqual(enriched["display_observacoes"], "Observação da API")

    def test_enrich_billing_hides_uuid_reference(self):
        enriched = enrich_billing({
            "id": "584fe3e0-11f3-4db3-9d91-264a60627b69",
            "reference": "584fe3e0-11f3-4db3-9d91-264a60627b69",
            "customer": {"name": "CIELO"},
            "contract": {"title": "Testes"},
            "period_start": "2026-01-01",
            "period_end": "2026-12-31",
        })
        self.assertNotIn("584fe3e0", enriched["display_referencia"])
        self.assertEqual(enriched["display_referencia"], "01/01/2026 — 31/12/2026")

    def test_enrich_billing_falls_back_to_contract_name(self):
        enriched = enrich_billing({
            "id": "584fe3e0-11f3-4db3-9d91-264a60627b69",
            "reference": "584fe3e0-11f3-4db3-9d91-264a60627b69",
            "customer": {"name": "CIELO"},
            "contract": {"title": "Testes"},
        })
        self.assertEqual(enriched["display_referencia"], "Testes")

    def test_enrich_billing_with_lookups_fills_customer_and_contract(self):
        enriched = enrich_billing_with_lookups(
            {
                "id": "billing-1",
                "customer_gai_id": 10,
                "contract_id": "contract-1",
                "reference": "REF-001",
                "value": "1500.00",
            },
            clients_by_gai={"10": {"gai_id": 10, "nome": "Cliente X"}},
            contracts_by_id={
                "contract-1": {
                    "id": "contract-1",
                    "title": "Contrato Alpha",
                    "number": "10",
                    "customer_gai_id": 10,
                },
            },
        )
        self.assertEqual(enriched["display_customer"], "Cliente X")
        self.assertEqual(enriched["display_contract"], "10 — Contrato Alpha")
        self.assertEqual(enriched["display_referencia"], "REF-001")
        self.assertEqual(enriched["display_valor"], "R$ 1.500,00")
        self.assertEqual(enriched["customer_gai_id"], 10)
        self.assertEqual(enriched["client_gai_id"], 10)

    def test_billing_initial_uses_enriched_fields(self):
        from crm.helpers.api_display import billing_form_json

        form_data = billing_form_json({
            "id": "billing-1",
            "contract_id": "contract-1",
            "customer_gai_id": 10,
            "planned_amount": "1500.00",
            "due_date": "2026-07-15",
            "display_referencia": "REF-2026-07",
            "reference": "584fe3e0-11f3-4db3-9d91-264a60627b69",
        })
        self.assertEqual(form_data["client_gai_id"], 10)
        self.assertEqual(form_data["contract_id"], "contract-1")
        self.assertEqual(form_data["referencia"], "REF-2026-07")
        self.assertEqual(form_data["valor"], "1500.00")
        self.assertEqual(form_data["data_vencimento"], "2026-07-15")

    def test_billing_to_json_includes_modal_fields(self):
        payload = billing_to_json({
            "id": 9,
            "reference": "REF-9",
            "value": "100",
            "status": "paid",
            "notes": "ok",
        })
        self.assertEqual(payload["id"], 9)
        self.assertEqual(payload["display_referencia"], "REF-9")
        self.assertEqual(payload["display_status"], "paid")
        self.assertEqual(payload["display_observacoes"], "ok")


class BillingSummaryTests(SimpleTestCase):
    def test_build_summary_cards_for_list_includes_totals(self):
        summary = {
            "total_records": 10,
            "total_value": "5000.00",
            "pending_count": 3,
            "pending_value": "1500.00",
            "paid_count": 5,
            "paid_value": "3000.00",
            "overdue_count": 2,
            "overdue_value": "500.00",
            "items": [{"id": 1}],
        }
        cards = build_summary_cards(summary, skip_keys=frozenset({"items", "detail"}))
        labels = [card["label"] for card in cards]
        self.assertIn("Total de registros", labels)
        self.assertIn("Valor total", labels)
        self.assertIn("Pendentes", labels)
        self.assertEqual(len(cards), 8)


class ListaFaturamentoViewTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        from crm.models import CrmPermissions
        from logistica.models import PermissaoUsuarioDummy

        self.user = User.objects.create_user(username="crm_billing", password="pass")
        crm_ct = ContentType.objects.get_for_model(CrmPermissions)
        logistica_ct = ContentType.objects.get_for_model(PermissaoUsuarioDummy)
        view_billing = Permission.objects.get_or_create(
            codename="view_billing",
            content_type=crm_ct,
            defaults={"name": "Visualizar faturamento"},
        )[0]
        add_billing = Permission.objects.get_or_create(
            codename="add_billing",
            content_type=crm_ct,
            defaults={"name": "Adicionar faturamento"},
        )[0]
        acesso = Permission.objects.get_or_create(
            codename="acesso_arancia",
            content_type=logistica_ct,
            defaults={"name": "Acesso Arancia"},
        )[0]
        self.user.user_permissions.add(view_billing, add_billing, acesso)

    @patch("crm.views.views_faturamento.view_lista_faturamento.clients_service.list_clients")
    @patch("crm.views.views_faturamento.view_lista_faturamento.contracts_service.list_contracts")
    @patch("crm.views.views_faturamento.view_lista_faturamento.CrmApiClient")
    @patch("crm.views.views_faturamento.view_lista_faturamento.billing_service.list_billing")
    @patch("crm.views.views_faturamento.view_lista_faturamento.billing_service.billing_summary")
    def test_lista_faturamento_renders_table_and_summary(
        self,
        mock_summary,
        mock_list,
        mock_client_cls,
        mock_contracts,
        mock_clients,
    ):
        from django.urls import reverse

        mock_client_cls.return_value = Mock()
        mock_clients.return_value = ([], 0)
        mock_contracts.return_value = ([], 0)
        mock_summary.return_value = {
            "total_records": 1,
            "total_value": "1500.00",
            "pending_count": 1,
            "pending_value": "1500.00",
        }
        mock_list.return_value = ([{
            "id": 1,
            "reference": "REF-1",
            "value": "1500.00",
            "planned_amount": "1600.00",
            "actual_amount": "1500.00",
            "due_date": "2026-07-15",
            "period_start": "2026-07-01",
            "period_end": "2026-07-31",
            "status": "pending",
            "notes": "Teste",
            "customer": {"name": "Cliente A"},
            "contract": {"title": "Contrato 1"},
            "contract_id": 3,
        }], 1)

        self.client.force_login(self.user)
        response = self.client.get(reverse("crm:lista_faturamento"))

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("Faturamento", content)
        self.assertIn("user-list-container", content)
        self.assertIn("user-table", content)
        self.assertIn("Total de registros", content)
        self.assertIn("REF-1", content)
        self.assertIn("Cliente A", content)
        self.assertIn("Contrato 1", content)
        self.assertIn("Valor planejado", content)
        self.assertIn("Valor realizado", content)
        self.assertIn("crm-billing-list-config", content)
        self.assertIn("modalFormBilling", content)
        self.assertIn("openCreateBillingModal", content)


class ContractOptionLabelTests(SimpleTestCase):
    def test_contract_option_label_uses_title_not_uuid(self):
        from crm.views.views_contratos._helpers import contract_option_label

        label = contract_option_label({
            "id": "e14c0ed4-243d-4965-9cf6-b44652c7c819",
            "title": "Contrato Mensal",
            "number": "81",
        })
        self.assertEqual(label, "81 — Contrato Mensal")
        self.assertNotIn("e14c0ed4", label)

    def test_billing_form_contract_choices_use_labels(self):
        from crm.forms import BillingForm

        form = BillingForm(lookups={
            "clients": [{"gai_id": 10, "nome": "Cliente X"}],
            "contracts": [{
                "id": "e14c0ed4-243d-4965-9cf6-b44652c7c819",
                "title": "Contrato Alpha",
                "number": "10",
                "customer_gai_id": 10,
            }],
        })
        choices = form.fields["contract_id"].widget.choices
        self.assertEqual(choices[1][0], "e14c0ed4-243d-4965-9cf6-b44652c7c819")
        self.assertEqual(choices[1][1], "10 — Contrato Alpha")


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
