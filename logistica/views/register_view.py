from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import PermissionRequiredMixin

class RegisterView(PermissionRequiredMixin, CreateView):
    raise_exception = True 
    template_name = 'logistica/register.html'
    form_class = UserCreationForm
    permission_required = 'auth.add_user'
    success_url = reverse_lazy('logistica:login')