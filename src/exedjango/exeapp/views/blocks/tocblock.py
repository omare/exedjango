from exedjango.exeapp.views.blocks.freetextblock import IdeviceForm,\
    IdeviceFormFactory
from exedjango.exeapp.views.blocks.genericblock import GenericBlock
from exedjango.exeapp.models.idevices.tocidevice import TOCIdevice
from exedjango.exeapp.views.blocks.widgets import FreeTextWidget


class TOCBlock(GenericBlock):
    """
    FreeTextBlock can render and process FreeTextIdevices as XHTML
    GenericBlock will replace it..... one day
    """
    form_factory = IdeviceFormFactory(IdeviceForm,
                                       TOCIdevice,
                                       ['content'],
                                       {'content' : FreeTextWidget})
