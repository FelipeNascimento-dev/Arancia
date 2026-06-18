from datetime import datetime

from django.conf import settings
from django.contrib.auth import logout
from django.contrib import messages


class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.TIMEOUT = getattr(
            settings, 'AUTO_LOGOUT_DELAY', 21600)  # 6 horas de inatividade
        self.WRITE_INTERVAL = getattr(
            settings, 'AUTO_LOGOUT_ACTIVITY_WRITE_INTERVAL', 300)

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

            last_written = request.session.get('last_activity_written')
            should_write = last_activity is None
            if not should_write and last_written:
                since_write = (
                    now - datetime.fromisoformat(last_written)
                ).total_seconds()
                should_write = since_write >= self.WRITE_INTERVAL
            elif not should_write:
                should_write = True

            if should_write:
                request.session['last_activity'] = now.isoformat()
                request.session['last_activity_written'] = now.isoformat()

        return self.get_response(request)
