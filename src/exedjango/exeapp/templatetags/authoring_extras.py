from django import template

register = template.Library()

@register.filter
def render_idevice(idevice):
    '''Convinience filter, just renders calls render function of a
block'''
    
    block = idevice.block
    return block.render(idevice)


    
