from datetime import datetime
from django.conf import settings
from django.contrib.auth import logout
from django.contrib import messages


class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.TIMEOUT = getattr(
            settings, 'AUTO_LOGOUT_DELAY', 21600)  # 6 horas de inatividade

    def __call__(self, request):
        if request.user.is_authenticated:
            now = datetime.now()
            last_activity = request.session.get('last_activity')

            if last_activity:
                elapsed = (
                    now - datetime.fromisoformat(last_activity)).total_seconds()
                if elapsed > self.TIMEOUT:
                    logout(request)
                    request.session.flush()
                    messages.info(
                        request, "Sua sessão expirou por inatividade.")
                    return self.get_response(request)

            request.session['last_activity'] = now.isoformat()

        return self.get_response(request)
