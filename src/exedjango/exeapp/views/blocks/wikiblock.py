from exeapp.views.blocks.ideviceform import IdeviceForm,\
    IdeviceFormFactory
from exeapp.views.blocks.genericblock import GenericBlock
from exeapp.models.idevices.wikiidevice import WikipediaIdevice
from exeapp.views.blocks.widgets import FreeTextWidget


class WikipediaBlock(GenericBlock):
    
    def process(self, action, data):
        if action == "Load":
            self.idevice.load_article(data['article_name'])
            self.idevice.save()
            return self.render()
        else:
            return super(WikipediaBlock, self).process(action, data)
    