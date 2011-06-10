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
    form = None # redefined by the child
    
    
    def __init__(self, idevice):
        """
        Initialize a new Block object
        """
        self.idevice = idevice
        self.id      = idevice.id
        self.purpose = idevice.purpose
        self.tip     = idevice.tip
        self.package = self.idevice.parent_node.package
        form = self.form()
        self._media = form.media

    def process(self, action, data):
        
        if action == 'delete':
            self.idevice.delete()
            # Don't save IDevice if it has to be deleted
            return ""
        elif action == 'move_up':
            self.idevice.move_up()
            return ""
        elif action == 'move_down':
            self.idevice.move_down()
            return ""
        elif action == 'edit_mode':
            self.idevice.edit_mode()
        elif action == 'apply_changes':
            form = self.form(data, instance=self.idevice)
            form.save(commit=False)
            self.idevice.apply_changes(form.cleaned_data)
        else:
            raise IdeviceActionNotFound("Action %s not found" % action)
        
        self.idevice.save()
        return self.render()
    
    @property
    def media(self):
        '''Returns a list of media files used in iDevice's HTML'''
        return self._media


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


    def processMoveNext(self, request):
        """
        Move this block forward to the next position
        """
        log.debug(u"processMoveNext id="+self.id)
        self.idevice.moveNext()


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
        Returns an XHTML string with the form element for editing this block
        """
        log.error(u"renderEdit called directly")
        return u"ERROR Block.renderEdit called directly"


    def renderEditButtons(self, undo=True):
        """
        Returns an XHTML string for the edit buttons
        """
        
        html  = common.submit_image(u"apply_changes", self.id, 
                                   u"images/stock-apply.png", 
                                   _(u"Done"),1)

        if undo:
            html  += common.submit_image(u"cancel", self.id, 
                                   u"images/stock-undo.png", 
                                   _(u"Undo Edits"),1)
        else:
            html  += common.submit_image(u"no_cancel", self.id, 
                                   u"images/stock-undoNOT.png", 
                                   _(u"Can NOT Undo Edits"),1)
        # TODO: change to ConfirmThenSubmitImage, when JS is ready
        html += common.submit_image(
            #_(u"This will delete this iDevice."
            # u"\\n"
            #  u"Do you really want to do this?"),
            u"delete",
            self.id, u"images/stock-cancel.png", 
            _(u"Delete"), 1)

        if self.idevice.is_first():
            html += common.image(u"move_up", u"images/stock-go-up-off.png")
        else:
            html += common.submit_image(u"movePrev", self.id, 
                                       u"images/stock-go-up.png", 
                                       _(u"Move Up"),1)

        if self.idevice.is_last():
            html += common.image(u"moveNext", u"images/stock-go-down-off.png")
        else:
            html += common.submit_image(u"move_down", self.id, 
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
        raise NotImplemented

    
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
        html  = common.submit_image(u"edit_mode", self.id, 
                                   u"images/stock-edit.png", 
                                   _(u"Edit"), True)
        return html

# ===========================================================================
