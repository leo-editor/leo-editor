#Leo's demo.py plugin

The demo.py plugin helps presenters run dynamic demos from Leo files.

- [Overview](../doc/demo.md#overview)
- [Demo scripts](../doc/demo.md#demo-scripts)
- [Example scripts](../doc/demo.md#example-scripts)
- [Helper methods](../doc/demo.md#helper-methods)
    - [Images](../doc/demo.md#images)
    - [Menus](../doc/demo.md#menus)
    - [Starting and ending](../doc/demo.md#starting-and-ending)
    - [Typing](../doc/demo.md#typing)
- [Magnification and styling](../doc/demo.md#magnification-and-styling)
- [Details](../doc/demo.md#details)
- [Acknowledgements](../doc/demo.md#acknowledgements)

#Overview

A **script tree**, a tree of **demo scripts**, controls the demo. Demo scripts free the presenter from having to type correctly or remember sequences of desired actions. 

The **demo-next** command executes the next demo script.  The plugin ends the presentation just after executing the last demo script. The **demo-end** command ends the demo early.

To start a demo, presenters run a **top-level script**. Top-level scripts instantiate the Demo class, and then call demo.start(p), where p is the root of the script tree. For example:
```python
import leo.plugins.demo as demo

class Demo_1(demo.Demo):
    
    def setup(self, p):
        fn = 'c:/demos/demo1.leo'
        demo.user_dict['c'] = g.openWithFileName(fn, old_c=c)
        
    def teardown():
        c = demo.user_dict.get('c')
        if c: c.close()

Demo_1(c).start(g.findNodeInTree(c, p, 'demo1-commands'))
```

This plugin boasts significant advantages compared with Leo's screencast plugin:

- The demo plugin does not interfere with focus or key-handling. As a result, the full power of Leo scripting is available to demo scripts. Few helper methods are needed.

- Demo scripts can (and should) be descriptive. Subclasses of demo.Demo can define methods that hide implementation and configuration details.

- Demo scripts can insert fixed delays, callouts and subtitles. As a result, demo scripts can be fully automated. There is little need for post-production editing.

#Demo scripts

Demo scripts have access to c, g and p as usual.  Demo scripts also have access to the predefined **demo** variable, bound to the Demo instance. This allows demo scripts to use all the **helper methods** in the Demo class. These methods can:

- Simulate typing in headlines, body text, the minibuffer, or anywhere else.
- Overlay a scaled image on the screen.
- Open any Leo menu, selecting particular menu items.
- Scale font sizes.

For example, this demo script executes the insert-node command:

```python
    demo.key('Alt-x')
    demo.keys('insert-node\n')
```

Within the script tree, **@ignore** and **@ignore-tree** work as expected. The demo-script command ignores any nodes whose headline starts with `@ignore`, and ignores entire trees whose root node's headline starts with `@ignore-tree`.

**Note**: The demo-next command executes demo scripts *in the present outline*. Demo scripts may create new outlines, thereby changing the meaning of c. It is up to each demo script to handle such complications.

#Example scripts
This section *teaches by example* by giving short demo scripts.

emo scripts may free use all of Leo's scripting API.

##Show typing in the minibuffer
```python
'''Show typing in the minibuffer.'''
demo.key('Alt+x')
demo.keys('insert-node')
demo.wait(2)
demo.key('\n')
```

##Show typing in a headline
```pythonc.insertHeadline()
c.redraw()
c.editHeadline()
demo.head_keys('My Headline')
demo.wait(1)
c.endEditing()

# wrapper = c.edit_widget(p)
# wrapper.setSelectionRange(0, len(p.h))
```

##Switching focus
```python
'''Switch focus to the tree.'''
c.treeWantsFocusNow()

# Other possibilities:
    # c.bodyWantsFocusNow()
    # c.logWantsFocusNow()
    # c.minibufferWantsFocusNow()
```

##Select all headline text
```python
'''Begin editing a headline and select all its text.'''
c.editHeadline()
wrapper = c.edit_widget(p)
wrapper.setSelectionRange(0, len(p.h))
```

#Helper methods

The following sections describe all public ivars and helper methods of the Demo class.

The valid values for `pane` arguments are the strings, "body", "log" or "tree".

Helper methods call `c.undoer.setUndoTypingParams(...)` only if the `undo` keyword argument is True.  Methods without an `undo` argument do not support undo .

##Ivars

**demo.user_dict**

This ivar is a Python dictionary that demo scripts may freely use.

**demo.n1** and **demo.n2**

These ivars determine the speed of the simulated typing provided by the following methods. Demo scripts may change either at any time. If both are given, each character is followed by a wait of between n1 and n2 seconds. If n2 is None, the wait is exactly n1. The default values are 0.02 and 0.175 seconds, respectively.

**demo.speed**

This ivar is initially 1.0.  The demo.wait method multiplies both the n1 nd n2 ivars by the speed factor before waiting.  So using demo.speed factor is the easy way to adjust simulated typing speed.

##Images

**demo.caption(s, pane)**

Creates a caption with text s in the indicated pane. A **caption** is a text area that overlays part of Leo's screen. By default, captions have a distinctive yellow background. The appearance of captions can be changed using Qt stylesheets. See below.

**demo.image(pane,fn,center=None,height=None,width=None)**

Overlays an image in a pane.

- `pane`: Valid values are 'body', 'log' or 'tree'.
- `fn`: The path to the image file, relative to the leo/Icons directory for relative paths.
- `height`: Scales the image so it has the given height.
- `width`: Scales the image i so it has the given width.
- `center`: If True, centers the image horizontally in the given pane.

##Menus

**demo.open_menu(menu_name)**

Opens the menu whose name is given, ignoring case and any non-alpha characters in menu_name. This method shows all parent menus, so demo.open_menu('cursorback') suffices to show the `Cmds\:Cursor/Selection\:Cursor Back...` menu.

**demo.dismiss_menubar()**

Close the menu opened with demo.open_menu.

##Starting and ending

**demo.setup(p)**

May be overridden in subclasses. Called before executing the first demo script.

**demo.start(p)**

Starts a demo. p is the root of demo script tree. 

**demo.end()**

Ends the demo and calls the teardown script. The demo automatically ends after executing the last demo script.

**demo.teardown()**

May be overridden in subclasses. Called when the demo ends.

##Typing

**demo.body_keys(s, undo=False)**

Simulates typing the string s in the body pane.

**demo.head_keys(s, undo=False)**

Simulates typing the string s in the body pane.

**demo.keys(s, undo=False)**

Simulates typing the string s in the present widget.

**demo.key(setting)**

Types a single key in the present widget. This method does not support undo. Examples:
```python
   demo.key('Alt-X') # Activate the minibuffer
   demo.key('Ctrl-F') # Execute Leo's Find command
```

#Magnification and styling

**demo.set_text_delta(self, delta, w=None)**

Updates the style sheet for the given widget w (default is the body pane). Delta increases the text size by the given number of points.

Presenters may alter the appearance of captions by using changing the
following stylesheet::

```css
    QPlainTextEdit#democaption {
        background-color: yellow;
        font-family: DejaVu Sans Mono;
        font-size: 18pt;
        font-weight: normal; /* normal,bold,100,..,900 */
        font-style: normal; /* normal,italic,oblique */
    }
```

You will find this stylesheet in the node @data
``qt-gui-plugin-style-sheet`` in leoSettings.leo or myLeoSettings.leo.

#Details

- Demo scripts can not be undone/redone in a single step, unless each demo script makes *itself* undoable.

- Leo's undo command is limited to the presently selected outline. If a demo script opens another outline, there is no *automatic* way of selecting the previous outline.

- Chaining from one script to another using demo.next() cause a recursion. This would be a problem only if a presentation had hundreds of demo scripts.

#Acknowledgements

Edward K. Ream wrote this plugin on January 29-31, 2017, using Leo's screencast plugin as a starting point. 

The [demo-it](https://github.com/howardabrams/demo-it/blob/master/demo-it.org) inspired this plugin. Or perhaps the screencast plugin inspired demo-it.

