from django.template.loader import render_to_string

def _create_children_list(node, template=None, current_node=None,
                           current_node_template=None):
        """Creates a list of all children from the root recursively.
Root node has to be appended manually in a higher level function. List items will
be rendered using given template. If node is the same as current_node, 
current_node_template will be used"""
        children_list = []
        
        if node.children:
            for child in node.children:
                if current_node != None and child == current_node:
                    used_template = current_node_template
                else:
                    used_template = template
                if used_template is not None:
                    node_item = render_to_string(used_template, {"node" : child})
                else:
                    node_item = child.title
                children_list.append(node_item)
                if child.children:
                    children_list.append(_create_children_list(child,
                            template, current_node, current_node_template))
        return children_list