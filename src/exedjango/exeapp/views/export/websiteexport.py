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
    def __init__(self, data_package, file_obj):
        """
        'style_dir' is the directory where we can copy the stylesheets from
        'outputDir' is the directory that will be [over]written
        with the website
        """
        self.data_package = data_package
        self.style_dir = Path("%s/css/styles/%s" % (settings.STATIC_ROOT, 
                                            data_package.style))
        self.scripts_dir = Path("%s/scripts/" % settings.STATIC_ROOT)
        self.file_obj = file_obj

    def exportZip(self):
        """ 
        Export web site
        Cleans up the previous packages pages and performs the export
        """
        
        outputDir = Path(tempfile.mkdtemp())

        # Import the Website Page class.  If the style has it's own page class
        # use that, else use the default one.
#        if (self.style_dir/"websitepage.py").exists():
#            global WebsitePage
#            module = imp.load_source("websitepage", 
#                                     self.style_dir/"websitepage.py")
#            WebsitePage = module.WebsitePage

        # List of page objects. "in" and "out" identify depth
        # grows and decreae
        self.page_structure = _generate_pages(self.data_package.root, 0)
        self.pages = [page for page in self.page_structure\
                       if isinstance(page, WebsitePage)]
        uniquifyNames(self.pages)

        for page in self.pages:
            page.save(outputDir, self.page_structure)
            

        self.copyFiles(self.data_package, outputDir)
        # Zip up the website package
        self.doZip(self.file_obj, outputDir)
        # Clean up the temporary dir
        outputDir.rmtree()

    def doZip(self, fileObj, outputDir):
        """
        Actually saves the zip data. Called by 'Path.safeSave'
        """
        zipped = ZipFile(fileObj, "w")
        for scormFile in outputDir.files():
            zipped.write(scormFile, scormFile.basename().encode('utf8'), ZIP_DEFLATED)
        zipped.close()
        
    def export(self, package):
        """ 
        Export web site
        Cleans up the previous packages pages and performs the export
        """
        outputDir = self.filename
        if not outputDir.exists(): 
            outputDir.mkdir()
        
        # Import the Website Page class.  If the style has it's own page class
        # use that, else use the default one.
        if (self.style_dir/"websitepage.py").exists():
            global WebsitePage
            module = imp.load_source("websitepage", 
                                     self.style_dir/"websitepage.py")
            WebsitePage = module.WebsitePage

        self.pages = [ WebsitePage("index", 1, package.root) ]
        self._generate_pages(package.root, 1)
        uniquifyNames(self.pages)

        prevPage = None
        thisPage = self.pages[0]

        for nextPage in self.pages[1:]:
            thisPage.save(outputDir, prevPage, nextPage, self.pages)
            prevPage = thisPage
            thisPage = nextPage

        thisPage.save(outputDir, prevPage, None, self.pages)
        
        self.copyFiles(package, outputDir)


    def copyFiles(self, package, outputDir):
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
        self.style_dir.copylist(styleFiles, outputDir)

        # copy the package's resource files
#        package.resourceDir.copyfiles(outputDir)
            
        # copy script files.
        self.scripts_dir.copylist(('libot_drag.js',), 
                                  outputDir)
        
        # copy players for media idevices.                
        hasFlowplayer     = False
        hasMagnifier      = False
        hasXspfplayer     = False
        isBreak           = False
        
        for page in self.pages:
            if isBreak:
                break
            for idevice in page.node.idevices.all():
                if (hasFlowplayer and hasMagnifier and hasXspfplayer):
                    isBreak = True
                    break
                if not hasFlowplayer:
                    if 'flowPlayer.swf' in idevice.system_resources:
                        hasFlowplayer = True
                if not hasMagnifier:
                    if 'magnifier.swf' in idevice.system_resources:
                        hasMagnifier = True
                if not hasXspfplayer:
                    if 'xspf_player.swf' in idevice.system_resources:
                        hasXspfplayer = True
                        
        if hasFlowplayer:
            videofile = (self.templatesDir/'flowPlayer.swf')
            videofile.copyfile(outputDir/'flowPlayer.swf')
        if hasMagnifier:
            videofile = (self.templatesDir/'magnifier.swf')
            videofile.copyfile(outputDir/'magnifier.swf')
        if hasXspfplayer:
            videofile = (self.templatesDir/'xspf_player.swf')
            videofile.copyfile(outputDir/'xspf_player.swf')

        if package.license == "GNU Free Documentation License":
            # include a copy of the GNU Free Documentation Licence
            (self.templatesDir/'fdl.html').copyfile(outputDir/'fdl.html')



def _generate_pages(node, depth, prev_page=None):
    """
    Recursively generate pages and store in pages member variable
for retrieving later.
    """
    page = WebsitePage(node, depth, prev_page)
    if prev_page is not None:
        prev_page.next_page = page
    pages = [page]
    prev_page = page
    
    if node.children.exists():
        pages.append("in")
        for child in node.children.all():
            child_pages = _generate_pages(child, depth + 1,
                                                       prev_page)
            # find last page
            i = -1
            while child_pages[i] == 'out':
                i -= 1
            prev_page = child_pages[i]
            pages += child_pages
        pages.append("out")
    
    return pages



