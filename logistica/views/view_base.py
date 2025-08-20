from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required(login_url='logistica:login')
def index(request):
    user = request.user
    first = user.first_name or user.username
    last = user.last_name or ""
    messages.info(
        request,
        f"👋 Olá, {first} {last}! Seja bem-vindo ao Arancia, nossa nova plataforma de gestão."
    )
    return render(request, 'global/base.html')
