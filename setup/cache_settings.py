"""Configuração de cache Django (Redis ou LocMem fallback)."""


def build_redis_url(*, host, port, db, password=""):
    auth = f":{password}@" if password else ""
    return f"redis://{auth}{host}:{port}/{db}"


def build_caches(
    *,
    redis_enabled=True,
    redis_host="127.0.0.1",
    redis_port=6379,
    redis_db=1,
    redis_password="",
    redis_max_connections=50,
    redis_socket_timeout=2.0,
    redis_socket_connect_timeout=2.0,
):
    """
    Monta CACHES para settings.py.

    Usa db Redis separado do Celery (db 0) por padrão para evitar colisão de chaves.
    """
    if not redis_enabled:
        return {
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "arancia-default",
            }
        }

    return {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": build_redis_url(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
            ),
            "OPTIONS": {
                "max_connections": redis_max_connections,
                "socket_timeout": redis_socket_timeout,
                "socket_connect_timeout": redis_socket_connect_timeout,
            },
        }
    }
