"""Structural validation for CRM aggregated bundle JSON (handoff contracts)."""

from __future__ import annotations

CRM_LOOKUP_KEYS = frozenset({
    "customers",
    "service_types",
    "prioritys",
    "status_tasks",
    "boards",
    "designations",
})

BOARD_PAGE_KEYS = frozenset({"crm", "gais", "groups", "column_templates"})
BILLING_LOOKUPS_KEYS = frozenset({"clients", "contracts"})
KANBAN_BUNDLE_KEYS = frozenset({"board", "columns", "tasks", "access"})
DASHBOARD_SUMMARY_KEYS = frozenset({"billing", "alerts", "my_tasks"})


def _missing_keys(data: dict, required: frozenset[str]) -> list[str]:
    if not isinstance(data, dict):
        return sorted(required)
    return sorted(key for key in required if key not in data)


def validate_board_page_response(data: dict) -> list[str]:
    errors = []
    errors.extend(_missing_keys(data, BOARD_PAGE_KEYS))
    if isinstance(data, dict):
        crm_errors = _missing_keys(data.get("crm") or {}, CRM_LOOKUP_KEYS)
        errors.extend(f"crm.{key}" for key in crm_errors)
        column_templates = data.get("column_templates")
        if column_templates is not None and not isinstance(column_templates, dict):
            errors.append("column_templates must be object")
    return errors


def validate_billing_lookups_response(data: dict) -> list[str]:
    errors = _missing_keys(data, BILLING_LOOKUPS_KEYS)
    for key in ("clients", "contracts"):
        value = (data or {}).get(key)
        if value is not None and not isinstance(value, list):
            errors.append(f"{key} must be list")
    return errors


def validate_kanban_bundle_response(data: dict) -> list[str]:
    errors = _missing_keys(data, KANBAN_BUNDLE_KEYS)
    if isinstance(data, dict):
        board = data.get("board")
        if board is not None and not isinstance(board, dict):
            errors.append("board must be object")
        elif isinstance(board, dict) and not board.get("id"):
            errors.append("board.id required")
        for key in ("columns", "tasks"):
            value = data.get(key)
            if value is not None and not isinstance(value, list):
                errors.append(f"{key} must be list")
        access = data.get("access")
        if access is not None and not isinstance(access, dict):
            errors.append("access must be object")
    return errors


def validate_dashboard_summary_response(data: dict) -> list[str]:
    errors = _missing_keys(data, DASHBOARD_SUMMARY_KEYS)
    for key in ("alerts", "my_tasks"):
        value = (data or {}).get(key)
        if value is not None and not isinstance(value, list):
            errors.append(f"{key} must be list")
    billing = (data or {}).get("billing")
    if billing is not None and not isinstance(billing, dict):
        errors.append("billing must be object")
    return errors
