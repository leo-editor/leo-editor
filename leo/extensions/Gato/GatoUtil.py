################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   GatoUtil.py
#	author: Alexander Schliep (schliep@molgen.mpg.de)
#
#       Copyright (C) 1998-2005, Alexander Schliep, Winfried Hochstaettler and 
#       Copyright 1998-2001 ZAIK/ZPR, Universitaet zu Koeln
#                                   
#       Contact: schliep@molgen.mpg.de, wh@zpr.uni-koeln.de             
#
#       Information: http://gato.sf.net
#
#       This library is free software; you can redistribute it and/or
#       modify it under the terms of the GNU Library General Public
#       License as published by the Free Software Foundation; either
#       version 2 of the License, or (at your option) any later version.
#
#       This library is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#       Library General Public License for more details.
#
#       You should have received a copy of the GNU Library General Public
#       License along with this library; if not, write to the Free
#       Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#
#
#       This file is version $Revision: 1.1 $ 
#                       from $Date: 2007/10/04 14:36:39 $
#             last change by $Author: edream $.
#
################################################################################

from Tkinter import *
import time

def gatoPath():
    """ Returns the path to the directory containint Gato.py or Gred.py """
    import os
    return os.path.dirname(__name__ == '__main__' and sys.argv[0] or __file__)
    
def extension(pathAndFile):
    """ Return ext if path/filename.ext is given """
    import string
    return string.split(stripPath(pathAndFile),".")[-1]
    
def stripPath(pathAndFile):
    """ Return filename.ext if path/filename.ext is given """
    import os 
    return os.path.split(pathAndFile)[1]
    
def orthogonal(u):
    """ Return a unit length vector (v1,v2) which has an angle of
        90 degrees clockwise to the vector u = (u1,u2) """
    from math import sqrt
    (u1,u2) = u
    length = sqrt(u1**2 + u2**2)
    if length < 0.001:
        length = 0.001
    u1 = u1 / length
    u2 = u2 / length
    return (-u2,u1)
    
    
def ArgMin(list,val):
    """ Returns the element e of list for which val[e] is minimal """
    if len(list) > 0:
        min     = val[list[0]]
        minElem = list[0]
    for e in list:
        if val[e] < min:
            min     = val[e]
            minElem = e
    return minElem
    
    
def ArgMax(list,val):
    """ Returns the element e of list for which val[e] is maximal """
    if len(list) > 0:
        max     = val[list[0]]
        maxElem = list[0]
    for e in list:
        if val[e] > max:
            max     = val[e]
            maxElem = e
    return maxElem
    
    
class MethodLogger:
    """ Provide logging of method calls with parameters 
        E.g., for regression testing
    
        XXX specify output channel (or do it via redirect ?)
    """
    
    def __init__(self, object):
        self.object = object
        
    def __getattr__(self,arg):
        self.methodName = arg
        self.method = getattr(self.object,arg)
        return getattr(self,'caller')
        
    def caller(self,*args):
        print self.methodName,"(",args,")"
        return apply(self.method,args)
        
        
        
class TimedMethodLogger:
    """ Provide logging of method calls with parameters 
        E.g., for regression testing
    
        XXX specify output channel (or do it via redirect ?)
    """
    
    def __init__(self, object):
        self.object = object
        self.tml_calls = []
        self.tml_log_method_names = ['SetEdgeColor','SetVertexColor']
        self.tml_log_method_argnr = {'SetEdgeColor':2,
                                     'SetVertexColor':1}
        
        
    def __getattr__(self,arg):
        self.methodName = arg
        self.method = getattr(self.object,arg)
        return getattr(self,'caller')
        
    def caller(self,*args):
        if self.methodName in self.tml_log_method_names:
            i = self.tml_log_method_argnr[self.methodName]
            self.tml_calls.append( (time.time(), self.methodName, tuple(args[0:i])) + args[i:])
            print self.tml_calls[-1]
        return apply(self.method,args)
        
    def getLog(self):
        return self.tml_calls
        
        
class ImageCache:
    """ Provides a global cache for PhotoImages displayed in the 
        application. Singleton Pattern """
    
    images = None	
    
    def __init__(self):
        if ImageCache.images == None:
            ImageCache.images = {}
            
    def __getitem__(self, relURL):
        """ Given a relative URL to an image file return the 
            corresponding PhotoImage. """
        try:    
            if relURL not in self.images.keys():
                ImageCache.images[relURL] = PhotoImage(file=relURL)
            return ImageCache.images[relURL]
        except IndexError, IOError:
            import logging
            log = logging.getLogger("GatoUtil.py")
            log.exception("Error finding image %s" % relURL)
            
    def AddImage(self, relURL, imageData):
        ImageCache.images[relURL] = PhotoImage(data=imageData)
