from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import PermissionRequiredMixin

# @permission_required('Dashboard.pode_deletar_relatorio')
class RegisterView(PermissionRequiredMixin, CreateView):
    raise_exception = True 
    template_name = 'logistica/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('logistica:login')