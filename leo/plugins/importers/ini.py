#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18142: * @file importers/ini.py
'''The @auto importer for .ini files.'''
import re
# import leo.core.leoGlobals as g
import leo.plugins.importers.linescanner as linescanner
Importer = linescanner.Importer
Target = linescanner.Target
#@+others
#@+node:ekr.20140723122936.18043: ** class Ini_Importer
class Ini_Importer(Importer):

    def __init__(self, importCommands, atAuto):
        '''Ini_Importer.__init__'''
        # Init the base class.
        Importer.__init__(self,
            importCommands,
            atAuto = atAuto,
            language = 'ini',
            state_class = Ini_ScanState,
            strict = False,
        )

    #@+others
    #@+node:ekr.20161123112121.1: *3* ini.start_new_block
    ini_at_others_flag = False

    def start_new_block(self, line, new_state, prev_state, stack):
        '''Create a child node and update the stack.'''
        # Unlike the base class, all nodes are direct children of the root.
        target=stack[-1]
        target_p = self.root
        if not self.ini_at_others_flag:
            self.ini_at_others_flag = True
            h = self.v2_gen_ref(line, target_p, target)
        else:
            h = line.strip()
        child = self.v2_create_child_node(target_p, line, h)
        stack.append(Target(child, new_state))
    #@+node:ekr.20161123103554.1: *3* ini_i.starts_block
    ini_pattern = re.compile(r'^\s*\[(.*)\]')

    def starts_block(self, line, new_state, prev_state):
        '''name if the line is [ a name ].'''
        m = self.ini_pattern.match(line)
        return bool(m and m.group(1).strip())
    #@-others
#@+node:ekr.20161123104303.1: ** class Ini_ScanState
class Ini_ScanState:
    '''A do-nothing class'''
    
    def __init__(self, d=None):
        '''Ini_ScanState.__init__'''
        if d:
            self.context = d.get('context')
        else:
            self.context = ''
            
    def __repr__(self):
        return 'Ini_ScanState context: %r' % self.context
    
    __str__ = __repr__
        
    #@+others
    #@+node:ekr.20161123105058.3: *3* ini_state.update
    def update(self, data):
        '''
        Ini_ScanState.update

        Update the state using the 6-tuple returned by v2_scan_line.
        Return i = data[1]
        '''
        context, i, delta_c, delta_p, delta_s, bs_nl = data
        # All ScanState classes must have a context ivar.
        self.context = context
        return i
    #@+node:ekr.20161123112012.1: *3* ini_state.level
    def level(self):
        '''Ini_ScanState.level.'''
        return 0
    #@-others
#@-others
importer_dict = {
    'class': Ini_Importer,
    'extensions': ['.ini',],
}
#@-leo
