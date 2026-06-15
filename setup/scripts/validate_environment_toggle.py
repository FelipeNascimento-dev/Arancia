"""
Checklist manual homolog↔prod (DB, APIs, URLs, permissões, integridade do arquivo).

Uso: python manage.py shell < setup/scripts/validate_environment_toggle.py
Ou:  python setup/scripts/validate_environment_toggle.py (com DJANGO_SETTINGS_MODULE)
"""
import os
import re
import shutil
import sys
from pathlib import Path

import django

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from django.contrib.auth.models import AnonymousUser, Permission, User
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, override_settings

from setup.environments import ENVIRONMENT_PROFILES, apply_environment, get_profile
from setup.services.environment_switch import (
    get_current_environment_from_file,
    read_local_settings_content,
    write_environment_to_local_settings,
)
from setup.settings import environment_context
from logistica.views.views_user.toggle_db_view import toggle_db

LOCAL_SETTINGS = BASE_DIR / 'setup' / 'local_settings.py'
ENV_LINE_RE = re.compile(r"^ENVIRONMENT\s*=", re.MULTILINE)
DB_HOST_LINE_RE = re.compile(r"^DB_HOST\s*=", re.MULTILINE)

PASS = []
FAIL = []


def ok(name, detail=''):
    PASS.append((name, detail))


def fail(name, detail=''):
    FAIL.append((name, detail))


def assert_eq(name, got, expected):
    if got == expected:
        ok(name, f'{got!r}')
    else:
        fail(name, f'esperado {expected!r}, obtido {got!r}')


def validate_profile(env_key):
    profile = get_profile(env_key)
    ns = {
        'DATABASES': {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'HOST': '0.0.0.0',
            }
        }
    }
    apply_environment(env_key, ns)
    assert_eq(f'{env_key}: DB_HOST', ns['DB_HOST'], profile['db_host'])
    assert_eq(f'{env_key}: BASE_PATH', ns['BASE_PATH'], profile['base_path'])
    assert_eq(f'{env_key}: STOCK_API_URL hg/prod', 'hg-' in ns['STOCK_API_URL'], env_key == 'homolog')
    assert_eq(f'{env_key}: API_BASE coerente', ns['API_BASE'], profile['api_base'])
    assert_eq(f'{env_key}: LOCAL_DEBUG', ns['LOCAL_DEBUG'], env_key == 'homolog')
    assert_eq(f'{env_key}: DATABASES HOST', ns['DATABASES']['default']['HOST'], profile['db_host'])


def validate_context_processor():
    ctx = environment_context(RequestFactory().get('/'))
    for key in ('DB_HOST', 'ENVIRONMENT', 'IS_HOMOLOG', 'BASE_PATH'):
        if key not in ctx:
            fail(f'context processor: chave {key}', 'ausente')
        else:
            ok(f'context processor: {key}', repr(ctx[key]))
    env = ctx['ENVIRONMENT']
    if env in ENVIRONMENT_PROFILES:
        profile = get_profile(env)
        assert_eq('context processor: DB_HOST vs perfil', ctx['DB_HOST'], profile['db_host'])
        assert_eq('context processor: BASE_PATH vs perfil', ctx['BASE_PATH'], profile['base_path'])
        assert_eq('context processor: IS_HOMOLOG', ctx['IS_HOMOLOG'], env == 'homolog')


@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
def validate_permissions():
    rf = RequestFactory()
    request = rf.post('/toggle-db/')
    request.user = AnonymousUser()

    response = toggle_db(request)
    if getattr(response, 'status_code', None) == 302:
        ok('toggle_db sem login', 'redirect 302')
    else:
        fail('toggle_db sem login', f'resposta {getattr(response, "status_code", type(response))}')

    user = User(username='test_env_toggle', is_active=True)
    user.save()
    try:
        perm = Permission.objects.get(codename='acesso_arancia', content_type__app_label='logistica')
        user.user_permissions.add(perm)
        request.user = user
        try:
            toggle_db(request)
            fail('toggle_db sem ti_interno', 'deveria levantar PermissionDenied')
        except PermissionDenied:
            ok('toggle_db sem ti_interno', 'PermissionDenied')
    finally:
        user.delete()


def validate_file_integrity_after_toggle(original_env):
    content = read_local_settings_content()
    env_lines = ENV_LINE_RE.findall(content)
    db_host_lines = DB_HOST_LINE_RE.findall(content)
    assert_eq('integridade: uma linha ENVIRONMENT', len(env_lines), 1)
    assert_eq('integridade: sem DB_HOST solto no arquivo', len(db_host_lines), 0)
    assert_eq('integridade: ENVIRONMENT no arquivo', get_current_environment_from_file(content), original_env)


def validate_toggle_roundtrip():
    backup = LOCAL_SETTINGS.with_suffix('.py.validate_bak')
    shutil.copy2(LOCAL_SETTINGS, backup)
    try:
        start = get_current_environment_from_file()
        other = 'prod' if start == 'homolog' else 'homolog'
        write_environment_to_local_settings(other)
        validate_file_integrity_after_toggle(other)
        other_profile = get_profile(other)
        content = read_local_settings_content()
        assert_eq('toggle: ENVIRONMENT gravado', get_current_environment_from_file(content), other)

        write_environment_to_local_settings(start)
        validate_file_integrity_after_toggle(start)
        start_profile = get_profile(start)
        assert_eq('toggle reverso: ENVIRONMENT restaurado', get_current_environment_from_file(), start)

        ok('toggle: redirect_url homolog/prod', other_profile['base_path'])
        ok('toggle: redirect_url prod/homolog', start_profile['base_path'])
    finally:
        shutil.copy2(backup, LOCAL_SETTINGS)
        backup.unlink(missing_ok=True)


def main():
    print('=== Validacao ambiente homolog <-> prod ===\n')
    validate_profile('homolog')
    validate_profile('prod')
    validate_context_processor()
    validate_permissions()
    validate_toggle_roundtrip()

    print(f'PASS: {len(PASS)}')
    for name, detail in PASS:
        print(f'  [OK] {name}' + (f' — {detail}' if detail else ''))

    if FAIL:
        print(f'\nFAIL: {len(FAIL)}')
        for name, detail in FAIL:
            print(f'  [X] {name}' + (f' — {detail}' if detail else ''))
        sys.exit(1)

    print('\nChecklist concluído com sucesso.')
    sys.exit(0)


if __name__ == '__main__':
    main()
