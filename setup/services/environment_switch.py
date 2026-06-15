"""
Leitura e troca segura de ENVIRONMENT em setup/local_settings.py.
"""
import os
import re
from pathlib import Path

from django.conf import settings

from setup.environments import (
    VALID_ENVIRONMENTS,
    get_profile,
    normalize_environment,
)

_ENVIRONMENT_LINE_RE = re.compile(
    r"^(\s*)ENVIRONMENT\s*=\s*['\"](homolog|prod)['\"]\s*$",
    re.MULTILINE,
)
_LEGACY_LOCAL_DEBUG_RE = re.compile(
    r"^(\s*)LOCAL_DEBUG\s*=\s*(True|False)\s*$",
    re.MULTILINE,
)


def _local_settings_path():
    return Path(settings.BASE_DIR) / 'setup' / 'local_settings.py'


def read_local_settings_content():
    path = _local_settings_path()
    if not path.exists():
        raise FileNotFoundError(f'Arquivo não encontrado: {path}')
    return path.read_text(encoding='utf-8')


def get_current_environment_from_file(content=None):
    """Lê ENVIRONMENT do arquivo local_settings.py."""
    if content is None:
        content = read_local_settings_content()

    match = _ENVIRONMENT_LINE_RE.search(content)
    if match:
        return match.group(2)

    # Compatibilidade com formato legado LOCAL_DEBUG
    match_debug = _LEGACY_LOCAL_DEBUG_RE.search(content)
    if match_debug:
        return 'homolog' if match_debug.group(2) == 'True' else 'prod'

    raise ValueError(
        'Linha ENVIRONMENT (ou LOCAL_DEBUG legado) não encontrada em local_settings.py'
    )


def get_current_environment():
    """Retorna o ambiente atual (módulo importado ou arquivo)."""
    try:
        from setup import local_settings
        if hasattr(local_settings, 'ENVIRONMENT'):
            return normalize_environment(local_settings.ENVIRONMENT)
    except ImportError:
        pass

    return get_current_environment_from_file()


def write_environment_to_local_settings(environment):
    """
    Reescreve somente a linha ENVIRONMENT em local_settings.py.

    Se o arquivo ainda usar LOCAL_DEBUG legado, converte para ENVIRONMENT.
    """
    env = normalize_environment(environment)
    path = _local_settings_path()
    content = read_local_settings_content()

    if _ENVIRONMENT_LINE_RE.search(content):
        new_content = _ENVIRONMENT_LINE_RE.sub(
            f"ENVIRONMENT = '{env}'",
            content,
            count=1,
        )
    elif _LEGACY_LOCAL_DEBUG_RE.search(content):
        new_content = _LEGACY_LOCAL_DEBUG_RE.sub(
            f"ENVIRONMENT = '{env}'",
            content,
            count=1,
        )
    else:
        raise ValueError(
            'Linha ENVIRONMENT (ou LOCAL_DEBUG legado) não encontrada em local_settings.py'
        )

    path.write_text(new_content, encoding='utf-8')
    return env


def _build_redirect_url(base_path):
    return f"/{base_path}"


def _requires_restart():
    """WSGI/gunicorn não recarrega local_settings sem restart do processo."""
    return os.environ.get('RUN_MAIN') != 'true'


def build_environment_metadata(environment):
    """Metadados do ambiente para resposta JSON da view de toggle."""
    env = normalize_environment(environment)
    profile = get_profile(env)
    base_path = profile['base_path']
    return {
        'ambiente': profile['label'],
        'environment': env,
        'db_host': profile['db_host'],
        'base_path': base_path,
        'redirect_url': _build_redirect_url(base_path),
        'requires_restart': _requires_restart(),
    }


def toggle_environment():
    """
    Alterna homolog ↔ prod no arquivo local_settings.py.

    Retorna metadados do novo ambiente.
    """
    current = get_current_environment()
    new_env = 'prod' if current == 'homolog' else 'homolog'
    write_environment_to_local_settings(new_env)
    return build_environment_metadata(new_env)
