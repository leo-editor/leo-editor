#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18152: * @file importers/typescript.py
'''The @auto importer for TypeScript.'''
import leo.plugins.importers.javascript as javascript
JavaScriptScanner = javascript.JavaScriptScanner
#@+others
#@+node:ekr.20140723122936.18111: ** class TypeScriptScanner(JavaScriptScanner)
class TypeScriptScanner (JavaScriptScanner):

    #@+others
    #@+node:ekr.20140723122936.18112: *3* TypeScriptScanner.__init__
    def __init__ (self,importCommands,atAuto):

        # Init the base class.
        JavaScriptScanner.__init__(self,importCommands,
            atAuto=atAuto,language='typescript',
            alternate_language='javascript')

        # Overrides of ivars.
        self.hasClasses = True
        self.classTags = ['module','class','interface',]
        self.functionTags = [
            'constructor','enum','function',
            'public','private','export',]
    #@+node:ekr.20140723122936.18113: *3* getSigId (TypeScriptScanner)
    def getSigId (self,ids):

        '''Return the signature's id.

        This is the last id of the ids list, or the id before extends anotherId.
        '''

        if len(ids) > 2 and ids[-2] == 'extends':
            return ids[-3]
        else:
            return ids and ids[-1]
    #@-others
#@-others
importer_dict = {
    'class': TypeScriptScanner,
    'extensions': ['.ts',],
}
#@-leo
