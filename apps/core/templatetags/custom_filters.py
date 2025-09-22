from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    """Filtre personnalisé pour splitter une chaîne"""
    if not value:
        return []
    return [item.strip() for item in value.split(delimiter) if item.strip()]
