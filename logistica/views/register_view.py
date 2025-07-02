from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

class RegisterView(CreateView):
    template_name = 'logistica/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('logistica:login')