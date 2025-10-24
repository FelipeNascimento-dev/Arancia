from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def query_update(context, **kwargs):
    """
    Mantém os parâmetros atuais da query string e substitui só os passados.
    Exemplo:
      {% query_update status_janela='atrasado' %}
    """
    request = context['request']
    updated = request.GET.copy()
    for k, v in kwargs.items():
        updated[k] = v
    return "?" + updated.urlencode()
