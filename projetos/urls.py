from django.urls import path

from .views import *

app_name = "projetos"

urlpatterns = [
    path("projetos/", lista_projetos, name="lista_projetos"),
    # Rotas fixas de boards antes de projetos/<project_id>/ (senão "boards" vira UUID).
    path("projetos/boards/", lista_boards, name="lista_boards"),
    path("projetos/boards/new/", form_board, name="form_board"),
    path("projetos/boards/<str:board_id>/", kanban_board, name="kanban_board"),
    path("projetos/boards/<str:board_id>/edit/", form_board, name="edit_board"),
    path("projetos/boards/<str:board_id>/access/", acesso_board, name="acesso_board"),
    path("projetos/boards/<str:board_id>/columns/", colunas_board, name="colunas_board"),
    path(
        "projetos/ajax/boards/<str:board_id>/columns/reorder/",
        ajax_reorder_columns,
        name="ajax_reorder_columns",
    ),
    path("projetos/<str:project_id>/edit/", form_projeto, name="edit_projeto"),
    path("projetos/<str:project_id>/members/", membros_projeto, name="membros_projeto"),
    path("projetos/<str:project_id>/tasks/", tasks_projeto, name="tasks_projeto"),
    path("projetos/<str:project_id>/", detalhe_projeto, name="detalhe_projeto"),
]
