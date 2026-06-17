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
    enrich_assignee_for_display,
    enrich_attachment_for_display,
    enrich_comment_for_display,
    enrich_move_history_for_display,
    enrich_subtask_for_display,
    enrich_task_for_display,
    enrich_watcher_for_display,
    load_task_lookups,
    menu_context,
    task_display_value,
)


@crm_permission_required("view_task")
def detalhe_task(request, task_id):
    client = CrmApiClient(request)
    active_tab = request.GET.get("tab", "info")
    task = None
    subtasks = []
    links = []
    assignees = []
    watchers = []
    attachments = []
    move_history = []
    comments = []
    board_access = {}

    lookups = load_task_lookups(client)
    comment_form = TaskCommentForm()
    subtask_form = TaskSubtaskForm()
    link_form = TaskLinkForm()
    assignee_form = TaskAssigneeForm(lookups=lookups)

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
                    return redirect(f"{request.path}?tab=comentarios")
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
                    return redirect(f"{request.path}?tab=subtasks")
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
                    return redirect(f"{request.path}?tab=links")
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
            return redirect(f"{request.path}?tab=links")

        elif "add_assignee" in request.POST:
            if not request.user.has_perm("crm.assign_task"):
                messages.error(request, "Você não tem permissão para atribuir tasks.")
                return redirect("crm:detalhe_task", task_id=task_id)
            assignee_form = TaskAssigneeForm(request.POST, lookups=lookups)
            if assignee_form.is_valid():
                try:
                    tasks_service.add_assignee(
                        client, task_id, assignee_payload(assignee_form.cleaned_data),
                    )
                    messages.success(request, "Responsável adicionado.")
                    return redirect(f"{request.path}?tab=info")
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
            return redirect(f"{request.path}?tab=info")

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
            return redirect(f"{request.path}?tab=info")

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
            return redirect(f"{request.path}?tab=anexos")

    try:
        subtasks = [enrich_subtask_for_display(s) for s in tasks_service.list_subtasks(client, task_id)]
    except CrmApiError:
        pass
    try:
        links = tasks_service.list_links(client, task_id)
    except CrmApiError:
        pass
    try:
        assignees = [enrich_assignee_for_display(a) for a in tasks_service.list_assignees(client, task_id)]
    except CrmApiError:
        pass
    try:
        watchers = [enrich_watcher_for_display(w) for w in tasks_service.list_watchers(client, task_id)]
    except CrmApiError:
        pass
    try:
        attachments = [
            enrich_attachment_for_display(a)
            for a in tasks_service.list_attachments(client, task_id)
        ]
    except CrmApiError:
        pass
    try:
        move_history = [
            enrich_move_history_for_display(h)
            for h in tasks_service.get_move_history(client, task_id)
        ]
    except CrmApiError:
        pass

    comments = [
        enrich_comment_for_display(c)
        for c in (task.get("comments", []) if task else [])
    ]
    linked_tasks = task.get("linked_tasks", []) if task else []
    recurrence_template_id = task.get("recurrence_template_id") if task else None

    return render(
        request,
        "crm/templates_tasks/detalhe_task.html",
        {
            "site_title": f"CRM — {task.get('display_title') or task_id}",
            "task": task,
            "task_id": task_id,
            "subtasks": subtasks,
            "links": links,
            "linked_tasks": linked_tasks,
            "assignees": assignees,
            "watchers": watchers,
            "attachments": attachments,
            "move_history": move_history,
            "comments": comments,
            "comment_form": comment_form,
            "subtask_form": subtask_form,
            "link_form": link_form,
            "assignee_form": assignee_form,
            "active_tab": active_tab,
            "can_comment": can_comment,
            "board_access": board_access,
            "recurrence_template_id": recurrence_template_id,
            "task_display_value": task_display_value,
            **menu_context("projetos_tasks", "detalhe"),
        },
    )
