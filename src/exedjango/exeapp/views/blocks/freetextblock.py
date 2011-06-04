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
"""
FreeTextBlock can render and process FreeTextIdevices as XHTML
"""

from django import forms
from django.conf import settings

import logging
import re
from tinymce.widgets import TinyMCE

from exeapp.views.blocks.block import Block
from exeapp.views.blocks.elements import TextAreaElement
from exeapp.models.idevices import FreeTextIdevice

from exedjango.utils import common

# from exe.webui                     import common

log = logging.getLogger(__name__)


def _(value):
    return value

class FreeTextForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE(attrs={"class" : "mceEditor"}))
    

        
    def render_edit(self):
        return str(self.visible_fields()[0])
    
    def render_preview(self):
        return mark_safe(self.instance.content)
    
    def render_export(self):
        content = self.instance.content
        # replace resources
        reg_exp = r'src=".*%s.*/(.*?)"' % settings.MEDIA_URL
        result_content = re.sub(reg_exp, r'src="\g<1>"', content)
        return mark_safe(result_content)
        
        
    
    class Meta:
        fields = ('content',)
        model = FreeTextIdevice
        
    
    

# ===========================================================================
class FreeTextBlock(Block):
    """
    FreeTextBlock can render and process FreeTextIdevices as XHTML
    GenericBlock will replace it..... one day
    """
    form = FreeTextForm
    
    
    def __init__(self, idevice):
        super(FreeTextBlock, self).__init__(idevice)
        
        if not hasattr(self.idevice,'undo'): 
            self.idevice.undo = True

    def renderEdit(self):
        """
        Returns an XHTML string with the form element for editing this block
        """
        form = self.form(instance=self.idevice, auto_id=False)
        self._media = form.media
        return render_to_string("exe/idevices/freetext/edit.html",
                                 locals())

    def renderPreview(self):
        """
        Returns an XHTML string for previewing this block
        """
        idevice = self.idevice
        form = self.form(instance=self.idevice, auto_id=False)
        return render_to_string("exe/idevices/freetext/preview.html",
                                 locals())

    def renderView(self):
        """
        Returns an XHTML string for viewing this block
        """
        idevice = self.idevice
        form = self.form(instance=self.idevice, auto_id=False)
        return render_to_string("exe/idevices/freetext/export.html",
                                locals())
# ===========================================================================
