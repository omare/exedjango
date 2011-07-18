from tinymce.widgets import TinyMCE
import settings
from django.utils.safestring import mark_safe
import re
from django.utils.html import escape
from django.forms.widgets import TextInput

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
    
    def render_export(self, content):
        # replace resources
        reg_exp = r'src=".*%s.*/(.*?)"' % settings.MEDIA_URL
        result_content = re.sub(reg_exp, r'src="\g<1>"', content)
        return mark_safe(result_content)
    
    
class TitleWidget(TextInput):
    
    def render_preview(self, content):
        return ""
    
    def render_export(self, content):
        return ""