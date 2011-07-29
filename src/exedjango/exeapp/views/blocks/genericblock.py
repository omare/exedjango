from django.template.loader import render_to_string
from django.template.base import TemplateDoesNotExist
from exeapp.views.blocks.block import Block
from exedjango.exeapp.views.blocks.ideviceform import IdeviceFormFactory


class TemplateNotDefined(BaseException):
    pass


class GenericBlock(Block):
    """
    Generic class for blocks. Uses the idevice form and templates to render
    the idevice
    """
    edit_template = "exe/idevices/generic/edit.html"
    preview_template = "exe/idevices/generic/preview.html"
    view_template = "exe/idevices/generic/export.html"
    
    # Use these templates if the export and preview version of
    # an iDevice has the same content 
    use_common_content = False
    COMMON_PREVIEW = "exe/idevices/generic/common/preview.html"
    COMMON_EXPORT = "exe/idevices/generic/common/preview.html"
    content_template = ""
    
    
    def __init__(self, idevice, fields=()):
        super(GenericBlock, self).__init__(idevice)
        self.form_factory = IdeviceFormFactory(model=self.idevice.__class__,
                                                fields=fields)
        
        if not hasattr(self.idevice,'undo'): 
            self.idevice.undo = True

    def renderEdit(self, form=None):
        """
        Returns an XHTML string with the form element for editing this block
        """
        return self._render_view(self.edit_template, form=form)

    def renderPreview(self):
        """
        Returns an XHTML string for previewing this block
        """
        template = self.COMMON_PREVIEW if self.use_common_content else\
                    self.preview_template
        return self._render_view(template)

    def renderView(self):
        """
        Returns an XHTML string for viewing this block
        """
        template = self.COMMON_EXPORT if self.use_common_content else\
                    self.view_template
        return self._render_view(template)
        
    def _render_view(self, template, form=None):
        """
        Code reuse function for rendering the correct template
        """
        idevice = self.idevice
        form = form or self.form_factory(instance=self.idevice,
                             auto_id="%s_field_" % self.idevice.id + "%s")
        try:
            html = render_to_string(template, {"idevice" : idevice,
                                               "form" : form,
                                               "content" : self.content_template,
                                               "self" : self,
                                               }
                                    )
        except TemplateDoesNotExist, e:
            if template:
                raise e
            else:
                raise TemplateNotDefined(
                        "Please define a template for the action")
        else:
            return html