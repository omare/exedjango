# ===========================================================================
# eXe 
# Copyright 2004-2006, University of Auckland
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# ===========================================================================
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from exeapp.views.blocks.widgets import FreeTextWidget
from exeapp.views.blocks.genericblock import GenericBlock
from django.forms.models import modelformset_factory
"""
FreeTextBlock can render and process FreeTextIdevices as XHTML
"""

from django import forms
from django.conf import settings

import logging
import re

from exeapp.views.blocks.block import Block
from exeapp.models.idevices import FreeTextIdevice

from exedjango.utils import common

# from exe.webui                     import common

log = logging.getLogger(__name__)


def _(value):
    return value

class IdeviceForm(forms.ModelForm):
    
    def render_edit(self):
        return str(self)
    
    def render_preview(self):
        return self._render_view("preview")
    
    def render_export(self):
        return self._render_view("export")
    
    def _render_view(self, purpose):
        '''Decouples field rendering from the purpose'''
        html = ""
        renderer_name = "render_%s" % purpose
        for name, field_object in self.fields.items():
            if hasattr(field_object.widget, renderer_name):
                renderer = getattr(field_object.widget, renderer_name)
                html += renderer(self.initial[name])
            else:
                # dumb widget, just return <p>
                html += "<p>%s</p>" % self.initial[name]
        
        return mark_safe(html) 
    
class IdeviceFormFactory(object):
    def __init__(self, form, model, fields, widgets):
        self.model = model
        self.fields = tuple(fields)
        self.widgets = widgets
        self.form = form
        
    def __call__(self, *args, **kwargs):
        class NewIdeviceForm(self.form):
            pass
            
            class Meta:
                model = self.model
                fields = self.fields
                widgets = self.widgets
                
        return NewIdeviceForm(*args, **kwargs)

# ===========================================================================
class FreeTextBlock(GenericBlock):
    """
    FreeTextBlock can render and process FreeTextIdevices as XHTML
    GenericBlock will replace it..... one day
    """
    form_factory = IdeviceFormFactory(IdeviceForm,
                                       FreeTextIdevice,
                                       ['content'],
                                       {'content' : FreeTextWidget})
    edit_template = "exe/idevices/freetext/edit.html"
    preview_template = "exe/idevices/freetext/preview.html"
    view_template = "exe/idevices/freetext/export.html"
    
