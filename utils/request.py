import logging
import httpx

logger = logging.getLogger()


def log_request_result(prefix, endpoint, method, request_data, res):
    logger.info(
        f"{prefix} | request_method: {method} | request_url: {endpoint!r} | request_body: {request_data} | response_code: {res.status_code} | response_body {res.text}"
    )


class RequestClient:
    def __init__(self, method, url: str, headers, request_data: dict = None, timeout: int = 100) -> None:
        self.method = method
        self.url = url
        self.request_data = request_data
        self.headers = headers
        self.timeout = timeout

    def upload_file(api_url, headers, files, timeout=30):

        with httpx.Client(timeout=timeout) as client:
            response = client.post(api_url, headers=headers, files=files)
        return response

    def send_api_request(self):
        logger.info(f"Sending a {self.method} request to: {self.url}")
        logger.info(f"Request body/params: {self.request_data}")
        logger.info(f"Request HEADERS: {self.headers}")

        with httpx.Client(timeout=self.timeout) as client:
            try:
                request = httpx.Request(
                    self.method.upper(),
                    url=self.url,
                    **{f"{'params' if self.method.lower() == 'get' else 'json'}": self.request_data},
                    headers=self.headers
                )
                response = client.send(request)
                response.raise_for_status()

            except httpx.HTTPStatusError as exc:
                # Se a resposta não for JSON válido
                try:
                    data = response.json()
                except Exception:
                    data = {"detail": response.text or "Erro interno do servidor"}

                if response.status_code == 500:
                    data = {"detail": response.text or "Erro interno do servidor"}
                    return data

                log_request_result('request_error', self.url,
                                   self.method, data, response)
                return data

            # --- Sucesso ---
            try:
                data = response.json()
            except Exception:
                data = {"detail": response.text or "Resposta não JSON"}

            log_request_result('request_success', self.url,
                               self.method, self.request_data, response)
        return data

    def send_api_request_no_json(self, *, stream: bool = True):
        """
        Envia a requisição e SEMPRE retorna httpx.Response (sem fazer .json()).
        - stream=True: mantém o corpo em streaming (use response.iter_bytes()).
        - Em erro HTTP (4xx/5xx), retorna exc.response (também httpx.Response).
        """
        method = (self.method or "GET").upper()
        url = self.url
        headers = self.headers or {}
        data = self.request_data

        logger.info("Sending %s %s", method, url)
        logger.info("Request params/json: %r", data)
        logger.info("Request headers: %r", headers)

        # Monta kwargs corretos para httpx (params para GET/DELETE, json para outros)
        req_kwargs = {"headers": headers}
        if method in ("GET", "DELETE"):
            req_kwargs["params"] = data
        else:
            req_kwargs["json"] = data

        try:
            with httpx.Client(timeout=getattr(self, "timeout", None), follow_redirects=True) as client:
                request = client.build_request(method, url, **req_kwargs)
                # stream=True => permite iterar com response.iter_bytes() sem carregar tudo em memória
                response = client.send(request, stream=stream)

                try:
                    response.raise_for_status()
                except httpx.HTTPStatusError as exc:
                    resp = exc.response  # httpx.Response
                    # LOG: não tente resp.json() aqui — pode ser binário
                    ct = resp.headers.get("content-type")
                    logger.warning("HTTP error %s on %s (CT: %s)",
                                   resp.status_code, url, ct)
                    # Seu logger custom
                    try:
                        log_request_result(
                            "request_error", url, method, data, resp)
                    except Exception:
                        pass
                    return resp

        except httpx.RequestError as exc:
            # Erros de rede/DNS/timeout
            logger.exception("Network error on %s %s: %s", method, url, exc)
            raise

        # Sucesso
        try:
            log_request_result("request_success", url, method, data, response)
        except Exception:
            pass

        return response
