'''
Created on Nov 28, 2010

@author: alendit
'''
from collections import defaultdict

from django import template

from exeapp.models import idevice_storage
from exeapp.models.idevices.idevice import Idevice

register = template.Library()

@register.inclusion_tag('exe/outlinepane.html')
def render_outlinepane(package):
    return {'node_list' : _create_node_list(package.root)}

def _create_node_list(node):
        """
        Creates a list of all children recursively.
        """
        ul = [node]
        if node.children:
            ul.append(_create_node_list(node))
        return ul

@register.inclusion_tag('exe/idevicepane.html')
def render_idevicepane(prototypes):
    """
    Returns an html string for viewing idevicepane
    """

    groups = defaultdict(list)

    def sortfunc(pt1, pt2):
        """Used to sort prototypes by title"""
        return cmp(pt1.title, pt2.title)
    prototypes.sort(sortfunc)
    for prototype in prototypes:
        if prototype.group:
            groups[prototype.group].append(prototype)
        else:
            groups[Idevice.Unknown] += prototype
    # used to perserve the group order
    group_order = sorted(groups.keys())
    return locals()