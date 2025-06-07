from django import template

register = template.Library()

@register.filter
def get(d, key):
    """Return the value of dictionary d for the given key."""
    if isinstance(d, dict):
        return d.get(key)
    return None
