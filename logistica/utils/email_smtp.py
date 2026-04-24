import smtplib
import socket

from django.conf import settings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EnvioEmailSmtp:
    def __init__(self, para: str, assunto: str, corpo: str) -> None:
        self.smtp_host = settings.EMAIL_SMTP_HOST
        self.smtp_port = int(settings.EMAIL_SMTP_PORT)
        self.email_user = settings.EMAIL_USER
        self.email_pass = settings.EMAIL_PASS
        self.de = settings.EMAIL_USER
        self.para = para
        self.assunto = assunto
        self.corpo = corpo

    def envia_email(self):
        msg = MIMEMultipart()
        msg["From"] = self.de
        msg["To"] = self.para
        msg["Subject"] = self.assunto
        msg.attach(MIMEText(self.corpo, "html", "utf-8"))

        try:
            timeout = 15

            if self.smtp_port == 465:
                server = smtplib.SMTP_SSL(
                    self.smtp_host,
                    self.smtp_port,
                    timeout=timeout
                )
            else:
                server = smtplib.SMTP(
                    self.smtp_host,
                    self.smtp_port,
                    timeout=timeout
                )
                server.ehlo()
                server.starttls()
                server.ehlo()

            server.login(self.email_user, self.email_pass)
            server.sendmail(self.de, [self.para], msg.as_string())
            server.quit()

            return True, "E-mail enviado com sucesso!"

        except smtplib.SMTPAuthenticationError:
            return False, "Falha ao autenticar no SMTP. Verifique usuário, senha ou senha de aplicativo."

        except smtplib.SMTPConnectError:
            return False, "Falha ao conectar no servidor SMTP. Verifique host e porta."

        except smtplib.SMTPException as e:
            return False, f"Erro SMTP: {e}"

        except socket.timeout:
            return False, "Tempo limite ao tentar conectar no SMTP. Verifique host, porta ou bloqueio de rede."

        except Exception as e:
            return False, f"Falha ao enviar o e-mail: {e}"
