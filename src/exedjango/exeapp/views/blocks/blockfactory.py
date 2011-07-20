'''
Created on Apr 18, 2011

@author: Alendit

Provides block_factory. Returns block object based on given idevice.
'''


from exeapp.models.idevices import FreeTextIdevice
from exeapp.views.blocks.freetextblock import FreeTextBlock
from exeapp.models.idevices.activityidevice import ActivityIdevice
from exeapp.views.blocks.activityblock import ActivityBlock
from exeapp.views.blocks.glossaryblock import GlossaryBlock
from exeapp.models.idevices.glossaryidevice import GlossaryIdevice
from exeapp.models.idevices.pdfidevice import PDFIdevice
from exeapp.views.blocks.pdfblock import PDFBlock
from exeapp.views.blocks.readingactblock import ReadingActivityBlock
from exeapp.models.idevices.readingactidevice import ReadingActivityIdevice
from exeapp.models.idevices.reflectionidevice import ReflectionIdevice
from exeapp.views.blocks.reflectionblock import ReflectionBlock
from exeapp.models.idevices.tocidevice import TOCIdevice
from exeapp.views.blocks.tocblock import TOCBlock
from exeapp.models.idevices.wikiidevice import WikipediaIdevice
from exeapp.views.blocks.wikiblock import WikipediaBlock

idevices = {
          FreeTextIdevice : FreeTextBlock,
          ActivityIdevice : ActivityBlock,
          GlossaryIdevice : GlossaryBlock,
          ReadingActivityIdevice : ReadingActivityBlock,
          ReflectionIdevice : ReflectionBlock,
          TOCIdevice : TOCBlock,
          WikipediaIdevice : WikipediaBlock,
          PDFIdevice : PDFBlock,
          }
    
block_factory = lambda idevice : idevices[idevice.__class__](idevice)