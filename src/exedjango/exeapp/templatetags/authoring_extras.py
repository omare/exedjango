from django import template

from exeapp.views.blocks.blockfactory import block_factory
from exeapp.shortcuts import render_idevice as shortcut_render_idevice

register = template.Library()

@register.simple_tag
def render_idevice(idevice):
    '''Convinience filter, just renders calls render function of a
block'''
    
    return shortcut_render_idevice(idevice)

@register.simple_tag
def render_form_media(node, media_types=("js", "css")):
    '''Rendern media for very form on the given node'''
    idevices = node.idevices.all()
    output = set()
    for media_type in media_types:
        for idevice in idevices:
            idevice = idevice.as_child()
            block = block_factory(idevice)
            media = str(block.form().media) 
            output.update(media.split('\n'))
    
    return "\n".join(output)
