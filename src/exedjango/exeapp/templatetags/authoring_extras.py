from django import template
from exeapp.views.blocks.blockfactory import block_factory

register = template.Library()

@register.filter
def render_idevice(idevice):
    '''Convinience filter, just renders calls render function of a
block'''
    
    leaf_idevice = idevice.as_leaf_class()
    block = block_factory(leaf_idevice)
    return block.render(leaf_idevice)

@register.filter
def render_field_edit(field):
    '''Convinience filter, just renders calls render_view function of field's 
element'''

    return field.controller.render_edit()

@register.filter
def render_field_preview(field):
    '''Convinience filter, just renders calls render_view function of field's 
element'''
    
    return field.controller.render_preview()

@register.filter
def render_field_export(field):
    '''Convinience filter, just renders calls render_export function of field's 
element'''
    
    return field.controller.render_export()

    
