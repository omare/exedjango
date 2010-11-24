from django.template import Context, Template
from django.template.loader import get_template

def render_to_unicode(template_name, context):
    '''Convinience function. Renders a template to unicode object'''
    t = get_template(template_name)
    c = Context(context)
    return t.render(c)