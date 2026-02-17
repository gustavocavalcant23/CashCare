from django import template
from decimal import Decimal


register = template.Library()

@register.filter
def br_number(value, decimals=0):
    if value is None:
        return '0'

    try:
        value = Decimal(value)
    except Exception:
        return value

    decimals = int(decimals)

    formatted = f"{value:,.{decimals}f}"

    return (
        formatted
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )
