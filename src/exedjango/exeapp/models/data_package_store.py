'''Temporary place to hold loaded persistent packages'''

class AlreadyRegistredError(Exception):
    pass

class PackageStore(dict):
        
    def __setitem__(self, id, package):
        if id in self:
            raise AlreadyRegistredError("Package with id %s is already registered" %
                                        id) 
        else:
            dict.__setitem__(self, id, package)

package_storage = PackageStore()