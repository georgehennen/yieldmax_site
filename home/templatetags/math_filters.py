from django import template

register = template.Library()

@register.filter(name='div') # Good practice to explicitly name the filter
def division(value, arg):
    try:
        # Ensure args are float for division
        return float(value) / float(arg) if float(arg) != 0 else 0
    except (ValueError, TypeError, ZeroDivisionError): # Catch ZeroDivisionError too
        return 0 # Or handle as you see fit, e.g., return None or 'N/A'

@register.filter(name='mul') # Good practice to explicitly name the filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0 # Or handle as you see fit