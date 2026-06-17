from django.db import models


class CrmPermissions(models.Model):
    """Modelo dummy — permissões reais vêm do seed Alembic (app_label=crm).

    Gates de template usam estes codenames (ex.: view_task, view_contract).
    A API `/me/context` pode expor plural (view_tasks, view_contracts) — não
    substituir gates Django sem alinhar seed Alembic.
    """

    class Meta:
        managed = False
        verbose_name = "--CRM--"
        verbose_name_plural = "--CRM--"
        permissions = [
            ("view_clients", "Visualizar clientes"),
            ("add_client", "Adicionar cliente"),
            ("change_client", "Alterar cliente"),
            ("delete_client", "Excluir cliente"),
            ("view_contract", "Visualizar contratos"),
            ("add_contract", "Adicionar contrato"),
            ("change_contract", "Alterar contrato"),
            ("delete_contract", "Excluir contrato"),
            ("upload_contract_file", "Enviar arquivo de contrato"),
            ("view_billing", "Visualizar faturamento"),
            ("add_billing", "Adicionar faturamento"),
            ("change_billing", "Alterar faturamento"),
            ("view_task", "Visualizar tasks"),
            ("add_task", "Adicionar task"),
            ("change_task", "Alterar task"),
            ("delete_task", "Excluir task"),
            ("move_task", "Mover task"),
            ("assign_task", "Atribuir task"),
            ("manage_watchers", "Gerenciar observadores"),
            ("view_board", "Visualizar boards"),
            ("add_board", "Adicionar board"),
            ("change_board", "Alterar board"),
            ("delete_board", "Excluir board"),
            ("manage_board_columns", "Gerenciar colunas do board"),
            ("manage_board_access", "Gerenciar acesso ao board"),
            ("view_project", "Visualizar projetos"),
            ("add_project", "Adicionar projeto"),
            ("change_project", "Alterar projeto"),
            ("delete_project", "Excluir projeto"),
            ("manage_project_members", "Gerenciar membros do projeto"),
            ("view_teams", "Visualizar equipes"),
            ("view_task_recurrence", "Visualizar recorrências"),
            ("add_task_recurrence", "Adicionar recorrência"),
            ("change_task_recurrence", "Alterar recorrência"),
            ("delete_task_recurrence", "Excluir recorrência"),
            ("run_task_scheduler", "Executar agendador de tasks"),
            ("view_settings", "Visualizar configurações"),
            ("change_settings", "Alterar configurações"),
            ("manage_service_types", "Gerenciar tipos de serviço"),
            ("manage_priorities", "Gerenciar prioridades"),
            ("manage_status_tasks", "Gerenciar status de tasks"),
        ]

    def __str__(self):
        return "CRM Permissions"
