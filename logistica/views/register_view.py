from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from ..forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required, permission_required


@login_required(login_url='logistica:login')
@permission_required('auth.add_user', raise_exception=True)
def registrar_usuario(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Cadastro realizado com sucesso!")
            messages.info(request, f"Anote o username: {user.username}")
            form = CustomUserCreationForm()
            return render(request, 'logistica/register.html', {
                'form': form,
                'site_title': 'Cadastro',
            })

        else:
<<<<<<< HEAD
            messages.error(request, form.errors)
=======
            if form.errors:
                for erro in form.errors:
                    messages.error(request, form.errors[erro][0])
>>>>>>> release4-transp

    else:
        form = CustomUserCreationForm()
    return render(request, 'logistica/register.html', {
        'form': form,
        'site_title': 'Cadastro',
    })
