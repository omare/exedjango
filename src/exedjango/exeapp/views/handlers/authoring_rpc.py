from jsonrpc import jsonrpc_method
from exeapp.shortcuts import get_package_by_id_or_error

__all__ = ['handle_action']

@jsonrpc_method('package.idevice_action', authenticated=True)
@get_package_by_id_or_error
def idevice_action(request, package, idevice_id, action, arguments={}):
    
    # have to circumvent a bug in python < 2.7
    package.get_data_package().handle_action(idevice_id, 
                                             action, arguments);
