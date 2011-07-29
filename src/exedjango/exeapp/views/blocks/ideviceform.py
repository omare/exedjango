from django import forms
from django.utils.safestring import mark_safe
from django.forms.widgets import Media

class IdeviceForm(forms.ModelForm):
    
    def render_edit(self):
        return self.as_p()
    
    def render_preview(self):
        return self._render_view("preview")
    
    def render_export(self):
        return self._render_view("export")
    
    def _render_view(self, purpose):
        '''Decouples field rendering from the purpose'''
        html = ""
        renderer_name = "render_%s" % purpose
        for name, field_object in self.fields.items():
            if hasattr(field_object.widget, renderer_name):
                renderer = getattr(field_object.widget, renderer_name)
                html += renderer(self.initial[name])
            else:
                # dumb widget, shouldn't be exported
                html += ""
        return mark_safe(html) 
        
    
    @property
    def view_media(self):
        media = Media()
        for field in self.fields.values():
            if hasattr(field.widget, "view_media"):
                    media += field.widget.view_media
        return media
    
class IdeviceFormFactory(object):
    def __init__(self, model, fields, form_class=IdeviceForm, widgets={}):
        
        self.model = model
        self.fields = fields
        self.widgets = widgets
        self.form = form_class
        
    def __call__(self, *args, **kwargs):
        class NewIdeviceForm(self.form):
            pass
            
            class Meta:
                model = self.model
                if self.fields:
                    fields = self.fields
                exclude = ("parent_node", "edit")
                widgets = self.widgets
                
        return NewIdeviceForm(*args, **kwargs)