import secrets

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.shortcuts import render, redirect

from logistica.models import PasswordResetAccessCode, UserPasswordControl
from logistica.utils.email_smtp import EnvioEmailSmtp


User = get_user_model()


def esqueci_minha_senha(request):
    if request.method == "POST":
        email = request.POST.get("email")

        user = User.objects.filter(
            Q(email__iexact=email) | Q(username__iexact=email),
            is_active=True
        ).first()

        if user:
            code = str(secrets.randbelow(900000) + 100000)

            print(">>> Código gerado:", code)

            PasswordResetAccessCode.objects.filter(
                user=user,
                used=False
            ).update(used=True)

            novo_codigo = PasswordResetAccessCode.objects.create(
                user=user,
                code_hash=make_password(code)
            )

            control, _ = UserPasswordControl.objects.get_or_create(
                user=user
            )
            control.force_change_password = True
            control.save(update_fields=["force_change_password"])

            assunto = "Senha temporária de acesso - Arancia"

            corpo = f"""
            <html>
            <body style="font-family: Arial, sans-serif; color: #1f2937; line-height: 1.5;">

                <h2>Olá, {user.first_name or user.username}!</h2>

                <p>
                    Recebemos uma solicitação para recuperar o seu acesso ao sistema Arancia.
                </p>

                <p>
                    Para entrar no sistema, use a senha temporária abaixo no campo
                    <strong>Senha</strong> da tela de login.
                </p>

                <div style="
                    background-color: #f3f6fb;
                    border: 1px solid #d8e2f0;
                    padding: 18px;
                    margin: 20px 0;
                    text-align: center;
                    border-radius: 8px;
                ">
                    <p style="margin: 0 0 8px 0; font-size: 14px;">
                        Sua senha temporária é:
                    </p>

                    <h1 style="
                        color: #153e70;
                        letter-spacing: 4px;
                        margin: 0;
                        font-size: 32px;
                    ">
                        {code}
                    </h1>
                </div>

                <p>
                    Essa senha temporária é única e expira em <strong>15 minutos</strong>.
                </p>

                <p>
                    Depois que você entrar no sistema usando essa senha temporária,
                    será necessário criar uma nova senha definitiva.
                </p>

                <p>
                    Resumo do que fazer:
                </p>

                <ol>
                    <li>Acesse a tela de login do Arancia.</li>
                    <li>Informe seu usuário ou e-mail.</li>
                    <li>No campo <strong>Senha</strong>, digite a senha temporária acima.</li>
                    <li>Após entrar, cadastre uma nova senha.</li>
                </ol>

                <p>
                    Se você não solicitou a recuperação de acesso, ignore este e-mail.
                </p>

                <br>

                <p>
                    Atenciosamente,<br>
                    Equipe Arancia
                </p>

            </body>
            </html>
            """

            client = EnvioEmailSmtp(
                para=user.email,
                assunto=assunto,
                corpo=corpo
            )

            ok, response = client.envia_email()

            if not ok:
                messages.error(request, response)
                return redirect("logistica:esqueci_minha_senha")

        messages.success(
            request,
            "Se o usuário estiver cadastrado, enviaremos uma senha temporária de acesso. Use essa senha para entrar no sistema e criar uma nova senha definitiva."
        )
        return redirect("logistica:login")

    return render(request, "logistica/templates_user/login.html", {
        "modo": "forgot"
    })
