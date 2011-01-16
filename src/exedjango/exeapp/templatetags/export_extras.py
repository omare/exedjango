from django import template

from django.template.loader import render_to_string
from django.template.defaultfilters import unordered_list

from exedjango.utils import common

import re

register = template.Library()

@register.filter
def export_idevice(idevice):
    '''Convinience filter, just renders calls render function of a
block'''
    
    block = idevice.block
    return block.render_export(idevice)

@register.inclusion_tag('navigation_bar.html')
def navigation_bar(page_structure, current_page):
    return locals()

@register.filter
def process_internal_links(html, package):
    """
    take care of any internal links which are in the form of:
       href="exe-node:Home:Topic:etc#Anchor"
    For this WebSite Export, go ahead and process the link entirely,
    using the fully exported (and unique) file names for each node.
    """
    return common.renderInternalLinkNodeFilenames(package, html)
