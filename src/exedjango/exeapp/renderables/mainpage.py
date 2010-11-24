from django.template import Context, Template
from django.template.loader import get_template

from exeapp.renderables.renderable import Renderable
from exeapp.renderables.outlinepane import OutlinePane
from exeapp.renderables.idevicepane import IdevicePane
from exedjango.utils.shortcuts import render_to_unicode

class MainPage(Renderable):
    
    def render(self):
        outline_pane = OutlinePane(self)
        idevice_pane = IdevicePane(self)
        return render_to_unicode('exe/mainpage.html', locals())