.. rst3: filename: html/theory.html

#########################
Exploring Leo's Code Base
#########################

.. |br| raw:: html

   <br />
   
This chapter is for anyone who wants to understand Leo's code base,
including those who want to be one of Leo's implementors.

You already know that leoFind.py and leoUndo.py implement Leo's find and
undo command, and so on.

This chapter focuses on the *process* of finding your way around Leo's
code, not the myriad details you will find within Leo's code.

It's actually very easy! Try it. You'll see.

Reading this chapter should take about 20 minutes.

.. contents:: Contents
    :depth: 3
    :local:

How to explore Leo's sources
++++++++++++++++++++++++++++

You can learn *anything* about Leo, provided that you can cause Leo to execute the relevant code. That's usually very easy!

- It should be straightforward to isolate the module or modules involved.
- The next several sections give hints about finding interesting code.
- Once you find a bit of interesting code, use g.pdb or g.trace to study it.

The following sections provide more details...

Finding commands
****************

Leo creates commands in two ways:

1. Using the @g.command(command-name) decorator.

2. Using tables, usually getPublicCommands methods in various classes.

For example, to find the code for the sort-lines command, search for
sort-lines. You will find::

    'sort-lines':    self.sortLines,
    
Now search for "def sortLines" and you have arrived.

Finding key-handling code
*************************

The following methods and their helpers all have useful traces:

- leoQtEventFilter.eventFilter (qtGui.py) and helpers create keystrokes 
  (LeoKeyEvents) from QKeyEvent events.

- k.masterKeyHandler (leoKeys.py) receives LeoKeyEvents from eventFilter
  and invokes one of Leo's commands based on the users bindings.

- k.getArg handles commands like Ctrl-F (search-with-present-options)
  that prompt the user for input.

Finding redraw and refocus code
*******************************

c.outerUpdate and helpers eliminate flicker by redrawing the screen only at
the end of each command.

c.outerUpdate contains several sophisticated and useful traces.

qtGui.set_focus (qtGui.py) is the only place that actually explicitly sets
focus in Leo. Enabling a trace there can be useful.

Finding all uses of a symbol
****************************

Just use cff (clone-find-all-flattened).  This is my workhorse command when fixing complex bugs.

Debugging with g.trace, g.callers & g.pdb
*****************************************

Once you know approximately where to look, it is easy to use traces to
discover what is going on. To trace the last n (default 4) callers of any
function::

    g.trace(g.callers(n))
    
Many complex methods define a trace variable::

    trace = False and not g.unitTesting
    
A good rule of thumb: the more complex a method is, the more useful its
traces are likely to be.

You can also to use g.pdb() to single-step through the code.
I typically use g.pdb() only for deep mysteries!

**Note**: you must run Leo from a console window to use either g.trace or
g.pdb. I recommend always running Leo from a console.

The design of Leo's classes
+++++++++++++++++++++++++++

Leo uses a model/view/controller architecture.

- Controller: The Commands class and its helpers in leoCommands.py and leoEditCommands.py.

- Model (data): The VNode and Position classes in leoNodes.py.

- View: The gui-independent base classes are in the node "Gui Base Classes". The Qt-Specific subclasses are in the node "Qt gui".

.. _`David Parnas`:   http://en.wikipedia.org/wiki/David_Parnas
.. _`Glenford Myers`: http://en.wikipedia.org/wiki/Glenford_Myers

In Leo, each class hides (encapsulates) the details of its internal workings from user (client) classes. This design principle has been spectacularly successful. Leo's overall design has remained remarkably stable for 20 years, even as the internal details of many classes have radically changed. Two computer scientists influenced my thinking greatly: `David Parnas`_ and `Glenford Myers`_.

The distinction between gui-dependent and gui-independent is important. Almost all gui-dependent code resides in the plugins folder. Leo's core code is almost completely gui independent.

Leo's core typically assumes that w (an abstract widget) is a subclass of the baseTextWidget class. This class implements the DummyHighLevelInterface interface. Actually, w is usually a LeoQTextBrowser or leoQtBaseTextWidget object, defined in qtGui.py. These classes provide thin wrappers for corresponding Qt widgets.

Wrapper classes are useful, regardless of gui independence:

- Wrapper classes often simplify the corresponding code in Leo's code.
- Wrapper classes provide convenient methods for debugging and tracing.

Fragile methods
+++++++++++++++

The following methods are surprisingly fragile. Change them only after careful thought. Make *sure* to run all unit tests after changing them in any way:

- leoTree.select and c.selectPosition switch nodes.

- c.endEditing ends editing in a headline and updates undo data.

- leoBody.onBodyChanged updates undo data when body text changes.

- baseNativeTree.onHeadChanged (baseNativeTree.py) updates undo data.

  **Note**: This method overrides leoTree.onHeadChanged (leoFrame.py),
  which is not used.

In addition, *all* event handling in baseNativeTree.py is extremely fragile. Don't even think about changing this code unless you know exactly what you are doing.

Read long comments with caution
+++++++++++++++++++++++++++++++

Several modules contain long comments::

    << about new sentinels >> (leoAtFile.py)
    << about the leoBridge module >> (leoBridge.py)
    << how to write a new importer >> (leoImport.py)
    << How Leo implements unlimited undo >> (leoUndo.py)
    << about gui classes and gui plugins >>
    << About handling events >> (leoFrame.py)
    << Theory of operation of find/change >> (leoFind.py)
    << Key bindings, an overview >> (leoKeys.py)
    << about 'internal' bindings >> (leoKeys.py)
    << about key dicts >> (leoKeys.py)
    
These comments may be helpful, but do *not* assume that they are accurate. When in doubt, trust the code, not the comments.

Startup
+++++++

The LoadManager (LM) class (in leoApp.py) is responsible for initing all objects and settings. This is a complex process. Here is the big picture:

- The LM reads each local (non-settings) file twice. The first load discovers the settings to be used in the second load. This ensures that proper settings are *available* during the second load.

- Ctors init settings "early", before calling the ctors for subsidiary objects. This ensures that proper settings are *in effect* for subsidiary ctors.

Unicode
+++++++

Leo's grand strategy for handling text is as follows:

1. Internally, Leo uses unicode objects for all text.

2. When reading files or user input, Leo converts all plain (encoded)
   strings to unicode.

3. When reading or writing files, Leo converts unicode strings to encoded
   strings.
   
To make this strategy work, Leo must know the encoding used for external files. This is why Leo supports the @encoding directive and various encoding-related settings.

The g.toUnicode and g.toEncodedString functions convert to and from unicode. These methods catch all unicode-related exceptions.

The g.u function should be used *only* to convert from the Qt string type (a wrapper for a unicode string) to unicode. Do not use g.u instead of g.toUnicode.

Why key handling is complex
+++++++++++++++++++++++++++

Leo's key handling is complex because it does inherently complex things:

- Code in various places translate user key bindings to dictionaries.

- eventFilter and its helpers translates incoming QKeyEvents to LeoKeyEvents.

- k.masterKeyHandler associates incoming LeoKeyEvents with
  mode-and-pane-dependent bindings.
  
Much of this complexity is a direct result in the flexibility given to users in specifying key bindings.

Leo must have sentinels, even without clones
++++++++++++++++++++++++++++++++++++++++++++

Sentinels are necessary for clones, but sentinels would still be necessary if clones did not exist.

Sentinels create **identity**, the notion that a particular nodes starts at *this* place in the external file and extends to *this other* place. Identity is a persistent, invariant attribute of a file: Leo recreates all the nodes of the external files when re-reading the file.

It's really that simple, but here are some consequences:

1. Identity remains even when the contents of a node changes. Thus, there is *no way* to use content-related mechanisms to recreate identity. Git can never help recover identity.

2. Leo's sentinels mark an *arbitrary* range of text within the external file. @auto files can never be as flexible as @file nodes.

Setting focus
+++++++++++++

Leo's handling of focus is complicated in order to reduce unwanted screen flash. The following methods queue *requests* for focus::

    c.bodyWantsFocus()
    c.logWantsFocus()
    c.minibufferWantsFocus()
    c.treeWantsFocus()
    c.widgetWantsFocus(w)
    
Similarly, c.redraw and c.recolor queue requests to redraw the outline pane and to recolorize the body pane.
    
c.outerUpdate honors all requests after the present command completes, that is, just before idle time.

Sometimes a command requires that an action happen immediately.  The following methods queue a request and then immediately call c.outerUpdate::

    c.bodyWantsFocusNow()
    c.logWantsFocusNow()
    c.minibufferWantsFocusNow()
    c.recolor_now()
    c.redraw_now()
    c.treeWantsFocusNow()
    c.widgetWantsFocusNow(w)

