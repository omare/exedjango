from exeapp.views.blocks.freetextblock import IdeviceForm,\
    IdeviceFormFactory
from exeapp.views.blocks.genericblock import GenericBlock
from exeapp.models.idevices.wikiidevice import WikipediaIdevice
from exeapp.views.blocks.widgets import FreeTextWidget


class WikipediaBlock(GenericBlock):
    """
    FreeTextBlock can render and process FreeTextIdevices as XHTML
    GenericBlock will replace it..... one day
    """
    form_factory = IdeviceFormFactory(IdeviceForm,
                                       WikipediaIdevice,
                                       ['title', 'article_name', 'content'],
                                       {'content' : FreeTextWidget},
                                       )
    edit_template = "exe/idevices/wikipedia/edit.html"
    preview_template = "exe/idevices/freetext/preview.html"
    view_template = "exe/idevices/freetext/export.html"
    
    def process(self, action, data):
        if action == "Load Article":
            self.idevice.load_article(data['article_name'])
            self.idevice.save()
        else:
            super(WikipediaBlock, self).process(action, data)
    