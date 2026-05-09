from django import template

from players.utils import format_money


register = template.Library()


@register.filter
def money(value):
    return format_money(value)
