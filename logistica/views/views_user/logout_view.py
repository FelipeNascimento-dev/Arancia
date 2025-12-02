from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
def logout_view(request):
    logout(request)
    return redirect('logistica:login')
