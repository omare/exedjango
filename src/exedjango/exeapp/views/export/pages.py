# ===========================================================================
# eXe 
# Copyright 2004-2005, University of Auckland
# Copyright 2004-2008 eXe Project, http://eXeLearning.org/
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
import codecs
from exedjango.exeapp.views.blocks.blockfactory import block_factory
from django import forms
"""
Export Pages functions
"""

import logging
from urllib                   import quote
import re


log = logging.getLogger(__name__)


# ===========================================================================
class Page(object):
    """
    This is an abstraction for a page containing a node
    e.g. in a SCORM package or Website
    """
    def __init__(self, node, depth, exporter, prev_page=None, next_page = None, has_children=False):
        """
        Initialize
        """
        self.depth = depth
        self.node  = node
        self.exporter = exporter
        self.prev_page = prev_page
        self.next_page = next_page
        self.has_children = has_children
        self.name = self._generate_name()
        self.view_media = forms.Media()
        for idevice in node.idevices.all():
            block = block_factory(idevice.as_child())
            form = block.form_factory()
            if hasattr(form, "view_media"):
                self.view_media += form.view_media
            
        
    def save(self, outputDir):
        """
        This is the main function. It will render the page and save it to a
        file.  'outputDir' is the directory where the filenames will be saved
        (a 'path' instance)
        """
        outfile = codecs.open(outputDir / self.name+".html", "w", "utf-8")
        content = self.render()
        outfile.write(content)
        outfile.close()
        
        
    def _generate_name(self):
        return self.node.unique_name()


# ===========================================================================
