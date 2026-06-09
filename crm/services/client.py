import logging

import httpx
from django.conf import settings

from .context import build_crm_headers, build_service_crm_headers
from .exceptions import CrmConnectionError, raise_for_status

logger = logging.getLogger(__name__)


def _safe_headers_for_log(headers):
    safe = dict(headers or {})
    if 'Authorization' in safe:
        safe['Authorization'] = 'Bearer ***'
    return safe


class CrmApiClient:
    """Cliente HTTP para a API CRM (FastAPI) via BFF Django."""

    def __init__(self, user=None, *, service=False, extra_headers=None):
        self.user = user
        self.service = service
        self.extra_headers = extra_headers or {}

    @property
    def api_v1_base(self):
        base = settings.CRM_API_BASE_URL.rstrip('/')
        return f'{base}{settings.CRM_API_V1_STR}'

    @property
    def api_root(self):
        return settings.CRM_API_BASE_URL.rstrip('/')

    def _build_headers(self, *, json_body=True):
        if self.service:
            headers = build_service_crm_headers()
        elif self.user is not None:
            headers = build_crm_headers(self.user)
        else:
            raise ValueError('CrmApiClient requer user ou service=True.')

        if json_body:
            headers.setdefault('Content-Type', 'application/json')
        headers.update(self.extra_headers)
        return headers

    def _url(self, path):
        path = path if path.startswith('/') else f'/{path}'
        return f'{self.api_v1_base}{path}'

    def _request(self, method, path, *, params=None, json=None, data=None, files=None):
        url = self._url(path)
        json_body = files is None and data is None
        headers = self._build_headers(json_body=json_body)

        if files is not None:
            headers.pop('Content-Type', None)

        timeout = settings.CRM_API_TIMEOUT
        verify = settings.CRM_API_VERIFY_SSL

        logger.info(
            'CRM API %s %s | headers=%s',
            method.upper(),
            url,
            _safe_headers_for_log(headers),
        )

        try:
            with httpx.Client(timeout=timeout, verify=verify) as client:
                response = client.request(
                    method.upper(),
                    url,
                    params=params,
                    json=json,
                    data=data,
                    files=files,
                    headers=headers,
                )
        except httpx.RequestError as exc:
            logger.exception('CRM API connection error: %s %s', method.upper(), url)
            raise CrmConnectionError(str(exc)) from exc

        logger.info('CRM API %s %s -> HTTP %s', method.upper(), url, response.status_code)
        raise_for_status(response)

        if response.status_code == 204 or not response.content:
            return None
        try:
            return response.json()
        except Exception:
            return {'detail': response.text}

    def get(self, path, params=None):
        return self._request('GET', path, params=params)

    def post(self, path, json=None, params=None):
        return self._request('POST', path, json=json, params=params)

    def patch(self, path, json=None):
        return self._request('PATCH', path, json=json)

    def delete(self, path, params=None):
        return self._request('DELETE', path, params=params)

    def post_multipart(self, path, data=None, files=None):
        return self._request('POST', path, data=data, files=files)

    def health_check(self):
        """GET na raiz da API (fora de /api/v1)."""
        url = f'{self.api_root}/'
        timeout = settings.CRM_API_TIMEOUT
        verify = settings.CRM_API_VERIFY_SSL
        logger.info('CRM health GET %s', url)
        try:
            with httpx.Client(timeout=timeout, verify=verify) as client:
                response = client.get(url)
        except httpx.RequestError as exc:
            raise CrmConnectionError(str(exc)) from exc
        logger.info('CRM health GET %s -> HTTP %s', url, response.status_code)
        return response
