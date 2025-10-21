import re, requests, concurrent.futures
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_naive
from django.core.cache import cache

session = requests.Session()
API_TOKEN = "123"

def format_datetime(value):
    if not value:
        return "—"
    try:
        dt = parse_datetime(value)
        return dt.strftime("%d/%m/%Y %H:%M") if dt else "—"
    except Exception:
        return "—"

def get_api_data(cache_key, url, params, headers, ttl=0):
    data = cache.get(cache_key)
    if not data:
        resp = session.get(url, params=params, headers=headers)
        data = resp.json() if resp.status_code == 200 else {}
        cache.set(cache_key, data, ttl)
    return data

def get_multiple_api_data(requests_list, headers, ttl=0):
    results = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_key = {
            executor.submit(get_api_data, key, url, params, headers, ttl): key
            for key, url, params in requests_list
        }
        for future in concurrent.futures.as_completed(future_to_key):
            key = future_to_key[future]
            try:
                results[key] = future.result()
            except Exception:
                results[key] = {}
    return results

def normalizar_celular(numero: str) -> str:
    if not numero:
        return ""
    numero = re.sub(r"\D", "", numero)
    if numero.startswith("55") and len(numero) > 11:
        numero = numero[2:]
    return numero
