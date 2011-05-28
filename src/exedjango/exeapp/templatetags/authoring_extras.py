from django import template

from exeapp.views.blocks.blockfactory import block_factory
from exeapp.shortcuts import render_idevice as shortcut_render_idevice
from exeapp.views.authoring import get_media_list

register = template.Library()

@register.simple_tag
def render_idevice(idevice):
    '''Convinience filter, just renders calls render function of a
block'''
    
    return shortcut_render_idevice(idevice)

@register.simple_tag
def render_form_media(node):
    '''Rendern media for very form on the given node'''
    return get_media_list(node)
