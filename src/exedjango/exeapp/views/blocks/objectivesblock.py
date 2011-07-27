from exeapp.views.blocks.freetextblock import IdeviceForm,\
    IdeviceFormFactory
from exeapp.views.blocks.genericblock import GenericBlock
from exeapp.models.idevices.objectivesidevice import ObjectivesIdevice
from exeapp.views.blocks.widgets import FreeTextWidget
from exeapp.views.blocks.widgets import TitleWidget


class ObjectivesBlock(GenericBlock):
    """
    FreeTextBlock can render and process FreeTextIdevices as XHTML
    GenericBlock will replace it..... one day
    """
    form_factory = IdeviceFormFactory(IdeviceForm,
                                       ObjectivesIdevice,
                                       ['title', 'content'],
                                       {'title' : TitleWidget,
                                        'content' : FreeTextWidget})
