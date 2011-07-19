'''
Created on Apr 18, 2011

@author: Alendit

Provides block_factory. Returns block object based on given idevice.
'''

from exeapp.models.idevices import FreeTextIdevice

from exeapp.views.blocks.freetextblock import FreeTextBlock
from exeapp.models.idevices.activityidevice import ActivityIdevice
from exeapp.views.blocks.activityblock import ActivityBlock
from exedjango.exeapp.views.blocks.glossaryblock import GlossaryBlock
from exedjango.exeapp.models.idevices.glossaryidevice import GlossaryIdevice
from exedjango.exeapp.views.blocks.readingactblock import ReadingActivityBlock
from exedjango.exeapp.models.idevices.readingactidevice import ReadingActivityIdevice

idevices = {
          FreeTextIdevice : FreeTextBlock,
          ActivityIdevice : ActivityBlock,
          GlossaryIdevice : GlossaryBlock,
          ReadingActivityIdevice : ReadingActivityBlock,
          }
    
block_factory = lambda idevice : idevices[idevice.__class__](idevice)