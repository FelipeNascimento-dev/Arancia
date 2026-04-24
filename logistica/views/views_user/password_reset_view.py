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

        print(">>> Usuário encontrado:", user)

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

            print(">>> Código salvo no banco. ID:", novo_codigo.id)

            control, _ = UserPasswordControl.objects.get_or_create(
                user=user
            )
            control.force_change_password = True
            control.save(update_fields=["force_change_password"])

            assunto = "Código de acesso único - Arancia"

            corpo = f"""
            <html>
            <body>
                <h2>Olá, {user.first_name or user.username}!</h2>

                <p>Recebemos uma solicitação para recuperação de acesso.</p>

                <p>Use o código abaixo no campo <strong>senha</strong> da tela de login:</p>

                <h1 style="color:#153e70; letter-spacing:4px;">{code}</h1>

                <p>Este código é único e expira em 15 minutos.</p>

                <p>
                    Após entrar no sistema, você será direcionado automaticamente
                    para alterar sua senha.
                </p>

                <p>Se você não solicitou essa alteração, ignore este e-mail.</p>
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
            "Se o usuário/e-mail estiver cadastrado, enviaremos um código de acesso."
        )
        return redirect("logistica:login")

    return render(request, "logistica/templates_user/login.html", {
        "modo": "forgot"
    })
