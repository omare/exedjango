from django import template

from exeapp.templatetags.utils import _create_children_list
from django.template.loader import render_to_string
from django.template.defaultfilters import unordered_list

from exedjango.utils import common

register = template.Library()

@register.filter
def export_idevice(idevice):
    '''Convinience filter, just renders calls render function of a
block'''
    
    block = idevice.block
    return block.render_export(idevice)

@register.filter
def navigation_bar(data_package, current_node):
    template = "exe/navigation_item.html"
    current_node_template = "exe/navigation_item_current.html"
    
    node_list = _create_children_list(data_package.root,
            template, current_node, current_node_template)
    if data_package.root == current_node:
        root_template = current_node_template
    else:
        root_template = template
    root_item = render_to_string(root_template,
                                {"node" : data_package.root})
    return unordered_list([root_item, [node_list]])

@register.filter
def process_internal_links(package, html):
    """
    take care of any internal links which are in the form of:
       href="exe-node:Home:Topic:etc#Anchor"
    For this WebSite Export, go ahead and process the link entirely,
    using the fully exported (and unique) file names for each node.
    """
    return common.renderInternalLinkNodeFilenames(package, html)
