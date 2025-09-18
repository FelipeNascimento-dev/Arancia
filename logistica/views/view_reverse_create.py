from django.shortcuts import render, redirect
from ..forms import ReverseCreateForm


def reverse_create(request):
    titulo = 'Reversa de Equipamento'
    form = ReverseCreateForm(request.POST or None, nome_form=titulo)

    if 'seriais' not in request.session:
        request.session['seriais'] = []

    if request.method == "POST" and form.is_valid():
        serial = form.cleaned_data.get("serial")
        if serial:
            seriais = request.session['seriais']
            seriais.append(serial)
            request.session['seriais'] = seriais
            request.session.modified = True
        return redirect("logistica:reverse_create")

    todos_seriais = request.session.get('seriais', [])
    table_reverse = [todos_seriais[i:i+10]
                     for i in range(0, len(todos_seriais), 10)]
    table_reverse = list(reversed(table_reverse))

    context = {
        'form': form,
        'botao_texto': 'Inserir',
        'site_title': 'Reversa',
        'table_reverse': table_reverse,
    }
    return render(request, 'logistica/reverse_create.html', context)
