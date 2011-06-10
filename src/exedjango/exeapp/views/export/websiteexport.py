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
from exeapp.models.idevices.idevice import Idevice
"""
WebsiteExport will export a package as a website of HTML pages
"""

from django.conf import settings

import logging
import re
import imp
from utils.path import Path
from exeapp.views.export.pages         import uniquifyNames
from exeapp.views.export.websitepage   import WebsitePage
from zipfile                  import ZipFile, ZIP_DEFLATED
import tempfile


def _(value):
    return value

log = logging.getLogger(__name__)

# ===========================================================================
class WebsiteExport(object):
    """
    WebsiteExport will export a package as a website of HTML pages
    """
    def __init__(self, package, file_obj):
        """
        'style_dir' is the directory where we can copy the stylesheets from
        'output_dir' is the directory that will be [over]written
        with the website
        """
        static_dir = Path(settings.STATIC_ROOT)
        self.package = package
        self.style_dir = static_dir / "css" / "styles" / package.style
        self.scripts_dir = static_dir / "scripts"
        self.pages = []
        self.file_obj = file_obj
        self.media_dir = Path(settings.MEDIA_ROOT)
        self.page_class = WebsitePage
        
        self.output_dir = Path(tempfile.mkdtemp())

    def export(self):
        """ 
        Export web site
        Cleans up the previous packages pages and performs the export
        """
        

        # Import the Website Page class.  If the style has it's own page class
        # use that, else use the default one.
#        if (self.style_dir/"websitepage.py").exists():
#            global WebsitePage
#            module = imp.load_source("websitepage", 
#                                     self.style_dir/"websitepage.py")
#            WebsitePage = module.WebsitePage

        # List of page objects. "in" and "out" identify depth
        # grows and decreae
        self.create_pages()

        self.copyFiles()
        # Zip up the website package
        self.doZip(self.file_obj)
        # Clean up the temporary dir
        self.output_dir.rmtree()

    def doZip(self, fileObj):
        """
        Actually saves the zip data. Called by 'Path.safeSave'
        """
        zipped = ZipFile(fileObj, "w")
        for scormFile in self.output_dir.files():
            zipped.write(scormFile, scormFile.basename().encode('utf8'), ZIP_DEFLATED)
        zipped.close()
        
    def copyFiles(self):
        """
        Copy all the files used by the website.
        """
        # Copy the style sheet files to the output dir
        styleFiles  = ["%s/../base.css" % self.style_dir]
        styleFiles.append("%s/../popup_bg.gif" % self.style_dir)
        styleFiles += self.style_dir.files("*.css")
        styleFiles += self.style_dir.files("*.jpg")
        styleFiles += self.style_dir.files("*.gif")
        styleFiles += self.style_dir.files("*.svg")
        styleFiles += self.style_dir.files("*.png")
        styleFiles += self.style_dir.files("*.js")
        styleFiles += self.style_dir.files("*.html")
        self.style_dir.copylist(styleFiles, self.output_dir)
        self.media_dir.copylist(self.package.resources, self.output_dir)
        self.scripts_dir.copylist(('libot_drag.js',), 
                                  self.output_dir)
        
        # copy players for media idevices.                
        hasFlowplayer     = False
        hasMagnifier      = False
        hasXspfplayer     = False
        isBreak           = False
        
        for page in self.pages:
            if isBreak:
                break
            for idevice in page.node.idevices.all():
                resources = idevice.as_child().system_resources
                if (hasFlowplayer and hasMagnifier and hasXspfplayer):
                    isBreak = True
                    break
                if not hasFlowplayer:
                    if 'flowPlayer.swf' in resources:
                        hasFlowplayer = True
                if not hasMagnifier:
                    if 'magnifier.swf' in resources:
                        hasMagnifier = True
                if not hasXspfplayer:
                    if 'xspf_player.swf' in resources:
                        hasXspfplayer = True
                        
        if hasFlowplayer:
            videofile = (self.templatesDir/'flowPlayer.swf')
            videofile.copyfile(self.output_dir/'flowPlayer.swf')
        if hasMagnifier:
            videofile = (self.templatesDir/'magnifier.swf')
            videofile.copyfile(self.output_dir/'magnifier.swf')
        if hasXspfplayer:
            videofile = (self.templatesDir/'xspf_player.swf')
            videofile.copyfile(self.output_dir/'xspf_player.swf')

        if self.package.license == "GNU Free Documentation License":
            # include a copy of the GNU Free Documentation Licence
            (self.templatesDir/'fdl.html').copyfile(self.output_dir/'fdl.html')



    def create_pages(self):
        self.pages.append(self.page_class(self.package.root, 1, exporter=self))
        self.generate_pages(self.package.root, 2)
        
        uniquifyNames(self.pages)
        
        for page in self.pages:
            page.save(self.output_dir)
        
        
    
    def generate_pages(self, node, depth):
        """
        Recursively generate pages and store in pages member variable
for retrieving later.
        """
        for child in node.children.all():
            
            
            page = self.page_class(child, depth, 
                           exporter = self,
                           has_children=child.children.exists())
            
            last_page = self.pages[-1] if self.pages else None
            if last_page:
                page.prev_page = last_page
                last_page.next_page = page
            self.pages.append(page)
            self.generate_pages(child, depth + 1)



