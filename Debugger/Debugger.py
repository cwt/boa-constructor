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
#import threading
#from Queue import Queue

from IsolatedDebugger import DebuggerConnection, DebuggerController

# Specific to in-process debugging:
debugger_controller = DebuggerController()


wxEVT_DEBUGGER_OK = NewId()
wxEVT_DEBUGGER_EXC = NewId()

def EVT_DEBUGGER_OK(win, id, func):
    win.Connect(id, -1, wxEVT_DEBUGGER_OK, func)

def EVT_DEBUGGER_EXC(win, id, func):
    win.Connect(id, -1, wxEVT_DEBUGGER_EXC, func)

class DebuggerCommEvent(wxPyCommandEvent):
    receiver_name = None
    receiver_args = ()
    result = None
    t = None
    v = None

    def __init__(self, evtType, id):
        wxPyCommandEvent.__init__(self, evtType, id)

    def SetResult(self, result):
        self.result = result

    def GetResult(self):
        return self.result

    def SetReceiverName(self, name):
        self.receiver_name = name

    def GetReceiverName(self):
        return self.receiver_name

    def SetReceiverArgs(self, args):
        self.receiver_args = args

    def GetReceiverArgs(self):
        return self.receiver_args

    def SetExc(self, t, v):
        self.t, self.v = t, v

    def GetExc(self):
        return self.t, self.v
    

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
        data = []

        pos = 0
        count = self.GetItemCount()
        for entry in stack:
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
            if pos == index:
                item = "> " + item
            if pos >= count:
                # Insert.
                self.InsertStringItem(pos, attrib)
                count = count + 1
            else:
                # Update.
                self.SetStringItem(pos, 0, attrib, -1)
            self.SetStringItem(pos, 1, `lineno`, -1)
            self.SetStringItem(pos, 2, sourceline, -1)
            pos = pos + 1

        while pos < count:
            self.DeleteItem(count - 1)
            count = count - 1
        self.selection = -1

    def OnStackItemSelected(self, event):
        self.selection = event.m_itemIndex

        stacklen = len(self.stack)
        if 0 <= self.selection < stacklen:
            self.debugger.invalidatePanes()
            self.debugger.updateSelectedPane()
        
    def OnStackItemDeselected(self, event):
        self.selection = -1

    def selectCurrentEntry(self):
        newsel = self.GetItemCount() - 1
        if newsel != self.selection:
            if self.selection >= 0:
                item = self.GetItem(self.selection)
                item.m_state = item.m_state & ~wxLIST_STATE_SELECTED
                self.SetItem(item)
            if newsel >= 0:
                item = self.GetItem(newsel)
                item.m_state = item.m_state | wxLIST_STATE_SELECTED
                self.SetItem(item)
            self.selection = newsel
        if newsel >= 0:
            self.EnsureVisible(newsel)
            
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

##        EVT_LIST_ITEM_SELECTED(self, wxID_BREAKVIEW,
##                               self.OnBreakpointSelected)
##        EVT_LIST_ITEM_DESELECTED(self, wxID_BREAKVIEW,
##                                 self.OnBreakpointDeselected)
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
        self.pos = None

        self.SetImageList(self.brkImgLst, wxIMAGE_LIST_SMALL)

        self.rightsel = -1
        self.debugger = debugger
        self.bps = []
        self.stats = {}

        #for file, lineno in bdb.Breakpoint.bplist.keys():
        #    self.debugger.set_internal_breakpoint(file, lineno)

    def destroy(self):
        self.menu.Destroy()
            
    def refreshList(self):
        self.rightsel = -1
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

            hits = ''
            ignore = ''
            if self.stats:
                for sbp in self.stats:
                    if (bp['filename'] == sbp['filename'] and
                        bp['lineno'] == sbp['lineno']):
                        hits = str(sbp['hits'])
                        ignore = str(sbp['ignore'])
                        break
            self.SetStringItem(p, 2, ignore)
            self.SetStringItem(p, 3, hits)
            self.SetStringItem(p, 4, bp['cond'] or '')
    
    def addBreakpoint(self, filename, lineno):
        self.refreshList()

##    def OnBreakpointSelected(self, event):
##        self.selection = event.m_itemIndex
        
##    def OnBreakpointDeselected(self, event):
##        self.selection = -1
    
    def OnGotoSource(self, event):
        sel = self.rightsel
        if sel != -1:
            bp = self.bps[sel]

            filename = self.debugger.resolvePath(bp['filename'])
            if not filename: return

            editor = self.debugger.model.editor
            editor.SetFocus()
            editor.openOrGotoModule(filename)
            model = editor.getActiveModulePage().model
            model.views['Source'].focus()
            model.views['Source'].SetFocus()
            model.views['Source'].selectLine(bp['lineno'] - 1)

    def OnEdit(self, event):
        pass

    def OnDelete(self, event):
        sel = self.rightsel
        if sel != -1:
            bp = self.bps[sel]
            bplist.deleteBreakpoints(bp['filename'], bp['lineno'])
            self.debugger.invokeInDebugger(
                'clear_breaks', (bp['filename'], bp['lineno']))
            # TODO: Unmark the breakpoint in the editor.
            self.refreshList()

    def OnRefresh(self, event):
        self.refreshList()

    def OnToggleEnabled(self, event):
        sel = self.rightsel
        if sel != -1:
            bp = self.bps[sel]
            filename = bp['filename']
            lineno = bp['lineno']
            enabled = not bp['enabled']
            bplist.enableBreakpoints(filename, lineno, enabled)
            self.debugger.invokeInDebugger(
                'enableBreakpoints', (filename, lineno, enabled))
            self.refreshList()
         
    def OnRightDown(self, event):
        self.pos = event.GetPosition()

    def OnRightClick(self, event):
        if not self.pos:
            return
        sel = self.HitTest(self.pos)[0]
        if sel != -1:
            self.rightsel = sel
            bp = self.bps[sel]
            self.menu.Check(wxID_BREAKENABLED, bp['enabled'])
            self.PopupMenu(self.menu, self.pos)


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
        self.pos = None
 
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
        if self.rightsel != -1:
            name = self.names[self.rightsel]
            self.add_watch(name, self.is_local)

    def OnAddAWatch(self, event):
        self.add_watch('', self.is_local)

    def OnItemSelect(self, event):
        self.selected = event.m_itemIndex

    def OnItemDeselect(self, event):
        self.selected = -1

    def OnRightDown(self, event):
        self.pos = event.GetPosition()

    def OnRightClick(self, event):
        if not self.pos:
            return
        sel = self.HitTest(self.pos)[0]
        if sel != -1:
            self.rightsel = sel
            self.PopupMenu(self.menu, self.pos)

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

##        EVT_LIST_ITEM_SELECTED(self, -1, self.OnItemSelect)
##        EVT_LIST_ITEM_DESELECTED(self, -1, self.OnItemDeselect)
        self.rightsel = -1

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
        id = NewId()
        self.menu.Append(id, 'Delete All')
        EVT_MENU(self, id, self.OnDeleteAll)
        self.pos = None
    
    def destroy(self):
        self.menu.Destroy()

    dict = -1
    
    def add_watch(self, name, local, pos=-1):
        if name:
            if pos < 0 or pos >= len(self.watches):
                self.watches.append((name, local))
            else:
                self.watches.insert(pos, (name, local))
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
        sel = self.rightsel
        if sel != -1:
            del self.watches[sel]
            self.DeleteItem(sel)

    def OnDeleteAll(self, event):
        del self.watches[:]
        self.DeleteAllItems()

    def OnExpand(self, event):
        sel = self.rightsel
        if sel != -1:
            name, local = self.watches[sel]
            self.debugger.requestWatchSubobjects(name, local, sel + 1)

##    def OnItemSelect(self, event):
##        self.selected = event.m_itemIndex

##    def OnItemDeselect(self, event):
##        self.selected = -1

    def OnRightDown(self, event):
        self.pos = event.GetPosition()

    def OnRightClick(self, event):
        if not self.pos:
            return
        sel = self.HitTest(self.pos)[0]
        if sel != -1:
            self.rightsel = sel
            self.PopupMenu(self.menu, self.pos)

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

    def writeError(self, message, is_error=1):
        if message and is_error:
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


wxID_PAGECHANGED = NewId()
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
        self.invalidatePanes()

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
        self.nbBottom = wxNotebook(self.splitter, wxID_PAGECHANGED)
        EVT_NOTEBOOK_PAGE_CHANGED(self.nbBottom, wxID_PAGECHANGED,
                                  self.OnPageChange)

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

##        self._command_queue = Queue()
##        self._client_thread_running = 0
        EVT_DEBUGGER_OK(self, self.GetId(), self.OnDebuggerOk)
        EVT_DEBUGGER_EXC(self, self.GetId(), self.OnDebuggerException)
        
	EVT_CLOSE(self, self.OnCloseWindow)

    def add_watch(self, name, local):
        self.watches.add_watch(name, local)
        self.nbBottom.SetSelection(0)
        self.invalidatePanes()
        self.updateSelectedPane()

    def OnPageChange(self, event):
        sel = event.GetSelection()
        if sel >= 0: # and sel != self.nbBottomPageNo:
            # self.nbBottomPageNo = sel
            self.updateSelectedPane(sel)
        event.Skip()
        
    def invalidatePanes(self):
        self.updated_panes = [0, 0, 0]
        # TODO: We may also want to clear the panes here
        # to show to the user that the data is not loaded yet.

    def updateSelectedPane(self, pageno=-1):
        if pageno < 0:
            pageno = self.nbBottom.GetSelection()
        if not self.updated_panes[pageno]:
            frameno = self.stackView.selection
            if pageno == 0:
                self.requestWatches(frameno)
            else:
                self.requestDict((pageno==1), frameno)

    def requestWatches(self, frameno):
        ws = self.watches.watches
        exprs = []
        for name, local in ws:
            exprs.append({'name':name, 'local':local})
        if exprs:
            self.invokeInDebugger(
                'evaluateWatches', (exprs, frameno), 'receiveWatches')
        else:
            # No exprs, so no request is necessary.
            self.watches.load_dict(None)
            self.updated_panes[0] = 1

    def receiveWatches(self, status):
        frameno = status['frameno']
        if frameno == self.stackView.selection:
            self.updated_panes[0] = 1
            self.watches.load_dict(status['watches'])
        else:
            # Re-request.
            self.updateSelectedPane()

    def requestDict(self, locs, frameno):
        self.invokeInDebugger(
            'getSafeDict', (locs, frameno), 'receiveDict')

    def receiveDict(self, status):
        frameno = status['frameno']
        if frameno == self.stackView.selection:
            if status.has_key('locals'):
                self.updated_panes[1] = 1
                self.locs.load_dict(status['locals'])
            if status.has_key('globals'):
                self.updated_panes[2] = 1
                self.globs.load_dict(status['globals'])
        else:
            # Re-request.
            self.updateSelectedPane()

    def requestWatchSubobjects(self, name, local, pos):
        self.invokeInDebugger(
            'getWatchSubobjects', (name, self.stackView.selection),
            'receiveWatchSubobjects', (name, local, pos))

    def receiveWatchSubobjects(self, subnames, name, local, pos):
        for subname in subnames:
            self.watches.add_watch('%s.%s' % (name, subname), local, pos)
            pos = pos + 1
        self.nbBottom.SetSelection(0)
        self.invalidatePanes()
        self.updateSelectedPane()

    def requestVarValue(self, name):
        self.invokeInDebugger(
            'pprintVarValue', (name, self.stackView.selection),
            'receiveVarValue')

    def receiveVarValue(self, val):
        if val:
            self.model.editor.statusBar.setHint(val)

##    def getVarValue(self, name):
##        return self.debug_conn.pprintVarValue(
##            name, frameno=self.stackView.selection)

    #def startMainLoop(self):
    #    self.model.editor.app.MainLoop()
    #    self.mlc = self.mlc + 1
        
    #def stopMainLoop(self):
    #    self.model.editor.app.ExitMainLoop()
    #    self.mlc = self.mlc - 1
    
#---------------------------------------------------------------------------

##    def canonic(self, filename):
##        # Canonicalize filename.
##        return os.path.normcase(os.path.abspath(filename))

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

##    def clientThread(self):
##        try:
##            while 1:
##                m_name, args = self._command_queue.get()
##                if m_name:
##                    try:
##                        m = getattr(self.debug_conn, m_name)
##                        status = apply(m, args)
##                    except:
##                        t, v = sys.exc_info()[:2]
##                        evt = DebuggerCommEvent(wxEVT_DEBUGGER_EXC,
##                                                self.GetId())
##                        evt.SetExc(t, v)
##                    else:
##                        evt = DebuggerCommEvent(wxEVT_DEBUGGER_OK,
##                                                self.GetId())
##                        evt.SetStatus(status)
##                    self.GetEventHandler().AddPendingEvent(evt)
##                if not self._client_thread_running:
##                    break
##        finally:
##            self._client_thread_running = 0

    def invokeInDebugger(self, m_name, m_args=(), r_name=None, r_args=()):
        '''
        Invokes a method asynchronously in the debugger,
        possibly expecting a debugger event to be generated
        when finished.
        '''
        evt = None
        try:
            m = getattr(self.debug_conn, m_name)
            result = apply(m, m_args)
        except:
            t, v = sys.exc_info()[:2]
            evt = DebuggerCommEvent(wxEVT_DEBUGGER_EXC,
                                    self.GetId())
            evt.SetExc(t, v)
        else:
            if r_name:
                evt = DebuggerCommEvent(wxEVT_DEBUGGER_OK,
                                        self.GetId())
                evt.SetReceiverName(r_name)
                evt.SetReceiverArgs(r_args)
                evt.SetResult(result)
        if evt:
            self.GetEventHandler().AddPendingEvent(evt)

##        q = self._command_queue
##        q.put((m_name, args))
##        if not getattr(self, '_client_thread_running', 0):
##            self._client_thread_running = 1
##            t = threading.Thread(target=self.clientThread)
##            t.setDaemon(1)
##            t.start()

##    def stopClientThread(self):
##        self._client_thread_running = 0
##        while not self._command_queue.empty():
##            self._command_queue.get_nowait()
##        self._command_queue.put((None, None))

    def OnDebuggerOk(self, event):
        receiver_name = event.GetReceiverName()
        if receiver_name is not None:
            rcv = getattr(self, receiver_name)
            apply(rcv, (event.GetResult(),) + event.GetReceiverArgs())

    def OnDebuggerException(self, event):
        t, v = event.GetExc()
        if (wxMessageDialog(
            self, '%s: %s.  Stop debugger?' % (t, v),
            'Debugger Communication Exception',
            wxYES_NO | wxYES_DEFAULT | wxICON_EXCLAMATION |
            wxCENTRE).ShowModal() == wxID_YES):
            self.disconnect()

    def runProcess(self):
        self.running = 1
        self.sb.writeError('Running...', 0)
        self.invokeInDebugger(
            'runFileAndRequestStatus',
            (self.filename, self.params or [], bplist.getBreakpointList()),
            'receiveDebuggerStatus')

##        self.debug_conn.setAllBreakpoints(bplist.getBreakpointList())
##        self.debug_conn.runFile(self.filename, self.params or [])
##        self.queryDebuggerStatus()

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

    def proceedAndRequestStatus(self, command):
        # - Ignores the command if we are waiting for status?
        # - Non-blocking.
        self.sb.writeError('Running...', 0)
        self.invokeInDebugger('proceedAndRequestStatus', (command,),
                              'receiveDebuggerStatus')

    def deleteBreakpoints(self, filename, lineno):
        self.invokeInDebugger('clear_breaks', (filename, lineno))
        self.breakpts.refreshList()

    def setBreakpoint(self, filename, lineno, tmp):
        self.invokeInDebugger('set_break', (filename, lineno, tmp))
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

    def receiveDebuggerStatus(self, info):
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
            sv.selectCurrentEntry()

        if bplist.hasBreakpoint(filename, lineno):
            bplist.clearTemporaryBreakpoints(filename, lineno)
            self.sb.error.SetBackgroundColour(wxNamedColour('red'))
            self.sb.error.SetLabel('Breakpoint.')
            rect = self.sb.GetFieldRect(1)
            self.sb.error.SetDimensions(rect.x+2, rect.y+2, 
                                        rect.width-4, rect.height-4)
            # TODO: Unmark temporary breakpoints in the editor.
            
        self.breakpts.stats = info['breaks']
        self.breakpts.refreshList()
        self.selectSourceLine(filename, lineno)

        # All info in watches, locals, or globals is now invalid.
        self.invalidatePanes()
        # Update the currently selected pane.
        self.updateSelectedPane()

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
                
            #self.model.editor.SetFocus()
            self.model.editor.openOrGotoModule(filename)
            model = self.model.editor.getActiveModulePage().model
            sourceView = model.views['Source']
            #sourceView.focus(false)
            #sourceView.SetFocus()
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
        self.proceedAndRequestStatus('set_continue')

    def OnDebug(self, event):
        if not self.running:
            self.runProcess()
        else:
            self.proceedAndRequestStatus('set_continue')
            # self.stopMainLoop()

    def OnStep(self, event):
        if not self.running:
            self.runProcess()
        else:
            self.proceedAndRequestStatus('set_step')
            # self.stopMainLoop()

    def OnOver(self, event):
        if not self.running:
            self.runProcess()
        else:
            self.proceedAndRequestStatus('set_step_over')
            # self.stopMainLoop()

    def OnOut(self, event):
        if not self.running:
            self.runProcess()
        else:
            self.proceedAndRequestStatus('set_step_out')
            # self.stopMainLoop()

    def disconnect(self):
        self.clearStepPos()
        self.stackView.load_stack([])
##        self.stopClientThread()

    def OnStop(self, event):
        #wxPhonyApp.inMainLoop = false
        self.invokeInDebugger('set_quit')
        self.disconnect()
        # self.stopMainLoop()
        # self.queryDebuggerStatus()
    
    def OnSourceTrace(self, event):
        pass

    def OnCloseWindow(self, event):
        try:
            if self.running:
                self.OnStop(event)
##            self.locs.destroy()
##            self.globs.destroy()
##            self.breakpts.destroy()
##            self.watches.destroy()
            self.model.editor.debugger = None
        finally:
##            self.Destroy()
            self.Show(0)
            event.Skip()
