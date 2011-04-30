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
"""
FreeTextBlock can render and process FreeTextIdevices as XHTML
"""

import logging
from exeapp.views.blocks.block import Block
from exeapp.views.blocks.elements import TextAreaElement
from exeapp.models.idevices import freetextidevice

from exedjango.utils import common
# from exe.webui                     import common

log = logging.getLogger(__name__)


def _(value):
    return value

# ===========================================================================
class FreeTextBlock(Block):
    """
    FreeTextBlock can render and process FreeTextIdevices as XHTML
    GenericBlock will replace it..... one day
    """
    def __init__(self, idevice):
        super(FreeTextBlock, self).__init__(idevice)
        
        self.contentElement = TextAreaElement(field=self.idevice.content)
        if not hasattr(self.idevice,'undo'): 
            self.idevice.undo = True


    def process(self, action, data):
        """
        Process the request arguments from the web server to see if any
        apply to this block
        """
        is_cancel = common.requestHasCancel(data)

        super(FreeTextBlock, self).process(action, data)

        if action != "delete": 
            self.contentElement.process(action, data) 
        #if "export" + self.id in request.args and not is_cancel:
        #    self.idevice.exportType = request.args["export" + self.id][0]


    def renderEdit(self):
        """
        Returns an XHTML string with the form element for editing this block
        """
        html = self.contentElement.renderEdit()
        ## drop down menu defines if element is exported for presentation
        #html += common.formField('select', self.package,
        #    _("Custom export options"), "export%s" % self.id,
        #    options = [[_('Don\'t export'), freetextidevice.NOEXPORT],
        #        [_('Presentation'), freetextidevice.PRESENTATION],
        #        [_('Handout'), freetextidevice.HANDOUT]],
        #    selection = self.idevice.exportType)
        html += self.renderEditButtons()
        return html


    def renderPreview(self):
        """
        Returns an XHTML string for previewing this block
        """
        html  = u"<div class=\"iDevice "
        html += u"emphasis"+unicode(self.idevice.emphasis)+"\" "
        html += u"ondblclick=\"submitLink('edit',%s, 0);\">\n" % self.id
        html += self.contentElement.renderPreview()
        html += self.renderViewButtons()
        html += "</div>\n"
        return html


    def renderView(self):
        """
        Returns an XHTML string for viewing this block
        """
        html  = u"<div class=\"iDevice "
        html += u"emphasis"+unicode(self.idevice.emphasis) + "\">\n"
        #html += u" presentable=" + unicode(self.idevice.presentable) + "\">\n"
        html += self.contentElement.renderView()
        html += u"</div>\n"
        return html
    
# ===========================================================================
