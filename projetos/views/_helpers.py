from crm.views.views_tasks._helpers import (
    load_board_lookups,
    load_project_lookups,
    load_task_lookups,
    task_display_value,
)


def menu_context(current_menu, current_submenu=None):
    ctx = {
        "current_parent_menu": "projetos",
        "current_menu": current_menu,
    }
    if current_submenu:
        ctx["current_submenu"] = current_submenu
    return ctx
