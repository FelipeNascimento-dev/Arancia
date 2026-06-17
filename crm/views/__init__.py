from .view_dashboard import crm_dashboard
from .views_ajax.view_ajax_billing import ajax_create_billing, ajax_get_billing, ajax_update_billing
from .views_ajax.view_ajax_boards import ajax_reorder_columns
from .views_ajax.view_ajax_clients import ajax_delete_client, ajax_get_client, ajax_update_client
from .views_ajax.view_ajax_contracts import (
    ajax_delete_contract_file,
    ajax_get_contract,
    ajax_update_contract,
)
from .views_ajax.view_ajax_health import ajax_health
from .views_ajax.view_ajax_tasks import (
    ajax_assign_task,
    ajax_attachment_task,
    ajax_comment_task,
    ajax_move_task,
    ajax_remove_assignee,
    ajax_remove_task_link,
    ajax_remove_watcher,
    ajax_subtask,
    ajax_task_link,
    ajax_watch_task,
)
from .views_alertas.view_lista_alertas import lista_alertas
from .views_clientes.view_detalhe_cliente import detalhe_cliente
from .views_clientes.view_form_cliente import form_cliente
from .views_clientes.view_lista_clientes import lista_clientes
from .views_comercial.view_acesso_comercial import acesso_comercial
from .views_comercial.view_colunas_comercial import colunas_comercial
from .views_comercial.view_kanban_comercial import kanban_comercial
from .views_configuracoes.view_config_index import config_index
from .views_configuracoes.view_priorities import priorities
from .views_configuracoes.view_service_types import service_types
from .views_configuracoes.view_status_tasks import status_tasks
from .views_contratos.view_detalhe_contrato import detalhe_contrato
from .views_contratos.view_form_contrato import form_contrato
from .views_contratos.view_lista_contratos import lista_contratos
from .views_faturamento.view_lista_faturamento import lista_faturamento
from .views_tasks.view_calendario_tasks import calendario_tasks
from .views_tasks.view_detalhe_task import detalhe_task
from .views_tasks.view_edit_task import edit_task
from .views_tasks.view_form_recorrencia import form_recorrencia
from .views_tasks.view_form_task import form_task
from .views_tasks.view_lista_recorrencias import lista_recorrencias
from .views_tasks.view_lista_tasks import lista_tasks
from .views_tasks.view_minhas_tasks import minhas_tasks
