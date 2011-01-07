from django import template

register = template.Library()

@register.filter
def render_idevice_view(idevice):
    '''Renders idevice for export'''
    return idevice.render_view()
        
@register.filter
def render_idevice_preview(idevice):
    '''Renders idevice for the in-app preview'''
    return idevice.render_preview()

@register.filter
def render_idevice_edit(idevice):
    '''Renders in-app edit view'''
    return idevice.render_edit()
    
     

        