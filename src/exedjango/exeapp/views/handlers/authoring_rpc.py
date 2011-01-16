from jsonrpc import jsonrpc_method
from exeapp.shortcuts import get_package_by_id_or_error

__all__ = ['handle_action']

@jsonrpc_method('authoring.idevice_action', authenticated=True)
@get_package_by_id_or_error
def idevice_action(request, package, idevice_id, action, arguments={}):
    
    # have to circumvent a bug in python < 2.7
    new_args = {}
    for k,v in arguments.items():
        new_args[str(k)] = v
    
    package.get_data_package().handle_action(idevice_id, 
                                             action, **new_args);
    return {'success' : True}