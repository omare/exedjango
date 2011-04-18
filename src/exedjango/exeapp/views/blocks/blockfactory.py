'''
Created on Apr 18, 2011

@author: Alendit

Provides block_factory. Returns block object based on given idevice.
'''

from exeapp.models.idevices import FreeTextIdevice

from exeapp.views.blocks.freetextblock import FreeTextBlock

blocks = {
          FreeTextIdevice : FreeTextBlock
          }
    
block_factory = lambda idevice : blocks[idevice.__class__]