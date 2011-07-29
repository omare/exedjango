from tinymce.widgets import TinyMCE
from django.conf import settings
from django.utils.safestring import mark_safe
import re
from django.utils.html import escape
from django.forms.widgets import TextInput
from django.template.loader import render_to_string
from django import forms
from django.core.urlresolvers import reverse

class FreeTextWidget(TinyMCE):
    
    def __init__(self, content_language=None, attrs=None, mce_attrs=None, height=None):
        if height is not None:
            style_height = "height: %dpx;" % height
            attrs = attrs or {}
            if "style" in attrs:
                attrs['style'] += style_height
            else:
                attrs['style'] = style_height
        super(FreeTextWidget, self).__init__(content_language,
                                             attrs,
                                             mce_attrs)
    
    def render_preview(self, content):
        return mark_safe(content)
    
    def _replace_sources(self, content):
        reg_exp = r'src=".*%s.*/(.*?)"' % settings.MEDIA_URL
        return re.sub(reg_exp, r'src="\g<1>"', content)
    
    def render_export(self, content):
        return mark_safe(self._replace_sources(content))
    
class FeedbackWidget(FreeTextWidget):
    view_media = forms.Media(
            js=["%sscripts/widgets/feedback.js" % settings.STATIC_URL],
            css={"all" : ["%scss/widgets/feedback.css" % settings.STATIC_URL]},
                    )
    def render_preview(self, content):
        return render_to_string("exe/idevices/widgets/feedback.html",
                                {"content" : content})
        
    def render_export(self, content):
        return self.render_preview(self._replace_sources(content))
    
class FileSelectWidget(TextInput):
    
    #media = forms.Media(js=reverse('tinymce-filebrowser'))
    pass
        
class URLWidget(TextInput):
    def render(self, *args, **kwargs):
        html = super(URLWidget, self).render(*args, **kwargs)
        html += '<input type="submit" name="idevice_action" value="Load" />'
        return html
        