# ===========================================================================
# eXe 
# Copyright 2004-2006, University of Auckland
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
"""
The base class for all iDevices
"""

from django.db import models
from django.contrib.contenttypes.models import ContentType

import logging
#from exe.engine.translate import lateTranslate

log = logging.getLogger(__name__)


# ===========================================================================
class Idevice(models.Model):
    """
    The base model for all iDevices
iDevices are mini templates which the user uses to create content in the 
package
    """

    # Class attributes
    # see derieved classes for persistenceVersion 
    NoEmphasis, SomeEmphasis, StrongEmphasis = range(3)
    Didactics, Content, Media, Test, Communication, Unknown = \
             "Didactics", "Content", "Media", "Test",\
             "Communication", "Unknown"
             
    # should be overwritten by child classes
    title = ""
    emphasis = NoEmphasis
    autor = ""
    purpose = ""
    tip = ""
    system_resources = []
             
    edit = models.BooleanField(default=True)
    icon = models.ImageField(upload_to="icons", blank=True, null=True)
    parent_node = models.ForeignKey('Node', related_name='idevices')
    
    child_type = models.CharField(max_length=32, editable=False, blank=True)
    
#    rawTitle = lateTranslate('title')
#    author   = lateTranslate('author')
#    purpose  = lateTranslate('purpose')
#    tip      = lateTranslate('tip')

    def get_klass(self):
        if hasattr(self, 'class_'):
            if self.class_ == '':
                return u'customIdevice'
            else:
                return self.class_ + u'Idevice'
        else:
            klass = str(self.as_child().__class__).split('.')[-1]
            return klass[:-2]
    klass = property(get_klass)
    
    @property
    def base_idevice(self):
        return Idevice.objects.get(pk=self.pk)
    
    @property
    def resources(self):
        '''Should be overridden in children to specify resource 
finding. Returns a set'''
        return set()
    
    def edit_mode(self):
        '''Sets idevice mode to edit'''
        self.edit = True
        
    def delete(self):
        super(Idevice, self).delete()
        
    def apply_changes(self, agruments, commit=True):
        self.edit = False
        if commit:
            self.save()
        

    def is_first(self):
        """
        Return true if this is the first iDevice in this node
        """
        return self._order == 0


    def is_last(self):
        """
        Return true if this is the last iDevice in this node
        """
        return self._order == \
            len(self.parent_node.idevices.get_query_set()) - 1       

    def move_up(self):
        """
        Move to the previous position
        """
        # Had to access _order directly because of a strange bug
        # May be reverted to use normal set_idevice_order routine
        # get_previous_in_order doesn't work either.
        base_idevice = self.base_idevice
        prev_idevice = base_idevice.get_previous_in_order()
        prev_idevice._order, self._order =\
                 self._order, prev_idevice._order
        prev_idevice.save()
        self.save()

    def move_down(self):
        """
        Move to the next position
        """
        prev_idevice = self.base_idevice.get_next_in_order()
        prev_idevice._order, self._order = self._order, prev_idevice._order
        prev_idevice.save()
        self.save()
            
    # Kudos to crucialfelix for djangosnippet 1031
    # http://djangosnippets.org/snippets/1031/        
    def save(self, *args, **kwargs):
        if (not self.child_type):
            self.child_type = self.__class__.__name__.lower()
        self.save_base(*args, **kwargs)
    
    def as_child(self):
        return getattr(self, self.child_type)


    def setParentNode(self, parentNode):
        """
        Change parentNode
        Now includes support for renaming any internal anchors and their links.
        """
        old_node = None
        if self.parentNode:
            old_node = self.parentNode
            self.parentNode.idevices.remove(self)
        parentNode.add_idevice(self)
        # and update any internal anchors and their links:
        self.ChangedParentNode(old_node, parentNode)


    def ChangedParentNode(self, old_node, new_node):
        """
        To update all fo the anchors (if any) that are defined within
        any of this iDevice's various fields, and any 
        internal links corresponding to those anchors.
        This is essentially a variation of Node:RenamedNode()
        It also removes any internal links from the data structures as well, 
        if this iDevice is being deleted
        """
        my_fields = self.getRichTextFields()
        num_fields = len(my_fields)
        for field_loop in range(num_fields-1, -1, -1):
            this_field = my_fields[field_loop]
            if hasattr(this_field, 'anchor_names') \
            and len(this_field.anchor_names) > 0:
                # okay, this is an applicable field with some anchors:
                this_field.ReplaceAllInternalAnchorsLinks(oldNode=old_node, 
                        newNode=new_node)

                if new_node:
                    # add this particular anchor field into the new node's list:
                    if not hasattr(new_node, 'anchor_fields'):
                        new_node.anchor_fields = []
                    if this_field not in new_node.anchor_fields: 
                        new_node.anchor_fields.append(this_field)
                    if new_package:
                        if not hasattr(new_package, 'anchor_nodes'):
                            new_package.anchor_nodes = []
                        if new_node not in new_package.anchor_nodes:
                            new_package.anchor_nodes.append(new_node)

            # now, regardless of whether or not that field has any anchors,
            # if this idevice is being deleted (new_node is None), then
            # go ahead and remove any of its internal links
            # from the corresponding data structures:
            if not new_node \
            and hasattr(this_field, 'intlinks_to_anchors') \
            and len(this_field.intlinks_to_anchors) > 0:
                this_field.RemoveAllInternalLinks()

        return

    def getResourcesField(self, this_resource):
        """
        Allow resources to easily find their specific corresponding field,
        to help out with loading and especially merging scenarios for resources
        with names already in use, for example.
        This method is expected to be overridden within each specific iDevice.
        """
        # in the parent iDevice class, merely return a None,
        # and let each specific iDevice class implement its own version:
        log.warn("getResourcesField called on iDevice; no specific "
                + "implementation available for this particular iDevice "
                + "class: " + repr(self) )
        return None

    def getRichTextFields(self):
        """
        Like getResourcesField(), a general helper to allow nodes to search 
        through all of their fields without having to know the specifics of each
        iDevice type.  
        Currently used by Extract to find all fields which have internal links.
        """
        # in the parent iDevice class, merely return an empty list,
        # and let each specific iDevice class implement its own version:
        log.warn("getRichTextFields called on iDevice; no specific "
                + "implementation available for this particular iDevice "
                + "class: " + repr(self) )
        return []
    
    def __unicode__(self):
        return "FreeTextIdevice: %s" % self._order
        
        
    class Meta:
        order_with_respect_to = 'parent_node'
        app_label = "exeapp"