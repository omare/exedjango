from django.db import models
from filebrowser.fields import FileBrowseField
from exeapp.models.idevices.idevice import Idevice

class PDFIdevice(Idevice):
    

    name = "Pdf iDevice"
    title = name #models.CharField(max_length=100, default=name)
    author = "TU Munich"
    purpose = '''Import local pdf and display them.
    Requires Acrobat Reader plugin.'''
    #pdf_file = models.CharField(max_length=100, blank=True, default="")
    pdf_file = FileBrowseField("PDF", max_length=100,
                               directory="pdf/", extensions=['.pdf'],
                               blank=True, null=True)
    
    #height = models.PositiveIntegerField()
    page_list = models.CharField(max_length=50, blank=True, default="",
                        help_text="Input coma-separated pages or page ranges to import. For example: 1,2,3-8. Leave empty to import all pages")
    group = Idevice.Content
    emphasis = Idevice.NoEmphasis
    
    def _resources(self):
        user = self.parent_node.package.user.username
        return set([self.pdf_file.path_relative_directory.replace("%s/" % user,
                                                                 "")])
    
    class Meta:
        app_label = "exeapp"
