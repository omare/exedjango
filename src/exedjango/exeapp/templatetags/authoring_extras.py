from django import template

register = template.Library()

@register.filter
def render_idevice(idevice):
    '''Convinience filter, just renders calls render function of a
block'''
    
    leaf_idevice = idevice.as_leaf_class()
    block = leaf_idevice.block
    return block.render(leaf_idevice)


    
