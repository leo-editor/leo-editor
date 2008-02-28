################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   AnimationHistory.py
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

import time
from GatoGlobals import gBlinkRate

class AnimationCommand:

    def __init__(self, method, target, args, undo_method=None, undo_args=None):
        self.target = target
        self.method = method
        self.args = args
        
        self.undo_method = undo_method
        self.undo_args = undo_args
        
        
    def Do(self):
        apply(self.method, self.target + self.args)
        
    def Undo(self):
        if self.undo_method == None:
            apply(self.method, self.target + self.undo_args)
        else:
            apply(self.undo_method, self.target + self.undo_args)
            
            
class AnimationHistory:
    """AnimationHistory provides a history of animation commands, and a undo and
       redo facility. It is to be used as a wrapper around a GraphDisplay and it
       will happily dispatch all calls to GraphDisplay.
    
       Animation commands for which undo/redo is provided, have to be methods of
       AnimationHistory
    """
    def __init__(self, animator):
        self.animator = animator
        self.history = []
        self.history_index = None
        
        #========== Provide Undo/Redo for animation commands from GraphDisplay ======
    def SetVertexColor(self, v, color):
        # print 'SetVertexColor', v, color
        animation = AnimationCommand(self.animator.SetVertexColor, (v,), (color,), 
                                     undo_args=(self.animator.GetVertexColor(v),))
        animation.Do()
        self.append(animation)
        
        #SetAllVerticesColor
        #SetAllEdgesColor
        
    def SetEdgeColor(self,tail, head, color):
        # print 'SetEdgeColor', tail, head, color
        animation = AnimationCommand(self.animator.SetEdgeColor, (tail,head), (color,),
                                     undo_args=(self.animator.GetEdgeColor(tail,head),))
        animation.Do()
        self.append(animation)
        
    def BlinkVertex(self, v, color=None):
        # print 'BlinkVertex', v, color
        animation = AnimationCommand(self.animator.BlinkVertex, (v,), (color,))
        animation.Do()
        self.append(animation)
        
    def BlinkEdge(self, tail, head, color=None):
        # print 'BlinkEdge', tail, head, color 
        animation = AnimationCommand(self.animator.BlinkEdge, (tail,head), (color,))
        animation.Do()
        self.append(animation)
        
        
    def SetVertexFrameWidth(self,v,val):
        # print 'SetVertexFrameWidth', v, val
        animation = AnimationCommand(self.animator.SetVertexFrameWidth, (v,), (val,),
                                     undo_args=(self.animator.GetVertexFrameWidth(v),))        
        animation.Do()
        self.append(animation)
        
    def SetVertexAnnotation(self,v,annotation,color="black"):
        # print 'SetVertexAnnotation',v,annotation,color
        animation = AnimationCommand(self.animator.SetVertexAnnotation, (v,), (annotation,),
                                     undo_args=(self.animator.GetVertexAnnotation(v),))                      
        animation.Do()
        self.append(animation)
        
        
        #========== Handle all other methods from GraphDisplay =====================
    def __getattr__(self,arg):
        # This is broken. Calls to self.animator methods as args in self.animator method
        # calls should fail.
        tmp = getattr(self.animator,arg)
        if callable(tmp):
            self.methodName = arg
            self.method = tmp
            return getattr(self,'caller')
        else:
            return self.animator.__dict__[arg]
            
    def caller(self,*args):
        # print self.methodName,"(",args,")"
        return apply(self.method,args)
        
        #========== AnimationHistory methods =======================================
    def Undo(self):
        if self.history_index == None: # Have never undone anything
            self.history_index = len(self.history) - 1
            
        if self.history_index >= 0:
            self.history[self.history_index][1].Undo()
            self.history_index -= 1
            
    def Do(self):
        if self.history_index is None:
            return
        if self.history_index >= len(self.history):
            self.history_index = None
        else:       
            self.history[self.history_index][1].Do()
            self.history_index += 1
            
    def DoAll(self):
        # Catchup
        if self.history_index is not None:
            for time, cmd in self.history[self.history_index:]:
                cmd.Do()
            self.history_index = None
            
    def Replay(self):
        if len(self.history) > 1:
            self.history[-1][1].Undo()
            self.animator.update()
            self.animator.canvas.after(10*gBlinkRate)
            self.history[-1][1].Do()
            self.animator.update()
            self.animator.canvas.after(10*gBlinkRate)
            self.history[-1][1].Undo()
            self.animator.update()
            self.animator.canvas.after(10*gBlinkRate)
            self.history[-1][1].Do()
            self.animator.update()
            
    def append(self, animation):
        #print "AnimationHistory: appending animation", animation.method
        self.history.append((time.time(), animation))
        
