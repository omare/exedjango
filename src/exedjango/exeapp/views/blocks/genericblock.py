from django.template.loader import render_to_string
from django.template.base import TemplateDoesNotExist
from exeapp.views.blocks.block import Block


class TemplateNotDefined(BaseException):
    pass


class GenericBlock(Block):
    """
    Generic class for blocks. Uses the idevice form and templates to render
    the idevice
    """
    edit_template = ""
    preview_template = ""
    view_template = ""
    
    def __init__(self, idevice):
        super(GenericBlock, self).__init__(idevice)
        
        if not hasattr(self.idevice,'undo'): 
            self.idevice.undo = True

    def renderEdit(self):
        """
        Returns an XHTML string with the form element for editing this block
        """
        return self._render_view(self.edit_template)

    def renderPreview(self):
        """
        Returns an XHTML string for previewing this block
        """
        return self._render_view(self.preview_template)

    def renderView(self):
        """
        Returns an XHTML string for viewing this block
        """
        return self._render_view(self.view_template)
        
    def _render_view(self, template):
        """
        Code reuse function for rendering the correct template
        """
        idevice = self.idevice
        form = self.form_factory(instance=self.idevice, auto_id="%s_field_" \
                                 % self.idevice.id + "%s")
        try:
            html = render_to_string(template, {"idevice" : idevice,
                                               "form" : form,
                                               "self" : self},)
        except TemplateDoesNotExist, e:
            if template:
                raise e
            else:
                raise TemplateNotDefined(
                        "Please define a template for the action")
        else:
            return html