'''Handlers for jsonRPC call from package page outline actions'''


from jsonrpc import jsonrpc_method
from exeapp.shortcuts import get_package_by_id_or_error, jsonrpc_authernticating_method

import logging

log = logging.getLogger()

__all__ = ['add_node', 'delete_current_node', 'change_current_node', 
           'rename_current_node', 'move_current_node_up']

@jsonrpc_authernticating_method('package.add_child_node')
def add_node(request, package):
    '''Handles jsonRPC request "package.add_node". Adds a new node 
to package_node_id as child of the current one and selectes it'''
    newNode = package.add_child_node()
    return {'id' : newNode.id, 'title' : newNode.title}


@jsonrpc_authernticating_method('package.delete_current_node')
def delete_current_node(request, package):
    '''Handles jsonRPC request "package.delete_current_node". Removes current
node'''
    deleted_status = package.delete_current_node()
    return {'deleted' : deleted_status}


@jsonrpc_authernticating_method('package.change_current_node')
def change_current_node(request, package, node_id):
    '''Handles jsonRPC request "package.change_current_node". Changes current
node to one with give node_id''' 
    package.set_current_node_by_id(node_id)

@jsonrpc_authernticating_method('package.rename_current_node')
def rename_current_node(request, package, new_title):
    '''Handles jsonRPC request "package.rename_current_node". Renames current
node to it's title'''
    node_title = package.rename_current_node(new_title)
    return {'title' : node_title}

@jsonrpc_authernticating_method('package.promote_current_node')
def promote_current_node(request, package):
    '''Handles jsonRPC request "package.promote_current_node". Moves current
node one step up in the hierarchie. Returns json variable promoted = 1
if successful'''
    promoted = int(package.promote_current_node())
    return {"promoted" : promoted}

@jsonrpc_authernticating_method('package.demote_current_node')
def demote_current_node(request, package):
    '''Handles jsonRPC request "package.demote_current_node". Moves current
node one step up in the hierarchie. Returns json variable demoted = 1
if successful'''
    demoted = int(package.demote_current_node())
    return {"demoted" : demoted}


@jsonrpc_authernticating_method('package.move_current_node_up')
def move_current_node_up(request, package):
    '''Handles jsonRPC request "package.move_current_node_up". Moves the 
current node up leaving it on the same level. Returns json variable moved = 1
if successful'''
    moved = package.move_current_node_up()

@jsonrpc_authernticating_method('package.move_current_node_down')

def move_current_node_down(request, package):
    '''Handles jsonRPC request "package.move_current_node_down". Moves the 
current node down leaving it on the same level. Returns json variable moved = 1
if successful'''
    moved = int(package.move_current_node_down())
    return {"moved" : moved}

