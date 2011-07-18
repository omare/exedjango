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
from exeapp.models.idevices.idevice import Idevice
from django.template.loader import render_to_string
"""
Block is the base class for the classes which are responsible for 
rendering and processing Idevices in XHTML
"""

import logging
from django.conf import settings
from django.utils.safestring import mark_safe
from exedjango.utils import common
log = logging.getLogger(__name__)

class IdeviceActionNotFound(Exception):
    '''Specified action with given arguments was not found'''
    pass

def _(value):
    return value

# ===========================================================================
class Block(object):
    """
    Block is the base class for the classes which are responsible for 
    rendering and processing Idevices in XHTML
    """
    nextId = 0
    Edit, Preview, View, Hidden = range(4)
    form_factory = None # redefined by the child
    formset_factory = None #
    
    
    def __init__(self, idevice):
        """
        Initialize a new Block object
        """
        self.idevice = idevice
        self.id      = idevice.id
        self.purpose = idevice.purpose
        self.tip     = idevice.tip
        self.package = self.idevice.parent_node.package
        form = self.form_factory()
        self._media = form.media

    def process(self, action, data):
        
        if action == 'move_up':
            self.idevice.move_up()
            return ""
        elif action == 'move_down':
            self.idevice.move_down()
            return ""
        elif action == 'edit_mode':
            self.idevice.edit_mode()
        elif action == 'apply_changes':
            if self.form_factory:
                form = self.form_factory(data, instance=self.idevice)
                form.save(commit=False)
                self.idevice.apply_changes(form.cleaned_data)
                
            if self.formset_factory:
                print data
                formset = self.formset_factory(data)
                formset.save()
                print
                
                
        else:
            raise IdeviceActionNotFound("Action %s not found" % action)
        
    @property
    def media(self):
        '''Returns a list of media files used in iDevice's HTML'''
        return self._media

    def render(self):
        """
        Returns the appropriate XHTML string for whatever mode this block is in.
        Descendants should not override it.
        """
        self._media = None
        html = '<input type="hidden" name="idevice_id" value="%s" />' % self.id
        broken = '<p><span style="font-weight: bold">%s:</span> %%s</p>' % _('IDevice broken')
        if self.idevice.edit == True:
            html += self.renderEdit()
        else:
            html += self.renderPreview()
        return mark_safe(html)


    def renderEdit(self):
        """
        Returns an XHTML string with the form_factory element for editing this block
        """
        log.error(u"renderEdit called directly")
        return u"ERROR Block.renderEdit called directly"


    def renderPreview(self):
        """
        Returns an XHTML string for previewing this block during editing
        """
        raise NotImplemented
    
    def renderExport(self):
        '''
        Returns the export representation of the block. Implemented in child
classes.
        '''
        raise NotImplemented
    
# ===========================================================================
