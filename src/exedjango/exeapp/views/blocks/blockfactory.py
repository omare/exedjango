'''
Created on Apr 18, 2011

@author: Alendit

Provides block_factory. Returns block object based on given idevice.
'''

from exeapp.models.idevices import FreeTextIdevice

from exeapp.views.blocks.freetextblock import FreeTextBlock
from exeapp.models.idevices.activityidevice import ActivityIdevice
from exeapp.views.blocks.activityblock import ActivityBlock

idevices = {
          FreeTextIdevice : FreeTextBlock,
          ActivityIdevice : ActivityBlock,
          }
    
block_factory = lambda idevice : idevices[idevice.__class__](idevice)