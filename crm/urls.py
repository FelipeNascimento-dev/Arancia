from django.urls import path
from django.views.generic import RedirectView

from .views import *

app_name = "crm"

urlpatterns = [
    path("crm/", crm_dashboard, name="dashboard"),
    path("crm/ajax/health/", ajax_health, name="ajax_health"),
    path("crm/ajax/clients/<int:gai_id>/", ajax_get_client, name="ajax_get_client"),
    path("crm/ajax/clients/<int:gai_id>/update/", ajax_update_client, name="ajax_update_client"),
    path("crm/ajax/clients/<int:gai_id>/delete/", ajax_delete_client, name="ajax_delete_client"),
    path(
        "crm/ajax/contracts/<str:contract_id>/",
        ajax_get_contract,
        name="ajax_get_contract",
    ),
    path(
        "crm/ajax/contracts/<str:contract_id>/update/",
        ajax_update_contract,
        name="ajax_update_contract",
    ),
    path(
        "crm/ajax/contracts/<str:contract_id>/files/<str:file_id>/delete/",
        ajax_delete_contract_file,
        name="ajax_delete_contract_file",
    ),
    path(
        "crm/ajax/billing/lookups/",
        ajax_billing_lookups,
        name="ajax_billing_lookups",
    ),
    path(
        "crm/ajax/billing/create/",
        ajax_create_billing,
        name="ajax_create_billing",
    ),
    path(
        "crm/ajax/billing/<str:billing_id>/",
        ajax_get_billing,
        name="ajax_get_billing",
    ),
    path(
        "crm/ajax/billing/<str:billing_id>/update/",
        ajax_update_billing,
        name="ajax_update_billing",
    ),
    path("crm/clients/", lista_clientes, name="lista_clientes"),
    path("crm/clients/new/", RedirectView.as_view(pattern_name="crm:lista_clientes", permanent=False), name="form_cliente"),
    path("crm/clients/<int:gai_id>/", detalhe_cliente, name="detalhe_cliente"),
    path("crm/clients/<int:gai_id>/edit/", form_cliente, name="edit_cliente"),
    path("crm/contracts/", lista_contratos, name="lista_contratos"),
    path(
        "crm/contracts/new/",
        RedirectView.as_view(pattern_name="crm:lista_contratos", permanent=False),
        name="form_contrato",
    ),
    path("crm/contracts/<str:contract_id>/", detalhe_contrato, name="detalhe_contrato"),
    path("crm/contracts/<str:contract_id>/edit/", form_contrato, name="edit_contrato"),
    path("crm/billing/", lista_faturamento, name="lista_faturamento"),
    path(
        "crm/billing/new/",
        RedirectView.as_view(pattern_name="crm:lista_faturamento", permanent=False),
        name="form_faturamento",
    ),
    path(
        "crm/billing/<str:billing_id>/edit/",
        RedirectView.as_view(pattern_name="crm:lista_faturamento", permanent=False),
        name="edit_faturamento",
    ),
    path("crm/alerts/", lista_alertas, name="lista_alertas"),
    # Tasks — rotas fixas antes de crm/tasks/<task_id>/ (senão "recurrences" vira UUID).
    path("crm/tasks/", lista_tasks, name="lista_tasks"),
    path("crm/tasks/my/", minhas_tasks, name="minhas_tasks"),
    path("crm/tasks/calendar/", calendario_tasks, name="calendario_tasks"),
    path("crm/tasks/new/", form_task, name="form_task"),
    path("crm/tasks/recurrences/", lista_recorrencias, name="lista_recorrencias"),
    path(
        "crm/tasks/recurrences/<str:recurrence_id>/edit/",
        form_recorrencia,
        name="form_recorrencia",
    ),
    path("crm/tasks/<str:task_id>/edit/", edit_task, name="edit_task"),
    path("crm/tasks/<str:task_id>/", detalhe_task, name="detalhe_task"),
    path("crm/ajax/tasks/<str:task_id>/tab/", ajax_task_tab, name="ajax_task_tab"),
    path("crm/ajax/tasks/<str:task_id>/move/", ajax_move_task, name="ajax_move_task"),
    path("crm/ajax/tasks/<str:task_id>/assign/", ajax_assign_task, name="ajax_assign_task"),
    path(
        "crm/ajax/tasks/<str:task_id>/assignees/<str:assignee_id>/remove/",
        ajax_remove_assignee,
        name="ajax_remove_assignee",
    ),
    path("crm/ajax/tasks/<str:task_id>/watch/", ajax_watch_task, name="ajax_watch_task"),
    path(
        "crm/ajax/tasks/<str:task_id>/watchers/<str:watcher_id>/remove/",
        ajax_remove_watcher,
        name="ajax_remove_watcher",
    ),
    path("crm/ajax/tasks/<str:task_id>/comment/", ajax_comment_task, name="ajax_comment_task"),
    path("crm/ajax/tasks/<str:task_id>/attachment/", ajax_attachment_task, name="ajax_attachment_task"),
    path("crm/ajax/tasks/<str:task_id>/links/", ajax_task_link, name="ajax_task_link"),
    path(
        "crm/ajax/tasks/<str:task_id>/links/<str:link_id>/remove/",
        ajax_remove_task_link,
        name="ajax_remove_task_link",
    ),
    path("crm/ajax/tasks/<str:task_id>/subtasks/", ajax_subtask, name="ajax_subtask"),
    # Projeto CRM Comercial (board crm_comercial)
    path("crm/comercial/", kanban_comercial, name="kanban_comercial"),
    path("crm/comercial/access/", acesso_comercial, name="acesso_comercial"),
    path("crm/comercial/columns/", colunas_comercial, name="colunas_comercial"),
    path(
        "crm/ajax/boards/<str:board_id>/tasks/",
        ajax_kanban_tasks,
        name="ajax_kanban_tasks",
    ),
    path(
        "crm/ajax/boards/<str:board_id>/columns/reorder/",
        ajax_reorder_columns,
        name="ajax_reorder_columns",
    ),
    # Redirects legados — projetos e boards migraram para app projetos/
    path(
        "crm/projects/",
        RedirectView.as_view(pattern_name="projetos:lista_projetos", permanent=False),
        name="lista_projetos",
    ),
    path(
        "crm/projects/<str:project_id>/edit/",
        RedirectView.as_view(pattern_name="projetos:edit_projeto", permanent=False),
        name="edit_projeto",
    ),
    path(
        "crm/projects/<str:project_id>/",
        RedirectView.as_view(pattern_name="projetos:detalhe_projeto", permanent=False),
        name="detalhe_projeto",
    ),
    path(
        "crm/projects/<str:project_id>/members/",
        RedirectView.as_view(pattern_name="projetos:membros_projeto", permanent=False),
        name="membros_projeto",
    ),
    path(
        "crm/projects/<str:project_id>/tasks/",
        RedirectView.as_view(pattern_name="projetos:tasks_projeto", permanent=False),
        name="tasks_projeto",
    ),
    path(
        "crm/boards/",
        RedirectView.as_view(pattern_name="projetos:lista_boards", permanent=False),
        name="lista_boards",
    ),
    path(
        "crm/boards/new/",
        RedirectView.as_view(pattern_name="projetos:form_board", permanent=False),
        name="form_board",
    ),
    path(
        "crm/boards/<str:board_id>/",
        RedirectView.as_view(pattern_name="projetos:kanban_board", permanent=False),
        name="kanban_board",
    ),
    path(
        "crm/boards/<str:board_id>/edit/",
        RedirectView.as_view(pattern_name="projetos:edit_board", permanent=False),
        name="edit_board",
    ),
    path(
        "crm/boards/<str:board_id>/access/",
        RedirectView.as_view(pattern_name="projetos:acesso_board", permanent=False),
        name="acesso_board",
    ),
    path(
        "crm/boards/<str:board_id>/columns/",
        RedirectView.as_view(pattern_name="projetos:colunas_board", permanent=False),
        name="colunas_board",
    ),
    # Configurações
    path("crm/settings/", config_index, name="config_index"),
    path("crm/settings/service-types/", service_types, name="service_types"),
    path("crm/settings/priorities/", priorities, name="priorities"),
    path("crm/settings/status-tasks/", status_tasks, name="status_tasks"),
]
