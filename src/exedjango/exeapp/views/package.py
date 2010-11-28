from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from exeapp.models import Package, User, idevice_storage

import logging

log = logging.getLogger(__name__)

@login_required
def package(request, package_id):
    package = get_object_or_404(Package, id=package_id)
    persist_package = package.get_persist_package()
    package.save_persist()
    log.info("%s accesses package of %s" % (request.user.username, 
                                            package.user.username))
    if package.user.username != request.user.username:
        return HttpResponseForbidden("You don't have an access to this package")
    else:
        prototypes = idevice_storage.get_prototypes()
        return render_to_response('exe/mainpage.html', locals())