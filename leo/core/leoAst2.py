# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20211220172611.1: * @file leoAst2.py
#@@first

import ast
from collections import defaultdict
import leo.core.leoGlobals as g
# Global data.
ctx_nodes = (ast.Load, ast.Store, ast.Del)
# Keys are ast.node names; values are lists of field names.
fields_dict = defaultdict(list)
# Keys are ast.node names; values are field names in token order.
order_dict = {} ### make_order_dict()
#@+others
#@+node:ekr.20211220172707.1: ** function: make_links
def make_links(path):
    with open(path, 'r') as f:
        contents = f.read()
    root = ast.parse(contents)
    node_list = [ (None, root) ]
    n = 0
    while node_list:
        n += 1
        parent, child = node_list.pop()
        child.parent = parent
        if parent:
            if not hasattr(parent, 'children'):
                parent.children = []
            parent.children.append(child)
        if 1:  # Temporay.
            fields = node_fields(child)
            update_fields_dict(child, fields)  
        for grand_child in node_children(child):
            node_list.append((child, grand_child))
    return n
#@+node:ekr.20211220172727.1: ** function: node_children
def node_children(node):
    if not node._fields:
        return []
    result = []
    for s in order_dict.get(node._fields, node._fields):
        val = getattr(node, s, None)
        if isinstance(val, list):
            result.extend(val)
        if isinstance(val, ctx_nodes):
            pass
        elif isinstance(val, ast.AST):
            result.append(val)
    return result
#@+node:ekr.20211220175029.1: ** function: node_fields
def node_fields(node):
    """Return the fields of the given ast node in token order."""
    if not node._fields:
        return []
    fields = []
    for s in node._fields:
        val = getattr(node, s, None)
        if isinstance(val, ctx_nodes):
            pass
        elif isinstance(val, (list, ast.AST)):
            fields.append(s)
    return fields
#@+node:ekr.20211220173421.1: ** function: print_fields_dict
def print_fields_dict():
    d = fields_dict
    g.trace('=====')
    if 1:
        # Suitable for make_order_dict
        for key in sorted(d):
            aList = list(d.get(key))
            if len(aList) == 1:
                if aList[0]:
                    fields_s = ', '.join(repr(z) for z in aList[0])
                    list_s = f"({fields_s}),"
                else:
                    list_s = '(),'
                print(f"'{key}': {list_s}")
            else:
                print(f"'{key}': (")
                for item in aList:
                    fields_s = ', '.join(f"{z!r}" for z in item)
                    list_s = f"({fields_s}),"
                    print(f"    {list_s}")
                print('),')
    else:
        for key in sorted(d):
            val = list(d.get(key))
            print(f"{key:>15}: {', '.join(z for z in val[0])!r}")
            if len(val) > 1:
                for item in val[1:]:
                    print(f"{' ':15}  {', '.join(z for z in item)!r}")
        
#@+node:ekr.20211221062418.1: ** function: token_order_children
# Keys are node.__class__.__name__. Values are functions
dispatch_dict = {}

def token_order_children(node):
    """
    Return the children of the node in token order.
    
    The default is node_fields(node), but many nodes will return
    "interleavings" of fields, akin to zip(field1, field2)
    
    Whether this can actually be done is an open question.
    """
    return dispatch_dict(node.__class__.__name__, node_fields(node))
#@+node:ekr.20211220174514.1: ** function: update_fields_dict
def update_fields_dict(node, fields):
    name = node.__class__.__name__
    if name not in fields_dict:
        fields_dict [name] = set()
    fields_dict [name].add(tuple(fields))
#@-others
#@@language python
#@-leo
