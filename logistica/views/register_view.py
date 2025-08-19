from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from ..forms import CustomUserCreationForm

def registrar_usuario(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.info(request, "Cadastro realizado com sucesso!" "Seu username é ")
            return redirect('logistica:index')
        else:
            messages.error(request, "Erro ao cadastrar. Verifique os dados.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'logistica/register.html', {
        'form': form,
        'site_title': 'Cadastro',
        })
