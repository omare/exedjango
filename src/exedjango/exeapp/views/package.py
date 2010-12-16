from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse
from django.core import serializers
from django.utils import simplejson

from exeapp.models import Package, User, idevice_storage, DataPackage
from exeapp.shortcuts import get_package_by_id_or_error

import logging

log = logging.getLogger(__name__)

__all__ = ['package', 'authoring', 'properties']

@login_required
@get_package_by_id_or_error
def package(request, package):
    '''Handle calls to package site. Renders exe/mainpage.html.'''
    
    if package.user.username != request.user.username:
        return HttpResponseForbidden("You don't have an access to this package")
    else:
        data_package = package.get_data_package()
        log.info("%s accesses package of %s" % (request.user.username, 
                                                package.user.username))
        prototypes = idevice_storage.get_prototypes()
        return render_to_response('exe/mainpage.html', locals())

@login_required
@get_package_by_id_or_error
def authoring(request, package):
    '''Handles calls to authoring iframe. Renders exe/authoring.html'''
    
    current_node = package.get_data_package().currentNode
    return render_to_response('exe/authoring.html', locals())

@login_required
def properties(request, package_id):
    '''Handles calls to properties iframe.'''
    
    return HttpResponse("<h1>Properties for %s</h1>" % package_id)
