from exeapp.models.idevices.freetextidevice import FreeTextIdevice

class IdeviceStore(object):
    '''Simple placeholder. Will be extended with idevices'''
    
    def __init__(self):
        
        self.idevices = {}
    
    def add_idevice(self, idevice):
        self.idevices[idevice.__name__] = idevice
        
    def get_prototypes(self):
        return self.idevices.values()
    
    
    
    def get_idevice(self, idevice_type):
        # TODO Fix the whole thing with id's and prototypes. Should contain
        # classes only
        return self.idevices[idevice_type]
        
idevice_storage = IdeviceStore()
idevice_storage.add_idevice(FreeTextIdevice)