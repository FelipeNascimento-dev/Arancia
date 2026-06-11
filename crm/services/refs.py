"""Resolução de labels a partir de objetos *Ref aninhados da API CRM."""

from crm.services.lookups import customer_label, gai_requester_label


def ref_label(ref, *keys, default='—'):
    """Extrai o primeiro campo não vazio de um dict *Ref."""
    if not isinstance(ref, dict):
        return default
    for key in keys:
        value = ref.get(key)
        if value not in (None, ''):
            return value
    return default


def _nested(record, key):
    if not isinstance(record, dict):
        return None
    value = record.get(key)
    return value if isinstance(value, dict) else None


def customer_ref_label(record, *, nested_key='customer', id_key='customer_gai_id', lookups=None):
    """record.customer.razao_social → nome → lookup → GAI {id}."""
    if not isinstance(record, dict):
        return '—'
    customer = _nested(record, nested_key)
    label = ref_label(customer, 'razao_social', 'nome', 'name', default='')
    if label:
        return label
    gai_id = record.get(id_key)
    if gai_id is not None and lookups:
        return customer_label(lookups, gai_id)
    if gai_id is not None:
        return f'GAI {gai_id}'
    return '—'


def client_ref_label(record, *, nested_key='client', id_key='client_id', lookups=None):
    """ServiceTypeResponse.client (CustomerGAIRef)."""
    return customer_ref_label(
        record,
        nested_key=nested_key,
        id_key=id_key,
        lookups=lookups,
    )


def contract_ref_label(record, *, nested_key='contract', id_key='contract_id'):
    """record.contract.title → Contrato {id}."""
    if not isinstance(record, dict):
        return '—'
    contract = _nested(record, nested_key)
    title = ref_label(contract, 'title', default='')
    if title:
        return title
    contract_id = record.get(id_key)
    if contract_id:
        return f'Contrato {contract_id}'
    return '—'


def board_ref_label(record, *, nested_key='board', flat_key='board_name', id_key='board_id'):
    if not isinstance(record, dict):
        return '—'
    board = _nested(record, nested_key)
    label = ref_label(board, 'name', 'title', 'code', default='')
    if label:
        return label
    flat = record.get(flat_key)
    if flat:
        return flat
    board_id = record.get(id_key)
    return str(board_id) if board_id else '—'


def status_ref_label(record, *, nested_key='status', flat_key='status_name', id_key='status_id'):
    if not isinstance(record, dict):
        return '—'
    status = _nested(record, nested_key)
    label = ref_label(status, 'name', default='')
    if label:
        return label
    flat = record.get(flat_key)
    if flat:
        return flat
    status_id = record.get(id_key)
    return str(status_id) if status_id else '—'


def priority_ref_label(record, *, nested_key='priority', flat_key='priority_name', id_key='priority_id'):
    if not isinstance(record, dict):
        return '—'
    priority = _nested(record, nested_key)
    label = ref_label(priority, 'name', 'slug', default='')
    if label:
        return label
    flat = record.get(flat_key)
    if flat:
        return flat
    priority_id = record.get(id_key)
    return str(priority_id) if priority_id else '—'


def project_ref_label(record, *, nested_key='project', flat_key='project_name', id_key='project_id'):
    if not isinstance(record, dict):
        return '—'
    project = _nested(record, nested_key)
    label = ref_label(project, 'name', 'title', default='')
    if label:
        return label
    flat = record.get(flat_key)
    if flat:
        return flat
    project_id = record.get(id_key)
    return str(project_id) if project_id else '—'


def user_ref_label(record, *, nested_key='created_by', flat_key='username', id_key='created_by_id'):
    if not isinstance(record, dict):
        return '—'
    user = _nested(record, nested_key)
    label = ref_label(user, 'username', 'full_name', default='')
    if label:
        return label
    flat = record.get(flat_key)
    if flat:
        return flat
    user_id = record.get(id_key)
    return str(user_id) if user_id else '—'


def service_type_ref_label(record, *, nested_key='service_type', id_key='service_type_id'):
    if not isinstance(record, dict):
        return '—'
    service_type = _nested(record, nested_key)
    label = ref_label(service_type, 'description', 'type', default='')
    if label:
        return label
    type_id = record.get(id_key)
    return str(type_id) if type_id else '—'


def subject_ref_label(access_row):
    """BoardAccessResponse.subject — username, razao_social, nome ou label."""
    if not isinstance(access_row, dict):
        return '—'
    subject = access_row.get('subject')
    if isinstance(subject, dict):
        label = ref_label(
            subject,
            'username',
            'razao_social',
            'nome',
            'name',
            'label',
            default='',
        )
        if label:
            return label
    if access_row.get('username'):
        return access_row['username']
    if access_row.get('user_id'):
        return f'Usuário {access_row["user_id"]}'
    if access_row.get('designation_id'):
        return f'Designação {access_row["designation_id"]}'
    if access_row.get('team_gai_id'):
        return f'Equipe {access_row["team_gai_id"]}'
    subject_type = access_row.get('subject_type')
    subject_id = access_row.get('subject_id')
    if subject_type and subject_id:
        return f'{subject_type} {subject_id}'
    return '—'


def task_ref_label(run_or_link, *, nested_key='task', id_key='task_id'):
    if not isinstance(run_or_link, dict):
        return '—'
    task = _nested(run_or_link, nested_key)
    title = ref_label(task, 'title', default='')
    if title:
        return title
    task_id = run_or_link.get(id_key) or (task or {}).get('id')
    return str(task_id) if task_id else '—'


def template_ref_label(run_or_link, *, nested_key='template', id_key='template_id'):
    if not isinstance(run_or_link, dict):
        return '—'
    template = _nested(run_or_link, nested_key)
    title = ref_label(template, 'title', default='')
    if title:
        return title
    template_id = run_or_link.get(id_key) or (template or {}).get('id')
    return str(template_id) if template_id else '—'


def requester_ref_label(requester):
    """Label para item de task.requesters[]."""
    if not isinstance(requester, dict):
        return str(requester)
    nested_gai = requester.get('gai') if isinstance(requester.get('gai'), dict) else None
    label = ref_label(
        requester,
        'razao_social',
        'nome',
        'name',
        'group_name',
        default='',
    )
    if label:
        return label
    if nested_gai:
        label = ref_label(nested_gai, 'razao_social', 'nome', 'name', default='')
        if label:
            return label
    return gai_requester_label(requester)


def move_status_label(entry, *, direction='from'):
    """Label de status em move-history (from_status / to_status refs)."""
    if not isinstance(entry, dict):
        return '—'
    prefix = direction if direction in ('from', 'to') else 'from'
    nested_key = f'{prefix}_status'
    flat_key = f'{prefix}_status_name'
    id_key = f'{prefix}_status_id'
    nested = _nested(entry, nested_key)
    label = ref_label(nested, 'name', 'code', default='')
    if label:
        return label
    flat = entry.get(flat_key)
    if flat:
        return flat
    status_id = entry.get(id_key)
    return str(status_id) if status_id else '—'


def moved_by_label(entry):
    """Autor de uma movimentação no histórico."""
    if not isinstance(entry, dict):
        return '—'
    moved_by = entry.get('moved_by')
    if isinstance(moved_by, dict):
        label = ref_label(moved_by, 'username', 'full_name', default='')
        if label:
            return label
    if entry.get('moved_by_username'):
        return entry['moved_by_username']
    moved_by_id = entry.get('moved_by_id')
    return f'Usuário {moved_by_id}' if moved_by_id else '—'
