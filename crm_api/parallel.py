"""Execução paralela de chamadas CRM (workers com cliente HTTP dedicado)."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

from crm_api.client import CrmApiClient


def run_parallel_crm_fetches(request, jobs, *, max_workers=4):
    """
    Executa jobs independentes em paralelo.

    ``jobs``: lista de ``(nome, callable(client) -> resultado)``.
    Retorna ``(results: dict, errors: dict)`` — exceções ficam em ``errors``.
    """
    if not jobs:
        return {}, {}

    if len(jobs) == 1:
        name, fn = jobs[0]
        client = CrmApiClient(request, dedicated_http=True)
        try:
            return {name: fn(client)}, {}
        except Exception as exc:
            return {}, {name: exc}

    results = {}
    errors = {}
    workers = min(len(jobs), max_workers)

    def _run(name, fn):
        client = CrmApiClient(request, dedicated_http=True)
        try:
            return name, fn(client), None
        except Exception as exc:
            return name, None, exc

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(_run, name, fn): name
            for name, fn in jobs
        }
        for future in as_completed(futures):
            name, result, exc = future.result()
            if exc is not None:
                errors[name] = exc
            else:
                results[name] = result

    return results, errors
