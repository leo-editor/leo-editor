#!/usr/bin/python
'''The MLTreeEditable class.'''
# By Edward K. Ream

# pylint: disable=logging-not-lazy

import curses
import logging
import npyscreen
import weakref
def print_list(aList, tag=None, sort=False, indent=''):
    
    if aList:
        bList = list(sorted(aList)) if sort else aList
        logging.info('%s...[' % (tag) if tag else '[')
        for e in bList:
            logging.info('%s%s' % (indent, repr(e).strip()))
        logging.info(']')
    else:
        logging.info(tag + '...[]' if tag else '[]')
class TreeDataEditable(npyscreen.TreeData):
    '''A TreeData class that has a len and new_first_child methods.'''

    def __len__(self):
        return len(self.content)
        
    def new_child_at(self, index, *args, **keywords):
        '''Same as TreeData.new_child, with insert(index, c) instead of append(c)'''
        if self.CHILDCLASS:
            cld = self.CHILDCLASS
        else:
            cld = type(self)
        c = cld(parent=self, *args, **keywords)
        self._children.insert(index, c)
        return weakref.proxy(c)
class TreeLineEditable(npyscreen.TreeLine):
    '''A editable TreeLine class.'''

    def __init__(self, *args, **kwargs):

        super(TreeLineEditable, self).__init__(*args, **kwargs)
        self.set_handlers()

    def edit(self):
        """Allow the user to edit the widget: ie. start handling keypresses."""
        self.editing = True
        # self._pre_edit()
        self.highlight = True
        self.how_exited = False
        # self._edit_loop()
        old_parent_editing = self.parent.editing
        self.parent.editing = True
        while self.editing and self.parent.editing:
            self.display()
            self.get_and_use_key_press()
                # A base TreeLine method.
        self.parent.editing = old_parent_editing
        self.editing = False
        self.how_exited = True
        # return self._post_edit()
        self.highlight = False
        self.update()
    def h_cursor_beginning(self, ch):

        self.cursor_position = 0
    def h_cursor_end(self, ch):
        
        # self.value is a TreeDataEditable.
        self.cursor_position = max(0, len(self.value.content)-1)
    def h_cursor_left(self, input):
        
        self.cursor_position = max(0, self.cursor_position -1)
    def h_cursor_right(self, input):

        self.cursor_position += 1

    def h_delete_left(self, input):

        # self.value is a TreeDataEditable.
        n = self.cursor_position
        s = self.value.content
        if 0 <= n <= len(s):
            self.value.content = s[:n] + s[n+1:]
            self.cursor_position -= 1
    def h_end_editing(self, ch):

        # logging.info('TreeLineEditable: %s' % ch)
        self.editing = False
        self.how_exited = None
    def h_insert(self, i):

        # self.value is a TreeDataEditable.
        n = self.cursor_position + 1
        s = self.value.content
        self.value.content = s[:n] + chr(i) + s[n:]
        self.cursor_position += 1
    def set_handlers(self):
        
        # pylint: disable=no-member
        # Override *all* other complex handlers.
        if 1:
            self.complex_handlers = (
                (curses.ascii.isprint, self.h_insert),
            )
        else:
            self.complex_handlers.append(
                (curses.ascii.isprint, self.h_insert),
            )
        self.handlers.update({
            curses.ascii.ESC:       self.h_end_editing,
            curses.ascii.NL:        self.h_end_editing,
            curses.ascii.LF:        self.h_end_editing,
            curses.KEY_HOME:        self.h_cursor_beginning,  # 262
            curses.KEY_END:         self.h_cursor_end,        # 358.
            curses.KEY_LEFT:        self.h_cursor_left,
            curses.KEY_RIGHT:       self.h_cursor_right,
            curses.ascii.BS:        self.h_delete_left,
            curses.KEY_BACKSPACE:   self.h_delete_left,
        })
class MLTreeLine (npyscreen.MLTree):

    # pylint: disable=used-before-assignment
    _contained_widgets = TreeLineEditable
        
    def set_up_handlers(self):
        super(MLTreeLine, self).set_up_handlers()
        assert not hasattr(self, 'hidden_root_node'), repr(self)
        ### self.leo_c = None # Set later.
        self.hidden_root_node = None
        self.set_handlers()

    def dump_values(self):
        
        def info(z):
            return '%15s: %s' % (z._parent.get_content(), z.get_content())

        print_list([info(z) for z in self.values])
        
    def dump_widgets(self):
        
        def info(z):
            return '%s.%s' % (id(z), z.__class__.__name__)

        print_list([info(z) for z in self._my_widgets])
    def delete_line(self):

        trace = True
        if trace:
            logging.info('cursor_line: %r' % self.cursor_line)
            self.dump_values()
        if self.values:
            del self.values[self.cursor_line]
            self.display()
    def edit_headline(self):

        trace = True
        if not self.values:
            if trace: logging.info('no values')
            self.insert_line()
            return False
        try:
            active_line = self._my_widgets[(self.cursor_line-self.start_display_at)]
            if trace: logging.info('MLTreeEditable.active_line: %r' % active_line)
        except IndexError:
            # pylint: disable=pointless-statement
            self._my_widgets[0]
                # Does this have something to do with weakrefs?
            self.cursor_line = 0
            self.insert_line()
            return True
        active_line.highlight = False
        active_line.edit()
        try:
            self.values[self.cursor_line] = active_line.value
        except IndexError:
            self.values.append(active_line.value)
            if not self.cursor_line:
                self.cursor_line = 0
            self.cursor_line = len(self.values) - 1
        self.reset_display_cache()
        self.display()
        return True
    def new_node(self):
        '''
        Insert a new outline TreeData widget at the current line.
        As with Leo, insert as the first child of the current line if
        the current line is expanded. Otherwise insert after the current line.
        '''
        trace = True
        trace_values = False
        node = self.values[self.cursor_line]
        if trace:
            logging.info('LeoMLTree: %r' % node)
            if trace_values:
                self.dump_values()
        headline = 'New headline'
        if node.has_children() and node.expanded:
            node = node.new_child_at(index=0, content=headline)
        elif node.get_parent():
            parent = node.get_parent()
            node = parent.new_child(content=headline)
        else:
            parent = self.hidden_root_node
            index = parent._children.index(node)
            node = parent.new_child_at(index=index, content=headline)
        if trace:
            logging.info('LeoMLTree: line: %3s %s' % (self.cursor_line, headline))
        return node
    def insert_line(self):
        
        trace = True
        trace_values = False
        if trace:
            logging.info('cursor_line: %r', self.cursor_line)
            if trace_values: self.dump_values()
        if self.cursor_line is None:
            self.cursor_line = 0
        self.values.insert(self.cursor_line+1, self.new_node())
        self.cursor_line += 1
        self.display()
        self.edit_headline()
       

    # These insert or delete entire outline nodes.
    def h_delete(self, ch):

        self.delete_line()
    def h_edit_headline(self, ch):
        
        self.edit_headline()
    def h_insert(self, ch):

        return self.insert_line()
    def h_move_left(self, ch):
        
        node = self.values[self.cursor_line]
        if self._has_children(node) and node.expanded:
            self.h_collapse_tree(ch)
        else:
            self.h_cursor_line_up(ch)
    def h_move_right(self, ch):
        
        node = self.values[self.cursor_line]
        if self._has_children(node):
            if node.expanded:
                self.h_cursor_line_down(ch)
            else:
                self.h_expand_tree(ch)
        else:
            self.h_cursor_line_down(ch)
    def set_handlers(self):
        
        # pylint: disable=no-member
        d = {
            curses.KEY_LEFT: self.h_move_left,
            curses.KEY_RIGHT: self.h_move_right,
            ord('d'): self.h_delete,
            ord('h'): self.h_edit_headline,
            ord('i'): self.h_insert,
            ### ord('o'): self.h_insert_after,
            # curses.ascii.CR:        self.h_edit_cursor_line_value,
            # curses.ascii.NL:        self.h_edit_cursor_line_value,
            # curses.ascii.SP:        self.h_edit_cursor_line_value,
            # curses.ascii.DEL:       self.h_delete_line_value,
            # curses.ascii.BS:        self.h_delete_line_value,
            # curses.KEY_BACKSPACE:   self.h_delete_line_value,
        }
        self.handlers.update(d)


