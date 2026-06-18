from crm.forms import TaskAssigneeForm, TaskCommentForm, TaskLinkForm, TaskSubtaskForm
from crm_api.exceptions import CrmApiError
from crm_api.services import tasks as tasks_service
from crm.views.views_tasks._helpers import (
    enrich_assignee_for_display,
    enrich_attachment_for_display,
    enrich_comment_for_display,
    enrich_move_history_for_display,
    enrich_subtask_for_display,
    enrich_watcher_for_display,
    load_task_lookups,
)

TASK_DETAIL_TABS = frozenset({"info", "subtasks", "links", "comentarios", "anexos", "historico"})


def fetch_task_tab_context(client, request, task_id, tab, *, task, board_access, can_comment):
    """Carrega dados de uma aba do detalhe de task (lazy-load)."""
    ctx = {
        "task": task,
        "task_id": task_id,
        "can_comment": can_comment,
        "board_access": board_access,
    }

    if tab == "info":
        lookups = load_task_lookups(client)
        try:
            assignees = [
                enrich_assignee_for_display(a)
                for a in tasks_service.list_assignees(client, task_id)
            ]
        except CrmApiError:
            assignees = []
        try:
            watchers = [
                enrich_watcher_for_display(w)
                for w in tasks_service.list_watchers(client, task_id)
            ]
        except CrmApiError:
            watchers = []
        ctx.update({
            "assignees": assignees,
            "watchers": watchers,
            "assignee_form": TaskAssigneeForm(lookups=lookups),
        })

    elif tab == "subtasks":
        try:
            subtasks = [
                enrich_subtask_for_display(s)
                for s in tasks_service.list_subtasks(client, task_id)
            ]
        except CrmApiError:
            subtasks = []
        ctx.update({
            "subtasks": subtasks,
            "subtask_form": TaskSubtaskForm(),
        })

    elif tab == "links":
        try:
            links = tasks_service.list_links(client, task_id)
        except CrmApiError:
            links = []
        ctx.update({
            "links": links,
            "linked_tasks": task.get("linked_tasks", []) if task else [],
            "link_form": TaskLinkForm(),
        })

    elif tab == "comentarios":
        comments = [
            enrich_comment_for_display(c)
            for c in (task.get("comments", []) if task else [])
        ]
        ctx.update({
            "comments": comments,
            "comment_form": TaskCommentForm(),
        })

    elif tab == "anexos":
        try:
            attachments = [
                enrich_attachment_for_display(a)
                for a in tasks_service.list_attachments(client, task_id)
            ]
        except CrmApiError:
            attachments = []
        ctx.update({"attachments": attachments})

    elif tab == "historico":
        try:
            move_history = [
                enrich_move_history_for_display(h)
                for h in tasks_service.get_move_history(client, task_id)
            ]
        except CrmApiError:
            move_history = []
        ctx.update({"move_history": move_history})

    return ctx
