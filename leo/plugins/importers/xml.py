#@+leo-ver=5-thin
#@+node:ekr.20161121204146.2: * @file importers/xml.py
'''The @auto importer for the xml language.'''
import re
import leo.core.leoGlobals as g
import leo.plugins.importers.linescanner as linescanner
Importer = linescanner.Importer
Target = linescanner.Target
#@+others
#@+node:ekr.20161121204146.3: ** class Xml_Importer
class Xml_Importer(Importer):
    '''The importer for the xml lanuage.'''

    def __init__(self, importCommands, atAuto, tags_setting='import_xml_tags'):
        '''Xml_Importer.__init__'''
        # Init the base class.
        Importer.__init__(self,
            importCommands,
            atAuto = atAuto,
            language = 'xml',
            state_class = Xml_ScanState,
            strict = False,
        )
        self.tags_setting = tags_setting
        
    #@+others
    #@+node:ekr.20161121204918.1: *3* xml_i.add_tags (revise)
    def add_tags(self):
        '''Add items to self.class/functionTags and from settings.'''
        trace = False
        c = self.c
        if trace: g.trace(self.c.fileName(), self.tags_setting)
            #### What's in the @data nodes?
        for ivar, setting in (
            ('classTags', self.tags_setting),
        ):
            aList = getattr(self, ivar)
            if trace: g.trace('aList', aList)
            aList2 = c.config.getData(setting) or []
            aList2 = [z.lower() for z in aList2]
            if trace: g.trace('aList2', aList2)
            aList.extend(aList2)
            setattr(self, ivar, aList)
            if trace: g.trace('result', ivar, aList)
    #@+node:ekr.20161121205214.2: *3* xml_i.get_new_table
    #@@nobeautify

    def get_new_table(self, context):
        '''Return an xml state table for the given context.'''
        comment, block1, block2 = self.single_comment, self.block1, self.block2
        assert not comment, repr(comment)
        table = (
            # in-ctx: the next context when the pattern matches the line *and* the context.
            # out-ctx:the next context when the pattern matches the line *outside* any context.
            # deltas: the change to the indicated counts.  Always zero when inside a context.

            # kind,   pattern, out-ctx,  in-ctx, delta{}, delta(), delta[]
            ('len',   '"',     '"',       '',       0,       0,       0),
            ('len',   block1,  block1,    context,  0,       0,       0),
            ('len',   block2,  context,   '',       0,       0,       0),
        )
        return table
    #@+node:ekr.20161121210726.1: *3* REF: use the base-class methods
    if 0:
        #@+others
        #@+node:ekr.20161121210651.1: *4* i.v2_gen_lines & helpers
        def v2_gen_lines(self, s, parent):
            '''
            Non-recursively parse all lines of s into parent, creating descendant
            nodes as needed.
            '''
            trace = False and g.unitTesting
            tail_p = None
            prev_state = self.state_class()
            target = Target(parent, prev_state)
            stack = [target, target]
            self.inject_lines_ivar(parent)
            for line in g.splitLines(s):
                new_state = self.v2_scan_line(line, prev_state)
                top = stack[-1]
                if trace: self.trace_status(line, new_state, prev_state, stack, top)
                if self.is_ws_line(line):
                    p = tail_p or top.p
                    self.add_line(p, line)
                elif self.starts_block(line, new_state, prev_state):
                    tail_p = None
                    self.start_new_block(line, new_state, prev_state, stack)
                elif new_state.level() >= top.state.level():
                    # Comparing new_state against prev_state does not work for python.
                    p = tail_p or top.p
                    self.add_line(p, line)
                else:
                    tail_p = self.end_block(line, new_state, stack)
                prev_state = new_state
        #@+node:ekr.20161121210651.2: *5* i.cut_stack
        def cut_stack(self, new_state, stack):
            '''Cut back the stack until stack[-1] matches new_state.'''
            trace = False and g.unitTesting
            if trace:
                g.trace(new_state)
                g.printList(stack)
            assert len(stack) > 1 # Fail on entry.
            while stack:
                top_state = stack[-1].state
                if new_state.level() < top_state.level():
                    if trace: g.trace('new_state < top_state', top_state)
                    assert len(stack) > 1, stack # <
                    stack.pop()
                elif top_state.level() == new_state.level():
                    if trace: g.trace('new_state == top_state', top_state)
                    assert len(stack) > 1, stack # ==
                    # This is the only difference between i.cut_stack and python/cs.cut_stack
                    # stack.pop()
                    break
                else:
                    # This happens often in valid Python programs.
                    if trace: g.trace('new_state > top_state', top_state)
                    break
            # Restore the guard entry if necessary.
            if len(stack) == 1:
                if trace: g.trace('RECOPY:', stack)
                stack.append(stack[-1])
            assert len(stack) > 1 # Fail on exit.
            if trace: g.trace('new target.p:', stack[-1].p.h)
        #@+node:ekr.20161121210651.3: *5* i.end_block (sets_tail_p)
        def end_block(self, line, new_state, stack):
            # The block is ending. Add tail lines until the start of the next block.
            p = stack[-1].p
            self.add_line(p, line)
            self.cut_stack(new_state, stack)
            tail_p = None if self.gen_refs else p
            return tail_p
        #@+node:ekr.20161121210651.4: *5* i.inject_lines_ivar
        def inject_lines_ivar(self, p):
            '''Inject _import_lines into p.v.'''
            assert not p.v._bodyString, repr(p.v._bodyString)
            p.v._import_lines = []
        #@+node:ekr.20161121210651.5: *5* i.start_new_block
        def start_new_block(self, line, new_state, prev_state, stack):
            '''Create a child node and update the stack.'''
            if hasattr(new_state, 'in_context'):
                assert not new_state.in_context(), ('start_new_block', new_state)
            target=stack[-1]
            # Insert the reference in *this* node.
            h = self.v2_gen_ref(line, target.p, target)
            # Create a new child and associated target.
            child = self.v2_create_child_node(target.p, line, h)
            stack.append(Target(child, new_state))
        #@+node:ekr.20161121210651.7: *5* i.trace_status
        def trace_status(self, line, new_state, prev_state, stack, top):
            '''Print everything important in the v2_gen_lines loop.'''
            print('')
            print('===== %r' % line)
            print('     top.p: %s' % top.p.h)
            print('len(stack): %s' % len(stack))
            print(' new_state: %s' % new_state)
            print('prev_state: %s' % prev_state)
            print(' top.state: %s' % top.state)
        #@+node:ekr.20161121210651.8: *5* i.v2_create_child_node
        def v2_create_child_node(self, parent, body, headline):
            '''Create a child node of parent.'''
            trace = False and g.unitTesting
            if trace: g.trace('\n\nREF: %s === in === %s\n%r\n' % (
                headline, parent.h, body))
            child = parent.insertAsLastChild()
            assert g.isString(body), repr(body)
            assert g.isString(headline), repr(headline)
            self.inject_lines_ivar(child)
            self.add_line(child, body)
            child.h = headline
            return child
        #@+node:ekr.20161121210651.9: *5* i.v2_gen_ref
        def v2_gen_ref(self, line, parent, target):
            '''
            Generate the ref line and a flag telling this method whether a previous
            #@+others
            #@-others
            '''
            trace = False and g.unitTesting
            indent_ws = self.get_str_lws(line)
            h = self.clean_headline(line) 
            if self.is_rst and not self.atAuto:
                return None, None
            elif self.gen_refs:
                headline = g.angleBrackets(' %s ' % h)
                ref = '%s%s\n' % (
                    indent_ws,
                    g.angleBrackets(' %s ' % h))
            else:
                if target.ref_flag:
                    ref = None
                else:
                    ref = '%s@others\n' % indent_ws
                    target.at_others_flag = True
                target.ref_flag = True
                    # Don't generate another @others in this target.
                headline = h
            if ref:
                if trace:
                    g.trace('%s indent_ws: %r line: %r parent: %s' % (
                    '*' * 20, indent_ws, line, parent.h))
                    g.printList(parent.v._import_lines)
                self.add_line(parent,ref)
            return headline
        #@-others
    #@+node:ekr.20161121210839.1: *3* xml_i.starts_block (Rewrite)
    starts_pattern = re.compile(r'\s*\<[\w+]\>')
        # Matches lines that apparently starts a class or def.

    def starts_block(self, line, new_state, prev_state):
        '''
        True if the line startswith class or def outside any context.
        
        As a side effect, sets new_state.tag_level.
        '''
        if prev_state.in_context():
            return False #### Must scan the entire line!
        else:
            ###### There could be many start tags on a line!
            return bool(self.starts_pattern.match(line))
    #@+node:ekr.20161121212858.1: *3* xml_i.is_ws_line (TO DO)
    #@-others
#@+node:ekr.20161121204146.7: ** class class Xml_ScanState
class Xml_ScanState:
    '''A class representing the state of the xml line-oriented scan.'''
    
    def __init__(self, d=None):
        '''Xml_ScanState.__init__'''
        if d:
            prev = d.get('prev')
            self.context = prev.context
            # xml_i.starts_block sets self.tag_level.
        else:
            self.context = ''
            self.tag_level = 0

    def __repr__(self):
        '''Xml_ScanState.__repr__'''
        return "Xml_ScanState context: %r tag_level: %s" % (
            self.context, self.tag_level)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20161121204146.8: *3* xml_state.level
    def level(self):
        '''Xml_ScanState.level.'''
        return self.tag_level
    #@+node:ekr.20161121204146.9: *3* xml_state.update
    def update(self, data):
        '''
        Xml_ScanState.update

        Update the state using the 6-tuple returned by v2_scan_line.
        Return i = data[1]
        '''
        context, i, delta_c, delta_p, delta_s, bs_nl = data
        self.context = context
        return i
    #@-others

#@-others
importer_dict = {
    'class': Xml_Importer,
    'extensions': ['.xml',],
}
#@@language python
#@@tabwidth -4

#@-leo
