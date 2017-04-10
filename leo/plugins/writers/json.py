#@+leo-ver=5-thin
#@+node:ekr.20160504083330.1: * @file writers/json.py
'''The @auto write code for .json files.'''
# pylint: disable=unused-import
# pylint: disable=import-self
# json is not the same as leo.plugins.json
import copy
import json
# import leo.core.leoGlobals as g
import leo.plugins.writers.basewriter as basewriter
#@+others
#@+node:ekr.20160504083330.2: ** class JSON_Writer
class JSON_Writer(basewriter.BaseWriter):
    '''The writer class for .json files.'''
    # No ctor.
    #@+others
    #@+node:ekr.20160504083330.3: *3* json.write
    def write(self, root):
        """Write all the @auto-json node."""
        nodes = list(set([p.v for p in root.subtree()]))
        nodes = [self.vnode_dict(v) for v in nodes]
        d = {
            'top': self.vnode_dict(root.v),
            'nodes': nodes,
        }
        # pylint: disable=no-member
        # pylint confuses this module with the stdlib json module
        s = json.dumps(d,
            sort_keys=True,
            indent=2, # Pretty print.
            separators=(',', ': '))
        self.put(s)
        root.setVisited()
        return True
    #@+node:ekr.20160504085408.1: *3* json.vnode_dict
    def vnode_dict(self, v):
        '''Return a json dict for v.'''
        return {
            'gnx': v.gnx,
            'h': v.h, 'b': v.b,
            'ua': copy.deepcopy(v.u),
            'children': [z.gnx for z in v.children]
        }
    #@-others
#@-others
writer_dict = {
    '@auto': ['@auto-json',],
    'class': JSON_Writer,
    'extensions': ['.json',],
}
#@@language python
#@@tabwidth -4
#@-leo
