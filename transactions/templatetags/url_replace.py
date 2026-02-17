from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.copy()
    
    # Atualiza com os novos valores
    for key, value in kwargs.items():
        query[key] = value
    
    # Remove valores vazios (opcional)
    for key in list(query.keys()):
        if not query[key]:
            del query[key]
    
    return query.urlencode()
