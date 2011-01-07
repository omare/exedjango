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
#from exe.webui.element          import TextAreaElement
#from exe.engine                 import freetextidevice
#from exe.webui                     import common

log = logging.getLogger(__name__)


# ===========================================================================
class FreeTextBlock(Block):
    """
    FreeTextBlock can render and process FreeTextIdevices as XHTML
    GenericBlock will replace it..... one day
    """
    def __init__(self, idevice):
        Block.__init__(self, idevice)
        if idevice.content.idevice is None: 
            # due to the loading process's timing, idevice wasn't yet set; 
            # set it here for the TextAreaElement's tinyMCE editor 
            idevice.content.idevice = idevice


    def process(self, request):
        """
        Process the request arguments from the web server to see if any
        apply to this block
        """
        is_cancel = common.requestHasCancel(request)

        if is_cancel:
            self.idevice.edit = False
            # but double-check for first-edits, and ensure proper attributes:
            if not hasattr(self.idevice.content, 'content_w_resourcePaths'):
                self.idevice.content.content_w_resourcePaths = ""
            if not hasattr(self.idevice.content, 'content_wo_resourcePaths'):
                self.idevice.content.content_wo_resourcePaths = ""
            return

        IdeviceBlock.process(self, request)

        if (u"action" not in request.args or 
            request.args[u"action"][0] != u"delete"): 
            content = self.contentElement.process(request) 
            if content: 
                self.idevice.content = content
        if "export" + self.id in request.args and not is_cancel:
            self.idevice.exportType = request.args["export" + self.id][0]


    def render_edit(self, style):
        """
        Returns an XHTML string with the form element for editing this block
        """
        return render_to_string('/exe/authoring/freetext/edit.html')


    def renderPreview(self, style):
        """
        Returns an XHTML string for previewing this block
        """
        html  = u"<div class=\"iDevice "
        html += u"emphasis"+unicode(self.idevice.emphasis)+"\" "
        html += u"ondblclick=\"submitLink('edit',"+self.id+", 0);\">\n"
        html += self.contentElement.renderPreview()
        html += self.renderViewButtons()
        html += "</div>\n"
        return html


    def renderView(self, style):
        """
        Returns an XHTML string for viewing this block
        """
        html  = u"<div class=\"iDevice "
        html += u"emphasis"+unicode(self.idevice.emphasis) + "\">\n"
        #html += u" presentable=" + unicode(self.idevice.presentable) + "\">\n"
        html += self.contentElement.renderView()
        html += u"</div>\n"
        return html
    
