'''Handlers for jsonRPC call from package page'''

import sys, traceback

from jsonrpc import jsonrpc_method
from exeapp.shortcuts import get_package_by_id_or_error

import logging

log = logging.getLogger()

__all__ = ['add_node', 'delete_current_node', 'change_current_node']

@jsonrpc_method('package.add_node', authenticated=True)
@get_package_by_id_or_error
def add_node(request, package, parent_node_id):
    '''Handles jsonRPC request "package.add_node". Adds a new node 
to package_node_id'''
    newNode = package.get_data_package().add_child_node(str(parent_node_id))
    return {'id' : newNode.id, 'title' : newNode.title}


@jsonrpc_method('package.delete_current_node', authenticated=True)
@get_package_by_id_or_error
def delete_current_node(request, package):
    '''Handles jsonRPC request "package.delete_current_node". Removes current
node'''
    deleted_status = package.get_data_package().delete_current_node()
    return {'deleted' : deleted_status}


@jsonrpc_method('package.change_current_node', authenticated=True)
@get_package_by_id_or_error
def change_current_node(request, package, node_id):
    '''Handles jsonRPC request "package.change_current_node". Changes current node to
one with give node_id''' 
    node_changed = package.get_data_package().set_current_node_by_id(node_id)
    return {'changed' : node_changed}