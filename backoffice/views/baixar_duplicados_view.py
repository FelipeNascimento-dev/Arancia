from django.http import HttpResponse
from backoffice.utils.excel_export import gerar_excel_retorno
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('backoffice.Importar', raise_exception=True)
def baixar_duplicados_view(request):
    duplicados = request.session.get("duplicados")

    if not duplicados:
        return HttpResponse("Nenhum dado de duplicados encontrado.", status=400)

    output = gerar_excel_retorno(duplicados)

    response_excel = HttpResponse(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response_excel['Content-Disposition'] = 'attachment; filename="duplicados.xlsx"'
    return response_excel
