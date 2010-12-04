from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from jsonrpc import jsonrpc_method

from exeapp.models import Package, User
from exeapp.forms import CreatePackageForm

@login_required
def main(request):
    user = User.objects.get(username=request.user.username)
    if request.is_ajax():
        return ajax_handler(request, Package.objects, user_manager_ajax_handlers)
    package_list = Package.objects.filter(user=user)
    create_package_form = CreatePackageForm()
    
    c = RequestContext(request, locals())
    return render_to_response('main.html', context_instance=c)

def create_package(request):
    if request.method == 'POST':
        form = CreatePackageForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username=request.user.username)
            cd = form.cleaned_data
            Package.objects.create(title=cd['package_title'], user=user)
    return redirect('/exeapp/main/')

@jsonrpc_method('main.create_package', authenticated=True)
def create(request, package_name):
    user = User.objects.get(username=request.user.username)
    p = Package.objects.create(title=package_name, user=user)
    return {'id' : p.id, 'title' : p.title}

