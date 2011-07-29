from filebrowser.fields import FileBrowseWidget
from exeapp.views.blocks.ideviceform import IdeviceForm,\
    IdeviceFormFactory
from exeapp.views.blocks.genericblock import GenericBlock


class PDFBlock(GenericBlock):
    
    use_common_content = True
    content_template = "exe/idevices/pdf/content.html"