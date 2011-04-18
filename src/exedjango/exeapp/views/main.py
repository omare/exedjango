'''Main view for a user. Handles both GET/POST request and rpc calls'''

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from jsonrpc import jsonrpc_method

from exeapp.models import Package, User
from exeapp.shortcuts import get_package_by_id_or_error

@login_required
def main(request):
    '''Serve the main page with a list of packages.
    TODO: Use a generic view'''
    user = User.objects.get(username=request.user.username)
    package_list = Package.objects.filter(user=user)
    
    return render_to_response('main.html', locals())

@jsonrpc_method('main.create_package', authenticated=True)
def create_package(request, package_name):
    user = User.objects.get(username=request.user.username)
    p = Package.objects.create(title=package_name, user=user)
    return {'id' : p.id, 'title' : p.title}

@jsonrpc_method('main.delete_package', authenticated=True)
@get_package_by_id_or_error
def delete_package(request, package):
    '''Removes a package'''
    
    package_id = package.id
    package.delete()
    return {"package_id" : package_id}

