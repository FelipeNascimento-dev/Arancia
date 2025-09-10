from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required


@login_required(login_url='logistica:login')
@permission_required('logistica.ger_skill', raise_exception=True)
def skill_ger(request):
    return render(request, 'logistica/skill_ger.html')
