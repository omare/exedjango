from exedjango.exeapp.views.blocks.genericblock import GenericBlock
from exedjango.exeapp.views.blocks.freetextblock import IdeviceForm,\
    IdeviceFormFactory
from exedjango.exeapp.models.idevices.reflectionidevice import ReflectionIdevice
from exedjango.exeapp.views.blocks.widgets import FreeTextWidget, TitleWidget,\
    FeedbackWidget

class ReflectionBlock(GenericBlock):
    form_factory = IdeviceFormFactory(IdeviceForm,
                                       ReflectionIdevice,
                                       ['title', 'activity', 'answer'],
                                       {'activity' : FreeTextWidget,
                                        'answer' : FeedbackWidget,
                                        'title' : TitleWidget
                                        },
                                      )
