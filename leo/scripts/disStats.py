#@+leo-ver=4
#@+node:EKR.20040502195213:@file-thin ../scripts/disStats.py
# routines to gather static statistics about opcodes based on dis module.
import leoGlobals as g
from leoGlobals import true,false

import compiler,dis,os,string,sys,types

#@+others
#@+node:EKR.20040502195213.1:go
def go():
	
	dir = "c:/prog/leoCVS/leo/"
	modules = getModules(dir)
	stats = [0] * 256
	try:
		# Importing these might start leo itself and hang idle.
		modules.remove("leo")
		modules.remove("openLeo")
		modules.remove("openEkr")
		modules.remove("setup")
	except: pass
	# print modules
	
	for m in modules:
		try:
			print "module:", m
			exec("import " + m)
			a = eval(m)
			any(a,stats)
		except:
			import traceback ; traceback.print_exc()
			print "----- no matching class in", m
			
	g.print_stats(stats)
#@nonl
#@-node:EKR.20040502195213.1:go
#@+node:EKR.20040502195213.2:getFiles
def getFiles (dir):
	
	from leoGlobals import os_path_join,os_path_split,os_path_splitext

	# Generate the list of modules.
	allFiles = os.listdir(dir)
	files = []
	for f in allFiles:
		head,tail = g.os_path_split(f)
		root,ext = g.os_path_splitext(tail)
		if ext==".py":
			files.append(g.os_path_join(dir,f))
			
	return files
#@nonl
#@-node:EKR.20040502195213.2:getFiles
#@+node:EKR.20040502195213.3:getModules
def getModules (dir):
	
	"""Return the list of Python files in dir."""
	
	from leoGlobals import os_path_split,os_path_splitext
	
	files = []
	
	try:
		allFiles = os.listdir(dir)
		for f in allFiles:
			head,tail = g.os_path_split(f)
			fn,ext = g.os_path_splitext(tail)
			if ext==".py":
				files.append(fn)
	except: pass
			
	return files
#@nonl
#@-node:EKR.20040502195213.3:getModules
#@+node:EKR.20040502195213.4:any
def any(x,stats,printName = 0):
	# based on dis.dis()
	"""Gathers statistics for classes, methods, functions, or code."""
	if not x:
		return
	if type(x) is types.InstanceType:
		x = x.__class__
	if hasattr(x, 'im_func'):
		x = x.im_func
	if hasattr(x, 'func_code'):
		x = x.func_code
	if hasattr(x, '__dict__'):
		items = x.__dict__.items()
		items.sort()
		for name, x1 in items:
			if type(x1) in (types.MethodType,
							types.FunctionType,
							types.CodeType):
				if printName: print name
				try:
					any(x1,stats)
				except TypeError, msg:
					print "Sorry:", msg
	elif hasattr(x, 'co_code'):
		code(x,stats)
	else:
		raise TypeError, \
			  "don't know how to disassemble %s objects" % \
			  type(x).__name__
#@nonl
#@-node:EKR.20040502195213.4:any
#@+node:EKR.20040502195213.5:code
def code (co, stats):
	"""Gather static count statistics for a code object."""

	codeList = co.co_code
	# Count the number of occurances of each opcode.
	i = 0 ;  n = len(codeList)
	while i < n:
		c = codeList[i]
		op = ord(c)
		stats[op] += 1
		i = i+1
		if op >= dis.HAVE_ARGUMENT:
			i = i+2
#@nonl
#@-node:EKR.20040502195213.5:code
#@+node:EKR.20040502195213.6:print_stats
def print_stats (stats):

	stats2 = [] ; total = 0
	for i in xrange(0,256):
		if stats[i] > 0:
			stats2.append((stats[i],i))
		total += stats[i]

	stats2.sort()
	stats2.reverse()
	for stat,i in stats2:
		print string.rjust(repr(stat),6), dis.opname[i]
	print "total", total
#@nonl
#@-node:EKR.20040502195213.6:print_stats
#@-others
#@nonl
#@-node:EKR.20040502195213:@file-thin ../scripts/disStats.py
#@-leo
