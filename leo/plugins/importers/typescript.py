#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18152: * @file importers/typescript.py
'''The @auto importer for TypeScript.'''
import leo.plugins.importers.javascript as javascript
JS_Importer = javascript.JS_Importer
#@+others
#@+node:ekr.20140723122936.18111: ** class TS_Importer(JS_Importer)
class TS_Importer(JS_Importer):
    
    def __init__(self, importCommands, atAuto):
        '''TS_Importer ctor.'''
        # Init the base class.
        JS_Importer.__init__(self,
            importCommands,
            atAuto=atAuto,
            language='typescript',
        )

    #@+others
    #@-others
#@-others
importer_dict = {
    'class': TS_Importer,
    'extensions': ['.ts',],
}
#@-leo
