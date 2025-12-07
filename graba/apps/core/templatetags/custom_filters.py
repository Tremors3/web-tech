from django import template

register = template.Library()

@register.filter(name='cents_to_price')
def cents_to_price(cents_: int) -> str:
    if cents_ is None: cents_ = 0.0
    return "{:,.2f}".format(cents_/100)
