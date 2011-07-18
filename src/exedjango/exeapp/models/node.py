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
from django.template.loader import render_to_string
import re
"""
Nodes provide the structure to the package hierarchy
"""

from django.db import models

from exeapp.models import idevice_store


import logging
from copy               import deepcopy
from urllib             import quote

#from exe.webui                import common


log = logging.getLogger()

class NodeManager(models.Manager):
    
    def create(self, package, parent, title="", is_root=False, 
               is_current_node=False):
        if not title:
            level = parent.level + 1
            if level > 3:
                title = "???"
            else:
                title = getattr(package, "level%s" % level)
        node = Node(package=package, parent=parent, title=title,
                    is_root=is_root, is_current_node=is_current_node)
        node.save()
        return node

class Node(models.Model):
    """
    Nodes provide the structure to the package hierarchy
    """
    package = models.ForeignKey('Package', related_name='nodes')
    parent = models.ForeignKey('self', related_name='children', 
                               blank=True, null=True)
    title = models.CharField(max_length=50)
    is_root = models.BooleanField(default=False)
    is_current_node = models.BooleanField(default=False)
    
    objects = NodeManager()

    #self.last_full_node_path = self.GetFullNodePath()

    # Properties

    # level
    def getLevel(self):
        """
        Calculates and returns our current level
        """
        return len(list(self.ancestors()))
    level = property(getLevel)


    def get_idevice(self, idevice_id):
        '''Returns idevice with given id. Can't use dictionary, because
it is unordered and can't use OrderedDict, because jelly doesn't play nice
with it'''
        for idevice in self.idevices:
            if idevice.id == idevice_id:
                return idevice
        raise KeyError("Idevice %s not found" % idevice_id)
    # 



    def GetFullNodePath(self, new_node_title=""):
        """
        A general purpose single-line node-naming convention,
        currently only used for the anchor names, to
        provide a path to its specific node.
        Create this path in an HTML-safe name, to closely match 
        the names used upon export of the corresponding files.
        Optional new_node_title allows the determination of the
        full path name should this node's name change.
        """
        # use lower-case for the exe-node, for TinyMCE copy/paste compatibility:
        full_path = "exe-node"
        # first go through all of the parentNode's ancestor nodes:
        this_nodes_ancestors = list(self.ancestors())
        num_ancestors = len(this_nodes_ancestors)
        for loop in range(num_ancestors-1, -1, -1):
            node = this_nodes_ancestors[loop]
            if node is not None:
                # note: if node is None,
                #   appears to be an invalid ancestor in an Extracted package,
                #   but continue on, since it was probably one of the top nodes 
                #   above the extraction that is None. 
                # but this node IS valid, so add it to the path:
                full_path = "%s:%s" % (full_path, self.title)

        # and finally, add this node itself:
        if new_node_title == "":
            full_path = "%s:%s" % (full_path, self.title)
        else:
            # a new_node_title was specified, create this path with the new name
            full_path = "%s:%s" % (full_path, new_node_title)
        return full_path



    def RenamedNodePath(self, isMerge=False, isExtract=False):
        """
        To update all of the anchors (if any) that are defined within
        any of this node's various iDevice fields, and any 
        internal links corresponding to those anchors.
        Called AFTER the actual rename has occurred.
        NOTE: isMerge & isExtract will also attempt to connect all the data 
        structures, and isExtract will also try to clear out any orphaned links.
        AND: especially for extracts, continue on through all the child nodes
        even if the node names & path appear to be the same, since the objects
        actually differ and internal linking data structures need to be updated.
        """
        if not hasattr(self, 'anchor_fields'):
            self.anchor_fields = []

        old_node_path = self.last_full_node_path
        new_node_path = self.GetFullNodePath()
        self.last_full_node_path = new_node_path
        log.debug('Renaming node path, from "' + old_node_path 
                + '" to "' + new_node_path + '"')

        current_package = self.package

        # First rename all of the source-links to anchors in this node's fields:
        for this_field in self.anchor_fields:
            if (isMerge or isExtract) and hasattr(this_field, 'anchor_names') \
            and len(this_field.anchor_names) > 0:
                # merging this field into a destination package,
                # setup the internal linking data structures:

                if not hasattr(self.package, 'anchor_fields'):
                    self.package.anchor_fields = []
                if this_field not in self.package.anchor_fields:
                    self.package.anchor_fields.append(this_field)

                if not hasattr(self.package, 'anchor_nodes'):
                    self.package.anchor_nodes = []
                if self not in self.package.anchor_nodes:
                    self.package.anchor_nodes.append(self)

            # now, for ANY type of node renaming, update corresponding links:
            if hasattr(this_field, 'anchor_names') \
            and hasattr(this_field, 'anchors_linked_from_fields'):
                for this_anchor_name in this_field.anchor_names:
                    old_full_link_name = old_node_path + "#" + this_anchor_name
                    new_full_link_name = new_node_path + "#" + this_anchor_name

                    # Remove any linked fields that no longer apply, 
                    # using reverse for loop to delete: 
                    num_links = len(this_field.anchors_linked_from_fields[\
                            this_anchor_name])
                    for i in range(num_links-1, -1, -1):
                        that_field = this_field.anchors_linked_from_fields[\
                            this_anchor_name][i]
                        that_field_is_valid = True
                        if isExtract: 
                            # first ensure that each linked_from_field is 
                            # still in the extracted package.
                            # as with the subsequent isExtract link detection...
                            # Now, carefully check that the this_anchor_field
                            # is indeed in the current extracted sub-package,
                            # being especially aware of zombie nodes which are 
                            # unfortunately included with the sub-package, but 
                            # are NOT actually listed within its _nodeIdDict!
                            if that_field.idevice is None \
                            or that_field.idevice.parentNode is None \
                            or that_field.idevice.parentNode.package \
                            != current_package \
                            or that_field.idevice.parentNode.id \
                            not in current_package._nodeIdDict \
                            or current_package._nodeIdDict[ \
                            that_field.idevice.parentNode.id] \
                            != that_field.idevice.parentNode:
                                that_field_is_valid = False
                                # and remove the corresponding link here.
                                this_field.anchors_linked_from_fields[\
                                        this_anchor_name].remove(that_field)
                        if that_field_is_valid: 
                            that_field.RenameInternalLinkToAnchor(\
                                this_field, unicode(old_full_link_name), 
                                unicode(new_full_link_name))

        # And a variation of the above, for all source-links to #auto_top,
        # which is directly to this node, and not to any of its fields:
        this_anchor_name = u"auto_top"
        old_full_link_name = old_node_path + "#" + this_anchor_name
        new_full_link_name = new_node_path + "#" + this_anchor_name
        if not hasattr(self, 'top_anchors_linked_from_fields'):
            self.top_anchors_linked_from_fields = []
        num_links = len(self.top_anchors_linked_from_fields)
        num_top_links = num_links
        if (isMerge or isExtract):
            # merging this node into a destination package,
            # setup the internal linking data structures:
            if not hasattr(self.package, 'anchor_nodes'):
                self.package.anchor_nodes = []
            if num_links > 0 and self not in self.package.anchor_nodes:
                self.package.anchor_nodes.append(self)
        # Remove any linked fields that no longer apply, 
        # using reverse for loop to delete: 
        for i in range(num_links-1, -1, -1):
            # now, for ANY type of node renaming, update corresponding links:
            that_field = self.top_anchors_linked_from_fields[i]
            that_field_is_valid = True
            if isExtract: 
                # first ensure that each linked_from_field is 
                # still in the extracted package.
                # as with the subsequent isExtract link detection...
                # Now, carefully check that the this_anchor_field
                # is indeed in the current extracte sub-package,
                # being especially aware of zombie nodes which are 
                # unfortunately included with the sub-package, but 
                # are NOT actually listed within its _nodeIdDict!
                if that_field.idevice is None \
                or that_field.idevice.parentNode is None \
                or that_field.idevice.parentNode.package \
                != current_package \
                or that_field.idevice.parentNode.id \
                not in current_package._nodeIdDict \
                or current_package._nodeIdDict[ \
                that_field.idevice.parentNode.id] \
                != that_field.idevice.parentNode:
                    that_field_is_valid = False
                    # and remove the corresponding link here.
                    self.top_anchors_linked_from_fields.remove(that_field)
            if that_field_is_valid: 
                # for auto_top, uses the actual Node as the anchor_field:
                anchor_field = self
                that_field.RenameInternalLinkToAnchor(\
                    anchor_field, unicode(old_full_link_name), 
                    unicode(new_full_link_name))
        # and determine if any links to this node remain
        num_links = len(self.top_anchors_linked_from_fields)
        if num_top_links > 0 and num_links <= 0:
            # there WERE links to this node's auto_top, 
            # but they no longer apply to this extracted sub-package.
            # If no other anchors are in any of this node's fields, then 
            # no need for this node to be in the package's anchor_nodes list:
            if len(self.anchor_fields) <= 0:
                if self.package and hasattr(self.package, 'anchor_nodes') \
                and self in self.package.anchor_nodes:
                    self.package.anchor_nodes.remove(self)

        # and for package extractions, also ensure that any internal links 
        # in ANY of its fields are to anchors that still exist in this package:
        if isExtract:
            for this_idevice in self.idevices:
                for this_field in this_idevice.getRichTextFields(): 
                    if hasattr(this_field, 'intlinks_to_anchors') \
                    and len(this_field.intlinks_to_anchors) > 0: 

                        # Remove any linked fields that no longer apply, 
                        # using reverse for loop to delete: 
                        these_link_names = this_field.intlinks_to_anchors.keys()
                        num_links = len(these_link_names)
                        for i in range(num_links-1, -1, -1):
                            this_link_name = these_link_names[i]
                            this_anchor_field = \
                                this_field.intlinks_to_anchors[this_link_name] 
                            # Now, carefully check that the this_anchor_field
                            # is indeed in the current extracted sub-package,
                            # being especially aware of zombie nodes which are 
                            # unfortunately included with the sub-package, but 
                            # are NOT actually listed within its _nodeIdDict!

                            # could not import this at the top:
                            from exe.engine.field         import Field

                            this_link_node = None
                            this_anchor_name = common.getAnchorNameFromLinkName(
                                    this_link_name)
                            if this_anchor_field \
                            and isinstance(this_anchor_field, Field) \
                            and this_anchor_name != u"auto_top": 
                                if this_anchor_field.idevice is not None \
                                and this_anchor_field.idevice.parentNode:
                                    this_link_node = \
                                        this_anchor_field.idevice.parentNode
                            elif this_anchor_field \
                            and isinstance(this_anchor_field, Node):
                                # can be a Node for an auto_top link
                                this_link_node = this_anchor_field
                            if this_link_node is None \
                            or this_link_node.package != current_package \
                            or this_link_node.id \
                            not in current_package._nodeIdDict \
                            or current_package._nodeIdDict[this_link_node.id] \
                            != this_link_node:
                                # this internal link points to an anchor 
                                # which is NO LONGER a VALID part of this
                                # newly extracted sub-package.  Remove it:
                                this_field.RemoveInternalLinkToRemovedAnchor( \
                                    this_anchor_field, unicode(this_link_name))

        # Then do the same for all of this node's children nodes:
        for child_node in self.children:
            child_node.RenamedNodePath(isMerge, isExtract)

    titleShort = property(lambda self: self.title.split('--', 1)[0].strip())
    titleLong = property(lambda self: self.title.split('--', 1)[-1].strip())

    # Normal methods

    def copyToPackage(self, newPackage, newParentNode=None):
        """
        Clone a node just like this one, still belonging to this package.
        if 'newParentNode' is None, the newly created node will replace the 
            root of 'newPackage'

        The newly inserted node is automatically selected.
        """
        log.debug(u"clone " + self.title)

        try: 
            # Setting self.parent in the copy to None, so it doesn't 
            # go up copying the whole tree 
            newNode = deepcopy(self, {id(self._package): newPackage,
                                  id(self.parent): None}) 
            newNode._id = newPackage._regNewNode(newNode)
        except Exception, e:
            raise

        # return nonpersistables to normal status:
        # Give all the new nodes id's
        for node in newNode.walkDescendants():
            node._id = newPackage._regNewNode(node)
        # Insert into the new package
        if newParentNode is None:
            newNode.parent = None
            newPackage.root = newPackage.currentNode = newNode
        else:
            newNode.parent = newParentNode
            newNode.parent.children.append(newNode)
            newPackage.currentNode = newNode
        return newNode

    def ancestors(self):
        """Iterates over our ancestors"""
        if self.parent: # All top level nodes have no ancestors
            node = self
            while node is not None and node is not self.package.root:
                if not hasattr(node, 'parent'):
                    log.warn("ancestor node has no parent")
                    node = None
                else: 
                    node = node.parent
                    yield node


    def isAncestorOf(self, node):
        """If we are an ancestor of 'node' returns 'true'"""
        return self in node.ancestors()

    
    @property
    def resources(self):
        """
        Return the resource files used by this node
        """
        log.debug(u"getResources ")
        resources = set()
        for idevice in self.idevices.all():
            resources.update(idevice.as_child().resources)
        return resources
    
    @property
    def link_list(self):
        '''
        Returns all links from idevices and a link to the node itself
        '''
        link_list = [(self.title, "%s.html" % self.unique_name())]
        for idevice in self.idevices.all():
            link_list += idevice.as_child().link_list
        return link_list
    
    def handle_action(self, idevice_id, action, data):
        '''Removes an iDevice or delegates action to it'''
        idevice = self.idevices.get(pk=idevice_id).as_child()
        from exeapp.views.blocks.blockfactory import block_factory
        block = block_factory(idevice)
        if action == 'delete':
            idevice.delete()
            return ""
        else:
            block.process(action, data)
            block.idevice.save()
            return block.render()


    def create_child(self):
        """
        Create a child node
        """
        log.debug(u"create_child ")
        return Node.objects.create(package=self.package, parent=self)


    def add_idevice(self, idevice_type):
        """
        Add the idevice to this node, sets idevice's parentNode. Throws
KeyError, if idevice_type is not found
        """
        log.debug(u"add_idevice %s" % idevice_type)
        try:
            idevice_class = idevice_store[idevice_type]
        except KeyError:
            KeyError("Idevice type %s does not exist." % idevice_type)
        for edited_device in self.idevices.filter(edit=True):
            edited_device.edit = False
        idevice = idevice_class.objects.create(parent_node=self) 
        return idevice
        
    def move(self, new_parent, next_sibling=None):
        """
        Moves the node around in the tree.
        """
        
        self.parent = new_parent
        self.save()
        node_order = self.parent.get_node_order()
        node_order.remove(self.id)
        if next_sibling is not None:
            sibling_index = node_order.index(next_sibling.pk)
        else:
            sibling_index = len(node_order)
        node_order.insert(sibling_index, self.pk)
        self.parent.set_node_order(node_order)  


    def promote(self):
        """
        Convenience function. Moves the node one step 
closer to the tree root.
Returns True is successful
        """
        log.debug(u"promote ")
        if self.parent and self.parent.parent:
            try:
                next_sibling = self.parent.get_next_in_order()
            except Node.DoesNotExist:
                next_sibling = None
            self.move(self.parent.parent, next_sibling)
            return True

        return False


    def demote(self):
        """
        Convenience function. Moves the node one step further away 
from its parent, tries to keep the same position in the tree.
Returns True is successful
        """
        log.debug(u"demote ")
        if self.parent:
            try:
                new_parent = self.get_previous_in_order()
            except Node.DoesNotExist:
                return False
            if new_parent is not None:
                self.move(new_parent)
                return True

        return False


    def up(self):
        """
        Moves the node up one node vertically, keeping to the same level in 
        the tree.
        Returns True is successful.
        """
        log.debug(u"up ")
        try:
            prev_sibling = self.get_previous_in_order()
        except Node.DoesNotExist:
            return False
        if prev_sibling is not None:
            self.move(self.parent, prev_sibling)
            return True
        return False


    def down(self):
        """
        Moves the node down one vertically, keeping its level the same.
        Returns True is successful.
        """
        log.debug(u"down ")
        try:
            next_sibling = self.get_next_in_order()
        except Node.DoesNotExist:
            return False
        try:
            next_next_sibling = next_sibling.get_next_in_order()
            
        except Node.DoesNotExist:
            next_next_sibling = None
        
        self.move(self.parent, next_next_sibling) 
        return True



    def walkDescendants(self):
        """
        Generator that walks all descendant nodes
        """
        for child in self.children.all():
            yield child
            for descendant in child.walkDescendants():
                yield descendant



    def launch_testForZombies(self):
        """
        a wrapper to testForZombieNodes(self), such that it might be called
        after the package has been loaded and upgraded.  Otherwise, due 
        to the seemingly random upgrading of the package and resource objects,
        this might be called too early.
        """
        # only bother launching the zombie node sub-tree check 
        # on potential root nodes, either valid or of zombie trees:
        if not hasattr(self, 'parent') or self.parent is None: 
            # supposedly the root of a sub-tree, but it could also be a zombie.
            # Allow all of the package to load up and upgrade before testing:
            G.application.afterUpgradeHandlers.append(self.testForZombieNodes)
        elif not hasattr(self.parent, 'children')\
        or not self in self.parent.children: 
            # this seems a child which is not properly connected to its parent:
            G.application.afterUpgradeHandlers.append(self.testForZombieNodes)

    def testForZombieNodes(self):
        """ 
        testing a possible post-load confirmation that this resource 
        is indeed attached to something.  
        to be called from twisted/persist/styles.py upon load of a Node.
        """
        # remembering that this is only launched for this nodes
        # with parent==None or not in the parent's children list.
        if not hasattr(self, '_package') or self._package is None\
        or not hasattr(self._package, 'root') or self._package.root != self: 
            log.warn("Found zombie Node \"" + self.getTitle() 
                + "\", nodeId=" + str(self.getId()) 
                + " @ " + str(id(self)) + ".")
            if not hasattr(self, '_title'):
                # then explicitly set its _title attribute to update below
                self._title = self.getTitle()
            # disconnect it from any package, parent, and idevice links,
            # and go through and delete any and all children nodes:
            zombie_preface = u"ZOMBIE("
            if self._title[0:len(zombie_preface)] != zombie_preface: 
                self._title = zombie_preface + self._title + ")"
            G.application.afterUpgradeZombies2Delete.append(self)
    
    def unique_name(self):
        '''Returns the name for saving'''
        if self.is_root:
            return "index"
        else:
            page_name = self.title.lower().replace(" ", "_")
            page_name = re.sub(r"\W", "", page_name)
            if not page_name:
                page_name = "__"
            page_name = "%s_%s" % (page_name, self.id)
            return page_name
    
    def __unicode__(self):
        """
        Return a node as a string
        """
    
        return "Node %s" % self.title
    
    class Meta:
        app_label = "exeapp"
        order_with_respect_to = 'parent'

# ===========================================================================
