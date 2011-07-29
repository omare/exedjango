'''
Created on Apr 18, 2011

@author: Alendit

Provides block_factory. Returns block object based on given idevice.
'''


from exedjango.exeapp.views.blocks.genericblock import GenericBlock
from exeapp.models.idevices import FreeTextIdevice
from exeapp.models.idevices.activityidevice import ActivityIdevice
from exeapp.views.blocks.glossaryblock import GlossaryBlock
from exeapp.models.idevices.glossaryidevice import GlossaryIdevice
from exeapp.models.idevices.pdfidevice import PDFIdevice
from exeapp.views.blocks.pdfblock import PDFBlock
from exeapp.models.idevices.readingactidevice import ReadingActivityIdevice
from exeapp.models.idevices.reflectionidevice import ReflectionIdevice
from exeapp.models.idevices.tocidevice import TOCIdevice
from exeapp.models.idevices.wikiidevice import WikipediaIdevice
from exeapp.views.blocks.wikiblock import WikipediaBlock
from exeapp.models.idevices.objectivesidevice import ObjectivesIdevice
from exeapp.models import PreknowledgeIdevice
from exeapp.models import CommentIdevice
from exeapp.views.blocks.commentblock import CommentBlock
from exeapp.models import FeedbackIdevice
from exeapp.views.blocks.feedbackblock import FeedbackBlock
from exeapp.models import RSSIdevice
from exeapp.views.blocks.rssblock import RSSBlock

idevice_map = {
          FreeTextIdevice : GenericBlock,
          ActivityIdevice : GenericBlock,
          GlossaryIdevice : GlossaryBlock,
          ReadingActivityIdevice : GenericBlock,
          ReflectionIdevice : GenericBlock,
          TOCIdevice : GenericBlock,
          WikipediaIdevice : WikipediaBlock,
          PDFIdevice : PDFBlock,
          ObjectivesIdevice : GenericBlock,
          PreknowledgeIdevice : GenericBlock,
          CommentIdevice : CommentBlock,
          FeedbackIdevice : FeedbackBlock,
          RSSIdevice : RSSBlock,
          }

block_map = dict((v, k) for k, v in idevice_map.items())

    
block_factory = lambda idevice : idevice_map[idevice.__class__](idevice)
def idevice_class_factory(block):
    if isinstance(block, type):
        return block_map[block]
    else:
        return block_map[block.__class__]
    
