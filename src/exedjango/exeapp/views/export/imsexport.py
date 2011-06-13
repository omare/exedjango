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
import tempfile
from django.conf import settings
from django.forms.models import model_to_dict
from exeapp.models.idevices.idevice import Idevice
from exeapp.views.export.websiteexport import WebsiteExport
import uuid
"""
Exports an eXe package as an IMS Content Package
"""

import logging
import re
from zipfile                       import ZipFile, ZIP_DEFLATED
from exedjango.utils import common
from django.template.loader import render_to_string
#from exe.webui.blockfactory        import g_blockFactory
#from exe.engine.error              import Error
from utils.path import Path 
from exeapp.views.export.pages import Page
from exeapp.views.blocks.blockfactory import block_factory

log = logging.getLogger(__name__)

_ = lambda x : x


# ===========================================================================
class Manifest(object):
    """
    Represents an imsmanifest xml file
    """
    def __init__(self, outputDir, package, pages):
        """
        Initialize
        'output_dir' is the directory that we read the html from and also output
        the mainfest.xml 
        """
        self.output_dir    = outputDir
        self.package      = package
        self.generate_id = uuid.uuid4
        self.pages        = pages
        self.itemStr      = ""
        self.resStr       = ""


    def save(self):
        """
        Save a imsmanifest file and metadata to self.output_dir
        """
        filename = "imsmanifest.xml"
        out = open(self.output_dir/filename, "wb")
        out.write(self.createXML().encode('utf8'))
        out.close()
        # if user did not supply metadata title, description or creator
        #  then use package title, description, or creator in imslrm
        #  if they did not supply a package title, use the package name
        lrm = model_to_dict(self.package.dublincore)
        if lrm.get('title', '') == '':
            lrm['title'] = self.package.title
        if lrm['title'] == '':
            lrm['title'] = self.package.name
        if lrm.get('description', '') == '':
            lrm['description'] = self.package.description
        if lrm['description'] == '':
            lrm['description'] = self.package.title
        if lrm.get('creator', '') == '':
            lrm['creator'] = self.package.author
        # Metadata
        templateFilename = Path(settings.STATIC_ROOT)/'templates'/'dublincore.xml'
        template = open(templateFilename, 'rb').read()
        xml = template % lrm
        out = open(self.output_dir/'dublincore.xml', 'wb')
        out.write(xml.encode('utf8'))
        out.close()

    def createXML(self):
        """
        returning XLM string for manifest file
        """
        manifest_id = self.generate_id()
        org_id      = self.generate_id()
        depth = 0
        for page in self.pages:
            while depth >= page.depth:
                self.itemStr += "</item>\n"
                depth -= 1
            self.genItemResStr(page)
            depth = page.depth
        
        while depth >= 1:
            self.itemStr += "</item>\n"
            depth -= 1
        

        manifest = self
        return render_to_string("exe/export/ims_manifest.html",
                                {"manifest" : manifest,
                                 "manifest_id" : manifest_id,
                                 "org_id" : org_id,
                                 })
                    
    def genItemResStr(self, page):
        """
        Returning xml string for items and resources
        """
        context = {"item_id" : "ITEM-%s" % self.generate_id(),
                   "res_id" : "RES-%s" % self.generate_id(),
                   "filename" : "%s.html" % page.name,
                   "page" : page,
                   } 
            
        
        self.itemStr += render_to_string("exe/export/ims_manifest_item.html",
                                         context)
        
        self.resStr += render_to_string("exe/export/ims_manifest_resource.html",
                                        context)


# ===========================================================================
class IMSPage(Page):
    """
    This class transforms an eXe node into a SCO 
    """

    def render(self):
        """
        Returns an XHTML string rendering this page.
        """
        return render_to_string("exe/export/imspage.html",
                                {"current_page" : self})



        
        
# ===========================================================================
class IMSExport(WebsiteExport):
    """
    Exports an eXe package as a SCORM package
    """
    title = "IMS Package"
    
    def __init__(self, *args, **kwargs):
        """ Initialize
        'style_dir' is the directory from which we will copy our style sheets
        (and some gifs)
        """
        super(IMSExport, self).__init__(*args, **kwargs)
        
        static_dir = Path(settings.STATIC_ROOT)
        self.templatesDir = static_dir / "templates"
        self.schemasDir   = static_dir / "schemas/ims"
        self.page_class = IMSPage

    def export(self):
        """ 
        Export SCORM package
        """

        self.create_pages()

        manifest = Manifest(self.output_dir, self.package, self.pages)
        manifest.save()
        
        self.copyFiles()
        
        self.doZip(self.file_obj, self.output_dir)
        # Clean up the temporary dir
        self.output_dir.rmtree()
        
    def copyFiles(self):
        super(IMSExport, self).copyFiles()
        self.schemasDir.copylist(('imscp_v1p1.xsd',
                                  'imsmd_v1p2p2.xsd',
                                  'ims_xml.xsd'), self.output_dir)

    def doZip(self, fileObj, outputDir):
        """
        Actually does the zipping of the file. Called by 'Path.safeSave'
        """
        zipped = ZipFile(fileObj, "w")
        for scormFile in outputDir.files():
            zipped.write(scormFile,
                    scormFile.basename().encode('utf8'), ZIP_DEFLATED)
        zipped.close()

# ===========================================================================
