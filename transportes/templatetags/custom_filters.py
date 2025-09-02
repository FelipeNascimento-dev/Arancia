from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Acessa um valor de dicionário no template"""
    if isinstance(dictionary, dict):
        return dictionary.get(key, 0)
    return 0
