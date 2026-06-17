import logging

import httpx
from django.conf import settings

from crm_api.context import (
    build_crm_headers_from_request,
    build_scheduler_headers,
    build_service_user_headers,
)
from crm_api.exceptions import (
    CrmApiError,
    CrmAuthError,
    CrmConnectionError,
    CrmNotFoundError,
    CrmPermissionError,
    CrmValidationError,
)

logger = logging.getLogger(__name__)


def _mask_headers(headers):
    masked = dict(headers)
    auth = masked.get("Authorization", "")
    if auth.startswith("Basic "):
        masked["Authorization"] = "Basic ***"
    elif auth.startswith("Bearer "):
        masked["Authorization"] = "Bearer ***"
    if masked.get("X-API-Key"):
        masked["X-API-Key"] = "***"
    return masked


def _parse_error_response(response):
    try:
        data = response.json()
    except Exception:
        data = {"detail": response.text or "Erro interno do servidor"}

    detail = data.get("detail") or data.get("message") or str(data)
    if isinstance(detail, list):
        detail = "; ".join(str(item) for item in detail)
    elif isinstance(detail, dict):
        detail = "; ".join(f"{k}: {v}" for k, v in detail.items())

    status = response.status_code
    if status == 401:
        raise CrmAuthError(detail or "Credenciais inválidas.", status_code=status, detail=detail)
    if status == 404:
        raise CrmNotFoundError(detail, status_code=status, detail=detail)
    if status == 403:
        raise CrmPermissionError(detail, status_code=status, detail=detail)
    if status == 422:
        raise CrmValidationError(detail, status_code=status, detail=detail)
    raise CrmApiError(detail, status_code=status, detail=detail)


class CrmApiClient:
    def __init__(self, request=None, *, service_user=False, scheduler=False, timeout=None):
        self.request = request
        self.service_user = service_user
        self.scheduler = scheduler
        self.timeout = timeout or getattr(settings, "CRM_API_TIMEOUT", 30)
        base = getattr(settings, "CRM_API_BASE_URL", "").rstrip("/")
        v1 = getattr(settings, "CRM_API_V1_STR", "/api/v1")
        self.base_url = f"{base}{v1}"
        self.api_root = base or self.base_url
        self.verify_ssl = getattr(settings, "CRM_API_VERIFY_SSL", False)

    def _headers(self):
        if self.scheduler:
            return build_scheduler_headers()
        if self.service_user:
            return build_service_user_headers()
        if self.request is not None:
            return build_crm_headers_from_request(self.request)
        raise CrmAuthError(
            "Credenciais CRM indisponíveis — informe request, service_user ou scheduler."
        )

    def _request(self, method, path, *, params=None, json=None, files=None, data=None, headers=None):
        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = headers if headers is not None else self._headers()
        if files:
            headers = {k: v for k, v in headers.items() if k.lower() != "content-type"}

        logger.info(
            "CRM API %s %s | headers=%s",
            method.upper(),
            url,
            _mask_headers(headers),
        )

        try:
            with httpx.Client(timeout=self.timeout, verify=self.verify_ssl) as client:
                response = client.request(
                    method.upper(),
                    url,
                    headers=headers,
                    params=params,
                    json=json,
                    files=files,
                    data=data,
                )
        except httpx.RequestError as exc:
            logger.exception("CRM connection error: %s", exc)
            raise CrmConnectionError(
                "Falha de conexão com a API CRM.",
                detail=str(exc),
            ) from exc

        logger.info("CRM API response %s %s", response.status_code, url)

        if response.status_code >= 400:
            _parse_error_response(response)

        if response.status_code == 204 or not response.content:
            return None

        try:
            return response.json()
        except Exception:
            return {"raw": response.text}

    def get(self, path, *, params=None):
        return self._request("GET", path, params=params)

    def post(self, path, *, json=None, files=None, data=None):
        return self._request("POST", path, json=json, files=files, data=data)

    def patch(self, path, *, json=None):
        return self._request("PATCH", path, json=json)

    def delete(self, path):
        return self._request("DELETE", path)

    def upload(self, path, *, files, data=None):
        return self._request("POST", path, files=files, data=data)

    def health(self):
        try:
            with httpx.Client(timeout=self.timeout, verify=self.verify_ssl) as client:
                response = client.get(self.api_root)
                return {"status_code": response.status_code, "ok": response.status_code < 500}
        except httpx.RequestError as exc:
            return {"status_code": 0, "ok": False, "detail": str(exc)}


def parse_list_response(data):
    if data is None:
        return [], None
    if isinstance(data, list):
        return data, None
    items = data.get("items") or data.get("results") or data.get("data") or []
    total = data.get("total") or data.get("count")
    return items, total
