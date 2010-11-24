from exeapp.models.idevices.freetextidevice import FreeTextIdevice

class IdeviceStore(object):
    '''Simple placeholder. Will be extended with idevices'''
    
    def __init__(self):
        
        self.generic = []
        self.extended = []
        
    def get_prototypes(self):
        return self.generic + self.extended
        
idevice_storage = IdeviceStore()
idevice_storage.extended.append(FreeTextIdevice())