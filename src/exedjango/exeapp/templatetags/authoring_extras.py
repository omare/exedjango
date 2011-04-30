from django import template
from django.utils.safestring import mark_safe

from exeapp.views.blocks.blockfactory import block_factory

register = template.Library()

@register.filter
def render_idevice(idevice):
    '''Convinience filter, just renders calls render function of a
block'''
    
    leaf_idevice = idevice.as_leaf_class()
    block = block_factory(leaf_idevice)
    return mark_safe(block.render())

    
