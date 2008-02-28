#@+leo-ver=4-thin
#@+node:mork.20041102091309:@file-thin exampleTemacsExtension.py
'''An example of a temacs Extension.  To test example:
    1. Create usetemacs.ini file.
    2. Make an [ extensions ] section.
    3. put:
       1=exampleTemacsExtension
       
    When Leo starts,
    select a set of lines
    type Alt-x
    the format-selection-as-list and hit Enter( or type format and hit tab, the autocompletion will work ).
    
    After typing Enter you should see you selection indented and each line prefixed with an ascending number.'''




def formatSelectionAsList( self, event ):
    '''This function indents and prepends a number to a selection of text'''
    try: #We guard against there not being anything selected, which throws an Exception in this block.
        tbuffer = event.widget # call the Text instance tbuffer as in Emacs class.
        self.indentRegion( event ) # use the Emacs instances indentRegion method to do initial formatting.
        start = tbuffer.index( 'sel.first linestart' )
        start = tbuffer.search( '\w', start, regexp = True, stopindex = '%s lineend' % 'sel.last' )
        if not start:
            return self.keyboardQuit( event )
        end = tbuffer.index( 'sel.last' )
    except Exception, x:
        return self.keyboardQuit( event )
    r1, c1 = start.split( '.' )
    r1, c1 = int( r1 ), int( c1 )
    r2, c2 = end.split( '.' )
    r2 = int( r2 )
    amount = r2 - r1
    for z in xrange( amount + 1 ):
        tbuffer.insert( '%s.%s' % ( r1, c1 ), '%s. ' % ( z + 1 ))
        r1 = r1 + 1
    self.keyboardQuit( event ) # this turns off the state and sets things to normal
    return self._tailEnd( tbuffer ) # this calls the _tailEnd method, which when used with usetemacs will ensure that the text sticks.
    
    




def getExtensions():

    return { 'format-selection-as-list': formatSelectionAsList } #We return the one function in this module.

#@-node:mork.20041102091309:@file-thin exampleTemacsExtension.py
#@-leo
