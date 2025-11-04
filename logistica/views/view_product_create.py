from ..forms import ProductCreateForm
from django.shortcuts import render


def product_create(request):
    titulo = "Criar Novo Produto"
    form = ProductCreateForm(nome_form=titulo)
    return render(request, 'logistica/product_create.html', {'form': form})
