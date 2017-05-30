#@+leo-ver=5-thin
#@+node:ekr.20170530024520.2: * @file importers/lua.py
'''
The @auto importer for the lua language.

Created 2017/05/30 by the `importer;;` abbreviation.
'''
import leo.core.leoGlobals as g
import leo.plugins.importers.linescanner as linescanner
Importer = linescanner.Importer
#@+others
#@+node:ekr.20170530024520.3: ** class Lua_Importer
class Lua_Importer(Importer):
    '''The importer for the lua lanuage.'''

    def __init__(self, importCommands):
        '''Lua_Importer.__init__'''
        # Init the base class.
        Importer.__init__(self,
            importCommands,
            language = 'lua',
            state_class = Lua_ScanState,
            strict = False,
        )
        
    #@+others
    #@+node:ekr.20170530024520.5: *3* lua_i.clean_headline
    if 0: # The base class
        def clean_headline(self, s):
            '''Return a cleaned up headline s.'''
            return s.strip()
            
    ### A more complex example, for the C language.
        # def clean_headline(self, s):
            # '''Return a cleaned up headline s.'''
            # import re
            # type1 = r'(static|extern)*'
            # type2 = r'(void|int|float|double|char)*'
            # class_pattern = r'\s*(%s)\s*class\s+(\w+)' % (type1)
            # pattern = r'\s*(%s)\s*(%s)\s*(\w+)' % (type1, type2)
            # m = re.match(class_pattern, s)
            # if m:
                # prefix1 = '%s ' % (m.group(1)) if m.group(1) else ''
                # return '%sclass %s' % (prefix1, m.group(2))
            # m = re.match(pattern, s)
            # if m:
                # prefix1 = '%s ' % (m.group(1)) if m.group(1) else ''
                # prefix2 = '%s ' % (m.group(2)) if m.group(2) else ''
                # h = m.group(3) or '<no c function name>'
                # return '%s%s%s' % (prefix1, prefix2, h)
            # else:
                # return s
    #@+node:ekr.20170530024520.6: *3* lua_i.clean_nodes
    def clean_nodes(self, parent):
        '''
        Clean all nodes in parent's tree.
        Subclasses override this as desired.
        See perl_i.clean_nodes for an examplle.
        '''
        pass
    #@+node:ekr.20170530031729.1: *3* lua_i.get_new_dict
    #@@nobeautify

    def get_new_dict(self, context):
        '''The scan dict for the lua language.'''
        trace = False and g.unitTesting
        comment, block1, block2 = self.single_comment, self.block1, self.block2
        assert comment
        assert block1 and block2
        
        def add_key(d, pattern, data):
            key = pattern[0]
            aList = d.get(key,[])
            aList.append(data)
            d[key] = aList

        if context:
            d = {
                # key    kind   pattern  ends?
                '\\':   [('len+1', '\\', None),],
                '"':    [('len', '"',    context == '"'),],
                "'":    [('len', "'",    context == "'"),],
            }
            # End Lua long brackets.
            for i in range(10):
                open_pattern = '[%s[' % ('='*i)
                pattern = ']%s]' % ('='*i)
                add_key(d, pattern, ('len', pattern, context==open_pattern))
            if block1 and block2:
                add_key(d, block2, ('len', block2, True))
        else:
            # Not in any context.
            d = {
                # key    kind pattern new-ctx  deltas
                '\\':[('len+1', '\\', context, None),],
                '"':    [('len', '"', '"',     None),],
                "'":    [('len', "'", "'",     None),],
                '{':    [('len', '{', context, (1,0,0)),],
                '}':    [('len', '}', context, (-1,0,0)),],
                '(':    [('len', '(', context, (0,1,0)),],
                ')':    [('len', ')', context, (0,-1,0)),],
                '[':    [('len', '[', context, (0,0,1)),],
                ']':    [('len', ']', context, (0,0,-1)),],
            }
            # Start Lua long brackets.
            for i in range(10):
                pattern = '[%s[' % ('='*i)
                add_key(d, pattern, ('len', pattern, pattern, None))
            if comment:
                add_key(d, comment, ('all', comment, '', None))
            if block1 and block2:
                add_key(d, block1, ('len', block1, block1, None))
        if trace: g.trace('created %s dict for %4r state ' % (self.name, context))
        return d
    #@-others
#@+node:ekr.20170530024520.7: ** class class Lua_ScanState
class Lua_ScanState:
    '''A class representing the state of the lua line-oriented scan.'''
    
    def __init__(self, d=None):
        '''Lua_ScanState.__init__'''
        if d:
            prev = d.get('prev')
            self.context = prev.context
        else:
            self.context = ''

    def __repr__(self):
        '''Lua_ScanState.__repr__'''
        return "Lua_ScanState context: %r " % (self.context)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20170530024520.8: *3* lua_state.level
    def level(self):
        '''Lua_ScanState.level.'''
        return 0
            ### Examples:
            # self.indent # for python, coffeescript.
            # self.curlies
            # (self, curlies, self.parens)
    #@+node:ekr.20170530024520.9: *3* lua_state.update
    def update(self, data):
        '''
        Lua_ScanState.update

        Update the state using the 6-tuple returned by v2_scan_line.
        Return i = data[1]
        '''
        context, i, delta_c, delta_p, delta_s, bs_nl = data
        # All ScanState classes must have a context ivar.
        self.context = context
        # self.curlies += delta_c  
        # self.bs_nl = bs_nl
        # self.parens += delta_p
        # self.squares += delta_s
        return i
    #@-others

#@-others
importer_dict = {
    'class': Lua_Importer,
    'extensions': ['.lua',],
}
#@@language python
#@@tabwidth -4


#@-leo
