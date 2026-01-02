from django.http import HttpResponse
from backoffice.utils.excel_export import gerar_excel_retorno
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('backoffice.Importar', raise_exception=True)
def baixar_duplicados_view(request):
    ignorados = request.session.get("ignorados")

    if not ignorados:
        return HttpResponse("Nenhum dado de ignorados encontrado.", status=400)

    output = gerar_excel_retorno(ignorados)

    response_excel = HttpResponse(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response_excel['Content-Disposition'] = 'attachment; filename="ignorados.xlsx"'
    return response_excel
