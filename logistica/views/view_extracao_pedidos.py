import csv
from datetime import datetime, date
from typing import Iterable, Iterator, List, Dict, Any, Optional
from django.http import StreamingHttpResponse, HttpRequest, HttpResponse
from django.shortcuts import render
from django.contrib import messages
from ..forms import ExtracaoForm

def _normalize_value(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, (datetime, date)):
        return v.strftime("%Y-%m-%d %H:%M:%S") if isinstance(v, datetime) else v.strftime("%Y-%m-%d")
    return str(v)

def _rows_to_stream(rows: Iterable[Dict[str, Any]],
                    headers: List[str],
                    delimiter: str = ";") -> Iterator[str]:
    class Echo:
        def write(self, value):
            return value

    echo = Echo()
    writer = csv.writer(echo, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)

    yield "\ufeff"
    yield writer.writerow(headers)

    for row in rows:
        values = [_normalize_value(row.get(h)) for h in headers]
        yield writer.writerow(values)

def _fetch_pedidos(tp_reg: str) -> List[Dict[str, Any]]:
    if tp_reg == "All":
        return [
            {
                "order_number": "12345",
                "cliente": "ACME LTDA",
                "status": "PCP",
                "criado_em": datetime(2025, 7, 16, 11, 0, 0),
                "qtd_itens": 4,
            },
            {
                "order_number": "98765",
                "cliente": "Foo Bar",
                "status": "Consolidação",
                "criado_em": datetime(2025, 7, 18, 15, 30, 0),
                "qtd_itens": 2,
            },
        ]
    return []

def extracao_pedidos(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ExtracaoForm(request.POST)
        if form.is_valid():
            tp_reg = form.cleaned_data["tp_reg"]

            rows = _fetch_pedidos(tp_reg)

            if not rows:
                messages.info(request, "Nenhum registro encontrado para os filtros selecionados.")
                return render(request, "logistica/extracao_pedidos.html", {"form": form})

            headers = list(rows[0].keys())

            agora = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"extracao_pedidos_{agora}.csv"
            response = StreamingHttpResponse(
                _rows_to_stream(rows, headers, delimiter=";"),
                content_type="text/csv; charset=utf-8",
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response
        messages.error(request, "Corrija os erros do formulário.")
        return render(request, "logistica/extracao_pedidos.html", {"form": form})

    form = ExtracaoForm()
    return render(request, "logistica/extracao_pedidos.html", {
        "form": form,
        "botao_texto": "Exportar CSV", 
        })