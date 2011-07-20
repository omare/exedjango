from filebrowser.fields import FileBrowseWidget
from exeapp.views.blocks.freetextblock import IdeviceForm,\
    IdeviceFormFactory
from exeapp.models.idevices.pdfidevice import PDFIdevice
from exeapp.views.blocks.genericblock import GenericBlock


class PDFBlock(GenericBlock):
    
    form_factory = IdeviceFormFactory(IdeviceForm,
                                      PDFIdevice,
                                      ['pdf_file', 'page_list'],
                                      )
    
    edit_template = "exe/idevices/pdf/edit.html"
    preview_template = "exe/idevices/pdf/preview.html"
    view_template = "exe/idevices/pdf/export.html"