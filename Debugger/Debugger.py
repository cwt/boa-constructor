#----------------------------------------------------------------------------
# Name:         Debugger.py                                                  
# Purpose:      wxPython debugger, currently a port of IDLE's debugger       
#               written by Guido van Rossum                                  
#                                                                            
# Author:       Riaan Booysen                                                
#                                                                            
# Created:      2000/01/11                                                   
# RCS-ID:       $Id$       
# Copyright:    (c) Riaan Booysen                                            
# Licence:      GPL                                                          
#----------------------------------------------------------------------------

# XXX I must still try to see if it's not possible the change code while
# XXX debugging, reload sometimes works
# XXX Going to source code on an error

from   wxPython.wx import *
import wxPython
import ShellEditor, Preferences
import string, sys, os
from os import path
from repr import Repr
import traceback, linecache, imp, pprint
import Utils
from Preferences import pyPath, IS, flatTools
#from PhonyApp import wxPhonyApp
from Breakpoint import bplist

from IsolatedDebugger import DebuggerConnection, DebuggerController

# Specific to in-process debugging:
debugger_controller = DebuggerController()


wxID_STACKVIEW = NewId()
class StackViewCtrl(wxListCtrl):
    def __init__(self, parent, flist, debugger):
        wxListCtrl.__init__(self, parent, wxID_STACKVIEW,
                            style = wxLC_REPORT | wxLC_SINGLE_SEL )
        self.InsertColumn(0, 'Frame', wxLIST_FORMAT_LEFT, 150) 
        self.InsertColumn(1, 'Line', wxLIST_FORMAT_LEFT, 35)
        self.InsertColumn(2, 'Code', wxLIST_FORMAT_LEFT, 300)
        EVT_LIST_ITEM_SELECTED(self, wxID_STACKVIEW,
                               self.OnStackItemSelected)
        EVT_LIST_ITEM_DESELECTED(self, wxID_STACKVIEW,
                                 self.OnStackItemDeselected)
        EVT_LEFT_DCLICK(self, self.OnGotoSource) 

        self.flist = flist
        self.debugger = debugger
        self.stack = []
        self.selection = -1

    def load_stack(self, stack, index=None):
        self.stack = stack
        self.DeleteAllItems()

        for i in range(len(stack)):
            entry = stack[i]
            lineno = entry['lineno']
            modname = entry['modname']
            filename = entry['filename']
            funcname = entry['funcname']
            sourceline = linecache.getline(filename, lineno)
            sourceline = string.strip(sourceline)
            if funcname in ("?", "", None):
                item = "%s, line %d: %s" % (modname, lineno, sourceline)
                attrib = modname
            else:
                item = "%s.%s(), line %d: %s" % (modname, funcname,
                                                 lineno, sourceline)
                attrib = modname+'.'+funcname
                
            if i == index:
                item = "> " + item
            pos = self.GetItemCount()
            self.InsertStringItem(pos, attrib)
            self.SetStringItem(pos, 1, `lineno`, -1)
            self.SetStringItem(pos, 2, sourceline, -1)

    def OnStackItemSelected(self, event):
        self.selection = event.m_itemIndex

        stacklen = len(self.stack)
        if 0 <= self.selection < stacklen:
            self.debugger.debug_conn.setWatchQueryFrame(
                stacklen - self.selection)
            self.debugger.show_variables()
            #self.debugger.show_frame(self.stack[self.selection])
        
    def OnStackItemDeselected(self, event):
        self.selection = -1
            
    def OnGotoSource(self, event):
        if self.selection != -1:
            entry = self.stack[self.selection]
            lineno = entry['lineno']
            modname = entry['modname']
            filename = entry['filename']
            
            if filename[0] != '<' and filename[-1] != '>':
                filename = self.debugger.resolvePath(filename)
                if not filename: return

                editor = self.debugger.model.editor
                editor.SetFocus()
                editor.openOrGotoModule(filename)
                model = editor.getActiveModulePage().model
                model.views['Source'].focus()
                model.views['Source'].SetFocus()
                model.views['Source'].selectLine(lineno - 1)


[wxID_BREAKVIEW, wxID_BREAKSOURCE, wxID_BREAKEDIT, wxID_BREAKDELETE, 
  wxID_BREAKENABLED, wxID_BREAKREFRESH] = map(lambda x: NewId(), range(6))

class BreakViewCtrl(wxListCtrl):
    def __init__(self, parent, debugger):#, flist, browser):
        wxListCtrl.__init__(self, parent, wxID_BREAKVIEW, 
          style = wxLC_REPORT | wxLC_SINGLE_SEL )
        self.InsertColumn(0, 'Module', wxLIST_FORMAT_LEFT, 90) 
        self.InsertColumn(1, 'Line', wxLIST_FORMAT_CENTER, 40)
        self.InsertColumn(2, 'Ignore', wxLIST_FORMAT_CENTER, 45)
        self.InsertColumn(3, 'Hits', wxLIST_FORMAT_CENTER, 45)
        self.InsertColumn(4, 'Condition', wxLIST_FORMAT_LEFT, 250)

        self.brkImgLst = wxImageList(16, 16)
        self.brkImgLst.Add(IS.load('Images/Debug/Breakpoint-red.bmp'))
        self.brkImgLst.Add(IS.load('Images/Debug/Breakpoint-yellow.bmp'))
        self.brkImgLst.Add(IS.load('Images/Debug/Breakpoint-gray.bmp'))
        self.brkImgLst.Add(IS.load('Images/Debug/Breakpoint-blue.bmp'))

        EVT_LIST_ITEM_SELECTED(self, wxID_BREAKVIEW,
                               self.OnBreakpointSelected)
        EVT_LIST_ITEM_DESELECTED(self, wxID_BREAKVIEW,
                                 self.OnBreakpointDeselected)
        EVT_LEFT_DCLICK(self, self.OnGotoSource) 

        EVT_RIGHT_DOWN(self, self.OnRightDown)
        EVT_COMMAND_RIGHT_CLICK(self, -1, self.OnRightClick)
        EVT_RIGHT_UP(self, self.OnRightClick)
        
        self.menu = wxMenu()

        self.menu.Append(wxID_BREAKSOURCE, 'Goto source')
        self.menu.Append(wxID_BREAKREFRESH, 'Refresh')
        self.menu.Append(-1, '-')
        self.menu.Append(wxID_BREAKEDIT, 'Edit')
        self.menu.Append(wxID_BREAKDELETE, 'Delete')
        self.menu.Append(-1, '-')
        self.menu.Append(wxID_BREAKENABLED, 'Enabled', checkable = true)
        self.menu.Check(wxID_BREAKENABLED, true)
        EVT_MENU(self, wxID_BREAKSOURCE, self.OnGotoSource)
        EVT_MENU(self, wxID_BREAKREFRESH, self.OnRefresh)
        EVT_MENU(self, wxID_BREAKEDIT, self.OnEdit)
        EVT_MENU(self, wxID_BREAKDELETE, self.OnDelete)
        EVT_MENU(self, wxID_BREAKENABLED, self.OnToggleEnabled)
        self.x = self.y = 0

        self.SetImageList(self.brkImgLst, wxIMAGE_LIST_SMALL)

        self.selection = -1
        self.debugger = debugger
        self.bps = []

        #for file, lineno in bdb.Breakpoint.bplist.keys():
        #    self.debugger.set_internal_breakpoint(file, lineno)

    def destroy(self):
        self.menu.Destroy()
            
    def refreshList(self):
        self.selection = -1
        self.DeleteAllItems()
        bps = bplist.getBreakpointList()
        # Sort by filename and lineno.
        bps.sort(lambda a, b:
                 cmp((a['filename'], a['lineno']),
                     (b['filename'], b['lineno'])))
        self.bps = bps
        for p in range(len(bps)):
            bp = bps[p]
            imgIdx = 0
            if not bp['enabled']:
                imgIdx = 2
            elif bp['temporary']: imgIdx = 3

            self.InsertImageStringItem(
                p, path.basename(bp['filename']), imgIdx)
            self.SetStringItem(p, 1, str(bp['lineno']))
            if bp['enabled']: self.SetStringItem(p, 3, '*')
            # TODO: Reenable hit counts.
            #self.SetStringItem(p, 2, `bp.ignore`)
            #self.SetStringItem(p, 3, `bp.hits`)
            self.SetStringItem(p, 2, '')
            self.SetStringItem(p, 3, '')
            self.SetStringItem(p, 4, bp['cond'] or '')
    
    def addBreakpoint(self, filename, lineno):
        self.refreshList()

    def OnBreakpointSelected(self, event):
        self.selection = event.m_itemIndex
        
    def OnBreakpointDeselected(self, event):
        self.selection = -1
    
    def OnGotoSource(self, event):
        if self.selection != -1:
            bp = self.bps[self.selection]

            filename = self.debugger.resolvePath(bp['filename'])
            if not filename: return

            editor = self.debugger.model.editor
            editor.SetFocus()
            editor.openOrGotoModule(filename)
            model = editor.getActiveModulePage().model
            model.views['Source'].focus()
            model.views['Source'].SetFocus()
            model.views['Source'].selectLine(bp.line - 1)

    def OnEdit(self, event):
        pass

    def OnDelete(self, event):
        if self.selection != -1:
            bp = self.bps[self.selection]
            bplist.deleteBreakpoints(bp['filename'], bp['lineno'])
            # TODO: notify process.
            self.refreshList()

    def OnRefresh(self, event):
        self.refreshList()

    def OnToggleEnabled(self, event):
        if self.selection != -1:
            bp = self.bps[self.selection]
            bp['enabled'] = not bp['enabled']
            # TODO: notify process.
            self.refreshList()
         
    def OnRightDown(self, event):
        self.x = event.GetX()
        self.y = event.GetY()

    def OnRightClick(self, event):
        if self.selection != -1:
            self.menu.Check(wxID_BREAKENABLED, 
              self.listAllBreakpoints()[self.selection].enabled)
            self.PopupMenu(self.menu, wxPoint(self.x, self.y))
        

# XXX Expose classes' dicts as indented items
wxID_NSVIEW = NewId()
class NamespaceViewCtrl(wxListCtrl):
    def __init__(self, parent, add_watch, is_local, name):  # , dict=None):
        wxListCtrl.__init__(self, parent, wxID_NSVIEW, 
          style = wxLC_REPORT | wxLC_SINGLE_SEL )
        self.InsertColumn(0, 'Attribute', wxLIST_FORMAT_LEFT, 125) 
        self.InsertColumn(1, 'Value', wxLIST_FORMAT_LEFT, 200)

        EVT_LIST_ITEM_SELECTED(self, -1, self.OnItemSelect)
        EVT_LIST_ITEM_DESELECTED(self, -1, self.OnItemDeselect)
        self.selected = -1

        EVT_RIGHT_DOWN(self, self.OnRightDown)
        EVT_COMMAND_RIGHT_CLICK(self, -1, self.OnRightClick)
        EVT_RIGHT_UP(self, self.OnRightClick)
        
        self.is_local = is_local
            
        self.menu = wxMenu()

        idAs = NewId()
        idA = NewId()
        self.menu.Append(idAs, 'Add as watch')
        self.menu.Append(idA, 'Add a %s watch' % name)
        EVT_MENU(self, idAs, self.OnAddAsWatch)
        EVT_MENU(self, idA, self.OnAddAWatch)
        self.x = self.y = 0
 
        self.repr = Repr()
        self.repr.maxstring = 60
        self.repr.maxother = 60
        self.names = []
        
        self.add_watch = add_watch

        # self.load_dict(dict)

    def destroy(self):
        self.menu.Destroy()

    dict = -1

    def load_dict(self, dict, force=0):
        if dict == self.dict and not force:
            return

        self.DeleteAllItems()
        self.dict = None
                
        if not dict:
            pass
        else:
            self.names = dict.keys()
            self.names.sort()
            row = 0
            for name in self.names:
                svalue = dict[name]
                #svalue = self.repr.repr(value) # repr(value)

                self.InsertStringItem(row, name)
                self.SetStringItem(row, 1, svalue, -1)
                
                row = row + 1

        self.dict = dict
    
    def OnAddAsWatch(self, event):
        if self.selected != -1:
            name = self.names[self.selected]
            self.add_watch(name, self.is_local)

    def OnAddAWatch(self, event):
        self.add_watch('', self.is_local)

    def OnItemSelect(self, event):
        self.selected = event.m_itemIndex

    def OnItemDeselect(self, event):
        self.selected = -1

    def OnRightDown(self, event):
        self.x = event.GetX()
        self.y = event.GetY()

    def OnRightClick(self, event):
        self.PopupMenu(self.menu, wxPoint(self.x, self.y))

##    def close(self):
##        self.frame.destroy()

wxID_WATCHVIEW = NewId()
class WatchViewCtrl(wxListCtrl):

    def __init__(self, parent, images, debugger):
        wxListCtrl.__init__(self, parent, wxID_WATCHVIEW, 
          style = wxLC_REPORT | wxLC_SINGLE_SEL )
        self.InsertColumn(0, 'Attribute', wxLIST_FORMAT_LEFT, 125) 
        self.InsertColumn(1, 'Value', wxLIST_FORMAT_LEFT, 200)
 
        self.repr = Repr()
        self.repr.maxstring = 60
        self.repr.maxother = 60
        self.debugger = debugger
        
        self.watches = []

        self.SetImageList(images, wxIMAGE_LIST_SMALL)

        EVT_LIST_ITEM_SELECTED(self, -1, self.OnItemSelect)
        EVT_LIST_ITEM_DESELECTED(self, -1, self.OnItemDeselect)
        self.selected = -1

        EVT_RIGHT_DOWN(self, self.OnRightDown)
        EVT_COMMAND_RIGHT_CLICK(self, -1, self.OnRightClick)
        EVT_RIGHT_UP(self, self.OnRightClick)

        self.menu = wxMenu()

        id = NewId()
        self.menu.Append(id, 'Delete')
        EVT_MENU(self, id, self.OnDelete)
        id = NewId()
        self.menu.Append(id, 'Expand')
        EVT_MENU(self, id, self.OnExpand)
        self.x = self.y = 0
    
    def destroy(self):
        self.menu.Destroy()

    dict = -1
    
    def add_watch(self, name, local):
        if name: 
            self.watches.append((name, local))
        else:  
            dlg = wxTextEntryDialog(
                self, 'Enter name:', 'Add a watch:', '')
            try:
                if dlg.ShowModal() == wxID_OK:
                    self.watches.append((dlg.GetValue(), local))
            finally:
                dlg.Destroy()         

    def load_dict(self, svalues, force=0):
        self.DeleteAllItems()
        row = 0
        for name, local in self.watches:
            if svalues:
                svalue = svalues.get(name, '???')
            else:
                svalue = '???'
            if local:
                idx = 3
            else:
                idx = 4
            self.InsertImageStringItem(row, name, idx)
            self.SetStringItem(row, 1, svalue, idx)
            row = row + 1

    def OnDelete(self, event):
        if self.selected != -1:
            del self.watches[self.selected]
            self.DeleteItem(self.selected)

    def OnExpand(self, event):
        if self.selected != -1:
            name, local = self.watches[self.selected]
            self.debugger.expand_watch(name, local)

    def OnItemSelect(self, event):
        self.selected = event.m_itemIndex

    def OnItemDeselect(self, event):
        self.selected = -1

    def OnRightDown(self, event):
        self.x = event.GetX()
        self.y = event.GetY()

    def OnRightClick(self, event):
        self.PopupMenu(self.menu, wxPoint(self.x, self.y))

class DebugStatusBar(wxStatusBar):
    def __init__(self, parent):
        wxStatusBar.__init__(self, parent, -1)
        self.SetFieldsCount(2)

        rect = self.GetFieldRect(0)
        self.status = wxStaticText(self, 1001, 'Ready')
        self.status.SetDimensions(rect.x+2, rect.y+2, 
                                  rect.width-4, rect.height-4)

        rect = self.GetFieldRect(1)
        self.error = wxStaticText(self, 1002, ' ')
        self.error.SetBackgroundColour(wxNamedColour('white'))
        self.error.SetDimensions(rect.x+2, rect.y+2, 
                                 rect.width-4, rect.height-4)

        dc = wxClientDC(self)
        dc.SetFont(self.GetFont())
        (w,h) = dc.GetTextExtent('X')
        h = int(h * 1.8)
        self.SetSize(wxSize(100, h))

    def writeError(self, message):
        if message:
            self.error.SetBackgroundColour(wxNamedColour('yellow'))
        else:
            self.error.SetBackgroundColour(wxNamedColour('white'))
        self.error.SetLabel(message)

        rect = self.GetFieldRect(1)
        self.error.SetDimensions(
            rect.x+2, rect.y+2, rect.width-4, rect.height-4)

    def OnSize(self, event):
        rect = self.GetFieldRect(0)
        self.status.SetDimensions(rect.x+2, rect.y+2,
                                  rect.width-4, rect.height-4)
        rect = self.GetFieldRect(1)
        self.error.SetDimensions(rect.x+2, rect.y+2,
                                 rect.width-4, rect.height-4)


class DebuggerFrame(wxFrame):
    def __init__(self, model, stack = None):
        wxFrame.__init__(
            self, model.editor, -1, 'Debugger - %s - %s'
            % (path.basename(model.filename), model.filename),
            wxPoint(0, Preferences.paletteHeight), 
            wxSize(Preferences.inspWidth, Preferences.bottomHeight))

        conn_id = debugger_controller.createServer()
        self.debug_conn = DebuggerConnection(debugger_controller,
                                             conn_id)

        if wxPlatform == '__WXMSW__':
	    self.icon = wxIcon(Preferences.toPyPath(
                'Images\\Icons\\Debug.ico'), 
	      wxBITMAP_TYPE_ICO)
	    self.SetIcon(self.icon)

        self.viewsImgLst = wxImageList(16, 16)
        self.viewsImgLst.Add(IS.load('Images/Debug/Stack.bmp'))
        self.viewsImgLst.Add(IS.load('Images/Debug/Breakpoints.bmp'))
        self.viewsImgLst.Add(IS.load('Images/Debug/Watches.bmp'))
        self.viewsImgLst.Add(IS.load('Images/Debug/Locals.bmp'))
        self.viewsImgLst.Add(IS.load('Images/Debug/Globals.bmp'))
        self.viewsImgLst.Add(IS.load('Images/Debug/Output.bmp'))

        self.running = 0

        if model.defaultName != 'App' and model.app:
            filename = model.app.filename
        else:
            filename = model.filename
        self.setDebugFile(filename)
#        self.app = app
        self.model = model

        self.sb = DebugStatusBar(self)
        self.SetStatusBar(self.sb)

        self.toolbar = wxToolBar(
            self, -1, style = wxTB_HORIZONTAL|wxNO_BORDER|flatTools)
        self.SetToolBar(self.toolbar)
        
        Utils.AddToolButtonBmpIS(self, self.toolbar, 
          'Images/Debug/Debug.bmp', 'Debug', self.OnDebug)
        Utils.AddToolButtonBmpIS(self, self.toolbar, 
          'Images/Debug/Step.bmp', 'Step', self.OnStep)
        Utils.AddToolButtonBmpIS(self, self.toolbar, 
          'Images/Debug/Over.bmp', 'Over', self.OnOver)
        Utils.AddToolButtonBmpIS(self, self.toolbar, 
          'Images/Debug/Out.bmp', 'Out', self.OnOut)
        Utils.AddToolButtonBmpIS(self, self.toolbar, 
          'Images/Debug/Stop.bmp',  'Stop', self.OnStop)
        self.toolbar.AddSeparator()
        Utils.AddToolButtonBmpIS(self, self.toolbar, 
          'Images/Debug/SourceTrace-Off.bmp',  'Trace in source',
          self.OnSourceTrace, '1')
#          true, 'Images/Debug/SourceTrace-Off.bmp')

        self.toolbar.Realize()
        self.splitter = wxSplitterWindow(self, -1, style=wxSP_NOBORDER)

        # Create a Notebook
        self.nbTop = wxNotebook(self.splitter, -1)
        if wxPlatform == '__WXMSW__':
            self.nbTop.SetImageList(self.viewsImgLst)
        
        self.stackView = StackViewCtrl(self.nbTop, None, self)
        #if stack is None:
        #    try:
        #        stack = get_stack()
        #        self.stackView.load_stack(stack)
        #    except:
        #        pass
        #else:
        #    self.stackView.load_stack(stack)

        if wxPlatform == '__WXMSW__':
            self.nbTop.AddPage(self.stackView, 'Stack', imageId = 0)
        elif wxPlatform == '__WXGTK__':
            self.nbTop.AddPage(self.stackView, 'Stack')

        self.breakpts = BreakViewCtrl(self.nbTop, self)
        if wxPlatform == '__WXMSW__':
            self.nbTop.AddPage(self.breakpts, 'Breakpoints', imageId = 1)
        elif wxPlatform == '__WXGTK__':
            self.nbTop.AddPage(self.breakpts, 'Breakpoints')

        self.outp = wxTextCtrl(self.nbTop, -1, '', style = wxTE_MULTILINE)
        self.outp.SetBackgroundColour(wxBLACK)
        self.outp.SetForegroundColour(wxWHITE)
        self.outp.SetFont(wxFont(7, wxDEFAULT, wxNORMAL, wxNORMAL, false))
        if wxPlatform == '__WXMSW__':
            self.nbTop.AddPage(self.outp, 'Output', imageId = 5)
        elif wxPlatform == '__WXGTK__':
            self.nbTop.AddPage(self.outp, 'Output')

        # Create a Notebook
        self.nbBottom = wxNotebook(self.splitter, -1)
        if wxPlatform == '__WXMSW__':
            self.nbBottom.SetImageList(self.viewsImgLst)
            
        self.watches = WatchViewCtrl(self.nbBottom, self.viewsImgLst, self)
        if wxPlatform == '__WXMSW__':
            self.nbBottom.AddPage(self.watches, 'Watches', imageId = 2)
        elif wxPlatform == '__WXGTK__':
            self.nbBottom.AddPage(self.watches, 'Watches')

        self.locs = NamespaceViewCtrl(self.nbBottom, self.add_watch, 1,
                                      'local')
        if wxPlatform == '__WXMSW__':
            self.nbBottom.AddPage(self.locs, 'Locals', imageId = 3)
        elif wxPlatform == '__WXGTK__':
            self.nbBottom.AddPage(self.locs, 'Locals')

        self.globs = NamespaceViewCtrl(
            self.nbBottom, self.add_watch, 0, 'global')
        
        if wxPlatform == '__WXMSW__':
            self.nbBottom.AddPage(self.globs, 'Globals', imageId = 4)
        elif wxPlatform == '__WXGTK__':
            self.nbBottom.AddPage(self.globs, 'Globals')
        
        self.splitter.SetMinimumPaneSize(40)
        self.splitter.SplitHorizontally(self.nbTop, self.nbBottom)
        self.splitter.SetSashPosition(175)
        
        self.mlc = 0
        self.frame = None

        self.lastStepView = None
        self.lastStepLineno = -1

	EVT_CLOSE(self, self.OnCloseWindow)

    def add_watch(self, name, local):
        self.watches.add_watch(name, local)
        self.nbBottom.SetSelection(0)
        self.show_variables()        

    def expand_watch(self, name, local):
        names = self.debug_conn.getWatchSubobjects(name)
        for item in names:
            self.watches.add_watch('%s.%s' %(name, item), local)
        self.nbBottom.SetSelection(0)
        self.show_variables()        
        
    def show_variables(self, force=0):
        ws = self.watches.watches
        exprs = []
        for name, local in ws:
            exprs.append({'name':name, 'local':local})
        info = self.debug_conn.getVariablesAndWatches(exprs)
        if info is not None:
            ldict, gdict, svalues = info
        else:
            ldict, gdict, svalues = None, None, {}
        #frame = self.frame
        #if not frame:
        #    ldict = gdict = None
        #else:
        #    ldict = frame.f_locals
        #    gdict = frame.f_globals
        #    if self.locs and self.globs and ldict is gdict:
        #        ldict = None
        if self.locs:
            self.locs.load_dict(ldict, force)
        if self.globs:
            self.globs.load_dict(gdict, force)
        self.watches.load_dict(svalues, force)

    #def show_frame(self, (frame, lineno)):
    #    self.frame = frame
    #    self.show_variables()
    
    def getVarValue(self, name):
        return self.debug_conn.pprintVarValue(name)

    #def startMainLoop(self):
    #    self.model.editor.app.MainLoop()
    #    self.mlc = self.mlc + 1
        
    #def stopMainLoop(self):
    #    self.model.editor.app.ExitMainLoop()
    #    self.mlc = self.mlc - 1
    
#---------------------------------------------------------------------------

    def canonic(self, filename):
        # Canonicalize filename.
        return os.path.normcase(os.path.abspath(filename))

    #def do_clear(self, arg):
    #    self.clear_bpbynumber(arg)

    def setParams(self, params):
        self.params = params

    def setDebugFile(self, filename):
        # IsolatedDebugger TODO: setup the execution environment
        # the way it used to be done.
        self.filename = path.join(pyPath, filename)
        #saveout = sys.stdout
        #saveerr = sys.stderr

        #owin = self.outp
        #editor = self.model.editor
        #tmpApp = wxPython.wx.wxApp
        #tmpArgs = sys.argv[:]
        #wxPhonyApp.debugger = self
        #wxPython.wx.wxApp = wxPhonyApp
        
        self.modpath = os.path.dirname(self.filename)
        #sys.argv = [filename] + params
        #tmpPaths = sys.path[:]
        #sys.path.append(self.modpath)
        #sys.path.append(Preferences.pyPath)
        #cwd = path.abspath(os.getcwd())
        #os.chdir(path.dirname(filename))

    def runProcess(self):
        self.running = 1
        self.debug_conn.setAllBreakpoints(bplist.getBreakpointList())
        self.debug_conn.runFile(self.filename, self.params or [])
        self.queryDebuggerStatus()

##        try:
##            #sys.stderr = ShellEditor.PseudoFileErrTC(owin)
##            try:
##                #sys.stdout = ShellEditor.PseudoFileOutTC(owin)
##                try:
##                    #editor.app.saveStdio = sys.stdout, sys.stderr

##                    modname, ext = os.path.splitext(
##                        os.path.basename(filename))
##                    if sys.modules.has_key(modname):
##                        mod = sys.modules[modname]
##                    else:
##                        mod = imp.new_module(modname)
##                        sys.modules[modname] = mod
                        
##                    mod.__file__ = filename

##                    self.run("execfile(%s)" % `filename`, mod.__dict__)
##                except:
##                    (sys.last_type, sys.last_value,
##                     sys.last_traceback) = sys.exc_info()
##                    linecache.checkcache()
##                    traceback.print_exc()
##            finally:
##                pass
##                #sys.stdout = saveout
##        finally:
##            #sys.stderr = saveerr
##            #editor.app.saveStdio = sys.stdout, sys.stderr
##            #wxPython.wx.wxApp = tmpApp
##            #sys.path = tmpPaths
##            #sys.argv = tmpArgs
##            #os.chdir(cwd)

    def deleteBreakpoints(self, filename, lineno):
        self.debug_conn.clear_breaks(filename, lineno)
        self.breakpts.refreshList()

    def setBreakpoint(self, filename, lineno, tmp):
        self.debug_conn.set_break(filename, lineno, tmp)
##        self.nbTop.SetSelection(1)
##        filename = self.canonic(filename)
##        brpt = self.set_break(filename, lineno, tmp)
        self.breakpts.refreshList()
##        return brpt

##    def run(self, *args):
###        print args
##        try:
##            self.sb.status.SetLabel('Running.')
##            self.running = 1
##            return apply(bdb.Bdb.run, (self,) + args)
##        finally:
##            self.running = 0
##            self.sb.status.SetLabel('Finished.')

    def queryDebuggerStatus(self):
        info = self.debug_conn.getInteractionUpdate()
        # TODO: Use info['stdout'] and info['stderr'].
        self.running = info['running']
        stack = info['stack']
        if stack:
            bottom = stack[-1]
            filename = bottom['filename']
            funcname = bottom['funcname']
            lineno = bottom['lineno']
            base = os.path.basename(filename)
        else:
            filename = funcname = lineno = base = ''
            
        message = "%s:%s" % (base, lineno)
        if funcname != "?":
            message = "%s: %s()" % (message, funcname)

        self.sb.status.SetLabel(message)

        exc_type = info['exc_type']
        exc_value = info['exc_value']
        if exc_type is not None:
            m1 = exc_type
            if exc_value is not None:
                try:
                    m1 = "%s: %s" % (m1, exc_value)
                except:
                    pass
            bg = wxNamedColour('yellow')
        else:
            m1 = ''
            bg = wxNamedColour('white')#self.errorbg

        self.sb.writeError(m1)
        
        sv = self.stackView

        if sv:
            i = info['frame_stack_len']
            sv.load_stack(stack, i)

##        if ((string.lower(filename), lineno) in
##            bdb.Breakpoint.bplist.keys()):
        if bplist.hasBreakpoint(filename, lineno):
            self.sb.error.SetBackgroundColour(wxNamedColour('red'))
            self.sb.error.SetLabel('Breakpoint.')

            rect = self.sb.GetFieldRect(1)
            self.sb.error.SetDimensions(rect.x+2, rect.y+2, 
                                        rect.width-4, rect.height-4)
            # TODO: Remove temporary breakpoints from bplist
            # and unmark them in the editor.
            
        self.breakpts.refreshList()
        self.selectSourceLine(filename, lineno)

        #self.startMainLoop()
        #self.sb.status.SetLabel('')
        #self.sb.writeError('')
        #self.frame = None
    
    def resolvePath(self, filename):
        # Try to find file in Main module directory,
        # Boa directory and Current directory
        fn = os.path.normpath(os.path.join(self.modpath, filename))
        if not os.path.exists(fn):
            fn = os.path.join(Preferences.pyPath, filename)
            if not os.path.exists(fn):
                fn = os.path.abspath(filename)
                if not os.path.exists(fn):
                    return ''
        return fn

    def clearStepPos(self):
        if self.lastStepView is not None:
            self.lastStepView.clearStepPos(self.lastStepLineno)
            self.lastStepView = None

    def selectSourceLine(self, filename, lineno):
        self.clearStepPos()
        if filename and filename[:1] != '<' and filename[-1:] != '>':
            filename = self.resolvePath(filename)
            if not filename: return
                
            self.model.editor.SetFocus()
            self.model.editor.openOrGotoModule(filename)
            model = self.model.editor.getActiveModulePage().model
            sourceView = model.views['Source']
            sourceView.focus(false)
            sourceView.SetFocus()
            sourceView.selectLine(lineno - 1)
            sourceView.setStepPos(lineno - 1)
            self.lastStepView = sourceView
            self.lastStepLineno = lineno - 1

    def isRunning(self):
        return self.running

    def ensureRunning(self):
        if not self.running:
            self.runProcess()

    def setContinue(self):
        if not self.running:
            self.runProcess()
        self.debug_conn.set_continue()
        self.queryDebuggerStatus()

    def OnDebug(self, event):
        if not self.running:
            self.runProcess()
        else:
            self.debug_conn.set_continue()
            self.queryDebuggerStatus()
            # self.stopMainLoop()

    def OnStep(self, event):
        if not self.running:
            self.runProcess()
        else:
            self.debug_conn.set_step()
            self.queryDebuggerStatus()
            # self.stopMainLoop()

    def OnOver(self, event):
        if not self.running:
            self.runProcess()
        else:
            self.debug_conn.set_step_over()
            self.queryDebuggerStatus()
            # self.stopMainLoop()

    def OnOut(self, event):
        if not self.running:
            self.runProcess()
        else:
            self.debug_conn.set_step_out()
            self.queryDebuggerStatus()
            # self.stopMainLoop()

    def OnStop(self, event):
        #wxPhonyApp.inMainLoop = false
        self.debug_conn.set_quit()
        self.clearStepPos()
        self.stackView.load_stack([])
        # self.stopMainLoop()
        # self.queryDebuggerStatus()
    
    def OnSourceTrace(self, event):
        pass

    def OnCloseWindow(self, event):
        try:
            if self.running:
                self.OnStop(None)
##            self.locs.destroy()
##            self.globs.destroy()
##            self.breakpts.destroy()
##            self.watches.destroy()
            self.model.editor.debugger = None
        finally:
##            self.Destroy()
            self.Show(0)
            event.Skip()
