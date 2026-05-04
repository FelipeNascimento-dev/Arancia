import random
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from ..utils.email_smtp import EnvioEmailSmtp


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
@permission_required('logistica.contas_privilegiadas', raise_exception=True)
def trigger_privileged_auth(request):
    user = request.user
    fake_code = str(random.randint(100000, 999999))

    assunto = "Acesso à Área de Gestão de Contas Privilegiadas - Auditoria ISO 27001"
    corpo = f"""
    <html>
        <body>
            <h2>Solicitação de Acesso Privilegiado</h2>
            <p>Olá <strong>{user.username}</strong>,</p>
            <p>Um acesso à área de Gestão de Contas Privilegiadas foi detectado.</p>
            <p>Seu código de verificação é: <b style="font-size: 20px;">{fake_code}</b></p>
            <p>Este acesso está sendo registrado para fins de conformidade com a ISO 27001:2022.</p>
        </body>
    </html>
    """

    envio = EnvioEmailSmtp(para=user.email, assunto=assunto, corpo=corpo)
    sucesso, mensagem = envio.envia_email()

    return render(request, 'global/gestao_contas.html', {
        'email': user.email,
        'site_title': 'Contas Privilegiadas - Autenticação',
        'current_parent_menu': 'seguranca_informacao',
        'current_menu': 'contas_privilegiadas'
    })


@login_required
def validate_privileged_access(request):
    if request.method == "POST":
        request.session['privileged_access_granted'] = True
        return redirect('logistica:gestao_contas_privilegiadas')

    return redirect('logistica:trigger_privileged_auth')
