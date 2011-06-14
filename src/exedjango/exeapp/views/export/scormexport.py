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
from utils.uniqueidgenerator import UniqueIdGenerator
from django.conf import settings
from exeapp.views.export.websiteexport import WebsiteExport
from django.template.loader import render_to_string
from django.forms.models import model_to_dict
"""
Exports an eXe package as a SCORM package
"""

import logging
import re
import time
from zipfile                       import ZipFile, ZIP_DEFLATED
from utils                     import common
from utils.path               import Path
from exeapp.views.export.pages              import Page

log = logging.getLogger(__name__)

def _(value):
    return value

# ===========================================================================

SCORM12 = "scorm1.2"
SCORM2004 = "scorm2004"
COMMONCARTRIDGE = "commoncartridge"

class Manifest(object):
    """
    Represents an imsmanifest xml file
    """
    def __init__(self, outputDir, package, pages, scormType):
        """
        Initialize
        'outputDir' is the directory that we read the html from and also output
        the mainfest.xml 
        """
        self.outputDir    = outputDir
        self.package      = package
        self.idGenerator  = UniqueIdGenerator()
        self.pages        = pages
        self.itemStr      = ""
        self.resStr       = ""
        self.scorm_type    = scormType
        self.dependencies = {}


    def createMetaData(self):
        """
        if user did not supply metadata title, description or creator
        then use package title, description, or creator in imslrm
        if they did not supply a package title, use the package name
        if they did not supply a date, use today
        """
        if self.scorm_type == SCORM12:
            template_name = 'imslrm.xml'
        elif self.scorm_type == COMMONCARTRIDGE:
            template_name = 'cc.xml'
        else:
            raise AttributeError("Can't create metadata for %s" \
                                 % self.scorm_type)
            
        static_dir = Path(settings.STATIC_ROOT)
        templateFilename = static_dir / 'templates' / template_name
        template = open(templateFilename, 'rb').read()
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
        if lrm['date'] == '':
            lrm['date'] = time.strftime('%Y-%m-%d')
        # if they don't look like VCARD entries, coerce to fn:
        for f in ('creator', 'publisher', 'contributors'):
            if re.match('.*[:;]', lrm[f]) == None:
                lrm[f] = u'FN:' + lrm[f]
        xml = template % lrm
        return xml

    def save(self, filename):
        """
        Save a imsmanifest file to self.outputDir
        """
        out = open(self.outputDir/filename, "w")
        if filename == "imsmanifest.xml":
            out.write(self.createXML().encode('utf8'))
        out.close()
        if self.scorm_type == SCORM12:
            xml = self.createMetaData()
            out = open(self.outputDir/'imslrm.xml', 'wb')
            out.write(xml.encode('utf8'))
            out.close()
    
    def createXML(self):
        manifestId = unicode(self.idGenerator.generate())
        orgId      = unicode(self.idGenerator.generate())
        
        if self.scorm_type == COMMONCARTRIDGE:
            # FIXME flatten hierarchy
            for page in self.pages:
                self.genItemResStr(page)
                self.itemStr += "</item>\n"
        else:
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
        
        return render_to_string("exe/export/scorm_manifest.html",
                                {"SCORM12" : SCORM12,
                                 "SCORM2004" : SCORM2004,
                                 "COMMONCARTRIDGE" : COMMONCARTRIDGE,
                                 "manifestId" : manifestId,
                                 "orgId" : orgId,
                                 "manifest" : self})
            
    def genItemResStr(self, page):
        """
        Returning xml string for items and resources
        """
        itemId   = "ITEM-"+unicode(self.idGenerator.generate())
        resId    = "RES-"+unicode(self.idGenerator.generate())
        filename = page.name+".html"
            
        
        self.itemStr += '<item identifier="'+itemId+'" '
        if self.scorm_type != COMMONCARTRIDGE:
            self.itemStr += 'isvisible="true" '
        self.itemStr += 'identifierref="'+resId+'">\n'
        self.itemStr += "    <title>"
        self.itemStr += page.node.titleShort
        self.itemStr += "</title>\n"
        
        self.resStr += "  <resource identifier=\""+resId+"\" "
        self.resStr += "type=\"webcontent\" "

        # FIXME force dependency on popup_bg.gif on every page
        # because it isn't a "resource" so we can't tell which
        # pages will use it from content.css
        if self.scorm_type == COMMONCARTRIDGE:
            self.resStr += """href="%s">
    <file href="%s"/>
    <file href="base.css"/>
    <file href="content.css"/>
    <file href="popup_bg.gif"/>""" % (filename, filename)
            if page.node.package.backgroundImg:
                self.resStr += '\n    <file href="%s"/>' % \
                        page.node.package.backgroundImg.basename()
            self.dependencies["../base.css"] = True
            self.dependencies["content.css"] = True
            self.dependencies["popup_bg.gif"] = True
        else:
            self.resStr += "adlcp:scormtype=\"sco\" "
            self.resStr += "href=\""+filename+"\"> \n"
            self.resStr += """\
    <file href="%s"/>
    <file href="base.css"/>
    <file href="content.css"/>
    <file href="popup_bg.gif"/>
    <file href="APIWrapper.js"/>
    <file href="SCOFunctions.js"/>""" % filename
        self.resStr += "\n"
        fileStr = ""

        for resource in page.node.resources:            
            fileStr += "    <file href=\""+resource+"\"/>\n"
            self.dependencies[resource] = True

        self.resStr += fileStr
        self.resStr += "  </resource>\n"


# ===========================================================================
class ScormPage(Page):
    """
    This class transforms an eXe node into a SCO
    """
    def __init__(self, *args, **kwargs):
        if "scorm_type" in kwargs:
            self.scorm_type = kwargs['scorm_type']
            del kwargs["scorm_type"]
        else:
            self.scorm_type = SCORM12 
        
        super(ScormPage, self).__init__(*args, **kwargs)

    def render(self):
        """
        Returns an XHTML string rendering this page.
        """
        return render_to_string("exe/export/scormpage.html",
                                {"current_page" : self})

# ===========================================================================
class ScormExport(WebsiteExport):
    """
    Exports an eXe package as a SCORM package
    """
    def __init__(self, *args, **kwargs):
        """ 
        Initialize
        'styleDir' is the directory from which we will copy our style sheets
        (and some gifs)
        """
        if "scorm_type" in kwargs:
            self.scorm_type = kwargs['scorm_type']
            del kwargs["scorm_type"]
        else:
            raise TypeError("ScormExport requires a kw argument scorm_type")
        
        super(ScormExport, self).__init__(*args, **kwargs)
        static_dir = Path(settings.STATIC_ROOT)
        self.imagesDir    = static_dir / "images"
        self.templatesDir = static_dir / "templates"
        self.schemasDir   = static_dir /"schemas"
        self.hasForum     = False
        
        self.page_class = ScormPage


    def export(self):
        """ 
        Export SCORM package
        """
        self.create_pages({"scorm_type" : self.scorm_type})
        
        for page in self.pages:
            if not self.hasForum:
                for idevice in page.node.idevices.all():
                    if hasattr(idevice, "isForum"):
                        if idevice.forum.lms.lms == "moodle":
                            self.hasForum = True
                            break
            else:
                break
        self.copyFiles()
        self.doZip()
        # Clean up the temporary dir
        self.output_dir.rmtree()
        
    def copyFiles(self):
        
        manifest = Manifest(self.output_dir, self.package,
                             self.pages, self.scorm_type)
        manifest.save("imsmanifest.xml")
        if self.hasForum:
            manifest.save("discussionforum.xml")
            
        if self.scorm_type == COMMONCARTRIDGE:
            self.style_dir.copylist(manifest.dependencies.keys(),
                                     self.output_dir)
        else:
            self.copy_style_files()
            
        self.copy_resources()
        if self.scorm_type == COMMONCARTRIDGE:
            self.scripts_dir.copylist(('libot_drag.js',
                                      'common.js'), self.output_dir)
        else:
            self.scripts_dir.copylist(('APIWrapper.js', 
                                      'SCOFunctions.js', 
                                      'libot_drag.js',
                                      'common.js'), self.output_dir)
        schemasDir = ""
        if self.scorm_type == SCORM12:
            schemasDir = self.schemasDir/SCORM12
            schemasDir.copylist(('imscp_rootv1p1p2.xsd',
                                'imsmd_rootv1p2p1.xsd',
                                'adlcp_rootv1p2.xsd',
                                'ims_xml.xsd'), self.output_dir)
        elif self.scorm_type == SCORM2004:
            schemasDir = self.schemasDir/SCORM2004
            schemasDir.copylist(('imscp_rootv1p1p2.xsd',
                                'imsmd_rootv1p2p1.xsd',
                                'adlcp_rootv1p2.xsd',
                                'ims_xml.xsd'), self.output_dir)
        self.copy_players()
        if self.scorm_type == SCORM12 or self.scorm_type == SCORM2004:
            self.copy_licence()
            
class ScormExport12(ScormExport):
    title = "Scorm 1.2"
    
    def __init__(self, *args, **kwargs):
        kwargs['scorm_type'] = SCORM12
        super(ScormExport12, self).__init__(*args, **kwargs)
    
        
class ScormExport2004(ScormExport):
    title = "Scorm 2004"
    
    def __init__(self, *args, **kwargs):
        kwargs['scorm_type'] = SCORM2004
        super(ScormExport2004, self).__init__(*args, **kwargs)
        
class CommonCartridge(ScormExport):
    title = "Common Cartridge"
    
    def __init__(self, *args, **kwargs):
        kwargs['scorm_type'] = SCORM12
        super(CommonCartridge, self).__init__(*args, **kwargs)

# ===========================================================================
