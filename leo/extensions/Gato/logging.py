################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   logging.py
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

import sys

class Logger:
    """ This is a no-frills place holder resembling logging.py from
        http://www.red-dove.com/python_logging.html API-wise (restricted to
        whats needed for Gato) until the 'real' logging.py becomes part of
        the standard distribution. Please dont use or redistribute it.
    """
    def __init__(self, module = None):
        self.module = module
        
    def log(self, message, prefix, exc_info = None):
        if verbose is not None:
            if self.module == None:
                print "%s: %s" %(prefix, message)
            else:
                print "%s: [%s] %s" %(prefix, self.module, message)
            if exc_info:
                exc_info = sys.exc_info()           
                #print exc_info
                import traceback
                traceback.print_exc(file=sys.stdout) # Prettier output
                
    def info(self, message):
        self.log(message,"INFO")
        
    def debug(self, message):
        self.log(message,"DEBUG")
        
    def error(self, message):
        self.log(message,"ERROR")
        
    def exception(self, message):
        self.log(message,"EXCEPTION", exc_info = 1)
        
    def critical(self, message):
        self.log(message,"CRITICAL")
        
        
def info(message):
    log = getLogger(None)
    log.info(message)
    
def debug(message):
    log = getLogger(None)
    log.debug(message)
    
def error(message):
    log = getLogger(None)
    log.error(message)
    
def exception(message):
    log = getLogger(None)
    log.exception(message)
    
def critical(message):
    log = getLogger(None)
    log.critical(message)
    
def getLogger(module = None):
    return Logger(module)
    
    
verbose = None
