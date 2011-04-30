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
Block is the base class for the classes which are responsible for 
rendering and processing Idevices in XHTML
"""

import sys

import logging
from django.conf import settings
from exedjango.utils import common
log = logging.getLogger(__name__)


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

    def __init__(self, idevice):
        """
        Initialize a new Block object
        """
        self.idevice = idevice
        self.id      = idevice.id
        self.purpose = idevice.purpose
        self.tip     = idevice.tip
        self.package = self.idevice.parent_node.package

        if idevice.edit:
            self.mode = Block.Edit
        else:
            self.mode = Block.Preview


    def process(self, action, request):
        """
        Process the request arguments from the web server to see if any
        apply to this block
        """
        
        # changing to a different node does not dirty package
        if action != u"changeNode":
            self.package.isChanged = 1
            log.debug(u"package.isChanged action=%s" % action)

        if action == u"done":               
            self.processDone(request)
            
        elif action == u"edit":
            self.processEdit(request)
          
        elif action == u"delete":
            self.processDelete(request)
            
        elif action == u"move":
            self.processMove(request)
            
        elif action == u"movePrev":
            self.processMovePrev(request)
            
        elif action == u"moveNext":
            self.processMoveNext(request)
            
        elif action == u"promote":
            self.processPromote(request)
            
        elif action == u"demote":
            self.processDemote(request)

        elif action == u"cancel":
            self.idevice.edit = False


    def processDone(self, request):
        """
        User has finished editing this block
        """
        log.debug(u"processDone id="+self.id)
        self.idevice.edit = False


    def processEdit(self, request):
        """
        User has started editing this block
        """
        log.debug(u"processEdit id="+self.id)
        self.idevice.lastIdevice = True
        self.idevice.edit = True


    def processDelete(self, request):
        """
        Delete this block and the associated iDevice
        """
        log.debug(u"processDelete id="+self.id)
        self.idevice.delete()


    def processMove(self, request):
        """
        Move this iDevice to a different node
        """
        log.debug(u"processMove id="+self.id)
        nodeId = request.args[u"move"+self.id][0]
        node   = self.package.findNode(nodeId)
        if node is not None:
            self.idevice.setParentNode(node)
        else:
            log.error(u"addChildNode cannot locate "+nodeId)


    def processPromote(self, request):
        """
        Promote this node up the hierarchy tree
        """
        log.debug(u"processPromote id="+self.id)


    def processDemote(self, request):
        """
        Demote this node down the hierarchy tree
        """
        log.debug(u"processDemote id="+self.id)


    def processMovePrev(self, request):
        """
        Move this block back to the previous position
        """
        log.debug(u"processMovePrev id="+self.id)
        self.idevice.movePrev()


    def processMoveNext(self, request):
        """
        Move this block forward to the next position
        """
        log.debug(u"processMoveNext id="+self.id)
        self.idevice.moveNext()


    def render(self):
        """
        Returns the appropriate XHTML string for whatever mode this block is in
        """
        html = u''
        broken = '<p><span style="font-weight: bold">%s:</span> %%s</p>' % _('IDevice broken')
        if self.mode == Block.Edit:
            self.idevice.lastIdevice = True
            html += u'<a "currentBlock"></a>\n'
            html += self.renderEdit()
        elif self.mode == Block.View:
            html += self.renderView()
        elif self.mode == Block.Preview:
            if self.idevice.lastIdevice:
                html += u'<a name="currentBlock"></a>\n'
            html += self.renderPreview()
        return html


    def renderEdit(self):
        """
        Returns an XHTML string with the form element for editing this block
        """
        log.error(u"renderEdit called directly")
        return u"ERROR Block.renderEdit called directly"


    def renderEditButtons(self, undo=True):
        """
        Returns an XHTML string for the edit buttons
        """
        
        html  = common.submitImage(u"done", self.id, 
                                   u"images/stock-apply.png", 
                                   _(u"Done"),1)

        if undo:
            html  += common.submitImage(u"cancel", self.id, 
                                   u"images/stock-undo.png", 
                                   _(u"Undo Edits"),1)
        else:
            html  += common.submitImage(u"no_cancel", self.id, 
                                   u"images/stock-undoNOT.png", 
                                   _(u"Can NOT Undo Edits"),1)

        html += common.confirmThenSubmitImage(
            _(u"This will delete this iDevice."
              u"\\n"
              u"Do you really want to do this?"),
            u"delete",
            self.id, u"images/stock-cancel.png", 
            _(u"Delete"), 1)

        if self.idevice.isFirst():
            html += common.image(u"movePrev", u"images/stock-go-up-off.png")
        else:
            html += common.submitImage(u"movePrev", self.id, 
                                       u"images/stock-go-up.png", 
                                       _(u"Move Up"),1)

        if self.idevice.isLast():
            html += common.image(u"moveNext", u"images/stock-go-down-off.png")
        else:
            html += common.submitImage(u"moveNext", self.id, 
                                       u"images/stock-go-down.png", 
                                       _(u"Move Down"),1)

        options  = [(_(u"---Move To---"), "")]
        options += self.__getNodeOptions(self.package.root, 0)
        html += common.select(u"move", self.id, options)

        if self.purpose.strip() or self.tip.strip():
            html += u'<a title="%s" ' % _(u'Pedagogical Help')
            html += u'onmousedown="Javascript:updateCoords(event);" '
            html += u"onclick=\"Javascript:showMe('p%s', 420, 240);\" " % self.id
            html += u'href="Javascript:void(0)" style="cursor:help;"> ' 
            html += u'<img alt="%s" class="info" src="%simages/info.png" ' \
                    % (_('Information'), settings.STATIC_URL)
            html += u'style="align:middle;" /></a>\n'
            html += u'<div id="p%s" style="display:none;">' % self.id
            html += u'<div style="float:right;">'
            html += u'<img alt="%s" src="%simages/stock-stop.png" ' % \
                (_('Close'), settings.STATIC_URL)
            html += u' title="%s" ' % _(u"Close")
            html += u'onmousedown="Javascript:hideMe();"/></div>'

            if self.purpose != "":
                html += u'<div class="popupDivLabel">'
                html += u' ' + _(u"Purpose") + u'</div>'
                html += self.purpose 
                
            if self.tip != "":
                html += u'<div class="block"><b>' + _(u"Tip:") + u'</b></div>'
                html += self.tip 
                html += u'\n'
                
            html += u'</div><br/><br/>\n'    
        
        return html


    def __getNodeOptions(self, node, depth):
        """
        TODO We should probably get this list from elsewhere rather than
        building it up for every block
        """
        options = [(u'&nbsp;&nbsp;&nbsp;'*depth + node.titleLong, node.id)]
        for child in node.children.all():
            options += self.__getNodeOptions(child, depth+1)
        return options
            

    def renderPreview(self):
        """
        Returns an XHTML string for previewing this block during editing
        """
        html  = u"<div class=\"iDevice "
        html += u"emphasis"+unicode(self.idevice.emphasis)+"\" "
        html += u"ondblclick=\"submitLink('edit', "+self.id+", 0);\">\n"
        if self.idevice.emphasis != Idevice.NoEmphasis:
            if self.idevice.icon:
                html += u'<img alt="%s" class="iDevice_icon" ' % _('IDevice Icon')
                html += u" src=\"/style/"+style
                html += "/icon_"+self.idevice.icon+".gif\"/>\n"
            html += u"<span class=\"iDeviceTitle\">"
            html += self.idevice.title
            html += u"</span>\n"
        html += self.renderViewContent()
        html += self.renderViewButtons()
        html += u"</div>\n"
        return html

    
    def renderView(self):
        """
        Returns an XHTML string for viewing this block, 
        i.e. when exported as a webpage or SCORM package
        """
        html  = u"<div class=\"iDevice "
        html += u"emphasis"+unicode(self.idevice.emphasis)+"\">\n"
        if self.idevice.emphasis != Idevice.NoEmphasis:
            if self.idevice.icon:
                html += u'<img alt="%s" class="iDevice_icon" ' % _('iDevice icon')
                html += u" src=\"icon_"+self.idevice.icon+".gif\"/>\n"
            html += u"<span class=\"iDeviceTitle\">"
            html += self.idevice.title
            html += u"</span>\n"
        html += self.renderViewContent()
        html += u"</div>\n"
        return html


    def renderViewContent(self):
        """
        overriden by derived classes
        """
        log.error(u"renderViewContent called directly")
        return _(u"ERROR: Block.renderViewContent called directly")


    def renderViewButtons(self):
        """
        Returns an XHTML string for the view buttons
        """
        html  = common.submitImage(u"edit", self.id, 
                                   u"images/stock-edit.png", 
                                   _(u"Edit"), self.package.isChanged)
        return html

# ===========================================================================
