from exeapp.shortcuts import jsonrpc_helper

__all__ = ['idevice_action']

@jsonrpc_helper('package.idevice_action')
def idevice_action(request, package, idevice_id, action, arguments={}):
    
    # have to circumvent a bug in python < 2.7
    # TODO replace it with normal form request
    class Request(object):
        POST = {}
        
        def __init__(self, POST):
            self.POST = POST
    package.handle_action(idevice_id, 
                                             action, Request(arguments));
