from django.contrib.auth.views import LoginView

class UserLoginView(LoginView):
    template_name = 'logistica/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_title"] = "Login"
        return context