from django.template.defaultfilters import unordered_list
from django.template.loader import render_to_string
from django import template
from django.conf import settings

from collections import defaultdict
from logging import getLogger

from exeapp.models.idevices.idevice import Idevice

log = getLogger()
register = template.Library()

@register.filter()
def idevice_ul(groups, group_order):
    idevice_list = []
    for group in group_order:
        idevice_list.append("<a>%s</a>" % group)
        prototype_list = []
        for prototype in groups[group]:
            prototype_list.append('<a class="ideviceItem" href="#"' +\
                ' ideviceid="%s">%s</a>' % (prototype.__name__,
                                             prototype.title))
        idevice_list.append(prototype_list)
    
    return unordered_list(idevice_list)
        
@register.filter
def nodes_ul(root):
    node_list = [_node_to_link(root),_create_children_list(root)]
    return unordered_list(node_list)

def _node_to_link(node):
    return render_to_string("exe/node_link.html", locals())

def _create_children_list(node):
        """
        Creates a list of all children from the root recursively.
        Root node has to be appended manually in a higher level function.
        """
        children_list = []
        
        if node.children:
            for child in node.children:
                children_list.append(_node_to_link(child))
                if child.children:
                    children_list.append(_create_children_list(child))
        return children_list
    
@register.tag
def testing(parser, token):
    '''Show content of a tag only if settings.DEBUG is set'''
    nodelist = parser.parse(('endtesting',))
    parser.delete_first_token()
    if settings.DEBUG:
        return TestingNode(nodelist)
    else:
        return TestingNode()

class TestingNode(template.Node):
    '''Renders nodes, if there are any'''
    
    def __init__(self, nodelist=None):
        self.nodelist = nodelist
        
    def render(self, context):
        if self.nodelist is not None:
            return self.nodelist.render(context)
        else:
            return ""
        
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
