from django.contrib import messages
from django.shortcuts import redirect, render

from crm.decorators import crm_permission_required
from crm.forms import TaskAssigneeForm, TaskCommentForm, TaskLinkForm, TaskSubtaskForm
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.payloads import assignee_payload, comment_payload, link_payload, subtask_payload
from crm_api.services import tasks as tasks_service
from crm.views.views_tasks._helpers import (
    board_access_for_task,
    can_comment_on_board,
    enrich_task_for_display,
    load_task_lookups,
    menu_context,
    task_display_value,
)
from crm.views.views_tasks.task_tab_helpers import (
    TASK_DETAIL_TABS,
    fetch_task_sidebar_context,
    fetch_task_tab_context,
)


@crm_permission_required("view_task")
def detalhe_task(request, task_id):
    client = CrmApiClient(request)
    active_tab = request.GET.get("tab", "")
    if active_tab and active_tab not in TASK_DETAIL_TABS:
        active_tab = ""
    task = None
    board_access = {}

    comment_form = TaskCommentForm()
    subtask_form = TaskSubtaskForm()
    link_form = TaskLinkForm()
    needs_assignee_lookups = (
        request.method == "POST" and "add_assignee" in request.POST
    )
    if needs_assignee_lookups:
        assignee_form = TaskAssigneeForm(lookups=load_task_lookups(client))
    else:
        assignee_form = TaskAssigneeForm()

    try:
        task = tasks_service.get_task(client, task_id)
        if task:
            task = enrich_task_for_display(task)
    except CrmApiError as exc:
        messages.error(request, crm_error_message_pt(exc))
        return redirect("crm:lista_tasks")

    board_access = board_access_for_task(client, task)
    can_comment = can_comment_on_board(request, board_access)

    if request.method == "POST":
        if "add_comment" in request.POST:
            if not can_comment:
                messages.error(request, "Você não tem permissão para comentar neste board.")
                return redirect("crm:detalhe_task", task_id=task_id)
            comment_form = TaskCommentForm(request.POST)
            if comment_form.is_valid():
                try:
                    tasks_service.add_comment(
                        client, task_id, comment_payload(comment_form.cleaned_data),
                    )
                    messages.success(request, "Comentário adicionado.")
                    return redirect(f"{request.path}?tab=comentarios#comentarios")
                except CrmApiError as exc:
                    messages.error(request, crm_error_message_pt(exc))

        elif "add_subtask" in request.POST:
            if not request.user.has_perm("crm.add_task"):
                messages.error(request, "Você não tem permissão para adicionar subtarefas.")
                return redirect("crm:detalhe_task", task_id=task_id)
            subtask_form = TaskSubtaskForm(request.POST)
            if subtask_form.is_valid():
                try:
                    tasks_service.create_subtask(
                        client, task_id, subtask_payload(subtask_form.cleaned_data),
                    )
                    messages.success(request, "Subtarefa adicionada.")
                    return redirect(f"{request.path}?tab=subtasks#subtasks")
                except CrmApiError as exc:
                    messages.error(request, crm_error_message_pt(exc))

        elif "add_link" in request.POST:
            if not request.user.has_perm("crm.change_task"):
                messages.error(request, "Você não tem permissão para vincular tasks.")
                return redirect("crm:detalhe_task", task_id=task_id)
            link_form = TaskLinkForm(request.POST)
            if link_form.is_valid():
                try:
                    tasks_service.create_link(
                        client, task_id, link_payload(link_form.cleaned_data),
                    )
                    messages.success(request, "Vínculo criado.")
                    return redirect(f"{request.path}?tab=links#links")
                except CrmApiError as exc:
                    messages.error(request, crm_error_message_pt(exc))

        elif "delete_link" in request.POST:
            link_id = request.POST.get("link_id")
            if link_id and request.user.has_perm("crm.change_task"):
                try:
                    tasks_service.delete_link(client, task_id, link_id)
                    messages.success(request, "Vínculo removido.")
                except CrmApiError as exc:
                    messages.error(request, crm_error_message_pt(exc))
            return redirect(f"{request.path}?tab=links#links")

        elif "add_assignee" in request.POST:
            if not request.user.has_perm("crm.assign_task"):
                messages.error(request, "Você não tem permissão para atribuir tasks.")
                return redirect("crm:detalhe_task", task_id=task_id)
            assignee_form = TaskAssigneeForm(request.POST, lookups=load_task_lookups(client))
            if assignee_form.is_valid():
                try:
                    tasks_service.add_assignee(
                        client, task_id, assignee_payload(assignee_form.cleaned_data),
                    )
                    messages.success(request, "Responsável adicionado.")
                    return redirect(f"{request.path}#atribuidos")
                except CrmApiError as exc:
                    messages.error(request, crm_error_message_pt(exc))

        elif "remove_assignee" in request.POST:
            assignee_id = request.POST.get("assignee_id")
            if assignee_id and request.user.has_perm("crm.assign_task"):
                try:
                    tasks_service.remove_assignee(client, task_id, assignee_id)
                    messages.success(request, "Responsável removido.")
                except CrmApiError as exc:
                    messages.error(request, crm_error_message_pt(exc))
            return redirect(f"{request.path}#atribuidos")

        elif "watch_task" in request.POST:
            if request.user.has_perm("crm.view_task"):
                try:
                    tasks_service.watch_task(client, task_id)
                    messages.success(request, "Você está observando esta task.")
                except CrmApiError as exc:
                    messages.error(request, crm_error_message_pt(exc))
            return redirect("crm:detalhe_task", task_id=task_id)

        elif "remove_watcher" in request.POST:
            watcher_id = request.POST.get("watcher_id")
            if watcher_id:
                try:
                    tasks_service.remove_watcher(client, task_id, watcher_id)
                    messages.success(request, "Observador removido.")
                except CrmApiError as exc:
                    messages.error(request, crm_error_message_pt(exc))
            return redirect(f"{request.path}#atribuidos")

        elif "upload_attachment" in request.POST:
            if not can_comment:
                messages.error(request, "Você não tem permissão para enviar anexos neste board.")
                return redirect("crm:detalhe_task", task_id=task_id)
            upload_file = request.FILES.get("attachment")
            if upload_file:
                try:
                    tasks_service.upload_attachment(
                        client,
                        task_id,
                        files={"file": (upload_file.name, upload_file.read(), upload_file.content_type)},
                    )
                    messages.success(request, "Anexo enviado.")
                except CrmApiError as exc:
                    messages.error(request, crm_error_message_pt(exc))
            return redirect(f"{request.path}?tab=anexos#anexos")

    sidebar_context = fetch_task_sidebar_context(client, task_id, user=request.user)

    tab_context = {}
    if active_tab:
        tab_context = fetch_task_tab_context(
            client,
            request,
            task_id,
            active_tab,
            task=task,
            board_access=board_access,
            can_comment=can_comment,
        )

    recurrence_template_id = task.get("recurrence_template_id") if task else None

    return render(
        request,
        "crm/templates_tasks/detalhe_task.html",
        {
            "site_title": f"CRM — {task.get('display_title') or task_id}",
            "task": task,
            "task_id": task_id,
            "comment_form": comment_form,
            "subtask_form": subtask_form,
            "link_form": link_form,
            "assignee_form": assignee_form,
            "active_tab": active_tab,
            "active_section": active_tab if active_tab in {"subtasks", "links", "comentarios", "anexos", "historico"} else "",
            "can_comment": can_comment,
            "board_access": board_access,
            "recurrence_template_id": recurrence_template_id,
            "task_display_value": task_display_value,
            **sidebar_context,
            **tab_context,
            **menu_context("projetos_tasks", "detalhe"),
        },
    )
