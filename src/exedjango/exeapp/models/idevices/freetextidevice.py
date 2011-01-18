# ===========================================================================
# eXe 
# Copyright 2004-2006, University of Auckland
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
FreeTextIdevice: just has a block of text
"""
from django.db import models
from django.contrib.contenttypes import generic

import logging
from exeapp.models.idevices.idevice import Idevice, extern_action

#from exe.engine.field   import TextAreaField
from exeapp.views.blocks.freetextblock import FreeTextBlock
log = logging.getLogger(__name__)

# ===========================================================================

NOEXPORT, PRESENTATION, HANDOUT = "1", "2", "3"
 
def x_(arg):
    '''Placeholder for translation'''
    return arg

class FreeTextIdevice(Idevice):
    """
    FreeTextIdevice: just has a block of text
    """
    group = Idevice.Content
    block = FreeTextBlock
    title="Free Text"
    author="University of Auckland"
    purpose="""The majority of a learning resource will be 
establishing context, delivering instructions and providing general information.
This provides the framework within which the learning activities are built and 
delivered."""
    emphasis=Idevice.NoEmphasis
    
    content = models.CharField(max_length=2048, default="")
    
    def getResourcesField(self, this_resource):
        """
        implement the specific resource finding mechanism for this iDevice:
        """
        # be warned that before upgrading, this iDevice field could not exist:
        if hasattr(self, 'content') and hasattr(self.content, 'images'):
            for this_image in self.content.images:
                if hasattr(this_image, '_imageResource') \
                and this_resource == this_image._imageResource:
                    return self.content

        return None
    
    @extern_action
    def apply_changes(self, content):
        '''Saves changes and sets idevice mode to non-edit'''
        self.content = content
        self.edit = False
        
       
    def getRichTextFields(self):
        """
        Like getResourcesField(), a general helper to allow nodes to search 
        through all of their fields without having to know the specifics of each
        iDevice type.  
        """
        fields_list = []
        if hasattr(self, 'content'):
            fields_list.append(self.content)
        return fields_list

    def burstHTML(self, i):
        """
        takes a BeautifulSoup fragment (i) and bursts its contents to 
        import this idevice from a CommonCartridge export
        """
        # Free Text Idevice:
        #title = i.find(name='span', attrs={'class' : 'iDeviceTitle' })
        #idevice.title = title.renderContents().decode('utf-8')
        # no title for this iDevice.

        # FreeText is also a catch-all idevice for any other which
        # is unable to be burst on its own.
        if i.attrMap['class']=="FreeTextIdevice":
            # For a REAL FreeText, just read the inner div with class:
            inner = i.find(name='div', 
                attrs={'class' : 'block' , 'style' : 'display:block' })
        else:
            # But for all others, read the whole thing:
            inner = i

        self.content.content_wo_resourcePaths = \
                inner.renderContents().decode('utf-8')
        # and add the LOCAL resource paths back in:
        self.content.content_w_resourcePaths = \
                self.content.MassageResourceDirsIntoContent( \
                    self.content.content_wo_resourcePaths)
        self.content.content = self.content.content_w_resourcePaths
        
    def __unicode__(self):
        return "FreeTextIdevice: %s" % self._order
        
    class Meta:
        app_label = "exeapp"
   
# ===========================================================================

