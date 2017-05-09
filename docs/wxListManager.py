from wxPython.wx import *
from wxPython.lib.mixins.listctrl import wxListCtrlAutoWidthMixin

import os
import time
import pickle
import socket
import select
import random
import ConfigParser
import threading
import re
import sys

from pywintypes import CreateGuid
from win32com.client import Dispatch
#import win32pdh
import win32api
#from win32com.client import constants #--> just needed two constants...

import MySQLdb
import sqlite
import mx.DateTime

from LMDialogs import CalendarDialog, ModifierDialog, TicklerDialog, MailDialog,LoggerDialog, FinishedDialog, FindDialog, EvalDialog, TreeDialog, StartupDialog
#from wxTreeCtrl import TreeDialog

from printout import PrintTable
cwd = os.getcwd()
DIRECTORY = os.path.split(cwd)[0]
os.chdir(DIRECTORY)
del cwd

#Outlook Constants
olMailItem = 0x0
olFlagMarked = 0x2

OFFLINE_ONLY = False #False-> Online only  ; True-> Online and Offline possible; REMOTE_HOST = None -> Offline only

VERSION = '1.02'
#File Menu-----------------#
idNEWLIST = 1000
idOPENLIST = 1010
idCLOSELIST = 1015
idCLOSEALL = 1017
idSAVEAS = 1020
idDELETELIST = 1025
idPAGESETUP = 1030
idPRINT = 1035
idPRINTPREV = 1040
idMAILLIST = 1045
idOFFLINE = 1048
idEXIT = 1050

#Edit Menu-----------------
idCUT = 1055
idCOPY = 1060
idPASTE = 1065
idDELETEITEMS = 1070
idCOMBINEITEMS = 1075
idFIND = 1080

#Item Menu-------------------
idNEWITEM = 1085
idTOGGLEFINISHED = 1090
idEDITOWNER = 1095
idDUEDATE = 1100
idEDITNOTE = 1105
idMAILITEM =1110

#Diplay Menu---------------------
idSHOWFINISHED = 1115
idSHOWALL = 1120
idREFRESH = 1125
idDISPLAYDATE = 1130

#Tool Menu------------------------
idTICKLERACTIVE = 1135
idSHOWNEXT = 1140
idSYNC = 1145
idARCHIVE = 1150
idEVALUATE = 1155
idTOOLPRINT = 1165
idSENDTO = 1170

#Help Menu-------------------------
idABOUT = 1175
idHELP = 1180
config_file = os.path.join(DIRECTORY, "List Manager.ini")
defaults = dict(pw='python', db='listmanager', ext='txt', local='wxLMDB:sqlite', x='700', y='400')
cp = ConfigParser.ConfigParser(defaults=defaults)
cp.read(config_file) #ConfigParser closes the file

USER = cp.has_option('User','user') and cp.get('User','user') or win32api.GetUserName()

# the following all have default values provided in the constructor
PW = cp.get('User','pw')
DB = cp.get('Database','db')
NOTE_EXT = cp.get('Note','ext')
LOCAL_HOST = cp.get('Hosts','local')
X = cp.getint('Configuration','x')
Y = cp.getint('Configuration','y')

# the folloowing default to None
MAIL_LIST_PATH = cp.has_option('Mail','path') and cp.get('Mail','path') or None
QUICK_LIST = cp.has_option('User','quicklist') and cp.get('User','quicklist') or None

# the following default to False
STARTUP_DIALOG = cp.has_option('User','startup_dialog') and cp.getboolean('User','startup_dialog')
DELETE_LIST = cp.has_option('User','delete_list') and cp.getboolean('User','delete_list')
OUTLOOK = cp.has_option('Mail','outlook') and cp.getboolean('Mail','outlook')

if cp.has_option('Hosts','remote'):
    REMOTE_HOST = cp.get('Hosts','remote')
else:
    REMOTE_HOST = None
    OFFLINE_ONLY = True
    
# reading it again because of the way defaults are handled
cp = ConfigParser.ConfigParser()
cp.read(config_file) #ConfigParser closes the file

if cp.has_section('Synchronization'):
    SYNC_TABLES = [t[1] for t in cp.items('Synchronization')]
else:
    SYNC_TABLES = ['follow_ups']

class ListManager(wxFrame):
	def __init__(self, parent, id, title, size):
	    wxFrame.__init__(self, parent, id, title, size = size)
	
	    self.SetIcon(wxIcon('bitmaps//wxpdemo.ico', wxBITMAP_TYPE_ICO))
	    self.CreateStatusBar()
	  
		self.PropertyDicts = []
		self.ItemLists = []
		self.ListCtrls = []
		self.OwnerLBoxes = []
		
		self.L = -1
		self.curIdx = -1
		
		self.printdata = wxPrintData()
		self.printdata.SetPaperId(wxPAPER_LETTER)
		self.printdata.SetOrientation(wxPORTRAIT)
		
		#self._options = {} #would be used in loadconfig
		
		self.copyitems = []    
		self.modified = {}
		self.tickler_active = False
		
		#there is a wxPanel in the AddListControl method so each wxListCtrl has a different panel as parent
		#there is a nb_sizer = wxNotebookSizer(nb) class but doesn't seem to make any difference
		
		self.editor = []
		
		self.Cursors = {}
		self.sqlite_connections = []
		self.popupvisible = False
		self.in_place_editor = None
		self.showrecentcompleted = 0
		
		self.LC_font = wxFont(9, wxSWISS, wxNORMAL, wxNORMAL)
		
		self.date_titles = {'createdate':"Create Date",'duedate':"Due Date",'timestamp':"Last Modified",'finisheddate':"Completion Date"}
		self.attr2col_num = {'priority':0, 'name':1,'owners':2, 'date':3}
		
		self.FindDialog = FindDialog(self, "Find...", "")
		self.EvalDialog = EvalDialog(self, "Evaluate...", "")
		filemenu = wxMenu()
		filemenu.Append(idNEWLIST, "New List...", "Create a new List")
		filemenu.Append(idOPENLIST, "Open List...", "Open a List")
		filemenu.Append(idCLOSELIST, "Close", "Close the current List")
		filemenu.Append(idCLOSEALL, "Close All", "Close all open Lists")
		filemenu.Append(idSAVEAS, "Save As Text File...", "Save the current List")
		filemenu.AppendSeparator()
		filemenu.Append(idDELETELIST, "Delete List...", "Select a list to delete")
		filemenu.AppendSeparator()
		filemenu.Append(idPAGESETUP, "Page Setup...")
		filemenu.Append(idPRINT, "Print...", "Print the current view")
		filemenu.Append(idPRINTPREV, "Print Preview")
		filemenu.AppendSeparator()
		filemenu.Append(idMAILLIST, "Mail...", "Mail the current view")
		filemenu.AppendSeparator()
		filemenu.AppendCheckItem(idOFFLINE, "Work Offline")
		filemenu.AppendSeparator()
		filemenu.Append(idEXIT, "Exit", "Exit the program")
		
		editmenu = wxMenu()
		editmenu.Append(idCUT, "Cut\tCtrl+X")
		editmenu.Append(idCOPY, "Copy\tCtrl+C")
		editmenu.Append(idPASTE, "Paste\tCtrl+V")
		editmenu.AppendSeparator()
		editmenu.Append(idDELETEITEMS, "Delete")
		editmenu.AppendSeparator()
		editmenu.Append(idCOMBINEITEMS, "Combine Items...")
		editmenu.AppendSeparator()
		editmenu.Append(idFIND, "Find...")
		
		itemmenu = wxMenu()
		itemmenu.Append(idNEWITEM, "New Item")
		itemmenu.AppendSeparator()
		itemmenu.Append(idTOGGLEFINISHED, "Toggle Finished")
		itemmenu.Append(idEDITOWNER, "Owner...")
		itemmenu.Append(idDUEDATE, "Due Date...")
		itemmenu.Append(idEDITNOTE, "Note...")
		itemmenu.AppendSeparator()
		itemmenu.Append(idMAILITEM, "Mail...")
		
		displaymenu = wxMenu()
		displaymenu.Append(idSHOWFINISHED, "Show/Hide Finished...")
		displaymenu.AppendSeparator()
		displaymenu.Append(idSHOWALL, "Show All", "Show all items in the current list")
		displaymenu.AppendSeparator()
		displaymenu.Append(idREFRESH, "Refresh Display", "Refresh the Display")
		displaymenu.Append(idDISPLAYDATE, "Select Date to Display")
		
		toolmenu = wxMenu()
		toolmenu.AppendCheckItem(idTICKLERACTIVE, "Tickler Active")
		toolmenu.Check(idTICKLERACTIVE,False)
		toolmenu.Append(idSHOWNEXT, "Show Next Reminder")
		toolmenu.Append(idSYNC, "Synchronize local and remote DBs")
		toolmenu.Append(idARCHIVE, "Archive completed items in list...")
		toolmenu.Append(idEVALUATE, "Evaluate an expression...")
		
		helpmenu = wxMenu()
		helpmenu.Append(idABOUT, "About ListManager")
		helpmenu.Append(idHELP, "Help")
		
		menubar = wxMenuBar()
		menubar.Append(filemenu, '&File')
		menubar.Append(editmenu, 'Edit')
		menubar.Append(itemmenu, 'Item')
		menubar.Append(displaymenu, 'Display')
		menubar.Append(toolmenu, 'Tools')
		menubar.Append(helpmenu, 'Help')
		self.SetMenuBar(menubar)
		toolmenu.Enable(idSHOWNEXT,self.tickler_active)
		filemenu.Enable(idDELETELIST,DELETE_LIST)
		filemenu.Check(idOFFLINE,OFFLINE_ONLY)
		
		#file history
		self.filehistory = wxFileHistory()
		self.filehistory.UseMenu(filemenu)
		
		tb = self.CreateToolBar(wxTB_HORIZONTAL|wxTB_FLAT)
		
		tb.AddLabelTool(idNEWLIST, "New (local) List", wxBitmap('bitmaps\\new.bmp'), shortHelp="Create New List")
		tb.AddLabelTool(idOPENLIST, "Open", wxBitmap('bitmaps\\open.bmp'), shortHelp="Open List")
		tb.AddSeparator()
		tb.AddLabelTool(idTOOLPRINT, "Print", wxBitmap('bitmaps\\print.bmp'), shortHelp="Print List")
		tb.AddLabelTool(idPRINTPREV, "Preview", wxBitmap('bitmaps\\preview.bmp'), shortHelp="Print Preview")
		tb.AddLabelTool(idPAGESETUP, "Setup", wxBitmap('bitmaps\\setup.bmp'), shortHelp="Page Setup")
		tb.AddSeparator()
		tb.AddLabelTool(idNEWITEM, "New Item", wxBitmap('bitmaps\\new_item.bmp'), shortHelp="Create New Item")
		tb.AddSeparator()
		tb.AddLabelTool(idREFRESH, "Refresh", wxBitmap('bitmaps\\refresh.bmp'), shortHelp="Refresh Display")     
		tb.AddSeparator()
		tb.AddLabelTool(idEDITNOTE, "Edit Note", wxBitmap('bitmaps\\edit_doc.bmp'), shortHelp="Edit Note")
		tb.AddSeparator()
		tb.AddLabelTool(idFIND, "Find", wxBitmap('bitmaps\\find.bmp'), shortHelp = "Find Item")        
		tb.AddSeparator()
		tb.AddLabelTool(idCUT, "Cut", wxBitmap('bitmaps\\editcut.bmp'), shortHelp ="Cut Item")        
		tb.AddLabelTool(idCOPY, "Copy", wxBitmap('bitmaps\\copy.bmp'), shortHelp ="Copy Item")
		tb.AddLabelTool(idPASTE, "Paste", wxBitmap('bitmaps\\paste.bmp'), shortHelp="Paste Item")
		tb.AddSeparator()
		tb.AddLabelTool(idTOGGLEFINISHED, "Toggle Date", wxBitmap('bitmaps\\filledbox.bmp'), shortHelp="Toggle Finished Date")
		tb.AddLabelTool(idDELETEITEMS, "Delete", wxBitmap('bitmaps\\delete.bmp'), shortHelp="Delete Item")
		tb.AddLabelTool(idDUEDATE, "Due Date", wxBitmap('bitmaps\\calendar.bmp'), shortHelp="Enter Due Date")
		tb.AddLabelTool(idEDITOWNER,"Owner", wxBitmap('bitmaps\\owners.bmp'), shortHelp="Select Owner(s)")
		tb.AddSeparator()
		tb.AddLabelTool(idMAILITEM, "Mail", wxBitmap('bitmaps\\mail.bmp'), shortHelp="Mail Item")
		
		if QUICK_LIST:
		    tb.AddSeparator()
		    tb.AddLabelTool(idSENDTO, "Send to", wxBitmap('bitmaps\\sendto.bmp'), shortHelp="Send to %s"%QUICK_LIST)
		    
		tb.Realize()
		#File Menu ------------------------------------
		EVT_MENU(self, idNEWLIST, self.OnNewList)
		EVT_MENU(self, idOPENLIST, self.OnOpenList)
		EVT_MENU(self, idCLOSELIST, self.OnCloseList)
		EVT_MENU(self, idCLOSEALL, self.OnCloseAll)
		EVT_MENU(self, idSAVEAS, self.OnSaveAsText)
		EVT_MENU(self, idDELETELIST, self.OnDeleteList)
		EVT_MENU(self, idPAGESETUP, self.OnPageSetup)
		EVT_MENU(self, idPRINT, self.OnPrint)
		EVT_MENU(self, idPRINTPREV, lambda e: self.OnPrint(e, prev=True))
		EVT_MENU(self, idOFFLINE, self.OnWorkOffline)
		EVT_MENU(self, idMAILLIST, self.OnMailView)      
		EVT_MENU_RANGE(self, wxID_FILE1, wxID_FILE9, self.OnFileList)
		EVT_MENU(self, idEXIT, self.OnExit)
		#Edit Menu ------------------------------------
		EVT_MENU(self, idCUT, lambda e: self.OnCopyItems(e, cut=True))        
		EVT_MENU(self, idCOPY, self.OnCopyItems)
		EVT_MENU(self, idPASTE, self.OnPasteItems)
		EVT_MENU(self, idDELETEITEMS, self.OnDeleteItems)
		EVT_MENU(self, idCOMBINEITEMS, self.OnCombineItems)
		EVT_MENU(self, idFIND, self.OnFind)
		#item Menu ------------------------------------
		EVT_MENU(self, idNEWITEM, self.OnNewItem)
		EVT_MENU(self, idTOGGLEFINISHED, self.OnToggleFinished)             
		EVT_MENU(self, idDUEDATE, self.OnDueDate)
		EVT_MENU(self, idEDITOWNER, self.OnEditOwner)
		EVT_MENU(self, idEDITNOTE, self.OnEditNote)
		EVT_MENU(self, idMAILITEM, self.OnMailItem)
		#Dips Menu ------------------------------------
		EVT_MENU(self, idSHOWFINISHED, self.OnShowFinished)
		EVT_MENU(self, idSHOWALL, self.OnShowAll)
		EVT_MENU(self, idREFRESH, self.OnRefresh)
		EVT_MENU(self, idDISPLAYDATE, self.OnDisplayDateCategory)
		#Tool Menu ---------------------------------------
		EVT_MENU(self, idTICKLERACTIVE, self.OnActivateTickler)
		EVT_MENU(self, idSHOWNEXT, self.OnShowTickler)
		EVT_MENU(self, idSYNC, self.OnSync)
		EVT_MENU(self, idARCHIVE, self.OnArchive)
		EVT_MENU(self, idEVALUATE, self.OnShowEvaluate)
		#Help Menu -----------------------------------------
		EVT_MENU(self, idABOUT, self.OnShowAbout)
		EVT_MENU(self, idHELP, self.OnShowHelp)
		
		EVT_TOOL(self, idTOOLPRINT, lambda e: self.OnPrint(e,showprtdlg=False))
		
		if QUICK_LIST:
		    EVT_TOOL(self, idSENDTO, lambda e: self.OnMoveToSpecificList(e,QUICK_LIST))
		upper_panel = wxPanel(self, -1)   #size = (900,400)
		bottom_panel = wxPanel(self, -1, size = (900,150)) #900 note that 000 seems to work???
		
		nb = wxNotebook(upper_panel, -1, size=(900,500), style=wxNB_BOTTOM)
		
		f = wxFont(10, wxSWISS, wxNORMAL, wxNORMAL)
		self.name = wxTextCtrl(bottom_panel, -1, size = (285,42), style = wxTE_MULTILINE|wxTE_RICH2)#34 #wxTE_PROCESS_ENTER
		self.name.SetDefaultStyle(wxTextAttr("BLACK", font = f))
		     
		self.owners = wxTextCtrl(bottom_panel, -1, size = (250,42),style = wxTE_MULTILINE|wxTE_RICH2)
		self.owners.SetDefaultStyle(wxTextAttr("BLACK", font = f))
		
		self.note = wxTextCtrl(bottom_panel, -1, size = (400,50), style=wxTE_MULTILINE)
		 		#Appears necessary to really get the listcontrol to size with the overall window  
		#upper_panel sizer
		sizer = wxBoxSizer(wxHORIZONTAL)
		sizer.Add(nb,1,wxALIGN_LEFT|wxEXPAND)
		upper_panel.SetSizer(sizer)        
		
		#sizer for the row of data items
		box = wxBoxSizer(wxHORIZONTAL)
		box.Add(self.name,1,wxEXPAND)
		box.Add(self.owners,0)
		
		#bottom_panel sizer  
		sizer = wxBoxSizer(wxVERTICAL)        
		sizer.AddSizer(box, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5)
		sizer.Add(self.note,1,wxALIGN_LEFT|wxEXPAND)
		bottom_panel.SetSizer(sizer)
		
		sizer = wxBoxSizer(wxVERTICAL)
		sizer.Add(upper_panel,1,wxALIGN_TOP|wxEXPAND)
		sizer.Add(bottom_panel,0,wxALIGN_TOP|wxEXPAND)
		
		self.SetAutoLayout(1)
		self.SetSizer(sizer)
		#sizer.Fit(self) #actively does bad things to the dimensions on startup
		EVT_TEXT(self, self.name.GetId(), lambda e: self.modified.update({'name':1}))
		EVT_TEXT(self, self.note.GetId(), lambda e: self.modified.update({'note':1}))
		EVT_TEXT(self, self.owners.GetId(), lambda e: self.modified.update({'owners':1}))
		
		EVT_CLOSE(self, self.OnWindowExit)
		
		EVT_IDLE(self, self.OnIdle)
		
		self.toolmenu = toolmenu
		self.filemenu = filemenu
		self.nb = nb
		self.tb = tb
		if OUTLOOK:
		    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a TCP socket
		    s.bind(('localhost',8888)) # Bind to port 8888
		    s.listen(5) # Listen, but allow no more than
		    self.sock = s
		try:
		    pathlist = [f[1] for f in cp.items('Files')]
		except:
		    pathlist = []
		    
		if pathlist:
		    pathlist.sort()
		    pathlist.reverse()
		    for path in pathlist[1:]:
		        self.OnFileList(path=path)
		
		    #don't want to trigger the page change event until n-1 of n files are loaded
		    EVT_NOTEBOOK_PAGE_CHANGED(self,nb.GetId(),self.OnPageChange)
		
		    self.OnFileList(path=pathlist[0])
		else:
		    EVT_NOTEBOOK_PAGE_CHANGED(self,nb.GetId(),self.OnPageChange)
		
		
		
		ID_TIMER = wxNewId()
		self.timer = wxTimer(self, ID_TIMER) 
		EVT_TIMER(self,  ID_TIMER, self.OnIdle)
		self.timer.Start(3000)
	    
	    ownerthread = threading.Thread(target=self.createownerlist)
	    ownerthread.start()
	    self.ModifierDialog = None
	
	def createownerlist(self):
	    
	    if REMOTE_HOST and OFFLINE_ONLY is False:
	        cursor = self.GetCursor(REMOTE_HOST)
	        sql = "SHOW TABLES" #sorted
	    else:
	        cursor = self.GetCursor(LOCAL_HOST)
	        sql = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
	        
	    cursor.execute(sql)
	    results = cursor.fetchall()
	
	    #excluding 'system' tables and archive tables
	    excluded_tables = ['user_sync','sync','owners']
	    tables = [t for (t,) in results if t.find('_archive')== -1 and t not in excluded_tables]
	
	    sql_list = []
	    for table in tables:
	        sql_list.append("""SELECT owner1 FROM %s UNION SELECT owner2 FROM %s UNION SELECT owner3 FROM %s"""%((table,)*3))
	                
	    sql = " UNION ".join(sql_list)
	    cursor.execute(sql)
	    results = cursor.fetchall()
	    
	    _list = [x[0] for x in results]
	    if '' in _list:
	        _list.remove('')
	    if None in _list:
	        _list.remove(None)
	        
	    self._list = _list
	    
	    #posting custom event to signal that this thread is done
	    evt = wxPyEvent()
	    evt_id = wxNewEventType()
	    evt.SetEventType(evt_id)
	    self.Connect(-1, -1, evt_id, self.createownerdialog)
	    wxPostEvent(self, evt)
	
	def createownerdialog(self, evt=None):
	    self.ModifierDialog = ModifierDialog(parent=self, title="Select owner(s)", size=(180,300), style=wxCAPTION, modifierlist = self._list)
	    del self._list
	
	def CreateNewNotebookPage(self, host, table):
	    
	    Properties = {'owner':'*ALL',
	                'LCdate':'duedate',
	                'sort':{'attribute':'priority','direction':0}, #these could be set in Config
	                'showfinished':0} #-1 show them all; 0 show none; integer show for that many days
	    
	    Properties['table'] = table
	    Properties['host'] = host
	                
	    self.PropertyDicts.append(Properties)
	
	    self.L = len(self.ItemLists)#could use self.ListCtrls, self.OwnerLBoxes, etc. with a -1
	    
	    results = self.ReadFromDB()
	    if results is None:
	        self.PropertyDicts = self.PropertyDicts[:-1]
	        self.L = self.L - 1
	        return
	        
	    panel = wxPanel(self.nb, -1, size = (900,400))
	    LCtrl = ListCtrl(panel, -1, style=wxLC_REPORT|wxSUNKEN_BORDER|wxLC_VRULES|wxLC_HRULES)
	    LCtrl.SetFont(self.LC_font)
	    self.ListCtrls.append(LCtrl)
	    
	    OLBox = wxListBox(panel, -1, size = (126,550), choices = [""], style=wxLB_SORT|wxSUNKEN_BORDER)
	    self.OwnerLBoxes.append(OLBox)
	    
	    sizer = wxBoxSizer(wxHORIZONTAL)
	    sizer.Add(OLBox,0,wxALIGN_LEFT|wxEXPAND)
	    sizer.Add(LCtrl,1,wxALIGN_LEFT|wxEXPAND)
	    panel.SetSizer(sizer)
	        
	    self.ItemLists.append(self.CreateAndDisplayList(results)) 
	
		cursor = self.GetCursor(host)
		if cursor is None:
		    print "Couldn't get cursor to fill OwnerListBox"
		    return
		    
		cursor.execute("SELECT owner1 FROM %s UNION SELECT owner2 FROM %s UNION SELECT owner3 FROM %s"%((table,)*3))
		
		owners = [x for (x,) in cursor.fetchall()]
		
		if None in owners:
		    owners.remove(None)
		if '' in owners:
		    owners.remove('')
		
		OLBox.Clear()
		for name in owners: 
		    OLBox.Append(name)
		OLBox.Append('*ALL')
		OLBox.SetSelection(0)
		
		LCId = LCtrl.GetId()
		EVT_LIST_ITEM_SELECTED(self, LCId, self.OnItemSelected)
		EVT_LIST_ITEM_ACTIVATED(self, LCId, self.OnDisplayInPlaceEditor)
		EVT_LEFT_DOWN(LCtrl, self.OnLeftDown) 
		EVT_LEFT_DCLICK(LCtrl, self.OnLeftDown)
		EVT_RIGHT_DOWN(LCtrl, self.OnRightDown)
		EVT_LIST_COL_CLICK(self, LCId, self.OnColumnClick)
		EVT_LIST_COL_RIGHT_CLICK(self, LCId, self.OnColumnRightClick)
		
		# the following is a ListBox event
		EVT_LISTBOX(self, OLBox.GetId(), self.OnFilterOwners)
		
	    
	    #img_num = LCtrl.arrows[Properties['sort']['direction']]
	    #LCtrl.SetColumnImage(self.attr2col_num[Properties['sort']['attribute']], img_num)
	    
	    rdbms = host.split(':')[1]
	    if rdbms == 'mysql':
	        tab_title = '%s (remote)'%table
	    else:
	        tab_title = table
	    
	    if table in SYNC_TABLES:
	        tab_title = '*'+tab_title
	                             
	    self.nb.AddPage(panel,tab_title)
	    self.nb.SetSelection(self.L)
	    
	    self.filehistory.AddFileToHistory('%s:%s'%(host,table))
	
	    self.SetStatusText("Successfully loaded %s"%tab_title)
	    
	def OnPageChange(self, evt=None):
	    if self.modified:
	        self.OnUpdate()
	        
	    self.L = L = self.nb.GetSelection()
	
		idx = self.ListCtrls[L].GetNextItem(-1, wxLIST_NEXT_ALL, wxLIST_STATE_SELECTED)
		if idx != -1:
		    self.curIdx = idx
		    #LCtrl.EnsureVisible(idx)
		    self.OnItemSelected()
		elif self.ItemLists[L]:
		    self.curIdx = 0
		    self.ListCtrls[L].SetItemState(0, wxLIST_STATE_SELECTED, wxLIST_STATE_SELECTED)
		    #the line above triggers an OnItemSelected EVT so don't need self.OnItemSelected() 092803
		else:
		    self.curIdx = -1
		
		location,rdbms = self.PropertyDicts[L]['host'].split(':')
		table = self.PropertyDicts[L]['table']
		self.SetTitle("List Manager:  %s:  %s:  %s"%(location,rdbms,table))
		
	    
	    evt.Skip() #051403
	    
	def OnShowTickler(self, evt=None):
	    if self.popupvisible:
	        return
	    
	    self.popupvisible = True
	    
	    host = 'wxLMDB:sqlite'
	    cursor = self.Cursors[host]
	    table = 'follow_ups'
	
	    sql = "SELECT COUNT() FROM "+table+" WHERE finisheddate IS NULL AND priority > 1"
	    cursor.execute(sql)
	    results = cursor.fetchone()
	
	    num_items = int(results[0])
	    
	    if not num_items:
	        return
	
	    if self.modified: #Should decide if this should be put back or not
	        self.OnUpdate()
	        
	    n = random.randint(0,num_items-1)
	
	    sql = "SELECT priority,name,createdate,finisheddate,duedate,owner1,owner2,owner3,id,timestamp,note FROM "+table+" WHERE finisheddate IS NULL AND priority > 1 LIMIT 1 OFFSET %d"%n
	    
	    try:
	        cursor.execute(sql)
	    except:
	        print "In OnShowTickler and attempt to Select an item failed"
	        return
	        
	    row = cursor.fetchone()
	    
	    class Item: pass
	    item = Item()
	
	    item.priority = int(row[0]) #int(row[0]) needs int because it seems to come back as a long from MySQL
	    item.name = row[1]
	    item.createdate = row[2]
	    item.finisheddate = row[3]
	    item.duedate = row[4]
	    item.owners = [z for z in row[5:7] if z is not None] #if you carry around ['tom',None,None] you have an issue when you go write it
	    item.id = row[8]
	    item.timestamp = row[9]
	    item.note = row[10]
	
	    dlg = TicklerDialog(self, "", "Do something about this!!!", size=(550,350))
	    TC = dlg.TC
	    
	    f = wxFont(14, wxSWISS, wxITALIC, wxBOLD, False)
	    TC.SetDefaultStyle(wxTextAttr("BLUE",wxNullColour, f))
	    TC.AppendText("%s..."%item.name)
	
	    if item.priority == 3:
	        TC.SetDefaultStyle(wxTextAttr("RED","YELLOW",f))
	    TC.AppendText("%d\n\n"%item.priority)
	    
	    f = wxFont(8, wxSWISS, wxNORMAL, wxNORMAL)
	    TC.SetDefaultStyle(wxTextAttr("BLACK","WHITE", f))
	    TC.AppendText("owners: %s\n"%", ".join(item.owners))
	    TC.AppendText("created on: %s\n"%item.createdate.Format('%m/%d/%y'))
	    if item.duedate:
	        ddate = item.duedate.Format('%m/%d/%y')
	    else:
	        ddate = "<no due date>"
	    TC.AppendText("due on: %s\n\n"%ddate)
	
	    note = item.note
	    if not note:
	        note = "<no note>"
	    TC.AppendText("%s\n\n"%note)
	    f = wxFont(10, wxSWISS, wxITALIC, wxBOLD)
	    TC.SetDefaultStyle(wxTextAttr("BLACK",wxNullColour, f))
	    TC.AppendText('follow_ups')
	    TC.ShowPosition(0)   #did not do anything
	    TC.SetInsertionPoint(0)
	    result = dlg.ShowModal()
	    dlg.Destroy()
	    self.popupvisible = False     
	
	    if result in (wxID_OK, wxID_APPLY):
	
	        for L,Properties in enumerate(self.PropertyDicts):
	            if Properties['table'] == table:
	                break
	        else:
	            print "Can't find %s"%table
	            return
	                    
	        self.nb.SetSelection(L) #if the page changes it sends a EVT_NOTEBOOK_PAGE_CHANGED, which calls OnPageChange
	        self.L = L
	        self.FindNode(item)
	        if result==wxID_APPLY:
	            self.OnMailItem(item)
	
	    elif result==wxID_FORWARD:
	        self.OnShowTickler()
	
	def OnActivateTickler(self, evt):
	    self.tickler_active = not self.tickler_active
	    self.toolmenu.Enable(idSHOWNEXT,self.tickler_active)
	
	    
	def OnMailItem(self, evt=None, item=None):
	    if item is None:
	        if self.curIdx == -1:
	            return
	        else:
	            item = self.ItemLists[self.L][self.curIdx]
	        
	    dlg = MailDialog(self,"Mail a reminder", size=(450,500),
	               recipients=item.owners,    
	               subject=item.name,
	               body=self.GetNote())          
	    result = dlg.ShowModal()
	    if result==wxID_OK:
	        outlook= Dispatch("Outlook.Application")
	        newMsg = outlook.CreateItem(olMailItem) #outlook.CreateItem(constants.olMailItem)
	        newMsg.To = to = dlg.RTC.GetValue()
	        newMsg.Subject = subject = dlg.STC.GetValue()
	        newMsg.Body = body = dlg.BTC.GetValue()
	
	        #newMsg.FlagStatus = constants.olFlagMarked
	        
	        newMsg.Display()
	
	        dlg.Destroy()            
	        #del outlook
	
	        self.note.SetSelection(0,0)
	        self.note.WriteText("**************************************************\n")
	        self.note.WriteText("Email sent on %s\n"%mx.DateTime.today().Format("%m/%d/%y"))
	        self.note.WriteText("To: %s\n"%to)
	        self.note.WriteText("Subject: %s\n"%subject)
	        self.note.WriteText("%s\n"%body)
	        self.note.WriteText("**************************************************\n")
	
	def OnMailView(self, evt=None):
	    recipients = [self.PropertyDicts[self.L]['owner']]
	    
	    body = ""
	    for i,item in enumerate(self.ItemLists[self.L]):
	        body = body+"%d. %s (%d)\n"%(i+1, item.name, item.priority)
	    
	    subject = "Follow-ups " + mx.DateTime.today().Format("%m/%d/%y")
	            
	    dlg = MailDialog(self,"Follow-up List", size=(450,500),
	               recipients=recipients,
	               subject=subject,
	               body=body)
	               
	    val = dlg.ShowModal()
	    dlg.Destroy()
	    if val==wxID_OK:
	        outlook= Dispatch("Outlook.Application")
	        newMsg = outlook.CreateItem(olMailItem) #outlook.CreateItem(constants.olMailItem)
	        newMsg.To = dlg.RTC.GetValue()
	        newMsg.Subject = dlg.STC.GetValue()
	        newMsg.Body = dlg.BTC.GetValue()
	
	        newMsg.FlagStatus = olFlagMarked #constants.olFlagMarked
	        newMsg.Categories = "Follow-up"
	        
	        newMsg.Display()
	    
	        #del outlook
	
	def OnCopyItems(self, event=None, cut=False):
	    if self.curIdx == -1:
	        return
	        
	    L = self.L
	    IList = self.ItemLists[L]
	    LCtrl = self.ListCtrls[L]
	    
		copyitems = []
		i = -1
		while 1:
		    i = LCtrl.GetNextItem(i, wxLIST_NEXT_ALL, wxLIST_STATE_SELECTED)
		    if i==-1:
		        break
		    item = IList[i]
		    item.notes = self.GetNote(L,item) #handles the database situation
		    copyitems.append(item)
		
		self.copyitems = copyitems	    
	    self.SetStatusText("%d items copied"%len(copyitems))
	    if cut:
	        self.OnDeleteItems()
	
	def OnPasteItems(self, evt=None, L=None): #noselect 051603
	    #used by OnMoveToList, OnMoveToSpecificList and called directly
	    if not self.copyitems:
	        print "Nothing was selected to be copied"
	        return
	        
	    if L is None: #this is not needed by OnMoveTo or OnDragToTab but is for a straight call
	        L = self.L
	        
	    Properties = self.PropertyDicts[L]
	    LCtrl = self.ListCtrls[L]
	    IList = self.ItemLists[L]
	    
	    items = self.copyitems
	    numitems = len(items)
	    
	    for item in items:
	
	        z = item.owners+[None,None,None]
	
	        id = self.GetUID() #we do give it a new id
	        host = Properties['host']
	        cursor = self.Cursors[host]
	        table = Properties['table']
	        
	        createdate = mx.DateTime.now() #need this or else it won't be seen as a new item when synching; would be seen as updated
	        command = "INSERT INTO "+table+" (priority,name,createdate,finisheddate,duedate,note,owner1,owner2,owner3,id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
	        cursor.execute(command,(item.priority,item.name,createdate,item.finisheddate,item.duedate,item.notes,z[0],z[1],z[2],id))
	        
	        timestamp = self.TimeStamper(host, cursor, table, id)
	        
	        #creating a new item breaks the connection between item.x and new_item.x
	        class Item: pass
	        new_item = Item()
	        new_item.id = id
	        new_item.priority = item.priority
	        new_item.owners = item.owners
	        new_item.name = item.name
	        new_item.timestamp = timestamp
	        new_item.duedate =item.duedate
	        new_item.finisheddate = item.finisheddate
	        new_item.createdate = createdate
	        IList.insert(0,new_item)
	        
	    self.DisplayList(IList,L)
	    
	    #If we didn't come from OnMoveToList or OnMoveToSpecificList where L != self.L
	    if L==self.L:
	        for i in range(numitems):
	            LCtrl.SetItemState(i, wxLIST_STATE_SELECTED, wxLIST_STATE_SELECTED)
	        self.curIdx = numitems-1
	
	
	
	def OnDeleteItems(self, event=None):
	    """Called directly and by OnCopyItems (cut = true)
	    """
	    if self.curIdx == -1: #not absolutely necessary but gets you out quickly
	        return
	        
	    L = self.L
	    LCtrl = self.ListCtrls[L]
	    IList = self.ItemLists[L]
	    Properties = self.PropertyDicts[L]
	    
	    i = -1
	    while 1:
	        i = LCtrl.GetNextItem(i, wxLIST_NEXT_ALL, wxLIST_STATE_SELECTED)
	        if i==-1:
	            break
	        item = IList.pop(i)
	        LCtrl.DeleteItem(i)
	
	        host = Properties['host']
	        cursor = self.Cursors[host]
	        table = Properties['table']
	        
	        cursor.execute("DELETE from "+table+" WHERE id = %s", (item.id,))
	            
	        #Track Deletes for Syncing ############################################
	        if table in SYNC_TABLES:
	            if host.split(':')[1] == 'sqlite':
	                timestamp = mx.DateTime.now()
	                cursor.execute("INSERT INTO sync (id,action,table_name,name,timestamp) VALUES (%s,%s,%s,%s,%s)",(item.id,'d',table,item.name,timestamp))
	            else:
	                cursor.execute("INSERT INTO sync (id,action,table_name,user,name) VALUES (%s,%s,%s,%s,%s)",(item.id,'d',table,USER,item.name))
	        #########################################################################
	        i-=1
	
	    self.name.Clear()
	    self.owners.Clear()
	    self.note.Clear()
	    #note that Clearing does cause self.modified -->{'name':1}
	    self.modified = {}
	    self.curIdx = -1
	
	def OnLeftDown(self, evt):
	    print "Here"
	    if self.modified:
	        #if inplace editor is open and you click anywhere (same or different row from current row) but in the editor itself then just to close editor
	        flag = self.modified.has_key('inplace')
	        self.OnUpdate()
	        if flag:
	            evt.Skip() #without Skip, EVT_LIST_ITEM_SELECTED is not generated if you click in a new row
	            return
	    
	    x,y = evt.GetPosition()
	    LCtrl = self.ListCtrls[self.L]
	    
	    #Using HitTest to obtain row clicked on because there was a noticable delay in the generation of an
	    #EVT_LIST_ITEM_SELECTED event when you click on the already selected row
	    idx,flags = LCtrl.HitTest((x,y))
	    
	    #if you are below rows of items then idx = -1 which could match self.curIdx = -1
	    if idx == -1:
	        return
	    
	    # only if you click on the currently selected row do the following events occur
	    if idx == self.curIdx:
	        if x < 18:
	            self.OnToggleFinished()
	        elif x < 33:
	            self.OnPriority()
	        elif x < 33 + LCtrl.GetColumnWidth(1):
	            self.OnDisplayInPlaceEditor()
	        elif x < 33 + LCtrl.GetColumnWidth(1) + LCtrl.GetColumnWidth(2): 
	            self.OnEditOwner()
	        else:
	            self.OnDueDate
	    else:
	        evt.Skip() #without Skip, EVT_LIST_ITEM_SELECTED is not generated if you click in a new row
	
	
	
	def OnRightDown(self, evt):
	    x,y = evt.GetPosition()
	    
	    sendtomenu = wxMenu()
	    
	    open_tables = []
	    for page,Properties in enumerate(self.PropertyDicts):
	        host,table = Properties['host'],Properties['table']
	        open_tables.append((host,table))
	        sendtomenu.Append(1+page,"%s (%s)"%(table,host))
	        EVT_MENU(self, 1+page, lambda e,p=page: self.OnMoveToList(e,p))
	        
	    sendtomenu.Delete(self.L+1) # don't send it to the page you're already on
	    sendtomenu.AppendSeparator()
	    
	    self.closed_tables = []
	    for host,cursor in self.Cursors.items():
	
	        location, rdbms = host.split(':')
	
	        if rdbms == 'sqlite':
	            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
	        elif rdbms == 'mysql':
	            cursor.execute("SHOW tables")
	
	        results = cursor.fetchall()
	        
	        page+=1
	        for (table,) in results:
	            if not ((host,table) in open_tables or table in ['user_sync','owners','sync']):
	                self.closed_tables.append((host,table))
	                sendtomenu.Append(1+page,"%s (%s)"%('*'+table,host))
	                EVT_MENU(self, 1+page, lambda e,p=page: self.OnMoveToList(e,p))
	                page+=1
	
	    self.PopupMenu(sendtomenu,(x+125,y+40))
	    sendtomenu.Destroy()
	
	def OnCombineItems(self, evt):
	    L = self.L
	    idx = self.curIdx
	    IList = self.ItemLists[L]
	    LCtrl = self.ListCtrls[L]
	    
	    combine_list = []
	    i = -1
	    while 1:
	        i = LCtrl.GetNextItem(i, wxLIST_NEXT_ALL, wxLIST_STATE_SELECTED)
	        if i==-1:
	            break
	        combine_list.append((IList[i].createdate,IList[i]))
	
	    
	    if len(combine_list) < 2:
	        print "Fewer than two items highlighted"
	        return
	    
	    combine_list.sort()
	    combine_list.reverse()
	    
	    dlg = wxMessageDialog(self,
	                        "Combine the %d selected items?"%len(combine_list),
	                        "Combine Items?",
	                        wxICON_QUESTION|wxYES_NO)
	                        
	    if dlg.ShowModal() == wxID_YES:
	        Properties = self.PropertyDicts[L]
	        host = Properties['host']
	        cursor = self.Cursors[host]
	        table = Properties['table']
	        
	        t_item = combine_list[0][1]
	        merge_list = combine_list[1:]
	        new_note = ""
	        
	        for date,item in merge_list:
	            note = self.GetNote(item=item)
	            date = date.Format("%m/%d/%y")
	            new_note = "%s\n%s %s\n\n%s"%(new_note, date, item.name, note)
	            
	            cursor.execute("DELETE from "+table+" WHERE id = %s", (item.id,))
	            #Track Deletes for Syncing ############################################
	            if table in SYNC_TABLES:
	                if host.split(':')[1] == 'sqlite':
	                    timestamp = mx.DateTime.now()
	                    cursor.execute("INSERT INTO sync (id,action,table_name,name,timestamp) VALUES (%s,%s,%s,%s,%s)",(item.id,'d',table,item.name,timestamp))
	                else:
	                    cursor.execute("INSERT INTO sync (id,action,table_name,user,name) VALUES (%s,%s,%s,%s,%s)",(item.id,'d',table,USER,item.name))
	            #########################################################################
	                
	        t_note = self.GetNote(item=t_item)
	        t_note = "%s\n%s"%(t_note,new_note)
	        
	        #What about combining owners?######################################
	        
	        cursor.execute("UPDATE "+table+" SET name = %s, note = %s WHERE id = %s", (t_item.name+"*",t_note,t_item.id))
	        t_item.timestamp = self.TimeStamper(host, cursor, table, t_item.id)
	        
	        self.OnRefresh()
	        LCtrl.SetItemState(0, 0, wxLIST_STATE_SELECTED)
	        IList = self.ItemLists[L]
	        id = t_item.id
	        idx = -1
	        for item in IList:
	            idx+=1
	            if id == item.id:
	                break
	        else:
	            idx = -1 
	    
	        #should never be -1
	        if idx != -1:	
	            LCtrl.SetItemState(idx, wxLIST_STATE_SELECTED, wxLIST_STATE_SELECTED)
	            LCtrl.EnsureVisible(idx)
	        self.curIdx = idx
	        
	    dlg.Destroy()
	
	def OnMoveToList(self, evt=None, page=0):
	    self.OnCopyItems(cut=True)
	    pc = self.nb.GetPageCount()
	    if page < pc:		
	        self.OnPasteItems(L=page)
	    else:
	        host,table = self.closed_tables[page-pc]
	        cursor = self.Cursors[host]# in ini self.Cursors[host]
	    
	        for item in self.copyitems:
	            z = item.owners+[None,None,None]
	            id = self.GetUID() #give it a new id
	            
	            #need this or else it won't be seen as a new item when syncing; would be seen as updated
	            createdate = mx.DateTime.now() 
	            command = "INSERT INTO "+table+" (priority,name,createdate,finisheddate,duedate,note,owner1,owner2,owner3,id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
	            cursor.execute(command,(item.priority,item.name,createdate,item.finisheddate,item.duedate,item.notes,z[0],z[1],z[2],id))
	            timestamp = self.TimeStamper(host, cursor, table, id)
	            
	    self.copyitems = []
	    
	def OnMoveToSpecificList(self, evt=None, table='follow_ups'):
	    matches = {}
	    for page,Properties in enumerate(self.PropertyDicts):
	        host,tble = Properties['host'],Properties['table']
	        if tble == table:
	            rdbms = host.split(':')[1]
	            matches[rdbms] = page
	        
	    self.OnCopyItems(cut=True)
	    
	    if matches:
	        if matches.get('mysql'):	
	            self.OnPasteItems(L=matches['mysql'])
	        else:
	            self.OnPasteItems(L=matches['sqlite'])
	    else:
	        cursor = self.Cursors[LOCAL_HOST]
	    
	        for item in self.copyitems:
	            z = item.owners+[None,None,None]
	            id = self.GetUID() #give it a new id
	            
	            #need this or else it won't be seen as a new item when syncing; would be seen as updated
	            createdate = mx.DateTime.now() 
	            command = "INSERT INTO "+table+" (priority,name,createdate,finisheddate,duedate,note,owner1,owner2,owner3,id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
	            cursor.execute(command,(item.priority,item.name,createdate,item.finisheddate,item.duedate,item.notes,z[0],z[1],z[2],id))
	            timestamp = self.TimeStamper(host, cursor, table, id)
	            
	    self.copyitems = []
	
	            
	
	def OnToggleFinished(self, evt=None):
	    L = self.L
	    LCtrl = self.ListCtrls[L]
	    Properties = self.PropertyDicts[L]
	    idx = self.curIdx
	
	    item = self.ItemLists[L][idx]
	    LC_Item = LCtrl.GetItem(idx)
	    
	    if not item.finisheddate:
	        item.finisheddate = mx.DateTime.today()
	        LC_Item.SetImage(LCtrl.idx0)
	    else:
	        item.finisheddate = None
	        LC_Item.SetImage(LCtrl.idx1)
	    
		if item.finisheddate:
		    #It appears that SetTextColour resets font weight to Normal but this makes no sense
		    #This means that all finished items have Normal weight whether they are priority 3,2 or 1
		    #May actually be that GetItem() and then SetItem() sets the weight to Normal no matter what it was originally
		    LC_Item.SetTextColour(wxLIGHT_GREY)
		    
		elif item.priority==1:
		    #see note above about SetTextColour apparently resetting weight
		    LC_Item.SetTextColour(wxBLACK)
		    
		elif item.priority==2:
		    #LC_Item.SetTextColour(wxBLACK) -- this line should be necessary but it does not appear to be
		    # ? font is black so ? if have to reset it
		    f = self.LC_font
		    f.SetWeight(wxBOLD)
		    LC_Item.SetFont(f)
		    f.SetWeight(wxNORMAL) # resetting font weight
		
		else:
		    LC_Item.SetTextColour(wxRED) #appears to be the only way to set color - can't through font
		    f = self.LC_font #LCtrl.font
		    f.SetWeight(wxBOLD)
		    LC_Item.SetFont(f)
		    f.SetWeight(wxNORMAL) # resetting font weight
		    
		LCtrl.SetItem(LC_Item)	
	    self.tb.EnableTool(30, True)
	    
	    host = Properties['host']	
	    cursor = self.Cursors[host]
	    table = Properties['table']
	    
	    cursor.execute("UPDATE "+table+" SET finisheddate = %s WHERE id = %s", (item.finisheddate, item.id))
	    item.timestamp = self.TimeStamper(host, cursor, table, item.id)
	    
	    if Properties['LCdate'] == 'timestamp':
	        LCtrl.SetStringItem(idx, self.attr2col_num['date'], item.timestamp.Format("%m/%d %H:%M:%S"))
	    elif Properties['LCdate'] == 'finisheddate':
	        LCtrl.SetStringItem(idx, self.attr2col_num['date'], item.finisheddate.Format('%m/%d/%y'))
	
	
	
	def OnPriority(self, event=None, input=None):
	    L = self.L
	    idx = self.curIdx
	    LCtrl = self.ListCtrls[L]
	    Properties = self.PropertyDicts[L]
	    item = self.ItemLists[L][idx]
	    
	    if input:
	        item.priority=input
	
	    else:
	        if item.priority < 3:
	            item.priority+= 1
	        else:
	            item.priority=1
	
	    LC_Item = LCtrl.GetItem(idx)
	
		if item.finisheddate:
		    #It appears that SetTextColour resets font weight to Normal but this makes no sense
		    #This means that all finished items have Normal weight whether they are priority 3,2 or 1
		    #May actually be that GetItem() and then SetItem() sets the weight to Normal no matter what it was originally
		    LC_Item.SetTextColour(wxLIGHT_GREY)
		    
		elif item.priority==1:
		    #see note above about SetTextColour apparently resetting weight
		    LC_Item.SetTextColour(wxBLACK)
		    
		elif item.priority==2:
		    #LC_Item.SetTextColour(wxBLACK) -- this line should be necessary but it does not appear to be
		    # ? font is black so ? if have to reset it
		    f = self.LC_font
		    f.SetWeight(wxBOLD)
		    LC_Item.SetFont(f)
		    f.SetWeight(wxNORMAL) # resetting font weight
		
		else:
		    LC_Item.SetTextColour(wxRED) #appears to be the only way to set color - can't through font
		    f = self.LC_font #LCtrl.font
		    f.SetWeight(wxBOLD)
		    LC_Item.SetFont(f)
		    f.SetWeight(wxNORMAL) # resetting font weight
		    
		LCtrl.SetItem(LC_Item)	
	    text = str(item.priority)        
	    LCtrl.SetStringItem(idx, 0, text)
	
	    host = Properties['host']
	    cursor = self.Cursors[host]
	    table = Properties['table']
	    
	    cursor.execute("UPDATE "+table+" SET priority = %s WHERE id = %s", (item.priority,item.id))
	    item.timestamp = self.TimeStamper(host, cursor, table, item.id)
	    
	    if Properties['LCdate'] == 'timestamp':
	        LCtrl.SetStringItem(idx, self.attr2col_num['date'], item.timestamp.Format('%m/%d %H:%M:%S'))
	        
	    wxCallAfter(LCtrl.SetFocus)
	    
	def OnDisplayInPlaceEditor(self,evt=None):
	    L = self.L
	    LCtrl = self.ListCtrls[L]
	    Properties = self.PropertyDicts[L]
	    idx = self.curIdx
	    item = self.ItemLists[L][idx]
	    
	    host = Properties['host']
	    cursor = self.Cursors[host]
	    table = Properties['table']
	        
	    #if self.Conflict(host, cursor, table, item): return #works -- may be overkill so i've commented it out
	    
	    TCid = wxNewId()
	    y = LCtrl.GetItemPosition(idx)[1] 
	    length = LCtrl.GetColumnWidth(1)
	
	    editor = wxTextCtrl(self, TCid, pos = (167,y+28), size = (length,23), style=wxTE_PROCESS_ENTER)
	    editor.SetFont(wxFont(9, wxSWISS, wxNORMAL, wxNORMAL))
	    editor.SetBackgroundColour(wxColour(red=255,green=255,blue=175)) #Yellow
	    editor.AppendText(item.name)
	    editor.Show(True)
	    editor.Raise()
	    editor.SetSelection(-1,-1)
	    editor.SetFocus()	
	    
	    EVT_TEXT_ENTER(self, TCid, self.OnCloseInPlaceEditor)		
	
	    self.in_place_editor = editor
	    self.modified['inplace'] = 1	
	
	
	
	
	
	def OnCloseInPlaceEditor(self,evt=None):
	    L = self.L
	    LCtrl = self.ListCtrls[L]
	    Properties = self.PropertyDicts[L]
	    idx = self.curIdx
	    item = self.ItemLists[L][idx]
	    
	    host = Properties['host']
	    cursor = self.Cursors[host]
	    table = Properties['table']
	    LCdate = Properties['LCdate']
	    
	    #if self.Conflict(host, cursor, table, item)...
	
	    text = self.in_place_editor.GetValue().strip()[:150]
	    item.name = text
	    LCtrl.SetStringItem(idx, self.attr2col_num['name'], text)
	    self.in_place_editor.Destroy()
	    
	    cursor.execute("UPDATE "+table+" SET name = %s WHERE id = %s", (text, item.id))
	    item.timestamp = self.TimeStamper(host, cursor, table, item.id)
	
	    if Properties['LCdate'] == 'timestamp':
	        LCtrl.SetStringItem(idx, self.attr2col_num['date'], item.timestamp.Format('%m/%d %H:%M:%S'))
	
	    self.name.Clear()
	    self.name.AppendText(text) #this will cause self.modified['name'] = 1, which is dealt with below
	    
	    #using default in case for some reason self.modified does not have the keys
	    self.modified.pop('inplace', None)
	    self.modified.pop('name', None)
	        
	    wxCallAfter(LCtrl.SetFocus) #sets focus on LCtrl and current selection to be highlighted
	
	
	
	def OnDueDate(self, evt=None):
	    idx = self.curIdx
	    if idx == -1:
	        return
	    L = self.L
	    Properties = self.PropertyDicts[L]
	    item = self.ItemLists[L][idx]
	    LCtrl = self.ListCtrls[L]
	
	    if item.duedate:
	        date = wxDateTime()
	        date.SetTimeT(item.duedate) #I am surprised it takes a mx.DateTime object; supposed to need ticks
	    else:
	        date = 0
	    dlg = CalendarDialog(parent=self,
	                 title="Select a date",
	                 size=(400,400),
	                 style=wxCAPTION,
	                 date = date)
	    if dlg.ShowModal()==wxID_OK:
	        date = dlg.cal.GetDate() # this is some date object
	        #date = date.GetTicks()
	        item.duedate = mx.DateTime.DateFromTicks(date.GetTicks())
	
	        host = Properties['host']
	        cursor = self.Cursors[host]
	        table = Properties['table']
	        
	        cursor.execute("UPDATE "+table+" SET duedate = %s WHERE id = %s", (item.duedate,item.id))
	        item.timestamp = self.TimeStamper(host, cursor, table, item.id)
	        if Properties['LCdate'] == 'timestamp':
	            LCtrl.SetStringItem(idx, self.attr2col_num['date'], item.timestamp.Format("%m/%d %H:%M:%S"))
	        elif Properties['LCdate'] == 'duedate':
	            LCtrl.SetStringItem(idx, self.attr2col_num['date'], item.duedate.Format('%m/%d/%y'))
	    dlg.cal.Destroy()
	    dlg.Destroy()
	    
	def OnEditOwner(self, evt=None): #, new=False) removed Aug. 31 for simplicity
	    idx = self.curIdx
	    if idx == -1:
	        return
	    L = self.L
	    Properties = self.PropertyDicts[L]
	    LCtrl = self.ListCtrls[L]
	    item = self.ItemLists[L][idx]
	    if not self.ModifierDialog:
	        print "self.ModifierDialog is still being constructed"
	        return
	    #need to clear the current selections or you'll just be making more and more selections
	    self.ModifierDialog.SelectCurrent(item.owners)
	    self.ModifierDialog.tc.Clear()
	    self.ModifierDialog.CenterOnParent()
	    
	    val = self.ModifierDialog.ShowModal()
	
	    if val == wxID_OK:
	        item.owners, new_names = self.ModifierDialog.GetUserInput()
	        
			owner_str = '; '.join(item.owners)
			LCtrl.SetStringItem(idx, self.attr2col_num['owners'], owner_str)
			self.owners.Clear()
			self.owners.AppendText(owner_str)
			        
			z = item.owners+[None,None,None] #note that + creates a new list
	
	        for owner in item.owners:
	            if self.OwnerLBoxes[L].FindString(owner) == -1:
	                self.OwnerLBoxes[L].Append(owner)
	
	        for owner in new_names:
	            self.ModifierDialog.lb.Append(owner)
	        
	        host = Properties['host']
	        cursor = self.Cursors[host]
	        table = Properties['table']
	
	        cursor.execute("UPDATE "+table+" SET owner1 = %s, owner2 = %s, owner3 = %s WHERE id = %s", (z[0],z[1],z[2],item.id))
	        item.timestamp = self.TimeStamper(host, cursor, table, item.id)
	        if Properties['LCdate'] == 'timestamp':
	            LCtrl.SetStringItem(idx, self.attr2col_num['date'], item.timestamp.Format("%m/%d %H:%M:%S"))
	
	        if 'owners' in self.modified:
	            del self.modified['owners']
	            
	    wxCallAfter(LCtrl.SetFocus)
	    
	def OnUpdate(self, evt=None):
	    if 'inplace' in self.modified:
	        self.OnCloseInPlaceEditor()
	        if not self.modified:
	            return
	
	    L = self.L
	    LCtrl = self.ListCtrls[L]
	    IList = self.ItemLists[L]
	    Properties = self.PropertyDicts[L]
	    OLBox = self.OwnerLBoxes[L]
	    idx = self.curIdx
	
	    # there is some chance that it is never true that idx == -1 and then this could be eliminated
	    if idx != -1:
	        item = IList[idx]
	    else:
	        msg = wxMessageDialog(self, "There is no selected item to update", "", wxICON_ERROR|wxOK)
	        msg.ShowModal()
	        msg.Destroy()
	        self.modified = {}
	        return
	        
	    host = Properties['host']
	    cursor = self.Cursors[host]
	    table = Properties['table']
	    
	    if 'name' in self.modified:
	        item.name = self.name.GetValue().strip()[:150]
	        LCtrl.SetStringItem(idx, self.attr2col_num['name'], item.name)
	        cursor.execute("UPDATE "+table+" SET name =%s WHERE id = %s",(item.name,item.id))
	        
	    if 'note' in self.modified:
	        note = self.note.GetValue() #a blank note starts out as None but after this it becomes '' -- ??
	        cursor.execute("UPDATE "+table+" SET note =%s WHERE id = %s",(note,item.id))
	        
	    if 'owners' in self.modified:
	        owner_str = self.owners.GetValue().strip()
	        item.owners = []
	        if owner_str:
	            owner_list = [x.strip() for x in owner_str.split(';')]
	            for owner in owner_list:
	                owner = ", ".join([x.strip().title() for x in owner.split(',')])
	                item.owners.append(owner)
	            
			owner_str = '; '.join(item.owners)
			LCtrl.SetStringItem(idx, self.attr2col_num['owners'], owner_str)
			self.owners.Clear()
			self.owners.AppendText(owner_str)
			        
			z = item.owners+[None,None,None] #note that + creates a new list
	
	        cursor.execute("UPDATE "+table+" SET owner1 = %s, owner2 = %s, owner3 = %s WHERE id = %s", (z[0],z[1],z[2],item.id))
	        
	        for owner in item.owners:
	            if self.ModifierDialog.lb.FindString(owner) == -1:
	                self.ModifierDialog.lb.Append(owner)
	                OLBox.Append(owner)
	            elif OLBox.FindString(owner) == -1:
	                OLBox.Append(owner)		
	                
	    item.timestamp = self.TimeStamper(host, cursor, table, item.id)
	    if Properties['LCdate'] == 'timestamp':
	        LCtrl.SetStringItem(idx, 3, item.timestamp.Format("%m/%d %H:%M:%S"))
	    
	    self.modified = {}
	    
	    
	def OnNewItem(self, evt=None):
	    L=self.L
	    LCtrl = self.ListCtrls[L]
	    Properties = self.PropertyDicts[L]
	    
	    if self.curIdx != -1:
	        LCtrl.SetItemState(self.curIdx, 0, wxLIST_STATE_SELECTED)
	    
		self.name.Clear()
		self.owners.Clear()
		self.note.Clear()	    
	    class Item: pass
	    item = Item()
	    item.name = '<New Item>'
	    item.priority = 1
	    item.owners = []
	    item.createdate = mx.DateTime.now() #need this to be a timestamp and not just date for syncing
	    item.duedate = item.finisheddate = None
	
	    self.ItemLists[L].insert(0,item)
	    
	    host = Properties['host']
	    cursor = self.Cursors[host]
	    table = Properties['table']
	    item.id = self.GetUID()
	    
	    cursor.execute("INSERT INTO "+table+" (priority,name,createdate,finisheddate,duedate,id) VALUES (%s,%s,%s,%s,%s,%s)",
	                (item.priority,item.name,item.createdate,None,None,item.id))
	        
	    item.timestamp = self.TimeStamper(host, cursor, table, item.id)
	    
	    #tracking new item for syncing will happen in Edit Name
	
	    LCtrl.InsertImageStringItem(0,"1", LCtrl.idx1)
	    LCtrl.SetStringItem(0,1,item.name)
	
	    if Properties['LCdate'] == 'timestamp':
	        LCtrl.SetStringItem(0, self.attr2col_num['date'], item.timestamp.Format("%m/%d %H:%M:%S"))
	    elif Properties['LCdate'] == 'createdate':
	        LCtrl.SetStringItem(0, self.attr2col_num['date'], item.createdate.Format('%m/%d/%y'))
	
	    self.curIdx = 0
	    
	    #if Display is being filtered we assume that is the owner of the new node
	    owner = Properties['owner']	
	    if owner and owner!='*ALL':
	        self.ListCtrls[L].SetStringItem(0, self.attr2col_num['owners'], owner)
	        item.owners = [owner]
	        
	        self.owners.Clear()
	        self.owners.AppendText(owner)
	        
	        cursor.execute("UPDATE "+table+" SET owner1 = %s WHERE id = %s", (owner,item.id))
	        item.timestamp = self.TimeStamper(host, cursor, table, item.id)  #not really necessary since just got a timestamp
	    
	    # decided that it was actually better not to ask for the owner on a new node	
	    #else:
	        #self.OnEditOwner()
	    
	    LCtrl.SetFocus() #needed for the in place editor to look right
	    LCtrl.SetItemState(0, wxLIST_STATE_SELECTED, wxLIST_STATE_SELECTED)
	    
	    self.OnDisplayInPlaceEditor() #(new=True)	# Need to decide if we are going to have timestamp checking to be sure 
	# something hasn't changed
	# Note that there would not need to be timestamp checking on a new node
	# Also  there is no need to timestamp check on a local DB
	# The following code seems to work fine, however, I have just commented 
	# out the calls to it in NameEditor methods
	def Conflict(self, host, cursor, table, item):
	    if host is 'sqlite':
	        return False
	    cursor.execute("Select timestamp from "+table+" WHERE id = %s", (item.id,))
	    db_timestamp = cursor.fetchone()[0]
	    if db_timestamp != item.timestamp:
	        print "There is a conflict and you should refresh display"
	        return True
	    else:
	        return False
	def OnEditNote(self, evt=None):
	    if self.modified:
	        self.OnUpdate()
	    
	    idx = self.curIdx
	    
	    if idx == -1:
	        return
	        
	    L = self.L
	        
	    #if self.editor:
	        #machine = None
	        #win32pdh.EnumObjects(None, machine, 0, 1) # resets Enum otherwise it seems to hold onto old data
	        #object = "Process"
	        #items, instances = win32pdh.EnumObjectItems(None,None,"Process", -1)
	        #if 'TextPad' in instances:
	            #print "TextPad is running"
	        #else:
	            #self.editor = {}
	    
	    item = self.ItemLists[L][idx]
	    file_name = re.sub('[\\/:*"<>|\?]','-',item.name) #make sure all chars are legal file name characters
	    
	    path = os.path.join(os.environ['TMP'],file_name[:50])+'.%s'%NOTE_EXT
	        
	    f = file(path,'w')
	    f.write(self.GetNote())
	    f.close()
	    
	    os.startfile(path)
	    
	    id = item.id
	    for d in self.editor:
	        if d['id'] == id:
	            return
	
	    ed = {}
	    ed['time'] = os.path.getmtime(path)
	    ed['host'] = self.PropertyDicts[L]['host']
	    ed['table'] = self.PropertyDicts[L]['table']
	    ed['path'] = path
	    ed['id'] = item.id
	    
	    self.editor.append(ed)
	    
	    time.sleep(.1)
	def OnNewList(self, event=None):
	    if self.modified:
	        self.OnUpdate()
	    
	    if OFFLINE_ONLY is True or REMOTE_HOST is None:
	        hosts = [LOCAL_HOST]
	    else:
	        hosts = [LOCAL_HOST, REMOTE_HOST]
	        
	    dlg = wxSingleChoiceDialog(self, 'Databases', 'Choose a database:', hosts, wxCHOICEDLG_STYLE)
	    val = dlg.ShowModal()
	    dlg.Destroy()
	    if val == wxID_OK:
	        host = dlg.GetStringSelection()
	    else:
	        return
	        
	    cursor = self.GetCursor(host)
	    if cursor is None:
	        return
	        
	    dlg = wxTextEntryDialog(self, 'What is the name of the new table?', 'Create Table')
	    val = dlg.ShowModal()
	    dlg.Destroy()
	    if val == wxID_OK:
	        table = dlg.GetValue()
	    else:
	        return
	    
	    if not table:
	        return
	        
	    location, rdbms = host.split(':')
	    
	    if rdbms == 'sqlite':
	        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
	    else:
	        cursor.execute("SHOW tables")
	    
	    if (table,) in cursor.fetchall():
	        msg = wxMessageDialog(self,
	                              "Table '%s' already exists"%table,
	                              "Duplicate Table",
	                              wxICON_ERROR|wxOK)
	        msg.ShowModal()
	        msg.Destroy()
	        return
	        
	    dlg = wxMessageDialog(self,
	          "Are you sure you want to create Table '%s'?"%table,
	          "Create Table?",
	          wxICON_QUESTION|wxYES_NO)
	
	    if dlg.ShowModal() == wxID_YES:
	        self.CreateTable(host,table)
	        self.CreateNewNotebookPage(host,table)
	
	        #self.AddListControl(tab_title) #add listcontrol displays the list
	        
	        #self.OnNewItem()
	        
	    dlg.Destroy()
	
	
	def OnFileList(self, evt=None, path=None):
	    if self.modified:
	        self.OnUpdate()
	        
	    #if there is no event, we got here through the start up loading of lists
	    if evt:
	        fileNum = evt.GetId() - wxID_FILE1			
	        path = self.filehistory.GetHistoryFile(fileNum)
	        location, rdbms, table = path.split(':')
	        host = '%s:%s'%(location, rdbms)
	        # only need to check if table is open if this is not at startup
	        if table in [p['table'] for p in self.PropertyDicts if p['host'] == host]:
	            dlg = wxMessageDialog(self,"%s (%s) is already open!"%(table,host),"List Open",wxICON_ERROR|wxOK)
	            dlg.ShowModal()
	            dlg.Destroy()
	            return
	        
	    else:
	        location, rdbms, table = path.split(':')
	        host = '%s:%s'%(location, rdbms)
	    
	    cursor = self.GetCursor(host)
	    if cursor is None:
	        return
	        
	    if rdbms == 'sqlite':
	        sql = "SELECT name FROM sqlite_master WHERE name = '%s'"%table
	    else:
	        sql = "SHOW TABLES LIKE '%s'"%table
	    
	    cursor.execute(sql)
	    if not cursor.fetchall():
	        dlg = wxMessageDialog(self,
	                    "Table '%s' at host '%s' does not appear to exist!"%(table,host),
	                    "Table does not exist",
	                    wxICON_ERROR|wxOK)
	        dlg.ShowModal()
	        dlg.Destroy()
	        return
	        
	    self.CreateNewNotebookPage(host,table)
	
	def OnOpenList(self, evt=None):
	    if self.modified:
	        self.OnUpdate()
	        
	    tree = {}
	    
	    if OFFLINE_ONLY is True or REMOTE_HOST is None:
	        hosts = [LOCAL_HOST]
	    else:
	        hosts = [LOCAL_HOST, REMOTE_HOST]
	        
	    for host in hosts:
	        cursor = self.GetCursor(host)
	        if cursor:
	            if host.split(':')[1] == 'sqlite':
	                sql = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
	            else:
	                sql = "SHOW TABLES" #sorted
	    
	            cursor.execute(sql)
	            results = cursor.fetchall()
	    
	            #excluding already open tables + 'system' tables
	            excluded_tables = [p['table'] for p in self.PropertyDicts if p['host'] == host]
	            excluded_tables.extend(['user_sync','sync','owners'])
	    
	            tables = [t for (t,) in results if t not in excluded_tables]
	    
	            tree[host] = tables
	
	    dlg = TreeDialog(self, "Open List", tree=tree)
	    val = dlg.ShowModal()
	    dlg.Destroy()
	    if val == wxID_OK:
	        sel = dlg.TreeCtrl.GetSelection()
	        table = dlg.TreeCtrl.GetItemText(sel)
	        sel = dlg.TreeCtrl.GetItemParent(sel)
	        host = dlg.TreeCtrl.GetItemText(sel)
	        
	        if host in hosts: #takes care of highlighting root or hosts
	            self.CreateNewNotebookPage(host,table)
	def OnDeleteList(self, evt=None):
	    #ini controls whether the menu item is enabled
	    Properties = self.PropertyDicts[self.L]
	    host = Properties['host']
	    table = Properties['table']
	        
	    #if table is in SYNC_TABLES, should we make a point of that?
	    dlg = wxMessageDialog(self,
	                        "Are you sure that you want to delete table %s (%s)?\n(Please note that you cannot recover it once it is deleted!)"%(table,host),
	                        "Delete Table...",
	                        wxICON_EXCLAMATION|wxYES_NO|wxNO_DEFAULT)
	    
	    val = dlg.ShowModal()
	    dlg.Destroy()
	    if val == wxID_NO:
	        return
	        
	    rdbms = host.split(':')[1]
	    
	    if rdbms == 'mysql':
	        dlg = wxMessageDialog(self,
	                        "Are you sure really really sure you want to delete table %s (%s)?\n(You really really cannot recover it once it is deleted)"%(table,host),
	                        "Delete Table...",
	                        wxICON_EXCLAMATION|wxYES_NO|wxNO_DEFAULT)
	                        
	        val = dlg.ShowModal()
	        dlg.Destroy()
	        if val == wxID_NO:
	            return
	
	    cursor = self.Cursors[host]
	    cursor.execute("DROP TABLE %s"%table)
	    
	    self.OnCloseList()
	
	def OnCloseList(self, evt=None):
	    if self.modified:
	        self.OnUpdate()
	        
	    L = self.L
	            
	    del self.ItemLists[L]
	    del self.PropertyDicts[L]
	    del self.ListCtrls[L]
	    del self.OwnerLBoxes[L]
	
	    self.nb.DeletePage(L)        
	
	    ln = len(self.PropertyDicts)
	    if ln:
	        self.nb.SetSelection(0)
	        self.L = 0
	    else:
	        self.L = -1
	
	
	
	
	def OnCloseAll(self, evt=None):
	    if self.modified:
	        self.OnUpdate()
	        
	    while self.L != -1:
	        self.OnCloseList()
	        
	    self.name.Clear()
	    self.owners.Clear()
	    self.note.Clear()
	    #note that Clearing does set self.modified (eg {'name':1})
	    self.modified = {}
	    
	def OnSaveAsText(self, evt=None):
	    if self.modified:
	        self.OnUpdate()
	        
	    Properties = self.PropertyDicts[self.L]
	    wildcard = "txt files (*.txt)|*.txt|All files (*.*)|*.*"
	    #dlg = wxFileDialog(self, "Save file", "", Properties['table'], wildcard, wxSAVE|wxOVERWRITE_PROMPT|wxCHANGE_DIR)
	        
	    body = ""
	    for i,item in enumerate(self.ItemLists[self.L]):
	        body = body+"%d. %s (%d)\n"%(i+1, item.name, item.priority)
	    
	    table = Properties['table']
	    location, rdbms = Properties['host'].split(':')
	    filename = re.sub('[\\/:*"<>|\?]','-','%s-%s-%s'%(location,rdbms,table)) 
	    filename = filename[:50]+'.txt'
	
	    path = os.path.join(DIRECTORY,filename)
	    
	    f = file(path,'w')
	    f.write(body)
	    f.close()
	
	    os.startfile(path)
	
	    self.SetStatusText("Saved file %s"%path)
	    
	def OnArchive(self, evt=None):
	    if self.modified:
	        self.OnUpdate()
	        
	    Properties = self.PropertyDicts[self.L]
	    host = Properties['host']
	    cursor = self.Cursors[host]
	    table = Properties['table']
	    rdbms = host.split(':')[1]
	        
	    table_archive = table+'_archive'
	    
	    #need to test for existence of table_archive
	    if rdbms == 'sqlite':
	        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
	    else:
	        cursor.execute("SHOW tables")
	
	    results = cursor.fetchall()
	    
	    if (table_archive,) not in results:
	        dlg = wxMessageDialog(self,
	                    "Do you want to create an archive for table %s (%s)"%(table,rdbms),
	                    "Create an archive...",
	                    wxICON_QUESTION|wxYES_NO)
	        val = dlg.ShowModal()
	        dlg.Destroy()
	        if val==wxID_YES:
	            self.CreateTable(host,table_archive)
	        else:
	            return
	    
	    label1 = "In table %s (%s) \narchive all finished items older than:"%(table,rdbms)
	    label2 = "Archive all finished items"
	    dlg = FinishedDialog(self, "Archive completed items", days=7, spin_label=label1, check_label=label2)
	    
	    val = dlg.ShowModal()
	    dlg.Destroy() #dialogs and frames not destroyed right away to allow processing events, methods
	    if val==wxID_CANCEL:
	        return
	        
	    if dlg.check.GetValue():
	        cursor.execute("SELECT id,priority,name,createdate,finisheddate,duedate,owner1,owner2,owner3,note FROM "+table+" WHERE finisheddate IS NOT NULL")
	    else:
	        days = dlg.text.GetValue()
	        date = mx.DateTime.today() - int(days)
	        cursor.execute("SELECT id,priority,name,createdate,finisheddate,duedate,owner1,owner2,owner3,note FROM "+table+" WHERE finisheddate < %s",(date,))
	
	    results = cursor.fetchall()
	    dlg = wxMessageDialog(self,
	                        "Archiving will remove %d records from %s.\nDo you want to proceed?"%(len(results),table),
	                        "Proceed to archive...",
	                        wxICON_QUESTION|wxYES_NO)
	    
	    val = dlg.ShowModal()
	    dlg.Destroy()
	    if val == wxID_NO:
	        return
	
	    if table in SYNC_TABLES:
	        if rdbms == 'sqlite':
	            def track_deletes():
	                timestamp = mx.DateTime.now()
	                cursor.execute("INSERT INTO sync (id,action,table_name,name,timestamp) VALUES (%s,%s,%s,%s,%s)",(id,'d',table,name,timestamp))
	        else:
	            def track_deletes():
	                cursor.execute("INSERT INTO sync (id,action,table_name,user,name) VALUES (%s,%s,%s,%s,%s)",(id,'d',table,USER,name))
	    else:
	        def track_deletes():
	            pass	
	
	    for row in results:
	        # the next line is necessary because pysqlite returns a tuple-like object that is not a tuple
	        r = tuple(row)
	        id = r[0]
	        name = r[2]
	        cursor.execute("INSERT INTO "+table_archive+"  (id,priority,name,createdate,finisheddate,duedate,owner1,owner2,owner3,note) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",r)
	        timestamp = self.TimeStamper(host, cursor, table_archive, id)
	        cursor.execute("DELETE from "+table+" WHERE id = %s", (id,))
	        track_deletes()
	        
	    self.OnRefresh()
	    dlg = wxMessageDialog(self,
	                        "Table %s had items older than %s days successfully archived"%(table,days),
	                        "Archiving successful...",
	                        wxICON_INFORMATION|wxOK)
	    dlg.ShowModal()
	def OnWorkOffline(self, evt=None):
	    global OFFLINE_ONLY
	    OFFLINE_ONLY = not OFFLINE_ONLY
	    if OFFLINE_ONLY:
	        del self.Cursors[REMOTE_HOST]
	    else:
	        server = REMOTE_HOST.split(':')[0]
	        try:
	            socket.gethostbyname(server)
	        except:
	            dlg = wxMessageDialog(None, "Cannot connect to remote server! Will set to work offline.", "ListManager", style=wxOK|wxICON_EXCLAMATION|wxSTAY_ON_TOP)
	            dlg.ShowModal()
	            dlg.Destroy()
	            OFFLINE_ONLY = True
	
	    self.filemenu.Check(idOFFLINE,OFFLINE_ONLY)
	    
	def OnItemSelected(self, evt=None):
	    if self.modified:
	        self.OnUpdate()
	
	    if evt:
	        idx = evt.GetIndex()
	    elif self.curIdx != -1:
	        idx = self.curIdx
	    else: # really to catch self.curIdx = -1 (see OnDelete and OnRefresh)
	        self.name.Clear() # could be moved out of if
	        self.owners.Clear() # could be moved out of if
	        self.note.Clear()
	        #note that Clearing does set self.modified (eg {'name':1})
	        self.modified = {}
	        return
	    
	    L = self.L
	    item = self.ItemLists[L][idx]
	
	    self.name.Clear()
	    self.name.AppendText(item.name) #SetValue(item.name) - if you use setvalue you don't get the font
	        
	    self.owners.Clear()
	    self.owners.AppendText('; '.join(item.owners))
	    
	    note = self.GetNote(L,item)
	    if note.find("<leo_file>") != -1:
	        self.note.SetValue("Leo Outline")
	        self.note.SetEditable(False)
	    else:
	        self.note.SetValue(note)
	        self.note.SetEditable(True)
	        
	    self.ListCtrls[L].EnsureVisible(idx)
	    self.curIdx = idx
	    
	    #writing to text widgets caused wxEVT_COMMAND_TEXT_UPDATED which is caught by EVT_TEXT, which updates self.modified
	    self.modified={}
	
	def OnItemActivated(self,evt):
	    print "On Activated"
	    
	def OnShowAll(self, evt=None):
	    L = self.L
	    OLBox = self.OwnerLBoxes[L]
	    
	    Properties = self.PropertyDicts[L]
	    Properties['showfinished'] = -1
	    Properties['owner'] = '*ALL'
	    
	    OLBox.SetStringSelection('*ALL')
	    
	    self.OnRefresh()
	def OnRefresh(self, evt=None):
	    #OnItemSelected should be able to handle no items so this could be very short
	    L = self.L
	    
	    results = self.ReadFromDB()
	    self.ItemLists[L] = self.CreateAndDisplayList(results)
	
	    if self.ItemLists[L]:
	        self.ListCtrls[L].SetItemState(0, wxLIST_STATE_SELECTED, wxLIST_STATE_SELECTED)
	        self.curIdx = 0
	    else:
	        self.curIdx = -1		
	        
	    self.OnItemSelected()
	def OnFilterOwners(self, evt=None):
	    if self.modified:
	        self.OnUpdate()
	    sel = self.OwnerLBoxes[self.L].GetStringSelection()
	    
	    if sel:
	        self.PropertyDicts[self.L]['owner'] = sel
	        self.OnRefresh()
	def OnColumnClick(self, evt):
	    col_num = evt.GetColumn()
	    L = self.L
	    LCtrl = self.ListCtrls[L]
	    Sort = self.PropertyDicts[L]['sort']
	    attr2col = self.attr2col_num
	    
	    prev_sort_attr = Sort.get('attribute') #if this is the first sort Properties['sort'] is {}
	    
	    #following is a little bit ugly but gets the key from the value, which is col_num
	    Sort['attribute'] = attr2col.keys()[attr2col.values().index(col_num)]
	    
	    if prev_sort_attr == Sort['attribute']:
	        Sort['direction'] = not Sort['direction']
	    else:
	        Sort['direction'] = 0
	    
	    self.OnRefresh()
	
	    LCtrl.ClearColumnImage(attr2col['priority'])
	    LCtrl.ClearColumnImage(attr2col['date'])
	    img_num = LCtrl.arrows[Sort['direction']]
	    LCtrl.SetColumnImage(col_num, img_num)
	    
	def OnShowFinished(self,evt):
	    Properties = self.PropertyDicts[self.L]
	    label1 = "Enter the number of days to retain\ncompleted tasks in the display:"
	    label2 = "Show all finished items"
	    dlg = FinishedDialog(self, "Display of completed items", days=Properties['showfinished'], spin_label=label1, check_label=label2)
	    if dlg.ShowModal()==wxID_OK:
	        if dlg.check.GetValue():
	            Properties['showfinished'] = -1
	        else:
	            days = dlg.text.GetValue()
	            Properties['showfinished'] = int(days)			
	        self.OnRefresh()
	    dlg.Destroy()
	    
	def OnColumnRightClick(self, evt=None):
	    col = evt.GetColumn()
	    if col != self.attr2col_num['date']:
	        return
	        
	    L = self.L
	    LCtrl = self.ListCtrls[L]
	    Properties = self.PropertyDicts[L]
	    
	    #x,y = evt.GetPosition()
	    datemenu = wxMenu()
	    
	    for i,date in enumerate(['Create Date','Last Modified','Due Date','Completion Date']):
	        datemenu.Append(200+i, date)
	        EVT_MENU(self, 200+i, lambda e, i=i: self.ChangeDateDisplayed(e,i))
	
	    x = LCtrl.GetColumnWidth(1)+ LCtrl.GetColumnWidth(2) + LCtrl.GetColumnWidth(3)
	    self.PopupMenu(datemenu,(x,40))
	    datemenu.Destroy()
	
	
	def OnDisplayDateCategory(self, evt=None):
	    dlg = wxSingleChoiceDialog(self, 'Date Display', 'Choose a date to display:',
	                    ['Create Date','Last Modified','Due Date','Completion Date']
	                    , wxOK|wxCANCEL)
	    val = dlg.ShowModal()
	    dlg.Destroy()
	    
	    if val == wxID_OK:
	        idx = dlg.GetSelection()
	        self.ChangeDateDisplayed(i=idx)
	        
	def ChangeDateDisplayed(self, evt=None, i=0):
	    L = self.L
	    LCtrl = self.ListCtrls[L]
	    self.PropertyDicts[L]['LCdate'] = displaydate = ('createdate','timestamp','duedate','finisheddate')[i]	
	    col_num = self.attr2col_num['date']
	    col_info = LCtrl.GetColumn(col_num)
	    col_info.SetText(self.date_titles[displaydate])
	    LCtrl.SetColumn(col_num,col_info)
	    self.DisplayList(self.ItemLists[L])
	    #self.OnRefresh() #have gone back and forth but think that it should be self.DisplayList
	def DisplayList(self, List, L=None):
	    #OnPasteItems needs to be able to have an L that is not self.L
	    if L is None:
	        L = self.L
	    LCtrl = self.ListCtrls[L]
	    LCdate = self.PropertyDicts[L]['LCdate']
	    if LCdate == 'timestamp':
	        format = '%m/%d %H:%M:%S'
	    else:
	        format = '%m/%d/%y'
	    LCtrl.DeleteAllItems()
	    
	    for x,item in enumerate(List):
			LCtrl.InsertImageStringItem(x, str(item.priority), LCtrl.idx1)
			LCtrl.SetStringItem(x,1,item.name)
			LCtrl.SetStringItem(x,2,'; '.join(item.owners))
			date = item.__dict__[LCdate]
			LCtrl.SetStringItem(x,3,date and date.Format(format) or "")
			
			if item.finisheddate:
			    LC_Item = LCtrl.GetItem(x)
			    LC_Item.SetImage(LCtrl.idx0) #might just want generic number or greyed one two three
			    LC_Item.SetTextColour(wxLIGHT_GREY)
			    LCtrl.SetItem(LC_Item)
			    
			elif item.priority==2:
			    LC_Item = LCtrl.GetItem(x)
			    f = self.LC_font
			    f.SetWeight(wxBOLD)
			    LC_Item.SetFont(f)
			    f.SetWeight(wxNORMAL) #resetting weight
			    LCtrl.SetItem(LC_Item)
			
			elif item.priority==3:
			    LC_Item = LCtrl.GetItem(x)
			    f = self.LC_font
			    f.SetWeight(wxBOLD)
			    LC_Item.SetFont(f)
			    f.SetWeight(wxNORMAL) #return to normal
			    LC_Item.SetTextColour(wxRED)
			    LCtrl.SetItem(LC_Item)	        
	
	def OnPageSetup(self, evt):
	    #need to pass printdata to tableprint
	
	    psdata = wxPageSetupDialogData()
	
	    # if want to vary margins will need to save them as ivars and then set
	    #psdata.SetMarginTopLeft((self.Left,self.Top))
	    psdata.EnableMargins(False)
	    psdata.SetPrintData(self.printdata) #gets Paper Orientation and PaperId info from printdata
	    
	    dlg = wxPageSetupDialog(self, psdata)
	    if dlg.ShowModal() == wxID_OK:
	        self.printdata = dlg.GetPageSetupData().GetPrintData()
	        dlg.Destroy()
	def OnPrint(self, evt=None, prev=False, showprtdlg=True): 		#???self.psdata = psdata
	    IList = self.ItemLists[self.L]
	    Properties = self.PropertyDicts[self.L]
	    
	    prt = PrintTable(self.printdata) #self.printdata is the wxPrintData object with Orientation Info
	
	    font_name = prt.default_font_name
	    prt.text_font = {'Name':font_name, 'Size':11, 'Colour':[0, 0, 0], 'Attr':[0, 0, 0]}
	    prt.label_font = {'Name':font_name, 'Size':12, 'Colour':[0, 0, 0], 'Attr':[1, 0, 0]}
	    prt.header_font = {'Name':font_name, 'Size':14, 'Colour':[0, 0, 0], 'Attr':[1, 0, 0]}
	    
	    prt.row_def_line_colour = wxLIGHT_GREY
	    prt.column_def_line_colour = wxLIGHT_GREY
	    
	    prt.left_margin = 0.5
	
	    data = []
	    for row,item in enumerate(IList):	
	        data.append([str(item.priority),
	                    item.name,
	                    item.duedate and item.duedate.Format('%m/%d/%y') or '',
	                    '; '.join([x.split(',')[0] for x in item.owners])]) #just last names
	                    
	        if item.finisheddate:
	            prt.SetCellText(row, 0, wxLIGHT_GREY)
	            prt.SetCellText(row, 1, wxLIGHT_GREY)
	            prt.SetCellText(row, 2, wxLIGHT_GREY)
	            prt.SetCellText(row, 3, wxLIGHT_GREY)
	
	    prt.data = data
	    prt.label = ['P','Item','Due','Owner']
	    
	    if self.printdata.GetOrientation() == wxPORTRAIT:
	        prt.set_column = [.2, 5, .65, 1]
	    else:
	        prt.set_column = [.2, 7, .65, 1.5]
	                       
	    title = "Table: %s   Owner: %s    "%(Properties['table'],Properties['owner'])
	    prt.SetHeader(title, type='Date & Time', align=wxALIGN_LEFT, indent = 1.5)
	    prt.SetFooter("Page No ", type ="Num")
	
	    if prev:
	        prt.Preview()
	    else:
	        prt.Print(prompt=showprtdlg)
	def OnWindowExit(self, evt):
	    #this is called if you close the ListManager Window with the X
	    if evt.CanVeto():
	        self.OnExit()
	    else:
	        evt.Skip()
	def OnExit(self, event=None):   
		cp.remove_section('Files')
		cp.add_section("Files")
		
		x,y = self.GetSizeTuple()
		
		cp.set('Configuration','x', str(x))
		cp.set('Configuration','y', str(y))
		
		numfiles = self.filehistory.GetNoHistoryFiles()
		
		for n in range(numfiles):
		    cp.set("Files", "path%d"%n, self.filehistory.GetHistoryFile(n))
		
		try:
		    #you have to give ConfigParser a writable object
		    cfile = file(config_file, 'w')
		    cp.write(cfile)
		    cfile.close()
		except IOError:
		    print "The configuration file can't be written!"
		    time.sleep(10) #so you can see that there was a problem
	    sys.stderr.dlg.Destroy() #destroys the error dialog; need to do this to shut down correctly
	    if self.ModifierDialog: #only reason to check is if closed before ModifierDialog is constructed
	        self.ModifierDialog.Destroy()
	    self.Close(1)
	def OnFind(self, evt=None):
	    self.FindDialog.Show(True)
	    self.FindDialog.FindText.SetSelection(-1,-1)
	    self.FindDialog.FindText.SetFocus()
	
	
	def FindString(self, evt=None):
	    L = self.L
	    Properties = self.PropertyDicts[L]
	    cursor = self.Cursors[Properties['host']]
	    table = Properties['table']
	    
	    pat = self.FindDialog.FindText.GetValue()
	    likepat = r"'%"+pat+r"%'"
	    finished = self.FindDialog.SearchFinished.GetValue()
	    notes = self.FindDialog.SearchNotes.GetValue()
	    
	    if finished:
	        WHERE = "WHERE "
	    else:
	        WHERE = "WHERE finisheddate IS NULL AND "
	    
	    if notes:
	        SELECT = "SELECT priority,name,createdate,finisheddate,duedate,owner1,owner2,owner3,id,timestamp,note FROM %s "%table
	        WHERE = WHERE + "(name LIKE %s OR note LIKE %s) ORDER BY timestamp DESC"%(likepat,likepat)
	    else:
	        SELECT = "SELECT priority,name,createdate,finisheddate,duedate,owner1,owner2,owner3,id,timestamp FROM %s "%table
	        WHERE = WHERE + "name LIKE %s ORDER BY timestamp DESC"%likepat
	
	    sql = SELECT + WHERE			
	    try:
	        cursor.execute(sql)
	    except:
	        print "Cannot read %s: %s"%(Properties['host'],table)
	        return
	    else:
	        results = cursor.fetchall()
	    
	    case = self.FindDialog.MatchCase.GetValue()
	    whole = self.FindDialog.MatchWhole.GetValue()
	    
	    if whole:
	        pat = '\\b%s\\b'%pat
	    
	    if case:
	        z = re.compile(pat)
	    else:
	        z =re.compile(pat, re.I)
	
	    if notes:
	        results = [x for x in results if re.search(z,x[1]) or re.search(z,x[10])]
	    else:
	        results = [x for x in results if re.search(z,x[1])]
	    
	    Properties['LCdate'] = 'timestamp'
	    self.ItemLists[L]= IList = self.CreateAndDisplayList(results)
	    
	    LCtrl = self.ListCtrls[L]
	    col_num = self.attr2col_num['date']
	    col_info = LCtrl.GetColumn(col_num)
	    col_info.SetText(self.date_titles['timestamp'])
	    LCtrl.SetColumn(col_num,col_info)
	    
	    if IList:
	        self.curIdx = 0
	        LCtrl.SetItemState(0, wxLIST_STATE_SELECTED, wxLIST_STATE_SELECTED)
	    else:		
	        self.curIdx = -1
	        
	    self.OnItemSelected()
	    
	    Properties['sort'] = {'direction':0,'attribute':'date'}
	    Properties['owner'] = '*ALL'
	    
	    owner_idx = self.OwnerLBoxes[L].GetSelection()
	    if owner_idx != -1:
	        self.OwnerLBoxes[L].SetSelection(owner_idx, 0) #get exception if index = -1
	
	    self.SetStatusText("Found %d items"%len(IList))
	def FindNode(self, item, showfinished=True):
	    L = self.L
	    LCtrl = self.ListCtrls[L]
	    Properties = self.PropertyDicts[L]
	    
	    Properties['owner'] = '*ALL'
	    Properties['showfinished'] = showfinished
	    
	    self.ItemLists[L] = IList = self.CreateAndDisplayList(self.ReadFromDB())
	    
	    id = item.id
	    idx = -1
	    for item in IList:
	        idx+=1
	        if id == item.id:
	            break
	    else:
	        idx = -1
	
	    if idx != -1:	
	        LCtrl.SetItemState(idx, wxLIST_STATE_SELECTED, wxLIST_STATE_SELECTED)
	        LCtrl.EnsureVisible(idx)
	    self.curIdx = idx
	    
	def GetCursor(self, host):
	    cursor = self.Cursors.get(host)
	    if cursor:
	        return cursor
	        
	    location, rdbms = host.split(':')
	        
	    if rdbms == 'sqlite':
	        db = os.path.join(DIRECTORY,location,DB)
	        try:
	            Con = sqlite.connect(db=db, autocommit=1)
	            cursor = Con.cursor()
	            self.sqlite_connections.append(Con)  #getting a weak reference error from PySQLite and this makes it go away
	        except:
	            dlg = wxMessageDialog(self,
	                    "Could not connect to SQLite database at %s"%location,
	                    "Connection problem!",
	                    wxICON_ERROR|wxOK)
	            dlg.ShowModal()
	            dlg.Destroy()
	            cursor = None
	        
	    elif not OFFLINE_ONLY:
	        try:
	            Con = MySQLdb.connect(host=location, user=USER, passwd=PW, db=DB)
	            cursor = Con.cursor()
	        except:
	            dlg = wxMessageDialog(self,
	                    "host = %s | user = %s | password = %s**** | db = %s - could not connect!"%(host,USER,PW[:3],DB),
	                    "Connection problem",
	                    wxICON_ERROR|wxOK)
	            dlg.ShowModal()
	            dlg.Destroy()
	            cursor = None
	            
	    if cursor:
	        self.Cursors[host] = cursor
	        
	    return cursor
	
	
	def GetNote(self, L=None, item=None):
	    if L is None:
	        L = self.L
	        
	    if item is None:
	        if self.curIdx != -1:
	            item = self.ItemLists[L][self.curIdx]
	        else:
	            return ''
	        
	    Properties = self.PropertyDicts[L]
	    
	    cursor = self.Cursors[Properties['host']]
	    table = Properties['table']
	    cursor.execute("SELECT note from "+table+" WHERE id = %s", (item.id,))
	    
	    ###### Debug -- this does happen where note brings back None 053003
	    z = cursor.fetchone()
	    if z is None:
	        print "In GetNote -> SELECT should not bring back None"
	        print "           -> item.id=",item.id
	        z = (None,)
	    note = z[0]
	    if note is None:
	        note = ''
	    return note
	    
	def CreateTable(self, host, table):
	    cursor = self.Cursors[host]
	    rdbms = host.split(':')[1]
	    if rdbms == 'sqlite':
	        sql = """CREATE TABLE '%s' ('id' varchar(36) PRIMARY KEY,
	'priority' int(1),
	'name' varchar(150),
	'createdate' datetime,
	'finisheddate' date,
	'duedate' date,
	'owner1' varchar(25),
	'owner2' varchar(25),
	'owner3' varchar(25),
	'note' text,
	'timestamp' timestamp(14))"""%table
	    else:
	        sql = """CREATE TABLE `%s` (`id` varchar(36) NOT NULL default '',
	`priority` int(1) NOT NULL default '1',
	`name` varchar(150) NOT NULL default '',
	`createdate` datetime NOT NULL default '0000-00-00 00:00:00',
	`finisheddate` date default '0000-00-00',
	`duedate` date default '0000-00-00',
	`owner1` varchar(25) default '',
	`owner2` varchar(25) default '',
	`owner3` varchar(25) default '',
	`note` text,
	`timestamp` timestamp(14) NOT NULL,PRIMARY KEY  (`id`)) TYPE=MyISAM"""%table
	        
	    cursor.execute(sql)
	def ReadFromDB(self):
	    L = self.L
	    Properties = self.PropertyDicts[L]
	    
	    host = Properties['host']
	    cursor = self.GetCursor(host)
	    if cursor is None:
	        return None
	        
	    table = Properties['table']
	    
	    owner = Properties['owner']
	    if owner == '*ALL':
	        WHERE = ""
	    else:
	        WHERE = 'WHERE (owner1 = "%s" OR owner2 = "%s" OR owner3 = "%s")'%(owner,owner,owner)
	    
	    #-1 show them all; 0 show none; integer show for that many days
	    days = Properties['showfinished']	
	    if days != -1:
	        if days:
	            date = mx.DateTime.now() - days
	            t = "(finisheddate IS NULL OR finisheddate > '%s')"%date
	        else:
	            t = "finisheddate IS NULL"
	        
	        if WHERE:
	            WHERE = "%s AND %s"%(WHERE,t)
	        else:
	            WHERE = " WHERE %s"%t
	
	    Sort = Properties['sort']
	    if Sort:
	        sort_attr = Sort['attribute']
	        if sort_attr == 'date':
	            sort_attr = Properties['LCdate']
	        elif sort_attr == 'owners':
	            sort_attr = 'owner1'
	        
	        WHERE = WHERE + " ORDER BY " + sort_attr
	        #if not direction: WHERE = WHERE + " DESC"   works because ASC is the default
	        if not Sort['direction']:
	            WHERE = WHERE + " DESC" 
	
	    sql = "SELECT priority,name,createdate,finisheddate,duedate,owner1,owner2,owner3,id,timestamp FROM %s %s"%(table,WHERE)
	            
	    try:
	        cursor.execute(sql)
	    except:
	        print "Cannot read %s: %s"%(Properties['host'],table)
	        return None #[]
	    else:
	        return cursor.fetchall()
	        
	
	
	def CreateAndDisplayList(self, results):
	    LCtrl = self.ListCtrls[self.L]
	    LCdate = self.PropertyDicts[self.L]['LCdate']
	    if LCdate == 'timestamp':
	        format = '%m/%d %H:%M:%S'
	    else:
	        format = '%m/%d/%y'
	    itemlist = []
	
	    LCtrl.DeleteAllItems()
	    class Item: pass
	    
	    for x,row in enumerate(results):
	        
	        item = Item()
			item.priority = int(row[0]) #int(row[0]) needs int because it seems to come back as a long from MySQL
			item.name = row[1]
			item.createdate = row[2]
			item.finisheddate = row[3]
			item.duedate = row[4]
			item.owners = [y for y in row[5:8] if y] #if you carry around ['tom',None,None] Note this is 5:8 not 5:7
			item.id = row[8]
			item.timestamp = row[9]
			
	        itemlist.append(item)
	        
			LCtrl.InsertImageStringItem(x, str(item.priority), LCtrl.idx1)
			LCtrl.SetStringItem(x,1,item.name)
			LCtrl.SetStringItem(x,2,'; '.join(item.owners))
			date = item.__dict__[LCdate]
			LCtrl.SetStringItem(x,3,date and date.Format(format) or "")
			
			if item.finisheddate:
			    LC_Item = LCtrl.GetItem(x)
			    LC_Item.SetImage(LCtrl.idx0) #might just want generic number or greyed one two three
			    LC_Item.SetTextColour(wxLIGHT_GREY)
			    LCtrl.SetItem(LC_Item)
			    
			elif item.priority==2:
			    LC_Item = LCtrl.GetItem(x)
			    f = self.LC_font
			    f.SetWeight(wxBOLD)
			    LC_Item.SetFont(f)
			    f.SetWeight(wxNORMAL) #resetting weight
			    LCtrl.SetItem(LC_Item)
			
			elif item.priority==3:
			    LC_Item = LCtrl.GetItem(x)
			    f = self.LC_font
			    f.SetWeight(wxBOLD)
			    LC_Item.SetFont(f)
			    f.SetWeight(wxNORMAL) #return to normal
			    LC_Item.SetTextColour(wxRED)
			    LCtrl.SetItem(LC_Item)	
	    return itemlist
	
	
	def OnSync(self, evt=None):
	    if self.modified:
	        self.OnUpdate()
	    #Note that the results of an sqlite query are an instance that you need to turn into a tuple or MySQL gets unhappy
	
	    if OFFLINE_ONLY:
	        dlg = wxMessageDialog(self, "You need to be online to synchronize!", style = wxOK|wxICON_ERROR)
	        dlg.ShowModal()
	        dlg.Destroy()
	        return
	        
	    dlg = wxMessageDialog(self,"Synchronize Table(s): "+" and ".join(SYNC_TABLES),"Synchronize...",wxICON_QUESTION|wxYES_NO)
	    val = dlg.ShowModal()
	    dlg.Destroy()
	    if val == wxID_NO:
	        return
	    
	    if REMOTE_HOST is None:
	        print "There doesn't appear to be a Remote Server"
	        return
	
	    if LOCAL_HOST is None:
	        print "There doesn't appear to be a Local Server"
	        return
	        
	    print "LOCAL_HOST=",LOCAL_HOST
	    print "REMOTE_HOST=",REMOTE_HOST
	
	    r_cursor = self.GetCursor(REMOTE_HOST)
	    if r_cursor is None:
	        print "Couldn't get a cursor for %s"%REMOTE_HOST
	        return
	
	    l_cursor = self.GetCursor(LOCAL_HOST)
	    if l_cursor is None:
	        print "Couldn't get a cursor for %s"%LOCAL_HOST
	        return
	
	    # moving the sync time back a second to make sure that we don't lose track of any nodes
	    #that are being updated or inserted at the same time as we are syncing
	    r_cursor.execute("SELECT NOW()")
	    l_now = mx.DateTime.now()-mx.DateTime.oneSecond
	    r_now = r_cursor.fetchone()[0]-mx.DateTime.oneSecond
	    #because of some inconsistent rounding appears necessary to make sure the sqlite timestamp is less than l_now
	    #having seen same issue for mysql but for consistency (and because sqlite could also be "server" rdbms
	    l_ts = l_now - mx.DateTime.DateTimeDelta(0,0,0,0.02)
	    r_ts = r_now - mx.DateTime.DateTimeDelta(0,0,0,0.02)
	    print "l_now=",l_now, "l_ts =",l_ts
	    print "r_now=",r_now, "r_ts=",r_ts
	
	    r_cursor.execute("SELECT MAX(last_sync) FROM user_sync WHERE user = %s", (USER,))
	    r_last_sync = r_cursor.fetchone()[0]
	    print "last sync (remote time) =",r_last_sync
	
	    l_cursor.execute("SELECT MAX(last_sync) FROM user_sync")
	    l_last_sync = l_cursor.fetchone()[0] #note MAX returns a string with sqlite so we turn it make into DateTime
	    l_last_sync = mx.DateTime.DateTimeFrom(l_last_sync)
	    print "last sync (local time) =",l_last_sync
	
	    for table in SYNC_TABLES:
	        # Need to pick up changes for both so syncing one doesn't add new things and screw up the second sync
	        print "Checking "+table+" on the Remote Server; changes (excluding deletes) are:"
	        r_cursor.execute("SELECT id,createdate from "+table+" WHERE timestamp > %s AND timestamp <= %s",(r_last_sync,r_now)) 
	        r_results = r_cursor.fetchall()
	        print "Server changes (excluding deletes)"
	        print r_results
	        
	        print "Checking "+table+" on Local; changes (excluding deletes) are:"
	        l_cursor.execute("SELECT id,createdate from "+table+" WHERE timestamp > %s AND timestamp <= %s",(l_last_sync,l_now))
	        l_results = l_cursor.fetchall()
	        print "Local changes (excluding deletes)"
	        print l_results
	
	        for id, createdate in r_results:
	            r_cursor.execute("SELECT priority,name,owner1,owner2,owner3,createdate,finisheddate,duedate,note,id FROM "+table+" WHERE ID = %s",(id,))
	            row = r_cursor.fetchone()
	            if row:
	                if createdate > r_last_sync:
	                    l_cursor.execute("INSERT INTO "+table+" (priority,name,owner1,owner2,owner3,createdate,finisheddate,duedate,note,id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", row) #*row also works
	                    print "Created %s in %s on Local"%(id,table)
	                else:
	                    l_cursor.execute("UPDATE "+table+" SET priority = %s, name =%s, owner1 = %s, owner2 = %s, owner3 = %s, createdate = %s, finisheddate = %s, duedate = %s, note = %s WHERE id = %s", row)
	                    print "Updated %s in %s on Local"%(id,table)
	                # for reasons I don't understand l_now here is a 1/100 ahead of l_now when inserted into user_sync
	                l_cursor.execute("UPDATE "+table+" SET timestamp = %s WHERE id = %s", (l_ts,id))
	        
	        for id, createdate in l_results:
	            l_cursor.execute("SELECT priority,name,owner1,owner2,owner3,createdate,finisheddate,duedate,note,id FROM "+table+" WHERE ID = %s",(id,))
	            row = l_cursor.fetchone()
	            if row:
	                row = tuple(row)
	                #above needed because sqlite returns an enhanced tuple-like object that is not a tuple
	                if createdate > l_last_sync:
	                    r_cursor.execute("INSERT INTO "+table+" (priority,name,owner1,owner2,owner3,createdate,finisheddate,duedate,note,id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", row)
	                    print "Created %s in %s on Server"%(id,table)
	                else:
	                    r_cursor.execute("UPDATE "+table+" SET priority = %s, name =%s, owner1 = %s, owner2 = %s, owner3 = %s, createdate = %s, finisheddate = %s, duedate = %s, note = %s WHERE id = %s", row)
	                    print "Updated %s in %s on Server"%(id,table)
	                r_cursor.execute("UPDATE "+table+" SET timestamp = %s WHERE id = %s", (r_ts,id))
	    
	    #Handle the deletes; Note if at some point only 'd's are being written won't have to check for 'd'
	    r_cursor.execute("SELECT id,table_name FROM sync WHERE timestamp > %s AND timestamp <= %s AND action = 'd'",(r_last_sync,r_now))
	    r_results = r_cursor.fetchall()
	
	    l_cursor.execute("SELECT id,table_name FROM sync WHERE timestamp > %s AND timestamp <= %s AND action = 'd'",(l_last_sync,l_now))
	    l_results = l_cursor.fetchall()
	
	    for id,table in l_results:
	        r_cursor.execute("DELETE from "+table+" WHERE id = %s", (id,))
	        print "Deleted %s from %s on Server (if it existed there)"%(id,table)
	
	    for id,table in r_results:
	        l_cursor.execute("DELETE from "+table+" WHERE id = %s", (id,))
	        print "Deleted %s from %s on Local (if it existed there)"%(id,table)	
	    #End of deletes code
	    
	    #update the user_sync database with the latest sync times
	    l_cursor.execute("INSERT INTO user_sync (user,last_sync) VALUES (%s,%s)", (USER,l_now)) #don't really need USER for local
	    r_cursor.execute("INSERT INTO user_sync (user,last_sync) VALUES (%s,%s)", (USER,r_now)) 
	    
	    print "Synchronization completed"
	
	def TimeStamper(self, host, cursor, table, id):
	    #note that you can insert a timestamp value into an mysql timestamp field
	    if host.split(':')[1] == 'sqlite': #host -> location:rdbms
	        timestamp = mx.DateTime.now()
	        cursor.execute("UPDATE "+table+" SET timestamp = %s WHERE id = %s", (timestamp,id))
	    else:
	        cursor.execute("Select timestamp from "+table+" WHERE id = %s", (id,))
	        timestamp = cursor.fetchone()[0]
	        
	    return timestamp
	def OnShowEvaluate(self, evt=None):
	    
	    self.EvalDialog.Show(True)
	    self.EvalDialog.EvalText.SetSelection(-1,-1)
	    self.EvalDialog.EvalText.SetFocus()
	    
	def OnEvaluate(self, evt=None):
	    expr = self.EvalDialog.EvalText.GetValue()
	    print "%s => "%expr,
	    print eval(expr)
	    
	def OnShowAbout(self, evt=None):
	    from about import AboutBox
	    dlg = AboutBox(self, app_version = VERSION)
	    dlg.ShowModal()
	    dlg.Destroy()
	    
	def OnShowHelp(self, evt=None):
	    os.startfile('ListManager.chm')
	    
	def GetUID(self):
	    pyiid = CreateGuid()
	    # the str(pyiid) looks like {....} and doing [1:-1] strips that off
	    return str(pyiid)[1:-1]
	    
	def OnIdle(self, evt):	
		if OUTLOOK:
		    input,output,exc = select.select([self.sock],[],[],0)
		    if input:
		        client,addr = self.sock.accept() # Get a connection
		        rec = client.recv(8192)
		        d = pickle.loads(rec)
		        
		        class Item: pass
		        
		        item = Item()
		        item.id = self.GetUID()
		        item.priority = 1
		        item.createdate = mx.DateTime.now()
		        item.duedate = item.finisheddate = None
		        
		        #outlook strings are unicode; ascii encode makes sure no chars above 127
		        name = d['Subject'].encode('ascii','replace') 
		        item.name = name[:150]
		        
		        owner = d['SenderName'].encode('ascii','replace') #encode takes unicode to standard strings
		        owner = owner[:25]
		        item.owners = [owner]
		        
		        note = d['CreationTime'] + '\n' + d['Body'].encode('ascii','replace')
		        #foldername = d['Parent.Name']
		        
		        #location, rdbms, table = MAIL_LIST_PATH.split(':')
		        #host = '%s:%s'%(location,rdbms)
		        host, table = re.split('(.*?:.*?):', MAIL_LIST_PATH)[1:3] #really just for fun
		        
		        cursor = self.Cursors[host]
		        
		        cursor.execute("INSERT INTO "+table+" (priority,name,createdate,finisheddate,duedate,owner1,note,id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
		            (item.priority, name, item.createdate, item.finisheddate, item.duedate, owner, note, item.id))
		        
		        item.timestamp = self.TimeStamper(host, cursor, table, item.id)
		        
		        #check to see if table is open
		        for L,Properties in enumerate(self.PropertyDicts):
		            if Properties['table'] == table and Properties['host'] == host:
		                break
		        else:
		            print "Table not open but wrote to database anyway" #Needs to be a dialog box
		            return
		        
		        # could have started to edit something and never finished it
		        if self.modified:
		            self.OnUpdate()
		        
		        if self.L != L:
		            self.nb.SetSelection(L) # Note that this does not call OnPageChange if the page doesn't change
		        
		        LCtrl = self.ListCtrls[L]
		        
		        if self.curIdx != -1:
		            LCtrl.SetItemState(self.curIdx, 0, wxLIST_STATE_SELECTED)
		        
		        self.ItemLists[L].insert(0,item)    
		        LCtrl.InsertImageStringItem(0,"1", LCtrl.idx1)
		        LCtrl.SetStringItem(0,self.attr2col_num['name'],name)
		        LCtrl.SetStringItem(0, self.attr2col_num['owners'], owner)
		        
		        if Properties['LCdate'] == 'timestamp':
		            LCtrl.SetStringItem(0, self.attr2col_num['date'], item.timestamp.Format("%m/%d %H:%M:%S"))
		        elif Properties['LCdate'] == 'createdate':
		            LCtrl.SetStringItem(0, self.attr2col_num['date'], item.createdate.Format('%m/%d/%y'))
		        
		        LCtrl.SetItemState(0, wxLIST_STATE_SELECTED, wxLIST_STATE_SELECTED)
		        self.curIdx = 0 
		
		for ed in self.editor:
		    path = ed['path']
		    t = os.path.getmtime(path)
		    if t != ed['time']:
		        f = file(path,'r')
		        note = f.read()
		        f.close()
		        ed['time'] = t
		        
		        host = ed['host']
		        cursor = self.Cursors[host]
		        table = ed['table']
		        id = ed['id']
		        cursor.execute("UPDATE "+table+" SET note = %s WHERE id = %s", (note,id)) 
		        # see @rst documentation note
		        ts = self.TimeStamper(host, cursor, table, id)
		        
		        idx = self.curIdx
		        L = self.L
		        if idx != -1:
		            item = self.ItemLists[L][idx]
		            if item.id == id:
		                self.note.SetValue(note)
		                item.timestamp = ts
		                
		                if self.PropertyDicts[L]['LCdate'] == 'timestamp':
		                    self.ListCtrls[L].SetStringItem(idx, self.attr2col_num['date'], item.timestamp.Format("%m/%d %H:%M:%S"))
		    
		                if 'note' in self.modified: #if necessary only if somehow note text didn't change
		                    del self.modified['note']
		
	    
class ListCtrl(wxListCtrl, wxListCtrlAutoWidthMixin):
	def __init__(self, parent, ID, pos=wxDefaultPosition, size=wxDefaultSize, style=0):
	    wxListCtrl.__init__(self, parent, ID, pos, size, style)
	    wxListCtrlAutoWidthMixin.__init__(self)
	
	    self.il = wxImageList(16,16)
	
	    sm_up = self.il.Add(wxBitmap('bitmaps\\up_arrow.bmp')) #(images.getSmallUpArrowBitmap())
	    sm_dn = self.il.Add(wxBitmap('bitmaps\\down_arrow.bmp'))
	    self.arrows = (sm_up,sm_dn)
	    
	    self.idx1 = self.il.Add(wxBitmap('bitmaps\\box.bmp'))
	    self.idx0 = self.il.Add(wxBitmap('bitmaps\\filledwhitebox.bmp'))    
	
	    self.SetImageList(self.il, wxIMAGE_LIST_SMALL)
	
	    EVT_LIST_COL_BEGIN_DRAG(self, self.GetId(), self.OnColBeginDrag)    
	
	    self.SetUpColumns()
	
	def SetUpColumns(self):
	    #Need to to construct column heads for columns with sorting by hand to get sorting images on columns
	    info = wxListItem()
	    info.m_mask = wxLIST_MASK_TEXT | wxLIST_MASK_IMAGE | wxLIST_MASK_FORMAT
	    info.m_image = -1
	
	    #Oth column is priority which is sortable
	    info.m_format = wxLIST_FORMAT_LEFT
	    info.m_text = "P"
	    self.InsertColumnInfo(0, info)
	    self.SetColumnWidth(0, 35)
	    
	    self.InsertColumn(1, "Name")
	    self.SetColumnWidth(1, 590)
	
	    self.InsertColumn(2, "Owner")
	    self.SetColumnWidth(2, 100)
	    
	    #3th column is create ate and same as with priority - needs to constructed by hand
	    info.m_format = wxLIST_FORMAT_LEFT
	    info.m_text = "Due Date"
	    self.InsertColumnInfo(3, info)
	    self.SetColumnWidth(3, 75)                
	
	def OnColBeginDrag(self, evt):
	    #if inplace editor then change its dimensions
	    if evt.GetColumn() == 0:
	        evt.Veto()
class MyApp(wxApp):
	def OnInit(self):
	    global OFFLINE_ONLY, CANCEL
	    wxInitAllImageHandlers()
	    
	    if STARTUP_DIALOG:
	        startup = StartupDialog(None, 'List Manager')
	        val = startup.ShowModal()
	        startup.Destroy()
	        if val == wxID_YES:
	            OFFLINE_ONLY = True
	        elif val == wxID_NO:
	            OFFLINE_ONLY = False
	        elif val == wxID_CANCEL:
	            CANCEL = True
	            return True
	
	    if OFFLINE_ONLY is False:
	        server = REMOTE_HOST.split(':')[0]
	        try:
	            socket.gethostbyname(server)
	        except:
	            dlg = wxMessageDialog(None, "Cannot connect to remote server! Only offline access is possible.", "ListManager", style=wxOK|wxICON_EXCLAMATION|wxSTAY_ON_TOP)
	            dlg.ShowModal()
	            dlg.Destroy()
	            OFFLINE_ONLY = True
	            
	    frame = ListManager(None, -1, "List Manager", size = (X,Y))
	    frame.Show(True)
	    self.SetTopWindow(frame)
	    CANCEL = False
	    return True
	
	
class Logger:
    def __init__(self):
        self.dlg = LoggerDialog(None, "", "Alerts and Exceptions", dir=DIRECTORY)
    def write(self, error_msg):
        if not self.dlg.IsShown():
            self.dlg.text.AppendText("\n%s\n"%time.asctime())
            self.dlg.Show(True)
        
        self.dlg.text.AppendText(error_msg)

def run():
    app = MyApp(0)
    if not CANCEL:
        sys.stderr = sys.stdout = Logger()
        app.MainLoop()
    
if __name__ == '__main__':
    run()
