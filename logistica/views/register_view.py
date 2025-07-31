# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from ..forms import CustomUserCreationForm

def registrar_usuario(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuário cadastrado com sucesso.")
            return redirect('logistica:login')
        else:
            messages.error(request, "Erro ao cadastrar. Verifique os dados.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'logistica/register.html', {'form': form})
