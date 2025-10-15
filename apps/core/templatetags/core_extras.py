from django import template

register = template.Library()

@register.filter
def add_class(field, css_class):
    """Add CSS class to form field"""
    return field.as_widget(attrs={'class': css_class})

@register.filter
def add_attr(field, attr):
    """Add attribute to form field"""
    attrs = {}
    if '=' in attr:
        key, value = attr.split('=', 1)
        attrs[key] = value
    return field.as_widget(attrs=attrs)
