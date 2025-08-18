from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required(login_url='logistica:login')
def logout_confirm_view(request):
    return render(
        request,
        'logistica/logout_confirm.html',
        {"site_title": "Confirmar Logout"}
    )