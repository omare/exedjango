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
This module contains resource classes used for eXe
"""

import logging
import os
from copy                 import deepcopy

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

log = logging.getLogger(__name__)

# ===========================================================================


class Resource(models.Model):
    """
    Contains reference to a file with some meta information
    """
    
    child_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    resource = models.FileField(upload_to="resource", blank=True, null=True)
    field = generic.GenericForeignKey()
    
    def get_absoulte_url(self):
        return self.resource.url()
    
    def __unicode__(self):
        return self.resource.name
    
    class Meta:
        app_label = "exeapp"
    
    
    def _setPackage(self, package):
        """
        Used to change the package.
        """
        if package is self._package: return
        oldPackage = self._package

        # new safety mechanism for old corrupt packages which
        # have non-existent resources that are being deleted:
        if not hasattr(self, 'checksum') or self.checksum is None:
            if package is None:
                log.warn("Resource " + repr(self) + " has no checksum " \
                        + "(probably no source file), but is being removed "\
                        + "anyway, so ignoring.")
            else: 
                if hasattr(self._package, 'resourceDir'):
                    log.warn("Resource " + repr(self) + " has no checksum " \
                        + "(probably old resource), and is being added to "\
                        + "valid package " + repr(package) )
                    log.warn("This resource should have been upgraded first!" \
                            + " Will be ignoring...")
                else:
                    log.warn("Resource " + repr(self) + " has no checksum " \
                        + "(probably no source file), and was being added to "\
                        + "invalid package " + repr(package) 
                        + "; setting to None.")
                # either way, play it safe and set its package to None and bail:
                self._package = None
            return

        if self._package and hasattr(self._package, 'resources')\
        and self.checksum in self._package.resources:
            # Remove our self from old package's list of resources
            siblings = self._package.resources[self.checksum]
            try: 
                # remove any multiple occurrences of this as well:
                # (as might in corrupt files)
                while self in siblings: 
                    siblings.remove(self) 
            except Exception, e:
                # this can occur with old corrupt files, wherein the resource 
                # was not actually properly connected to the package.  
                # Proceed anyhow, as if it just removed...
                bogus_condition = 1
            if len(siblings) == 0:
                # We are the last user of this file
                del self._package.resources[self.checksum]
            oldPath = self.path

        elif hasattr(self, '_originalFile'):
            oldPath = self._originalFile
        else:
            log.warn("Tried to remove a resource (\"" + repr(self)
                    + "\") from what seems to be a "
                    + "corrupt package: \"" + repr(self._package) 
                    + "\"; setting oldPackage to None.")
            # but let the new package fall right through, trying:
            oldPath = None
            oldPackage = None

        self._package = package
        if self._package:
            self._addOurselvesToPackage(oldPath)
        # Remove our old file if necessary
        if oldPackage and self.checksum not in oldPackage.resources:
            # ensure that oldPath really is an actual Path object as well.
            # on old corrupt files, oldPath is sometimes coming in as a 
            # string, perhaps when no resourceDir on its corrupt package(?).
            if oldPath and isinstance(oldPath, Path) and oldPath.exists():
                try: 
                    oldPath.remove()
                except WindowsError:
                    pass
            else:
                log.error("Tried to delete a resource that's already not "
                    + " there anymore: filename=\"%s\" "
                    + "userName=\"%s\"" % (oldPath, self.userName))
        # If our Idevice has not already moved, cut ourselves off from it
        if self._idevice \
        and self._idevice.parentNode.package is not self._package:
            self._idevice.userResources.remove(self)
            self._idevice = None

    # Properties
    storageName = property(lambda self:self._storageName)
    userName = property(lambda self:self._userName)
    package = property(lambda self:self._package, _setPackage)
    path = property(lambda self:self._package.resourceDir/self._storageName)

    # Protected methods

    def _addOurselvesToPackage(self, oldPath):
        """
        Adds ourselves into self._package.resources.
        Don't call if self._package is None.
        Does no copying or anything. Just sticks us in the list and sets our storage name
        """
        # new safety mechanism for old corrupt packages which
        # have non-existent resources that are being deleted and such:
        if not hasattr(self, 'checksum') or self.checksum is None:
            if self._package is None:
                log.warn("Resource " + repr(self) + " has no checksum " \
                        + "(probably no source file), but is being removed "\
                        + "anyway, so ignoring.")
                return
            else:
                if oldPath.isfile():
                    log.warn("Resource " + repr(self) + " has no checksum; " \
                            + " adding and continuing...")
                    # see if a few basic checks here can get it going to add:
                    self.checksum = oldPath.md5
                else: 
                    log.warn("Resource " + repr(self) + " has no checksum " \
                        + "(and no source file), and was being added to "\
                        + "package " + repr(self._package) + "; ignoring.")
                    return

        # Add ourselves to our new package's list of resources

        if not hasattr(self._package, 'resources'):
            log.error("_AddOurselvesToPackage called with an invalid package: " 
                    + " no resources on package " + repr(self._package)
                    + "; possibly after a deepcopy")
            return
        if not hasattr(self._package, 'resourceDir'):
            log.error("_AddOurselvesToPackage called with an invalid package: " 
                    + " no resourceDir on package " + repr(self._package)
                    + "; possibly an old/corrupt resource or package")
            return

        siblings = self._package.resources.setdefault(self.checksum, [])
        if siblings:
            # If we're in the resource dir, and already have a filename that's different to our siblings, delete the original file
            # It probably means we're upgrading from pre-single-file-resources or someone has created the file to be imported inside the resource dir
            # We are assuming that it's not a file used by other resources...
            newName = siblings[0]._storageName
            if oldPath.dirname() == self._package.resourceDir and self._storageName != newName:
                oldPath.remove()
            self._storageName = newName
        else:
            if Path(oldPath).dirname() == self._package.resourceDir:
                log.debug(u"StorageName=%s was already in self._package resources" % self._storageName)
            else:
                filename = (self._package.resourceDir/oldPath.basename())
                storageName = self._fn2ascii(filename)
                storageName = (self._package.resourceDir/storageName).unique()
                self._storageName = str(storageName.basename())
                oldPath.copyfile(self.path)
        if self not in siblings:
            # prevent doubling-up (as might occur when cleaning corrupt files)
            siblings.append(self)

    # Public methods

    def delete(self):
        """
        Remove a resource from a package
        """
        # Just unhooking from our package, does all we need
        self.package = None

    def __unicode__(self):
        """
        return the string
        """
        return self._storageName

    def __getinitargs__NOT__(self):
        """
        Used by copy.deepcopy, which is used by exe.engine.node.clone().
        Makes it so the copy for this resource, actually gets __init__ called
        """
        if self._idevice:
            return self._idevice, self.path
        else:
            return self._package, self.path

    def __deepcopy__(self, others={}):
        """
        Returns a copy of self, letting our package and idevice know what has happened
        'others' is the dict of id, object of everything that's been copied already
        """
        # Create a new me
        miniMe = self.__class__.__new__(self.__class__)
        others[id(self)] = miniMe
        # Do normal deep copy
        for key, val in self.__dict__.items():
            if id(val) in others:
                setattr(miniMe, key, others[id(val)])
            else:
                new = deepcopy(val, others)
                others[id(val)] = new
                setattr(miniMe, key, new)
        if miniMe.package:
            miniMe._addOurselvesToPackage(self.path)
        return miniMe
    
    # Protected methods

    def _fn2ascii(self, filename):
        """
        Changes any filename to pure ascii, returns only the basename
        """     
        nameBase, ext = Path(Path(filename).basename()).splitext()
        # Check if the filename is ascii so that twisted can serve it
        try: nameBase.encode('ascii')
        except UnicodeEncodeError:
            nameBase = nameBase.encode('utf-8').encode('hex')
        # Encode the extension separately so that you can keep file types a bit
        # at least
        try:
            ext = ext.encode('ascii')
        except UnicodeEncodeError:
            ext = ext.encode('utf8').encode('hex')
        return str(nameBase + ext)