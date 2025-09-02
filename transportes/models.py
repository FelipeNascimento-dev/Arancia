import httpx
from datetime import datetime
from setup.local_settings import status_labels,TOKEN 

def auth_headers():
    return {"accept": "application/json", "access_token": TOKEN}


async def fetch_json(url: str, default=None):
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(url, headers=auth_headers())
            r.raise_for_status()
            return r.json()
    except Exception as e:
        print(f"[ERRO] GET {url}: {e}")
        return default if default is not None else {}


def sum_counts(counts: dict) -> int:
    return sum(int(counts.get(k, 0) or 0) for k in status_labels.keys())


def initials(nome: str) -> str:
    parts = (nome or "").strip().split()
    if not parts:
        return "T"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def now_str():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")
