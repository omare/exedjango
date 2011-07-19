from exeapp.views.blocks.genericblock import GenericBlock
from exeapp.views.blocks.freetextblock import IdeviceForm, IdeviceFormFactory
from exeapp.models.idevices.activityidevice import ActivityIdevice
from exeapp.views.blocks.widgets import FreeTextWidget, TitleWidget
class ActivityBlock(GenericBlock):
    form_factory = IdeviceFormFactory(IdeviceForm,
                                       ActivityIdevice,
                                       ['title', 'content'],
                                       {'content' : FreeTextWidget,
                                        'title' : TitleWidget
                                        },
                                      )
    edit_template = "exe/idevices/freetext/edit.html"
    preview_template = "exe/idevices/freetext/preview.html"
    view_template = "exe/idevices/freetext/export.html"
