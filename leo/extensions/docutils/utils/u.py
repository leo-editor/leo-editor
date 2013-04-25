import sys

def u(s):
    '''A compatibility method called by --fix=unified_unicode.'''
    
    encoding = 'unicode_escape'

    if sys.version_info < (3,):
        return s if isinstance(s,unicode) else unicode(s,encoding)
    else:
        return s if isinstance(s,str) else str(s,encoding)

def ur(s):
    
    # Two unit test failures, regardless of order.
    encoding = 'ascii' if s.find('\\') > -1 else 'unicode_escape'
    if sys.version_info < (3,):
        return s if isinstance(s,unicode) else unicode(s,encoding)
    else:
        return s if isinstance(s,str) else str(s,encoding)
    # for encoding in ('unicode_escape','ascii',):
        # try:
            # if sys.version_info < (3,):
                # return s if isinstance(s,unicode) else unicode(s,encoding)
            # else:
                # return s if isinstance(s,str) else str(s,encoding)
        # except Exception:
            # pass
    # raise
