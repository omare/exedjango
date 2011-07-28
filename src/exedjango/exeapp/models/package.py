# ===========================================================================
# eXe 
# Copyright 2004-2006, University of Auckland
# Copyright 2006-2008 eXe Project, http://eXeLearning.org/
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
from django.db import models
import datetime

"""
Package represents the collection of resources the user is editing
i.e. the "package".
"""

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User


import logging
import time
import zipfile 
import re
from collections import defaultdict
from xml.dom                   import minidom
from exedjango.utils.path      import Path, TempDirPath, toUnicode
from exeapp.models        import Node
#from exe.engine.genericidevice import GenericIdevice
                                      
from BeautifulSoup  import BeautifulSoup

log = logging.getLogger()

def _(value):
    '''Placeholder for translation'''
    return value


def clonePrototypeIdevice(title):
    idevice = None

    for prototype in G.application.ideviceStore.getIdevices(): 
        if prototype.get_title() == title:
            log.debug('have prototype of:' + prototype.get_title()) 
            idevice = prototype.clone() 
            idevice.edit = False
            break 

    return idevice

def burstIdevice(idev_type, i, node): 
    # given the iDevice type and the BeautifulSoup fragment i, burst it:
    idevice = clonePrototypeIdevice(idev_type)
    if idevice is None:
        log.warn("unable to clone " + idev_type + " idevice")
        freetext_idevice = clonePrototypeIdevice('Free Text')
        if freetext_idevice is None:
            log.error("unable to clone Free Text for " + idev_type 
                    + " idevice")
            return
        idevice = freetext_idevice

    # For idevices such as GalleryImage, where resources are being attached,
    # the idevice should already be attached to a node before bursting it open:
    node.add_idevice(idevice)

    idevice.burstHTML(i)
    return idevice

def loadNodesIdevices(node, s):
    soup = BeautifulSoup(s)
    body = soup.find('body')

    if body:
        idevices = body.findAll(name='div', 
                attrs={'class' : re.compile('Idevice$') })
        if len(idevices) > 0:
            for i in idevices: 
                # WARNING: none of the idevices yet re-attach their media,
                # but they do attempt to re-attach images and other links.

                if i.attrMap['class']=="activityIdevice":
                    idevice = burstIdevice('Activity', i, node)
                elif i.attrMap['class']=="objectivesIdevice":
                    idevice = burstIdevice('Objectives', i, node)
                elif i.attrMap['class']=="preknowledgeIdevice":
                    idevice = burstIdevice('Preknowledge', i, node)
                elif i.attrMap['class']=="readingIdevice":
                    idevice = burstIdevice('Reading Activity', i, node)
                # the above are all Generic iDevices;
                # below are all others:
                elif i.attrMap['class']=="RssIdevice":
                    idevice = burstIdevice('RSS', i, node)
                elif i.attrMap['class']=="WikipediaIdevice":
                    # WARNING: Wiki problems loading images with accents, etc:
                    idevice = burstIdevice('Wiki Article', i, node)
                elif i.attrMap['class']=="ReflectionIdevice":
                    idevice = burstIdevice('Reflection', i, node)
                elif i.attrMap['class']=="GalleryIdevice":
                    # WARNING: Gallery problems with the popup html:
                    idevice = burstIdevice('Image Gallery', i, node)
                elif i.attrMap['class']=="ImageMagnifierIdevice":
                    # WARNING: Magnifier missing major bursting components:
                    idevice = burstIdevice('Image Magnifier', i, node)
                elif i.attrMap['class']=="AppletIdevice":
                    # WARNING: Applet missing file bursting components:
                    idevice = burstIdevice('Java Applet', i, node)
                elif i.attrMap['class']=="ExternalUrlIdevice":
                    idevice = burstIdevice('External Web Site', i, node)
                elif i.attrMap['class']=="ClozeIdevice":
                    idevice = burstIdevice('Cloze Activity', i, node)
                elif i.attrMap['class']=="FreeTextIdevice":
                    idevice = burstIdevice('Free Text', i, node)
                elif i.attrMap['class']=="CasestudyIdevice":
                    idevice = burstIdevice('Case Study', i, node)
                elif i.attrMap['class']=="MultichoiceIdevice":
                    idevice = burstIdevice('Multi-choice', i, node)
                elif i.attrMap['class']=="MultiSelectIdevice":
                    idevice = burstIdevice('Multi-select', i, node)
                elif i.attrMap['class']=="QuizTestIdevice":
                    idevice = burstIdevice('SCORM Quiz', i, node)
                elif i.attrMap['class']=="TrueFalseIdevice":
                    idevice = burstIdevice('True-False Question', i, node)
                else:
                    # NOTE: no custom idevices burst yet,
                    # nor any deprecated idevices. Just burst into a FreeText:
                    log.warn("unburstable idevice " + i.attrMap['class'] + 
                            "; bursting into Free Text")
                    idevice = burstIdevice('Free Text', i, node)

        else:
            # no idevices listed on this page,
            # just create a free-text for the entire page:
            log.warn("no idevices found on this node, bursting into Free Text.")
            idevice = burstIdevice('Free Text', i, node)

    else:
        log.warn("unable to read the body of this node.")


def test_for_node(html_content):
    # to see if this html really is an exe-generated node
    exe_string = u"<!-- Created using eXe: http://exelearning.org -->"
    if html_content.decode('utf-8').find(exe_string) >= 0:
        return True
    else:
        return False

def loadNode(pass_num, resourceDir, zippedFile, node, doc, item, level):
    # populate this node
    # 1st pass = merely unzipping all resources such that they are available,
    # 2nd pass = loading the actual node idevices.
    titles = item.getElementsByTagName('title')
    node.setTitle(titles[0].firstChild.data)
    node_resource = item.attributes['identifierref'].value
    log.debug('*' * level + ' ' + titles[0].firstChild.data + '->' + item.attributes['identifierref'].value)

    for resource in doc.getElementsByTagName('resource'):
        if resource.attributes['identifier'].value == node_resource:
            for file in resource.childNodes:
                if file.nodeName == 'file':
                    filename = file.attributes['href'].value

                    is_exe_node_html = False
                    if filename.endswith('.html') \
                    and filename != "fdl.html" \
                    and not filename.startswith("galleryPopup"):
                        # fdl.html is the wikipedia license, ignore it
                        # as well as any galleryPopups:
                        is_exe_node_html = \
                                test_for_node(zippedFile.read(filename))

                    if is_exe_node_html:
                        if pass_num == 1:
                            # 2nd pass call to actually load the nodes:
                            log.debug('loading idevices from node: ' + filename)
                            loadNodesIdevices(node, zippedFile.read(filename))
                    elif filename == "fdl.html" or \
                    filename.startswith("galleryPopup."):
                        # let these be re-created upon bursting.
                        if pass_num == 0:
                            # 1st pass call to unzip the resources:
                            log.debug('ignoring resource file: '+ filename)
                    else:
                        if pass_num == 0:
                            # 1st pass call to unzip the resources:
                            try:
                                zipinfo = zippedFile.getinfo(filename)
                                log.debug('unzipping resource file: '
                                        + resourceDir/filename )
                                outFile = open(resourceDir/filename, "wb") 
                                outFile.write(zippedFile.read(filename)) 
                                outFile.flush() 
                                outFile.close()
                            except:
                                log.warn('error unzipping resource file: '
                                        + resourceDir/filename )
                        ##########
                        # WARNING: the resource is now in the resourceDir,
                        # BUT it is NOT YET added into any of the project,
                        # much less to the specific idevices or fields!
                        # Although they WILL be saved out with the project
                        # upon the next Save.
                        ##########
            break

    # process this node's children
    for subitem in item.childNodes:
        if subitem.nodeName == 'item': 
            # for the first pass, of unzipping only, do not
            # create any child nodes, just cruise on with this one:
            next_node = node
            if pass_num == 1:
                # if this is actually loading the nodes:
                next_node = node.create_child()
            loadNode(pass_num, resourceDir, zippedFile, next_node,
                    doc, subitem, level+1)

def loadCC(zippedFile, filename):
    """
    Load an IMS Common Cartridge or Content Package from filename
    """
    package = Package(Path(filename).namebase)
    xmldoc = minidom.parseString( zippedFile.read('imsmanifest.xml')) 

    organizations_list = xmldoc.getElementsByTagName('organizations')
    level = 0
    # now a two-pass system to first unzip all applicable resources:
    for pass_num in range(2):
        for organizations in organizations_list:
            organization_list = organizations.getElementsByTagName(
                    'organization')
            for organization in organization_list:
                for item in organization.childNodes:
                    if item.nodeName == 'item':
                        loadNode(pass_num, package.resourceDir, zippedFile, 
                                package.root, xmldoc, item, level)
    return package

# ===========================================================================
class DublinCore(models.Model):
    title = models.CharField(blank=True, max_length=128)
    creator = models.CharField(blank=True, max_length=128)
    subject = models.CharField(blank=True, max_length=256)
    description = models.TextField(blank=True)
    publisher = models.CharField(blank=True, max_length=128)
    contributors = models.TextField(blank=True, max_length=256)
    date = models.DateField(default=datetime.date.today)
    type = models.CharField(blank=True, max_length=256)
    format = models.CharField(blank=True, max_length=128)
    identifier = models.CharField(blank=True, max_length=128)
    source = models.CharField(blank=True, max_length=128)
    language = models.CharField(blank=True, max_length=32)
    relation = models.CharField(blank=True, max_length=256)
    coverage = models.CharField(blank=True, max_length=128)
    rights = models.CharField(blank=True, max_length=256)
    
    class Meta:
        app_label = "exeapp"

class PackageManager(models.Manager):
    
    
    def create(self, *args, **kwargs):
        package = Package(*args, **kwargs)
        dublincore = DublinCore.objects.create()
        package.dublincore = dublincore
        package.save()
        root = Node(package=package, parent=None,
                    title="Home", is_current_node=True, is_root=True)
        root.save()
        
        
        return package

class Package(models.Model):
    """
    Package represents the collection of resources the user is editing
i.e. the "package".
    """
    
    DEFAULT_LEVEL_NAMES  = ["Topic", "Section", "Unit"]
    
    
    title = models.CharField(max_length=100)
    
    user = models.ForeignKey(User)
      
    author = models.CharField(max_length=50, blank=True)
    email = models.EmailField(max_length=50, blank=True)
    description = models.CharField(max_length=256, blank=True)
    
    backgroundImg = models.ImageField(upload_to='background', 
                                           blank=True, null=True)
    backgroundImgTile = models.BooleanField(default=False)
    footer = models.CharField(max_length=100, blank=True)
    footerImg     = models.ImageField(upload_to='footer', 
                                           blank=True, null=True)
    
    license = models.CharField(max_length=50, blank=True)
    style = models.CharField(max_length=20, default="default")
    resourceDir = models.FileField(upload_to="resources", 
                                    blank=True, null=True)
    dublincore = models.OneToOneField(DublinCore)
    
    level1 = models.CharField(max_length=20, default=DEFAULT_LEVEL_NAMES[0])
    level2 = models.CharField(max_length=20, default=DEFAULT_LEVEL_NAMES[1])
    level3 = models.CharField(max_length=20, default=DEFAULT_LEVEL_NAMES[2])
    
    
    
    objects = PackageManager()
    
        # self.dublinCore    = DublinCore()
        # self.license       = "None"
        # self.footer        = ""
        # self.sourcerefs    = {}
        # self.resourceDir = TempDirPath()

    # Property Handlers
    
    def set_current_node_by_id(self, node_id):
        try:
            node = Node.objects.get(pk=node_id, package=self)
            self.current_node = node 
        except Node.DoesNotExist:
            raise KeyError("Could not find node %s" % node_id)
        
    def set_current_node_by_unique_name(self, node_name):
        
        try:
            if node_name == 'index':
                node = self.root
            else:
                node_id = node_name.split("_")[-1]
                node = Node.objects.get(pk=node_id,
                                     package=self)
        except Node.DoesNotExist:
            raise KeyError("Package with name %s wasn't found"\
                           % node_name)
        else:
            self.current_node = node
        
        
    def add_child_node(self):
        '''Creates a child node of the current node, current node stays
the same'''
        node = self.current_node.create_child() 
        return node
            
    def delete_current_node(self):
        '''Removes current node. Sets current node to deleted node's 
parent'''
        node = self.current_node
        if node is not self.root:
            self.current_node = node.parent
            node.delete()
            return "1"
        else:
            return "0"
    
    def rename_current_node(self, new_title):
        '''Renames current node. Returns new name, if it's changed, old name else'''
        node = self.current_node
        if new_title not in ['', 'null']:
            node.title = new_title
            node.save()
        return node.title
    
    def promote_current_node(self):
        '''Moves current node one step up in the hierarchie. Returns True if
successful'''
        return self.current_node.promote()
    
    def demote_current_node(self):
        '''Moves current node one step up in the hierarchie. Returns True if
successful'''
        return self.current_node.demote()
    
    def move_current_node_up(self):
        '''Moves current node up on the same level. Returns true if 
successful'''
        return self.current_node.up()
    
    def move_current_node_down(self):
        '''Moves current node down on the same level. Returns true if 
successful'''
        return self.current_node.down()
    
    def add_idevice(self, idevice_type):
        '''Adds idevice by a given type to the current node.
Throws KeyError, if idevice_type is not found'''
        idevice = self.current_node.add_idevice(idevice_type) 
        return idevice
        
    def get_idevice_for_partial(self, idevice_id):
        '''Returns a idevice only in case its on the current node of this
package'''
        return self.current_node.idevices.get(id=int(idevice_id))
            
        
    def handle_action(self, idevice_id, action, data):
        '''Delegates a action to current_node'''
        return self.current_node.handle_action(idevice_id,
                                        action,
                                        data)

    def set_backgroundImg(self, value):
        """Set the background image for this package"""
        if self._backgroundImg:
            self._backgroundImg.delete()

        if value:
            if value.startswith("file://"):
                value = value[7:]

            imgFile = Path(value)
            self._backgroundImg = Resource(self, Path(imgFile))
        else:
            self._backgroundImg = u''
    

    def get_footerImg(self):
        """Get the footer image for this package"""
        if self._footerImg:
            return "file://" + self._footerImg.path
        else:
            return ""


    def set_footerImg(self, value):
        """Set the footer image for this package"""
        if self._footerImg:
            self._footerImg.delete()
        if value:
            if value.startswith("file://"):
                value = value[7:]
            imgFile = Path(value)
            self._footerImg = Resource(self, Path(imgFile))
        else:
            self._footerImg = u''


    # Properties
    @property
    def current_node(self):
        return self.nodes.get(is_current_node=True)
    
    @current_node.setter
    def current_node(self, node):
        old_node = self.current_node
        old_node.is_current_node = False
        old_node.save()
        node.is_current_node = True
        node.save()

    def set_style(self, style):
        self.style = style
        self.save()
        
    @property
    def root(self):
        return self.nodes.get(is_root=True)
    
    @property
    def resources(self):
        # ask each node to its resources to desceare coupling
        # implement as direct quety, should performance be too bad
        resources = set()
        for node in self.nodes.all():
            resources.update(node.resources)
        return resources
    
    
    @property
    def link_list(self):
        link_list = []
        for node in self.nodes.all():
            link_list += node.link_list
        return link_list 
        
    def levelName(self, level):
        """
        Return the level name
        """
        if level < len(self._levelNames):
            return _(self._levelNames[level])
        else:
            return _(u"?????")
        

    def updateRecentDocuments(self, filename):
        """
        Updates the list of recent documents
        """
        # TODO Fix the function
        return 0
        # Don't update the list for the generic.data "package"
        genericData = G.application.config.configDir/'idevices'/'generic.data'
        if genericData.isfile() or genericData.islink():
            if Path(filename).samefile(genericData):
                return
        # Save in recentDocuments list
        recentProjects = G.application.config.recentProjects
        if filename in recentProjects:
            # If we're already number one, carry on
            if recentProjects[0] == filename:
                return
            recentProjects.remove(filename)
        recentProjects.insert(0, filename)
        del recentProjects[5:] # Delete any older names from the list
        G.application.config.configParser.write() # Save the settings

    def extractNode(self):
        """
        Clones and extracts the currently selected node into a new package.
        """
        newPackage = Package('NoName') # Name will be set once it is saved..
        newPackage.title  = self.current_node.title
        newPackage.style  = self.style
        newPackage.author = self.author
        newPackage._nextNodeId = self._nextNodeId
        # Copy the nodes from the original package
        # and merge into the root of the new package
        self.current_node.copyToPackage(newPackage)
        return newPackage

    @staticmethod
    def load(filename, newLoad=True, destinationPackage=None):
        """
        Load package from disk, returns a package.
        """
        #if not zipfile.is_zipfile(filename):
        #    return None
        try:
            zippedFile = zipfile.ZipFile(filename, "r")
        except zipfile.BadZipFile:
            log.error("File %s is not a zip file" % file)
            return None
                
        
        try:
            # Get the jellied package data
            toDecode   = zippedFile.read(u"content.data")
        except KeyError:
            log.info("no content.data, trying Common Cartridge/Content Package")
            newPackage = loadCC(zippedFile, filename)
            newPackage.tempFile = False
            newPackage.isChanged = False
            newPackage.filename = Path(filename)

            return newPackage
            
        # Need to add a TempDirPath because it is a non-persistent member
        resourceDir = TempDirPath()

        # Extract resource files from package to temporary directory
        for fn in zippedFile.namelist():
            if unicode(fn, 'utf8') != u"content.data":
                outFile = open(resourceDir/fn, "wb")
                outFile.write(zippedFile.read(fn))
                outFile.flush()
                outFile.close()

        try:
            newPackage = decodeObjectRaw(toDecode)
#            G.application.afterUpgradeHandlers = []
            newPackage.resourceDir = resourceDir
#            G.application.afterUpgradeZombies2Delete = []

            if newLoad: 
                # provide newPackage to doUpgrade's versionUpgrade() to
                # correct old corrupt extracted packages by setting the
                # any corrupt package references to the new package:

                log.debug("load() about to doUpgrade newPackage \"" 
                        + newPackage._name + "\" " + repr(newPackage) )
                if hasattr(newPackage, 'resourceDir'):
                    log.debug("newPackage resourceDir = "
                            + newPackage.resourceDir)
                else:
                    # even though it was just set above? should not get here:
                    log.error("newPackage resourceDir has NO resourceDir!")

#                doUpgrade(newPackage)

                # after doUpgrade, compare the largest found field ID:
#                if G.application.maxFieldId >= Field.nextId:
#                    Field.nextId = G.application.maxFieldId + 1

            else: 
                # and when merging, automatically set package references to
                # the destinationPackage, into which this is being merged:

                log.debug("load() about to merge doUpgrade newPackage \"" 
                        + newPackage._name + "\" " + repr(newPackage)
                        + " INTO destinationPackage \"" 
                        + destinationPackage._name + "\" " 
                        + repr(destinationPackage))
                
                log.debug("using their resourceDirs:")
                if hasattr(newPackage, 'resourceDir'):
                    log.debug("   newPackage resourceDir = " 
                            + newPackage.resourceDir)
                else:
                    log.error("newPackage has NO resourceDir!")
                if hasattr(destinationPackage, 'resourceDir'):
                    log.debug("   destinationPackage resourceDir = " 
                            + destinationPackage.resourceDir)
                else:
                    log.error("destinationPackage has NO resourceDir!")

                doUpgrade(destinationPackage, 
                        isMerge=True, preMergePackage=newPackage)

                # after doUpgrade, compare the largest found field ID:
#                if G.application.maxFieldId >= Field.nextId:
#                    Field.nextId = G.application.maxFieldId + 1

        except:
            import traceback
            traceback.print_exc()
            raise

        if newPackage.tempFile:
            # newPackage.filename was stored as it's original filename
            newPackage.tempFile = False
        else:
            # newPackage.filename is the name that the package was last loaded from
            # or saved to
            newPackage.filename = Path(filename)

        # Let idevices and nodes handle any resource upgrading they may need to
        # Note: Package afterUpgradeHandlers *must* be done after Resources'
        # and the package should be updated before everything else,
        # so, prioritize with a 3-pass, 3-level calling setup
        # in order of: 1) resources, 2) package, 3) anything other objects

        newPackage.updateRecentDocuments(newPackage.filename)
        newPackage.isChanged = False
        return newPackage

    def cleanUpResources(self):
        """
        Removes duplicate resource files
        """
        # Delete unused resources.
        # Only really needed for upgrading to version 0.20,
        # but upgrading of resources and package happens in no particular order
        # and must be done after all resources have been upgraded

        # some earlier .elp files appear to have been corrupted with 
        # two packages loaded, *possibly* from some strange extract/merge
        # functionality in earlier eXe versions?
        # Regardless, only the real package will have a resourceDir,
        # and the other will fail.
        # For now, then, put in this quick and easy safety check:
        if not hasattr(self,'resourceDir'):
            log.warn("cleanUpResources called on a redundant package")
            return

        existingFiles = set([fn.basename() for fn in self.resourceDir.files()])
        usedFiles = set([reses[0].storageName for reses in self.resources.values()])
        for fn in existingFiles - usedFiles:
            (self.resourceDir/fn).remove()

    def findResourceByName(self, queryName):
        """
        Support for merging, and anywhere else that unique names might be
        checked before actually comparing against the files (as will be 
        done by the resource class itself in its _addOurselvesToPackage() )
        """
        foundResource = None
        queryResources = self.resources
        for this_checksum in queryResources:
            for this_resource in queryResources[this_checksum]:
                if queryName == this_resource.storageName:
                    foundResource = this_resource
                    return foundResource
        return foundResource
    
    def get_absolute_url(self):
        return reverse('exeapp.views.package.package_main',
                       kwargs={'package_id' : self.id})
    
    def __unicode__(self):
        return "Package %s: %s" % (self.id, self.title)
    
    class Meta:
        app_label = "exeapp"


# ===========================================================================
