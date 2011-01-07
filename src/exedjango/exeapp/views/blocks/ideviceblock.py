class IdeviceBlock(object):
    '''Basic class for  all idevices'''
    
    def __init__(self, idevice):
        self.idevice = idevice
        
    def render_view(self):
        return 'View'
    
    def render_preview(self):
        return 'Preview'

    def render_edit(self):
        return 'Edit'