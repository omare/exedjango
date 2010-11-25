from django.template import Context, Template
from django.template.loader import get_template, render_to_string


from exeapp.renderables.renderable import Renderable
from exeapp.renderables.outlinepane import OutlinePane
from exeapp.renderables.idevicepane import IdevicePane

class MainPage(Renderable):
    
    def render(self):
        outline_pane = OutlinePane(self)
        idevice_pane = IdevicePane(self)
        return render_to_string('exe/mainpage.html', locals())