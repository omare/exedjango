from exedjango.exeapp.views.blocks.genericblock import GenericBlock
from exedjango.exeapp.views.blocks.freetextblock import IdeviceForm,\
    IdeviceFormFactory
from exedjango.exeapp.models.idevices.readingactidevice import ReadingActivityIdevice
from exedjango.exeapp.views.blocks.widgets import FreeTextWidget, TitleWidget,\
    FeedbackWidget

class ReadingActivityBlock(GenericBlock):
    form_factory = IdeviceFormFactory(IdeviceForm,
                                       ReadingActivityIdevice,
                                       ['title', 'to_read', 'activity',
                                                             'feedback'],
                                       {'to_read' : FreeTextWidget,
                                        'activity' : FreeTextWidget,
                                        'feedback' : FeedbackWidget,
                                        'title' : TitleWidget
                                        },
                                      )
