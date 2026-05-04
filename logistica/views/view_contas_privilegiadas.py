from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required, permission_required


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
@permission_required('logistica.contas_privilegiadas', raise_exception=True)
def gestao_contas_privilegiadas(request):
    if not request.session.get('privileged_access_granted'):
        return redirect('trigger_privileged_auth')

    contas = [
        {
            'nome': 'Locaweb - SMTP Corporativo',
            'descricao': 'Envio de e-mails via C-Trends Flow',
            'servidor': 'smtp.locaweb.com.br',
            'usuario': 'rcvsouza',
            'token': '••••••••••••••••',
            'status': 'Ativa'
        },
        {
            'nome': 'Servidor de Produção - AWS',
            'descricao': 'Acesso SSH root - Infraestrutura Principal',
            'servidor': '192.168.•.••• (VPN)',
            'usuario': 'admin_ctrends',
            'token': '••••••••••••••••',
            'status': 'Aprovada'
        },
        {
            'nome': 'Banco de Dados - PostgreSQL',
            'descricao': 'Credenciais de leitura/escrita Master',
            'servidor': 'Banco de Dados Principal',
            'usuario': 'postgres_master',
            'token': '••••••••••••••••',
            'status': 'Revisada'
        },
        {
            'nome': 'Integração Cielo - Gateway',
            'descricao': 'Acesso CTRENDS para emissão de pagamentos/declaração de conteúdo',
            'servidor': 'api-internet.cielo.com.br',
            'usuario': 'c806530b-9a19-...',
            'token': '••••••••••••••••',
            'status': 'Aprovada'
        },
        {
            'nome': 'Google Maps API - Roteirização',
            'descricao': 'Chave de API restrita para cálculo de rotas (Arancia)',
            'servidor': 'maps.googleapis.com',
            'usuario': 'API Key',
            'token': 'AIzaSy••••••••••••••••',
            'status': 'Ativa'
        },
    ]

    return render(request, 'global/contas_privilegiadas.html', {
        'contas': contas,
        'site_title': 'Contas Privilegiadas',
        'current_parent_menu': 'seguranca_informacao',
        'current_menu': 'contas_privilegiadas'
    })
