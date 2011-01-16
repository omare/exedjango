# ===========================================================================
# eXe 
# Copyright 2004-2005, University of Auckland
# Copyright 2004-2007 eXe Project, New Zealand Tertiary Education Commission
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
"""
This class transforms an eXe node into a page on a self-contained website
"""

import logging
import re
from urllib                   import quote
from utils.path          import Path
from utils import common
from exeapp.views.export.pages         import Page, uniquifyNames
log = logging.getLogger(__name__)


# ===========================================================================
class WebsitePage(Page):
    """
    This class transforms an eXe node into a page on a self-contained website
    """

    def save(self, outputDir, page_structure):
        """
        This is the main function. It will render the page and save it to a
        file.  'outputDir' is the directory where the filenames will be saved
        (a 'path' instance)
        """
        outfile = open(outputDir / self.name+".html", "w")
        outfile.write(self.render(page_structure))
        outfile.close()
        

    def render(self, page_structure):
        """
        Returns an XHTML string rendering this page.
        """
        data_package = self.node.package
        current_page = self
        return render_to_string("exe/export/websitepage.html", locals())

        
    def leftNavigationBar(self, pages):
        """
        Generate the left navigation string for this page
        """
        depth    = 1
        nodePath = [None] + list(self.node.ancestors()) + [self.node]

        html = "<ul id=\"navlist\">\n"

        for page in pages:
            if page.node.parent in nodePath:
                while depth < page.depth:
                    html += "<div id=\"subnav\" "
                    #if page.node.children:
                        #    html += "class=\"withChild\""
                        #else:
                        #    html += "class=\"withoutChild\""
                    html += ">\n"
                    depth += 1
                while depth > page.depth:
                    html += "</div>\n"
                    depth -= 1

                if page.node == self.node:
                    if page.node.children:
                        html += "<div id=\"active\" "
                    else:
                        html += "<div id=\"activeWithoutChild\" "
                    html += ">"
                    html += page.node.titleShort
                    html += "</div>\n"
                else:
                    html += "<div><a href=\""+quote(page.name)+".html\" "
                    if page.node.children:
                        html += "class=\"withChild\""
                    else:
                        html += "class=\"withoutChild\""
                    html += ">"
                    html += page.node.titleShort
                    html += "</a></div>\n"

        while depth > 1:
            html += "</div>\n"
            depth -= 1
        html += "</ul>\n"
        return html
        
        
    def getNavigationLink(self, prevPage, nextPage):
        """
        return the next link url of this page
        """
        html = "<div class=\"noprt\" align=\"right\">"

        if prevPage:
            html += "<a id=\"go_prev\" href=\""+quote(prevPage.name)
            html += ".html\">\n"
            html += "<img src=\"arrowleft.gif\" border=0>"
            html += "<span>%s</span></a>\n" % _('Previous')

        if nextPage:
            if prevPage:
                html += " | "
            
            html += "<a id=\"go_next\" href=\""+quote(nextPage.name)
            html += ".html\">\n"
            html += "<img src=\"arrowright.gif\" border=0>"
            html += "<span>%s</span></a>\n" % _('Next')


           
        html += "</div>\n"
        return html        
