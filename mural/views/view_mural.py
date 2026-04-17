from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
def mural(request):
    mural_data = {
        "items": [
            {
                "id": 1,
                "title": "Leitura obrigatória: novo fluxo de atendimento Cielo",
                "summary": "Todos os usuários precisam revisar o novo procedimento antes de iniciar as operações do dia.",
                "content": "Fluxo atualizado com ajustes em validação, checklist e retorno do atendimento.",
                "item_type": "announcement",
                "item_type_label": "Comunicado",
                "severity": "critical",
                "severity_label": "Crítico",
                "starts_at": "13/04/2026 08:00",
                "until_read": True,
                "is_indefinite": True,
                "is_pinned": True,
                "is_read": False,
                "link": "#"
            },
            {
                "id": 2,
                "title": "Manual de abertura e acompanhamento de OS",
                "summary": "Documento com passo a passo operacional para criação, edição e consulta das ordens de serviço.",
                "content": "Manual completo com imagens, exemplos de preenchimento e boas práticas.",
                "item_type": "manual",
                "item_type_label": "Manual",
                "severity": "informational",
                "severity_label": "Informativo",
                "starts_at": "11/04/2026 10:20",
                "until_read": False,
                "is_indefinite": True,
                "is_pinned": False,
                "is_read": False,
                "link": "#"
            },
            {
                "id": 3,
                "title": "Script padrão para tratativa de divergência de coleta",
                "summary": "Modelo oficial de comunicação com orientações para uso em casos de divergência em campo.",
                "content": "Texto padronizado aprovado para agilizar tratativas com técnico e cliente.",
                "item_type": "script",
                "item_type_label": "Script",
                "severity": "important",
                "severity_label": "Importante",
                "starts_at": "12/04/2026 09:10",
                "until_read": False,
                "is_indefinite": True,
                "is_pinned": True,
                "is_read": True,
                "link": "#"
            },
            {
                "id": 4,
                "title": "Aviso operacional sobre atualização de senha",
                "summary": "Por política de segurança, a troca de senha deverá ser feita a cada 60 dias ou após retorno de férias.",
                "content": "A alteração é obrigatória para garantir conformidade e segurança de acesso.",
                "item_type": "notice",
                "item_type_label": "Aviso",
                "severity": "important",
                "severity_label": "Importante",
                "starts_at": "10/04/2026 15:40",
                "until_read": False,
                "is_indefinite": True,
                "is_pinned": False,
                "is_read": False,
                "link": "#"
            },
            {
                "id": 5,
                "title": "Guia rápido de etiquetas e movimentações",
                "summary": "Consulte as principais regras para geração de etiquetas, conferência e movimentação de pedidos.",
                "content": "Guia enxuto com atalhos, regras e observações de uso na operação.",
                "item_type": "manual",
                "item_type_label": "Manual",
                "severity": "moderate",
                "severity_label": "Moderado",
                "starts_at": "09/04/2026 08:15",
                "until_read": False,
                "is_indefinite": False,
                "is_pinned": False,
                "is_read": False,
                "link": "#"
            },
            {
                "id": 6,
                "title": "Comunicado sobre indisponibilidade parcial do módulo logístico",
                "summary": "Durante a janela de manutenção, algumas ações poderão apresentar lentidão ou bloqueio temporário.",
                "content": "Recomendado evitar operações críticas durante o período informado.",
                "item_type": "announcement",
                "item_type_label": "Comunicado",
                "severity": "moderate",
                "severity_label": "Moderado",
                "starts_at": "13/04/2026 07:30",
                "until_read": False,
                "is_indefinite": False,
                "is_pinned": False,
                "is_read": False,
                "link": "#"
            },
            {
                "id": 7,
                "title": "Leitura obrigatória: novo procedimento de evidência de treinamento",
                "summary": "Atualização do processo para garantir rastreabilidade de comunicados e comprovação de ciência dos usuários.",
                "content": "Regras aplicáveis a treinamentos, scripts e materiais críticos da operação.",
                "item_type": "announcement",
                "item_type_label": "Comunicado",
                "severity": "critical",
                "severity_label": "Crítico",
                "starts_at": "13/04/2026 06:55",
                "until_read": True,
                "is_indefinite": True,
                "is_pinned": False,
                "is_read": False,
                "link": "#"
            }
        ]
    }

    return render(request, 'mural/template_mural.html', {
        'site_title': 'Home',
        'current_menu': 'home',
        'mural_data': mural_data,
    })
