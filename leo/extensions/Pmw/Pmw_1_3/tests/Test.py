# Functions used by widget tests.

import imp
import os
import re
import string
import sys
import traceback
import types
import Tkinter
import _tkinter

if Tkinter.TkVersion >= 8.4:
  refcountafterdestroy = 7
else:
  refcountafterdestroy = 6

script_name = imp.find_module(__name__)[1]
if not os.path.isabs(script_name):
    script_name = os.path.join(os.getcwd(), script_name)

while 1:
    script_dir = os.path.dirname(script_name)
    if not os.path.islink(script_name):
	break
    script_name = os.path.join(script_dir, os.readlink(script_name))
script_dir = os.path.join(os.getcwd(), script_dir)
script_dir = os.path.normpath(script_dir)
 
# Add the '../../..' directory to the path.
package_dir = os.path.dirname(script_dir)
package_dir = os.path.dirname(package_dir)
package_dir = os.path.dirname(package_dir)
sys.path[:0] = [package_dir]

import Pmw
# Need to import TestVersion, rather than do its work here, since
# __name__ will be known there.
import TestVersion

# Set this to 1 to generate tracebacks on exceptions, rather than
# catching them and continuing with the tests.
# This is useful for debugging the test scripts.
dont_even_try = 0

_delay = 1
_verbose = 0
_printTraceback = 0
_initialised = 0

##############################################################################
# Public functions:

rand = 12345
def random():
    global rand
    rand = (rand * 125) % 2796203
    return rand

def initialise():
    global _initialised, font, flagup, earthris, emptyimage, \
            stringvar, floatvar, root, reliefs
    if not _initialised:
	root = Tkinter.Tk(className = 'PmwTest')
	root.withdraw()
        if os.name == 'nt':
            size = 16
        else:
            size = 12
        Pmw.initialise(root, size = size, fontScheme = 'pmw2')
	font = {}
	font['small'] = '6x13'
	font['large'] = '10x20'
	font['variable'] = '-Adobe-Helvetica-Bold-R-Normal--*-120-*-*-*-*-*-*'
	flagup = Tkinter.BitmapImage(file = 'flagup.bmp')
	earthris = Tkinter.PhotoImage(file = 'earthris.gif')
	emptyimage = Tkinter.PhotoImage()
	stringvar = Tkinter.StringVar()
	stringvar.set('this is some text')
	floatvar = Tkinter.DoubleVar()
	floatvar.set(50.0)
	if haveBlt():
	    global vectorSize, vector_x, vector_y
	    vector_x = Pmw.Blt.Vector()
	    vector_y = []
	    for y in range(3):
		vector_y.append(Pmw.Blt.Vector())
	    vectorSize = 50
	    for index in range(vectorSize):
		vector_x.append(index)
		vector_y[0].append(random() % 100)
		vector_y[1].append(random() % 200)
		vector_y[2].append(random() % 100 + 300)

	# "solid" relief type was added to 8.0
	if Tkinter.TkVersion >= 8.0:
	  reliefs = 'flat, groove, raised, ridge, solid, or sunken'
	else:
	  reliefs = 'flat, groove, raised, ridge, or sunken'

	_initialised = 1

def haveBlt():
    return Pmw.Blt.haveblt(root)

def bell():
    root.bell()

def setdelay(newdelay):
    global _delay
    _delay = newdelay

def setverbose(newverbose):
    global _verbose
    _verbose = newverbose

def printtraceback(newprintTraceback = 1):
    global _printTraceback
    _printTraceback = newprintTraceback

def num_options(widget):
    return len(widget.configure())

def callback():
    return 1

def callback1(dummy):
    # Callback taking 1 argument
    return dummy

def callback2(dummy1, dummy2):
    # Callback taking 2 arguments
    return (dummy1, dummy2)

def callbackN(*args):
    # Callback taking zero or more arguments
    return args

def actioncallback():
    w = currentWidget()
    w.action('button press')

def currentWidget():
    return _currentWidget

def delay():
    return _delay

def set_geom(width, height):
    _currentToplevel.geometry(str(width) + 'x' + str(height))

def runTests(allTestData):
    root.after(_delay, _runTest, None, None, allTestData, 0, -1, -1)
    root.mainloop()

_pattern = None

##############################################################################
# Private functions:

def _print_results(result, expected, description):
    if type(expected) == types.ClassType:
	if hasattr(result, '__class__'):
	    ok = (result.__class__ == expected)
	else:
	    ok = 0
    else:
	ok = (result == expected)

	# Megawidgets return a value of the correct type.  Tk widgets
	# always return a string, so convert the string and check again.
	if not ok:
	    if type(expected) == types.InstanceType:
	      if result == str(expected) and (
                  expected is earthris or expected is stringvar or
		  expected is floatvar or expected is flagup):
	        ok = 1
              elif hasattr(_tkinter, 'Tcl_Obj') and \
                    type(result) == _tkinter.Tcl_Obj:
                  ok = (str(stringvar) == result.string)
	    elif type(expected) == types.IntType:
		if type(result) is types.StringType:
		    try:
			ok = (string.atoi(result) == expected)
		    except ValueError:
			pass
                elif hasattr(_tkinter, 'Tcl_Obj') and \
                        type(result) == _tkinter.Tcl_Obj:
                    ok = (string.atoi(str(result)) == expected)
	    elif type(expected) == types.FloatType:
		if type(result) is types.StringType:
		    try:
			ok = (string.atof(result) == expected)
		    except ValueError:
			pass
	    elif expected == callback:
		ok = re.search('^[0-9]*callback$', str(result)) is not None
	    elif expected == callback1:
		ok = re.search('^[0-9]*callback1$', str(result)) is not None
	    elif expected == callback2:
		ok = re.search('^[0-9]*callback2$', str(result)) is not None
	    elif expected == actioncallback:
		ok = re.search('^[0-9]*actioncallback$',str(result)) is not None
        
    if not ok or _verbose > 0:
	print '====', description
	if not ok or _verbose > 1:
	    print '==== result was:'
	    print result, type(result)
    if ok:
	if _verbose > 1:
	    print '++++ PASSED'
    else:
        print '---- result should have been:'
	print expected, type(expected)
	if _printTraceback:
	    traceback.print_exc()
	print '---- FAILED'
	print

def _destroyToplevel(top, title):
    if _verbose > 0:
	print '==== destruction of Toplevel for', title
    top.destroy()

def _Toplevel(title):
    if _verbose > 0:
	print '==== construction of Toplevel for', title
    top = Tkinter.Toplevel()
    top.geometry('+100+100')
    top.title(title)
    return top

def _constructor(isWidget, top, classCmd, kw):
    if _verbose > 0:
	print '====', classCmd.__name__, 'construction'
    if isWidget:
	if dont_even_try:
	    w = apply(classCmd, (top,), kw)
	else:
	    try:
		w = apply(classCmd, (top,), kw)
	    except:
		print 'Could not construct', classCmd.__name__
		traceback.print_exc()
		print 'Can not continue'
		print 'Bye'
		return None

	isMegaWidget = hasattr(classCmd, 'defineoptions')
	# Check the option types:
	options = w.configure()
	option_list = options.keys()
	option_list.sort()
	for option in option_list:
	    # Some of the options (like bd, bg and fg) have only two parts
	    # and are just abbreviations.  Only check 'real' options.
	    if len(options[option]) == 5:
		initoption = isMegaWidget and w.isinitoption(option)
		if dont_even_try:
		    value = w.cget(option)
		    if option not in ('class', 'container') and not initoption:
		      apply(w.configure, (), {option : value})
		      newvalue = w.cget(option)
		      if newvalue != value:
			print '====', classCmd.__name__, 'widget', \
			  '\'' + option + '\'', 'option'
			print '---- setting option returns different value'
                        print '==== new value was:'
                        print newvalue, type(newvalue)
                        print '---- set value was:'
                        print value, type(value)
			print '---- FAILED'
			print
		else:
		    try:
			value = w.cget(option)
			if option not in ('class', 'container') and not initoption:
			  try:
			      apply(w.configure, (), {option : value})
			      newvalue = w.cget(option)
                              if hasattr(_tkinter, 'Tcl_Obj') and \
                              (
                                    (type(newvalue) == _tkinter.Tcl_Obj
                                        and str(newvalue) != str(value))
                                    or
                                    (type(newvalue) != _tkinter.Tcl_Obj
                                        and newvalue != value)
                              ) or \
                              (
                                  not hasattr(_tkinter, 'Tcl_Obj') and
                                    newvalue != value
                              ):
				print '====', classCmd.__name__, 'widget', \
				  '\'' + option + '\'', 'option'
				print '---- setting option returns different value'
                                print '==== new value was:'
                                print `newvalue`, type(newvalue)
                                print '---- set value was:'
                                print `value`, type(value)
				print '---- FAILED'
				print
			  except:
			    print '====', classCmd.__name__, 'widget', \
			      '\'' + option + '\'', 'option'
			    print '---- could not set option'
			    print '---- FAILED'
			    print
		    except KeyError:
			print '====', classCmd.__name__, 'widget', \
			    '\'' + option + '\'', 'option'
			print '---- unknown option'
			print '---- FAILED'
			print

	if hasattr(classCmd, 'geometry'):
	    w.geometry('+100+100')
	    w.title(classCmd.__name__)
    else:
	w = apply(classCmd, (), kw)
    return w

def _destructor(widget, isWidget):
    if _verbose > 0:
        print '====', widget.__class__.__name__, 'destruction'
    if isWidget:
	if dont_even_try:
	    widget.destroy()
	else:
	    try:
		widget.destroy()
                ref = sys.getrefcount(widget)
                if ref != refcountafterdestroy:
                    print '====', widget.__class__.__name__, 'destructor'
                    print '---- refcount', ref, 'not zero after destruction'
                    print '---- FAILED'
                    print
	    except:
		print 'Could not destroy', widget.__class__.__name__
		traceback.print_exc()
		print 'Can not continue'
		print 'Bye'
		return None
    return 1

# Structure of allTestData:
# (
#   (
#     'ButtonBox', 
#     (
#       (
#         Pmw.ButtonBox,
#         {},
#         (
#           (c.pack, ()),
#           (c.pack, ()),
#           (c.pack, ()),
#           ...
#         )
#       ),
#       (
#         Pmw.ButtonBox,
#         {},
#         (
#           (c.pack, ()),
#           (c.pack, ()),
#           (c.pack, ()),
#           ...
#         )
#       ),
#       ...
#     )
#   ),
#   (
#     'ButtonBox', 
#     (
#       (
#         Pmw.ButtonBox,
#         {},
#         (
#           (c.pack, ()),
#           (c.pack, ()),
#           (c.pack, ()),
#           ...
#         )
#       ),
#       (
#         Pmw.ButtonBox,
#         {},
#         (
#           (c.pack, ()),
#           (c.pack, ()),
#           (c.pack, ()),
#           ...
#         )
#       ),
#       ...
#     )
#   ),
#   ...
# )

def _runTest(top, w, allTestData, index0, index1, index2):
    if index0 >= len(allTestData):
	root.quit()
	return
    classCmd, fileTests = allTestData[index0]
    if classCmd == Tkinter.Menu:
	isToplevel = 1
    else:
	isToplevel = hasattr(classCmd, 'userdeletefunc')
    isWidget = hasattr(classCmd, 'cget')
    title = classCmd.__name__

    if index1 == -1:
	if isToplevel:
	    top = None
	else:
	    top = _Toplevel(title)
	global _currentToplevel
	_currentToplevel = top
	index1 = 0
    elif index1 >= len(fileTests):
	if not isToplevel:
	    _destroyToplevel(top, title)
	index1 = -1
	index0 = index0 + 1
    else:
	methodTests, kw = fileTests[index1]
	if index2 == -1:
	    w = _constructor(isWidget, top, classCmd, kw)
	    if w is None:
	        root.quit()
		return
	    global _currentWidget
	    _currentWidget = w
	    index2 = 0
	elif index2 >= len(methodTests):
	    if _destructor(w, isWidget) is None:
	        root.quit()
		return
	    index2 = -1
	    index1 = index1 + 1
	else:
	    methodTestData = methodTests[index2]
	    if type(methodTestData[0]) == types.StringType:
		_configureTest(w, methodTestData)
	    else:
		_methodTest(w, methodTestData)
	    index2 = index2 + 1
    root.update()
    root.after(_delay, _runTest, top, w, allTestData, index0, index1, index2)

def _configureTest(w, testData):
    option = testData[0]
    value = testData[1]
    if dont_even_try:
	apply(w.configure, (), {option: value})
	result = w.cget(option)
    else:
	try:
	    apply(w.configure, (), {option: value})
	    result = w.cget(option)
	except:
	    result = _getErrorValue()
    if len(testData) > 2:
	expected = testData[2]
    else:
	expected = value
    _print_results(result, expected, \
	w.__class__.__name__ + ' option ' + str(testData))

def _getErrorValue():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    if type(exc_type) == types.ClassType:
	# Handle python 1.5 class exceptions.
	exc_type = exc_type.__name__
    if type(exc_value) == types.StringType:
	return exc_type + ': ' + exc_value
    else:
        exc_value_str = str(exc_value)
        if exc_value_str[:1] == "'" and exc_value_str[-1:] == "'":
            exc_value_str = exc_value_str[1:-1]
        return str(exc_type) + ': ' + exc_value_str

def _methodTest(w, testData):
    func = testData[0]
    args = testData[1]
    kw = {}
    expected = None
    if len(testData) == 3:
	if type(testData[2]) == types.DictionaryType:
	    kw = testData[2]
	else:
	    expected = testData[2]
    elif len(testData) > 3:
	kw = testData[2]
	expected = testData[3]
    if type(args) != types.TupleType:
	args = (args,)
    if func is num_options:
	args = (w,) + args
    origArgs = args
    if type(func) == types.MethodType and func.im_self is None:
	args = (w,) + args
    if dont_even_try:
	result = apply(func, args, kw)
    else:
	try:
	    result = apply(func, args, kw)
	except:
	    result = _getErrorValue()
    if hasattr(func, 'im_func'):
	name = w.__class__.__name__ + ' method ' + \
	    func.im_func.func_code.co_name
    else:
	name = 'function ' + func.__name__
    name = name + ' ' + str(origArgs)
    if kw:
	name = name + ' ' + str(kw)
    _print_results(result, expected, name)
