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
    if package.user.username != request.user.username:
        return HttpResponseForbidden("You don't have an access to this package")
    else:
        data_package = package.get_data_package()
        if request.is_ajax():
            return ajax_handler(request, data_package, package_ajax_handlers)
        # temporary - saving package on each call
        package.save_persist()
        log.info("%s accesses package of %s" % (request.user.username, 
                                                package.user.username))
        prototypes = idevice_storage.get_prototypes()
        return render_to_response('exe/mainpage.html', locals())

@login_required
def authoring(request, package_id):
    return HttpResponse("<h1>Authoring for %s</h1>" % package_id)

@login_required
def properties(request, package_id):
    return HttpResponse("<h1>Properties for %s</h1>" % package_id)
