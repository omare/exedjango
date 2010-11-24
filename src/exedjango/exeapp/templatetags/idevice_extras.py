from django.template.defaultfilters import unordered_list
from django import template

register = template.Library()

@register.filter(name='idevice_ul')
def idevice_ul(groups, group_order):
    idevice_list = []
    for group in group_order:
        idevice_list.append(group)
        prototype_list = []
        for prototype in groups[group]:
            prototype_list.append('<a class="ideviceItem" ideviceid="%s">%s</a>' %\
                              (prototype.id, prototype.title))
        idevice_list.append(prototype_list)
    
    return unordered_list(idevice_list)
         