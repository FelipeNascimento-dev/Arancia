"""Filtros de exibição para templates CRM / Projetos."""

from django import template

from crm.helpers.api_display import display_label, is_opaque_id, short_ref

register = template.Library()


@register.filter
def hide_opaque(value):
    """Oculta UUIDs e IDs longos na interface."""
    if is_opaque_id(value):
        return ""
    return value


@register.filter
def crm_ref(value):
    """Referência curta (#abc12345) para IDs opacos."""
    ref = short_ref(value)
    if not ref:
        return ""
    if is_opaque_id(value):
        return f"#{ref}"
    return ref


@register.filter
def label_or_dash(value, arg="-"):
    """Valor legível ou traço quando o ID é opaco."""
    return display_label(value, default=arg)
