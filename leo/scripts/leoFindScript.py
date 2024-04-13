#@+leo-ver=4-thin
#@+node:EKR.20040502195118:@file-thin ../scripts/leoFindScript.py
# This file contains functions for non-interactive searching.
# You might find these useful while running other scripts.

import leo, string, re

#@+others
#@+node:EKR.20040502195118.1:changeAll
def changeAll(commander, findPat, changePat, bodyFlag=1):
    """
    changeAll       make changes in an entire Leo outline.

    commander       Commands object for a Leo outline window.
    findPat         the search string.
    changePat       the replacement string.
    bodyFlag        true: change body text.  false: change headline text.
    """
    n = len(changePat)
    v = commander.rootVnode()
    pos = 0
    while v != None:
        v, pos = changeNext(v, pos, findPat, changePat, bodyFlag)
        pos = pos + n
#@nonl
#@-node:EKR.20040502195118.1:changeAll
#@+node:EKR.20040502195118.2:changeNext
def changeNext(v, pos, findPat, changePat, bodyFlag=1):
    """
    changeNext:     use string.find() to change text in a Leo outline.

    v                       the vnode to start the search.
    pos                     the position within the body text of v to start the search.
    findPat         the search string.
    changePat       the replacement string.
    bodyFlag        true: change body text.  false: change headline text.

    returns a tuple (v,pos) showing where the change occured.
    returns (None,0) if no further match in the outline was found.

    Note: if (v,pos) is a tuple returned previously from changeNext,
    changeNext(v,pos+len(findPat),findPat,changePat)
    changes the next matching string.
    """
    n = len(findPat)
    v, pos = findNext(v, pos, findPat, bodyFlag)
    if v == None:
        return None, 0
    if bodyFlag:
        s = v.bodyString()
        # s[pos:pos+n] = changePat
        s = s[:pos] + changePat + s[pos + n :]
        v.setBodyStringOrPane(s)
    else:
        s = v.headString()
        # s[pos:pos+n] = changePat
        s = s[:pos] + changePat + s[pos + n :]
        v.setHeadStringOrHeadline(s)
        print("setting head string: ", result)
    return v, pos
#@nonl
#@-node:EKR.20040502195118.2:changeNext
#@+node:EKR.20040502195118.3:changePrev
def changePrev(v, pos, findPat, changePat, bodyFlag=1):
    """
    changePrev:     use string.rfind() to change text in a Leo outline.

    v                       the vnode to start the search.
    pos                     the position within the body text of v to start the search.
    findPat         the search string.
    changePat       the replacement string.
    bodyFlag        true: change body text.  false: change headline text.

    returns a tuple (v,pos) showing where the change occured.
    returns (None,0) if no further match in the outline was found.

    Note: if (v,pos) is a tuple returned previously from changePrev,
    changePrev(v,pos-len(findPat),findPat,changePat)
    changes the next matching string.
    """
    n = len(findPat)
    v, pos = findPrev(v, pos, findPat, bodyFlag)
    if v == None:
        return None, 0
    if bodyFlag:
        s = v.bodyString()
        # s[pos:pos+n] = changePat
        s = s[:pos] + changePat + s[pos + n :]
        v.setBodyStringOrPane(s)
    else:
        s = v.headString()
        # s[pos:pos+n] = changePat
        s = s[:pos] + changePat + s[pos + n :]
        v.setHeadStringOrHeadline(s)
    return v, pos
#@nonl
#@-node:EKR.20040502195118.3:changePrev
#@+node:EKR.20040502195118.4:findAll
def findAll(c, pattern, bodyFlag=1):
    """
    findAll         search an entire Leo outline for a pattern.

    c        commander for a Leo outline window.
    pattern         the search string.
    bodyFlag        true: search body text. false: search headline text.

    returns a list of tuples (v,pos) showing where matches occured.
    returns [] if no match were found.
    """
    v = c.rootVnode()
    n = len(pattern)
    result = []; pos = 0
    while v != None:
        v, pos = findNext(v, pos, pattern, bodyFlag)
        if v:
            result.append((v, pos),)
        pos = pos + n
    return result
#@nonl
#@-node:EKR.20040502195118.4:findAll
#@+node:EKR.20040502195118.5:findNext
def findNext(v, pos, pattern, bodyFlag=1):
    """
    findNext:       use string.find() to find a pattern in a Leo outline.

    v                       the vnode to start the search.
    pos                     the position within the body text of v to start the search.
    pattern         the search string.
    bodyFlag        true: search body text.  false: search headline text.

    returns a tuple (v,pos) showing where the match occured.
    returns (None,0) if no further match in the outline was found.

    Note: if (v,pos) is a tuple returned previously from findNext,
    findNext(v,pos+len(pattern),pattern) finds the next match.
    """
    while v != None:
        if bodyFlag:
            s = v.bodyString()
        else:
            s = v.headString()
        pos = s.find(pattern, pos)
        if pos != -1:
            return v, pos
        v = v.threadNext()
        pos = 0
    return None, 0
#@nonl
#@-node:EKR.20040502195118.5:findNext
#@+node:EKR.20040502195118.6:findPrev
def findPrev(v, pos, pattern, bodyFlag=1):
    """
    findPrev:       use string.rfind() to find a pattern in a Leo outline.

    v                       the vnode to start the search.
    pos                     the position within the body text of v to start the search.
    pattern         the search string
    bodyFlag        true: search body text.  false: search headline text.

    returns a tuple (v,pos) showing where the match occured.
    returns (None,0) if no further match in the outline was found.

    Note: if (v,pos) is a tuple returned previously from findPrev,
    findPrev(v,pos-len(pattern),pattern) finds the next match.
    """
    while v != None:
        if bodyFlag:
            s = v.bodyString()
        else:
            s = v.headString()
        pos = s.rfind(pattern, 0, pos)
        if pos != -1:
            return v, pos
        v = v.threadBack()
        pos = -1
    return None, 0
#@nonl
#@-node:EKR.20040502195118.6:findPrev
#@+node:EKR.20040502195118.7:reChangeAll
def reChangeAll(commander, findPat, changePat, bodyFlag, reFlags=None):
    """
    reChangeAll: make changes in an entire Leo outline using re module.

    commander       Commands object for a Leo outline window.
    findPat         the search string.
    changePat       the replacement string.
    bodyFlag        true: change body text.  false: change headline text.
    reFlags         flags argument to re.search().
    """
    n = len(changePat)
    v = commander.rootVnode()
    pos = 0
    while v != None:
        v, mo, pos = reChangeNext(
                v, pos, findPat, changePat, bodyFlag, reFlags)
        pos = pos + n
#@nonl
#@-node:EKR.20040502195118.7:reChangeAll
#@+node:EKR.20040502195118.8:reChangeNext
def reChangeNext(v, pos, findPat, changePat, bodyFlag, reFlags=None):
    """
    reChangeNext: use re.search() to change text in a Leo outline.

    v                       the vnode to start the search.
    pos                     the position within the body text of v to start the search.
    findPat         the search string.
    changePat       the replacement string.
    bodyFlag        true: change body text.  false: change headline text.
    reFlags         flags argument to re.search().

    returns a tuple (v,pos) showing where the change occured.
    returns (None,0) if no further match in the outline was found.

    Note: if (v,pos) is a tuple returned previously from reChangeNext,
    reChangeNext(v,pos+len(findPat),findPat,changePat,bodyFlag)
    changes the next matching string.
    """
    n = len(findPat)
    v, mo, pos = reFindNext(v, pos, findPat, bodyFlag, reFlags)
    if v == None:
        return None, None, 0
    if bodyFlag:
        s = v.bodyString()
        print(s, findPat, changePat)
        # s[pos:pos+n] = changePat
        s = s[:pos] + changePat + s[pos + n :]
        v.setBodyStringOrPane(s)
    else:
        s = v.headString()
        # s[pos:pos+n] = changePat
        s = s[:pos] + changePat + s[pos + n :]
        v.setHeadStringOrHeadline(s)
    return v, mo, pos
#@nonl
#@-node:EKR.20040502195118.8:reChangeNext
#@+node:EKR.20040502195118.9:reChangePrev
def reChangePrev(v, pos, findPat, changePat, bodyFlag, reFlags=None):
    """
    reChangePrev: use re.search() to change text in a Leo outline.

    v                       the vnode to start the search.
    pos                     the position within the body text of v to start the search.
    findPat         the search string.
    changePat       the replacement string.
    bodyFlag        true: change body text.  false: change headline text.
    reFlags         flags argument to re.search().

    returns a tuple (v,pos) showing where the change occured.
    returns (None,0) if no further match in the outline was found.

    Note: if (v,pos) is a tuple returned previously from reChangePrev,
    reChangePrev(v,pos-len(findPat),findPat,changePat,bodyFlag)
    changes the next matching string.
    """
    n = len(findPat)
    v, mo, pos = reFindPrev(v, pos, findPat, bodyFlag, reFlags)
    if v == None:
        return None, None, 0
    if bodyFlag:
        s = v.bodyString()
        # s[pos:pos+n] = changePat
        s = s[:pos] + changePat + s[pos + n :]
        v.setBodyStringOrPane(s)
    else:
        s = v.headString()
        # s[pos:pos+n] = changePat
        s = s[:pos] + changePat + s[pos + n :]
        v.setHeadStringOrHeadline(s)
    return v, mo, pos
#@nonl
#@-node:EKR.20040502195118.9:reChangePrev
#@+node:EKR.20040502195118.10:reFindAll
def reFindAll(c, findPat, bodyFlag, reFlags=None):
    """
    reFindAll       search an entire Leo outline using re module.

    c            commander for a Leo outline window.
    pattern         the search string.
    bodyFlag        true: search body text.  false: search headline text.
    reFlags         flags argument to re.search().

    returns a list of tuples (v,pos) showing where matches occured.
    returns [] if no match were found.
    """
    v = c.rootVnode()
    n = len(findPat)
    result = []; pos = 0
    while v != None:
        v, mo, pos = reFindNext(v, pos, findPat, bodyFlag, reFlags)
        if v != None:
            result.append((v, mo, pos))
        pos = pos + n
    return result
#@nonl
#@-node:EKR.20040502195118.10:reFindAll
#@+node:EKR.20040502195118.11:reFindNext
def reFindNext(v, pos, pattern, bodyFlag, reFlags=None):
    """
    reFindNext:     use re.search() to find pattern in a Leo outline.

    v                       the vnode to start the search.
    pos                     the position within the body text of v to start the search.
    pattern         the search string
    bodyFlag        true: search body text.  false: search headline text.
    reFlags         the flags argument to re.search()

    returns a tuple (v,mo,pos) showing where the match occured.
    returns (None,None,0) if no further match in the outline was found.
    mo is a "match object"

    Note: if (v,pos) is a tuple returned previously from reFindNext,
    reFindNext(v,pos+len(pattern),pattern) finds the next match.
    """
    while v != None:
        if bodyFlag:
            s = v.bodyString()
        else:
            s = v.headString()
        if reFlags == None:
            mo = re.search(pattern, s[pos:])
        else:
            mo = re.search(pattern, s[pos:], reFlags)
        if mo != None:
            return v, mo, pos + mo.start()
        v = v.threadNext()
        pos = 0
    return None, None, 0
#@nonl
#@-node:EKR.20040502195118.11:reFindNext
#@+node:EKR.20040502195118.12:reFindPrev
def reFindPrev(v, pos, pattern, bodyFlag, reFlags=None):
    """
    reFindPrev:     use re.search() to find pattern in a Leo outline.

    v                       the vnode to start the search.
    pos                     the position within the body text of v to start the search.
    pattern         the search string
    bodyFlag        true: search body text.  false: search headline text.
    reFlags         the flags argument to re.search()

    returns a tuple (v,mo,pos) showing where the match occured.
    returns (None,None,0) if no further match in the outline was found.

    Note 1: Searches vnodes in reverse (v.threadBack) direction.
    Searches text of vnodes in _forward_ direction.

    Note 2: if (v,pos) is a tuple returned previously from reFindPrev,
    reFindPrev(v,pos-len(pattern),pattern) finds the next match.
    """
    while v != None:
        if bodyFlag:
            s = v.bodyString()
        else:
            s = v.headString()
        # Forward search through text...
        if reFlags == None:
            mo = re.search(pattern, s[pos:])
        else:
            mo = re.search(pattern, s[pos:], reFlags)
        if mo != None:
            return v, mo, pos + mo.start()
        # Reverse search through vnode.
        v = v.threadBack()
        pos = 0
    return None, None, 0
#@nonl
#@-node:EKR.20040502195118.12:reFindPrev
#@+node:EKR.20040502195118.13:lineAtPos
def lineAtPos(s, pos):
    """
    lineAtPos: return the line of a string containing the given index.
    s               a string
    pos             an index into s
    """
    # find the start of the line containing the match
    if len(s) < 1:
        return ""
    if pos > len(s):
        pos = len(s) - 1

    while pos > 0:
        if s[pos] == '\n':
            pos = pos + 1
            break
        else:
            pos = pos - 1
    # return the line containing the match
    s = s[pos:]
    list = s.split("\n")
    return list[0]
#@nonl
#@-node:EKR.20040502195118.13:lineAtPos
#@+node:EKR.20040502195118.14:printFindList
def printFindList(findList, bodyFlag=1):
    """
    printFindList:  Print matching lines from the list.

    findList:               a list of (v,pos) tuples returned from findAll().
    Only the line containing the match is printed.
    Lines are printed once for each match found on the line.
    """
    for v, pos in findList:
        if v != None:
            if bodyFlag:
                s = v.bodyString()
            else:
                s = v.headString()
            print(lineAtPos(s, pos))
#@nonl
#@-node:EKR.20040502195118.14:printFindList
#@-others
#@nonl
#@-node:EKR.20040502195118:@file-thin ../scripts/leoFindScript.py
#@-leo
