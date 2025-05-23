#@+leo-ver=5-thin
#@+node:ekr.20170428084207.399: * @file ../external/npyscreen/npysTree.py
import collections
import weakref
from leo.core import leoGlobals as g
assert g
#@+others
#@+node:ekr.20170428084207.401: ** class TreeData
class TreeData:
    # This is a new version of NPSTreeData that follows PEP8.
    CHILDCLASS = None
    #@+others
    #@+node:ekr.20170428084207.402: *3* TreeData.__init__
    def __init__(self,
        content=None,
        parent=None,
        selected=False,
        selectable=True,
        highlight=False,
        expanded=True,
        ignore_root=True,
        sort_function=None,
    ):
        self.set_parent(parent)
            # EKR: set self._parent to None or weakref.proxy(parent)
        self.set_content(content)
            # EKR: sets self.content.
        # EKR: other ivars.
        self.selectable = selectable
        self.selected = selected
        self.highlight = highlight
        self.expanded = expanded
        self._children = []
        self.ignore_root = ignore_root
        self.sort = False
        self.sort_function = sort_function
        self.sort_function_wrapper = True
    #@+node:ekr.20170428084207.415: *3* TreeData._get_children_list
    def _get_children_list(self):
        return self._children

    #@+node:ekr.20170428084207.418: *3* TreeData.create_wrapped_sort_function
    def create_wrapped_sort_function(self, this_function):
        def new_function(the_item):
            if the_item:
                the_real_item = the_item.get_content()
                return this_function(the_real_item)
            else:
                return the_item
        return new_function

    #@+node:ekr.20170502144851.1: *3* TreeData.getters
    #@+node:ekr.20170428084207.410: *4* TreeData.find_depth
    def find_depth(self, d=0):
        parent = self.get_parent()
        while parent:
            d += 1
            parent = parent.get_parent()
        return d
        # Recursive
        #if self._parent == None:
        #    return d
        #else:
        #    return(self._parent.findDepth(d+1))
    #@+node:ekr.20170428084207.413: *4* TreeData.get_children
    def get_children(self):
        for c in self._children:
            try:
                yield weakref.proxy(c)
            except Exception:
                yield c
    #@+node:ekr.20170428084207.414: *4* TreeData.get_children_objects
    def get_children_objects(self):
        return self._children[:]
    #@+node:ekr.20170428084207.403: *4* TreeData.get_content
    def get_content(self):
        return self.content
    #@+node:ekr.20170428084207.404: *4* TreeData.get_content_for_display
    def get_content_for_display(self):
        return str(self.content)
    #@+node:ekr.20170428084207.409: *4* TreeData.get_parent
    def get_parent(self):
        return self._parent
    #@+node:ekr.20170428084207.421: *4* TreeData.get_tree_as_list
    def get_tree_as_list(self, only_expanded=True, sort=None, key=None):
        _a = []
        for node in self.walk_tree(
            only_expanded=only_expanded,
            ignore_root=self.ignore_root,
            sort=sort,
        ):
            try:
                _a.append(weakref.proxy(node))
            except Exception:
                _a.append(node)
        # g.trace('=====', _a)
            # Over-ridden in LeoTreeData.
        return _a
    #@+node:ekr.20170428084207.412: *4* TreeData.has_children
    def has_children(self):

        return len(self._children) > 0
        # if len(self._children) > 0:
            # return True
        # else:
            # return False
    #@+node:ekr.20170502144912.1: *3* TreeData.predicates
    #@+node:ekr.20170428084207.407: *4* TreeData.is_highlighted
    def is_highlighted(self):
        return self.highlight

    #@+node:ekr.20170428084207.411: *4* TreeData.is_last_sibling
    def is_last_sibling(self):
        if self.get_parent():
            if list(self.get_parent().get_children())[-1] == self:
                return True
            else:
                return False
        else:
            return None

    #@+node:ekr.20170428084207.406: *4* TreeData.is_selected
    def is_selected(self):
        return self.selected

    #@+node:ekr.20170502144922.1: *3* TreeData.setters
    #@+node:ekr.20170428084207.416: *4* TreeData.new_child
    def new_child(self, *args, **keywords):
        if self.CHILDCLASS:
            cld = self.CHILDCLASS
        else:
            cld = type(self)
        c = cld(parent=self, *args, **keywords)
        self._children.append(c)
        return weakref.proxy(c)
    #@+node:ekr.20170428084207.417: *4* TreeData.remove_child
    def remove_child(self, child):
        new_children = []
        for ch in self._children:
            # do it this way because of weakref equality bug.
            if not ch.get_content() == child.get_content():
                new_children.append(ch)
            else:
                ch.set_parent(None)
        self._children = new_children
    #@+node:ekr.20170428084207.405: *4* TreeData.set_content
    def set_content(self, content):
        self.content = content
    #@+node:ekr.20170428084207.408: *4* TreeData.set_parent
    def set_parent(self, parent):
        if parent == None:
            self._parent = None
        else:
            self._parent = weakref.proxy(parent)
    #@+node:ekr.20170428084207.419: *3* TreeData.walk_parents
    def walk_parents(self):
        p = self.get_parent()
        while p:
            yield p
            p = p.get_parent()
    #@+node:ekr.20170428084207.420: *3* TreeData.walk_tree
    def walk_tree(self, only_expanded=True, ignore_root=True, sort=None, sort_function=None):
        #Iterate over Tree
        if sort is None:
            sort = self.sort

        if sort_function is None:
            sort_function = self.sort_function

        # example sort function # sort = True
        # example sort function # def sort_function(the_item):
        # example sort function #     import email.utils
        # example sort function #     if the_item:
        # example sort function #         if the_item.getContent():
        # example sort function #             frm = the_item.getContent().get('from')
        # example sort function #             try:
        # example sort function #                 frm = email.utils.parseaddr(frm)[0]
        # example sort function #             except Exception:
        # example sort function #                 pass
        # example sort function #             return frm
        # example sort function #     else:
        # example sort function #         return the_item
        #key = operator.methodcaller('getContent',)

        if self.sort_function_wrapper and sort_function:
            # def wrapped_sort_function(the_item):
            #     if the_item:
            #         the_real_item = the_item.getContent()
            #         return sort_function(the_real_item)
            #     else:
            #         return the_item
            # _this_sort_function = wrapped_sort_function
            _this_sort_function = self.create_wrapped_sort_function(sort_function)
        else:
            _this_sort_function = sort_function

        key = _this_sort_function
        if not ignore_root:
            yield self
        nodes_to_yield = collections.deque()  # better memory management than a list for pop(0)
        if self.expanded or not only_expanded:
            if sort:
                # This and the similar block below could be combined into a nested function
                if key:
                    nodes_to_yield.extend(sorted(self.get_children(), key=key,))
                else:
                    nodes_to_yield.extend(sorted(self.get_children()))
            else:
                nodes_to_yield.extend(self.get_children())
            while nodes_to_yield:
                child = nodes_to_yield.popleft()
                if child.expanded or not only_expanded:
                    # This and the similar block above could be combined into a nested function
                    if sort:
                        if key:
                            # must be reverse because about to use extendleft() below.
                            nodes_to_yield.extendleft(sorted(child.get_children(), key=key, reverse=True))
                        else:
                            nodes_to_yield.extendleft(sorted(child.get_children(), reverse=True))
                    else:
                        #for node in child.getChildren():
                        #    if node not in nodes_to_yield:
                        #        nodes_to_yield.appendleft(node)
                        yield_these = list(child.get_children())
                        yield_these.reverse()
                        nodes_to_yield.extendleft(yield_these)
                        del yield_these
                yield child
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@nobeautify
#@-leo
