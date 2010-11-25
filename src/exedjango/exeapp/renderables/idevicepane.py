# ===========================================================================
# eXe 
# Copyright 2004-2005, University of Auckland
# Copyright 2006-2007 eXe Project, New Zealand Tertiary Education Commission
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
IdevicePane is responsible for creating the XHTML for iDevice links
"""

import logging
from collections import defaultdict

from django.template.loader import render_to_string

from exeapp.renderables.renderable import Renderable
from exeapp.models   import idevice_storage
from exeapp.models.idevices.idevice import Idevice


log = logging.getLogger(__name__)

# ===========================================================================
class IdevicePane(Renderable):
    """
    IdevicePane is responsible for creating the XHTML for iDevice links
    """
    name = 'idevicePane'

    def __init__(self, parent):
        """ 
        Initialize
        """ 
        Renderable.__init__(self, parent)
        log.debug("Load appropriate iDevices")
        


    def process(self, request):
        """ 
        Process the request arguments to see if we're supposed to 
        add an iDevice
        """
        log.debug("Process" + repr(request.args))
        if ("action" in request.args and 
            request.args["action"][0] == "AddIdevice"):

            self.package.isChanged = True
            prototype = self.prototypes.get(request.args["object"][0])
            if prototype:
                self.package.currentNode.addIdevice(prototype.clone())

            
    def addIdevice(self, idevice):
        """
        Adds an iDevice to the pane
        """
        log.debug("addIdevice id="+idevice.id+", title="+idevice.title)
        self.prototypes[idevice.id] = idevice
        self.client.call('XHAddIdeviceListItem', idevice.id, idevice.title)

        
    def render(self):
        """
        Returns an html string for viewing idevicepane
        """

        groups = defaultdict(list)

        prototypes = idevice_storage.get_prototypes()
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
        return render_to_string('exe/idevicepane.html', locals())


    def __renderPrototype(self, prototype):
        """
        Add the list item for an iDevice prototype in the iDevice pane
        """
        log.debug("Render "+prototype.title)
        log.debug("_title "+prototype._title)
        log.debug("of type "+repr(type(prototype.title)))
        html = u'<li>\n'
        html += u'  <a class="ideviceItem" ideviceid="%s">%s</a>' % (prototype.id, _(prototype.title))
        html += u'</li>\n'
        return html
        
    
# ===========================================================================
