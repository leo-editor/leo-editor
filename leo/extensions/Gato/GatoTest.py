#!/usr/bin/env python
################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   GatoTest.py
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
from Gato import *

testPath = "../CATBox/"

tests = [ ("04-MinimalSpanningTrees/Prim.alg",
           "04-MinimalSpanningTrees/MinimalSpanningTrees08.cat"),
          ("04-MinimalSpanningTrees/Kruskal.alg",
           "04-MinimalSpanningTrees/MinimalSpanningTrees08.cat"),
          ("06-MaximalFlows/FordFulkerson.alg",
           "06-MaximalFlows/FordFulkerson3.cat"),
          ("06-MaximalFlows/PreflowPush.alg",
           "06-MaximalFlows/PreflowPush2.cat")
        ]


if __name__ == '__main__':
    app = AlgoWin()    
    app.algorithm.logAnimator=1
    globals()['gInteractive'] = 0
    print "GatoTest",globals()['gInteractive']
    
    for case in tests:
        print "=== TEST ===",case[0],"===",case[1],"==="
        app.OpenAlgorithm(testPath + case[0])
        globals()['gInteractive'] = 0
        app.algorithm.ClearBreakpoints()
        app.update_idletasks()
        app.update()
        app.OpenGraph(testPath + case[1])
        app.update_idletasks()
        app.update()
        # Run it ...
        app.after_idle(app.CmdContinue) # after idle needed since CmdStart
        # does not return
        app.CmdStart()
        app.update_idletasks()
        #app.mainloop()
