from django import template

register = template.Library()
@register.filter(name='correct')
def correct(value, arg):
    return value.wordCorrect(arg)