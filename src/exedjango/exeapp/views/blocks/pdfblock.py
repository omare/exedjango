from filebrowser.fields import FileBrowseWidget
from exeapp.views.blocks.ideviceform import IdeviceForm,\
    IdeviceFormFactory
from exeapp.views.blocks.genericblock import GenericBlock


class PDFBlock(GenericBlock):
    
    edit_template = "exe/idevices/pdf/edit.html"
    preview_template = "exe/idevices/pdf/preview.html"
    view_template = "exe/idevices/pdf/export.html"