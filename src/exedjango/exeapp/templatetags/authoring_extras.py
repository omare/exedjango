from django import template

from exeapp.shortcuts import render_idevice as shortcut_render_idevice

register = template.Library()

@register.filter
def render_idevice(idevice):
    '''Convinience filter, just renders calls render function of a
block'''
    
    return shortcut_render_idevice(idevice)

    
