from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse
from django.core import serializers
from django.utils import simplejson

from exeapp.models import Package, User, idevice_storage, DataPackage

import logging

log = logging.getLogger(__name__)

@login_required
def package(request, package_id):
    package = get_object_or_404(Package, id=package_id)
    data_package = package.get_persist_package()
    if request.is_ajax():
        data = package_ajax_handler(request, data_package)
        return HttpResponse(simplejson.dumps(data), mimetype='application/json')
    package.save_persist()
    log.info("%s accesses package of %s" % (request.user.username, 
                                            package.user.username))
    if package.user.username != request.user.username:
        return HttpResponseForbidden("You don't have an access to this package")
    else:
        prototypes = idevice_storage.get_prototypes()
        return render_to_response('exe/mainpage.html', locals())
    
def package_ajax_handler(request, data_package):
    '''Ajax-requests are redirected to here'''
    if request.method ==  "POST":
        data = request.POST
        event = data.get('event', None)
        if event:
            params = _get_parameter_dict(data)
            try:
                callback_params = _get_func(data_package,
                    package_ajax_handlers[event])(**params)
                return callback_params
            except Exception, e:
                raise e
        return None
    return {'message' : 'seen'}

def _get_parameter_dict(data):
    params_dict = {}
    for param in data:
        if param.startswith('params'):
            params_dict[param[len('params') + 1: -1]] = data[param]
    return params_dict

def _get_func(obj, func_name):
    '''Works like getattr, but gets attributes recursive'''
    func = obj
    for part in func_name.split('.'):
        func = getattr(func, part)
    return func

package_ajax_handlers = {'addChild' : 'node_manager.handleAddChild',
                 }
    