# ===========================================================================
# eXe 
# Copyright 2004-2006, University of Auckland
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# ===========================================================================
from exedjango.exeapp.views.blocks.freetextblock import IdeviceForm,\
    IdeviceFormFactory
from exedjango.exeapp.views.blocks.widgets import TitleWidget, FreeTextWidget
from exedjango.exeapp.models.idevices.glossaryidevice import GlossaryIdevice,\
    GlossaryTerm
from exedjango.exeapp.views.blocks.block import Block
from django.forms.models import modelformset_factory
from django.template.loader import render_to_string
from django import forms
"""
ExternalUrlBlock can render and process ExternalUrlIdevices as XHTML
"""



# ===========================================================================
class GlossaryTermForm(forms.ModelForm):
    pass
    
    class Meta:
        model = GlossaryTerm
        fields = ['title', 'definition']
        widgets = {'title' : TitleWidget,
                   'definition' : FreeTextWidget,
                   }
        
class GlossaryBlock(Block):
    form_factory = IdeviceFormFactory(IdeviceForm,
                                      GlossaryIdevice,
                                      ['title'],
                                      {'title' : TitleWidget},
                                      )
    formset_factory = modelformset_factory(GlossaryTerm, GlossaryTermForm,
                                            fields=("title", "definition"),
                                            extra=0,
                                            can_delete=True,
                                            )
    
    edit_template = "exe/idevices/glossary/edit.html"
    preview_template = "exe/idevices/glossary/preview.html"
    view_template = "exe/idevices/glossary/export.html"
    
    def process(self, action, data):
        if action == "Add Term":
            super(GlossaryBlock, self).process("apply_changes", data)
            self.idevice.edit = True
            self.idevice.add_term()
        elif action == "Delete Selected":
            super(GlossaryBlock, self).process("apply_changes", data)
            self.idevice.edit = True
        else:
            super(GlossaryBlock, self).process(action, data)
    
    
    def renderEdit(self):
        form = self.form_factory(instance=self.idevice, auto_id=True)
        formset = self. formset_factory(queryset=GlossaryTerm.objects.\
                                    filter(idevice=self.idevice))
        return render_to_string(self.edit_template, locals())
    
    def renderPreview(self):
        ordered_terms = self.idevice.terms.order_by('title')
        return render_to_string(self.preview_template, 
                                {"idevice" : self.idevice,
                                 "ordered_terms" : ordered_terms,
                                 "self" : self,
                                 }
                                )
    
    def renderView(self):
        ordered_terms = self.idevice.terms.order_by('title')
        return render_to_string(self.view_template,
                                 {"idevice" : self.idevice,
                                  "ordered_terms" : ordered_terms,
                                  }
                                )
    
        
    
# ==========================================================================