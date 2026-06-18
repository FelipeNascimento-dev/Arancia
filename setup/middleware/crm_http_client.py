"""Cliente httpx reutilizável por request para chamadas à API CRM."""

import httpx
from django.conf import settings

CRM_HTTP_CLIENT_ATTR = "_crm_http_client"


class CrmHttpClientMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.timeout = getattr(settings, "CRM_API_TIMEOUT", 30)
        self.verify_ssl = getattr(settings, "CRM_API_VERIFY_SSL", False)

    def __call__(self, request):
        setattr(
            request,
            CRM_HTTP_CLIENT_ATTR,
            httpx.Client(timeout=self.timeout, verify=self.verify_ssl),
        )
        try:
            return self.get_response(request)
        finally:
            client = getattr(request, CRM_HTTP_CLIENT_ATTR, None)
            if client is not None:
                client.close()
                delattr(request, CRM_HTTP_CLIENT_ATTR)
