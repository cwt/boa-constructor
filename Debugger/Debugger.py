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
from Breakpoint import bplist
from DebugClient import EVT_DEBUGGER_OK, EVT_DEBUGGER_EXC
#from InProcessClient import InProcessClient
from ChildProcessClient import ChildProcessClient

# When an output window surpasses these limits, it will be trimmed.
TEXTCTRL_MAXLEN = 30000
TEXTCTRL_GOODLEN = 20000

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
                'clearBreakpoints', (bp['filename'], bp['lineno']))
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

    def showLoading(self):
        self.DeleteAllItems()
        self.InsertStringItem(0, '...')

    def load_dict(self, dict, force=0):
        #if dict == self.dict and not force:
        #    return

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

    def showLoading(self):
        self.load_dict(None, loading=1)

    def load_dict(self, svalues, force=0, loading=0):
        count = self.GetItemCount()
        row = 0
        for name, local in self.watches:
            if svalues:
                svalue = svalues.get(name, '???')
            elif loading:
                svalue = '...'
            else:
                svalue = '???'
            if local:
                idx = 3
            else:
                idx = 4
            if row >= count:
                # Insert.
                self.InsertImageStringItem(row, name, idx)
                count = count + 1
            else:
                # Update.
                self.SetStringItem(row, 0, name, idx)
            self.SetStringItem(row, 1, svalue, idx)
            row = row + 1
        while row < count:
            self.DeleteItem(count - 1)
            count = count - 1

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


def simplifyPathList(data,
                     SequenceTypes=(type(()), type([])),
                     ExcludeTypes=(type(None),) ):
    # Takes a possibly nested structure and turns it into a flat tuple.
    if type(data) in SequenceTypes:
        newdata = []
        for d in data:
            nd = simplifyPathList(d)
            if nd:
                newdata.extend(nd)
        return newdata
    elif type(data) in ExcludeTypes:
        return ()
    else:
        return list(string.split(str(data), os.pathsep))

def compareColors(c1, c2):
    return (c1.Red() == c2.Red() and
            c1.Green() == c2.Green() and
            c1.Blue() == c2.Blue())


wxID_PAGECHANGED = NewId()
wxID_TOPPAGECHANGED = NewId()
class DebuggerFrame(wxFrame):
    def __init__(self, model, stack = None):
        wxFrame.__init__(
            self, model.editor, -1, 'Debugger - %s - %s'
            % (path.basename(model.filename), model.filename),
            wxPoint(0, Preferences.paletteHeight), 
            wxSize(Preferences.inspWidth, Preferences.bottomHeight))

        self.debug_client = ChildProcessClient(self)
        # self.debug_client = InProcessDebugClient(self)

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
          'Images/Debug/Pause.bmp',  'Pause', self.OnPause)
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
        self.nbTop = wxNotebook(self.splitter, wxID_TOPPAGECHANGED)
        if wxPlatform == '__WXMSW__':
            self.nbTop.SetImageList(self.viewsImgLst)
        EVT_NOTEBOOK_PAGE_CHANGED(self.nbTop, wxID_TOPPAGECHANGED,
                                  self.OnUpperPageChange)
        
        self.stackView = StackViewCtrl(self.nbTop, None, self)

        if wxPlatform == '__WXMSW__':
            self.nbTop.AddPage(self.stackView, 'Stack', imageId = 0)
        elif wxPlatform == '__WXGTK__':
            self.nbTop.AddPage(self.stackView, 'Stack')

        self.breakpts = BreakViewCtrl(self.nbTop, self)
        if wxPlatform == '__WXMSW__':
            self.nbTop.AddPage(self.breakpts, 'Breakpoints', imageId = 1)
        elif wxPlatform == '__WXGTK__':
            self.nbTop.AddPage(self.breakpts, 'Breakpoints')

        self.outp = wxTextCtrl(self.nbTop, -1, '',
                               style = wxTE_MULTILINE | wxTE_READONLY)
        self.outp.SetBackgroundColour(wxBLACK)
        self.outp.SetForegroundColour(wxWHITE)
        if (not compareColors(self.outp.GetBackgroundColour(), wxBLACK) or
            not compareColors(self.outp.GetForegroundColour(), wxWHITE)):
            # The color setting was ignored.  Use standard colors instead.
            self.outp.SetBackgroundColour(wxWHITE)
            self.outp.SetForegroundColour(wxBLACK)
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

        self.stepping_enabled = 1

        EVT_DEBUGGER_OK(self, self.GetId(), self.OnDebuggerOk)
        EVT_DEBUGGER_EXC(self, self.GetId(), self.OnDebuggerException)

        self.stream_timer = wxPyTimer(self.OnStreamTimer)

	EVT_CLOSE(self, self.OnCloseWindow)

    def add_watch(self, name, local):
        self.watches.add_watch(name, local)
        self.nbBottom.SetSelection(0)
        self.invalidatePanes()
        self.updateSelectedPane()

    def OnPageChange(self, event):
        sel = event.GetSelection()
        if sel >= 0:
            self.updateSelectedPane(sel)
        event.Skip()
        
    def invalidatePanes(self):
        self.updated_panes = [0, 0, 0]

    def updateSelectedPane(self, pageno=-1, do_request=1):
        if pageno < 0:
            pageno = self.nbBottom.GetSelection()
        if not self.updated_panes[pageno]:
            frameno = self.stackView.selection
            if pageno == 0:
                self.watches.showLoading()
                if do_request:
                    self.requestWatches(frameno)
            else:
                if pageno==1: self.locs.showLoading()
                else: self.globs.showLoading()
                if do_request:
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
        self.filename = path.join(pyPath, filename)
        self.modpath = os.path.dirname(self.filename)

    def invokeInDebugger(self, m_name, m_args=(), r_name=None, r_args=()):
        '''
        Invokes a method asynchronously in the debugger,
        possibly expecting a debugger event to be generated
        when finished.
        '''
        self.debug_client.invokeOnServer(m_name, m_args, r_name, r_args)

    def killDebugger(self):
        self.debug_client.kill()

    def OnStreamTimer(self, event=None, force_timer=0):
        self.updateOutputWindow()
        if force_timer or self.nbTop.GetSelection() == 2:
            # The user is looking at the output page.
            self.stream_timer.Start(300, 1)  # One-shot mode.

    def appendToOutputWindow(self, t):
        # Before appending to the output, remove old data.
        outp = self.outp
        cursz = outp.GetLastPosition()
        newsz = cursz + len(t)
        if newsz >= TEXTCTRL_MAXLEN:
            #outp.Remove(0, min(newsz - TEXTCTRL_GOODLEN, cursz))
            olddata = outp.GetValue()[newsz - TEXTCTRL_GOODLEN:]
            outp.SetValue(olddata)
        outp.AppendText(t)

    def updateOutputWindow(self):
        while 1:
            stdout_text, stderr_text = self.debug_client.pollStreams()
            if stdout_text:
                self.appendToOutputWindow(stdout_text)
            if stderr_text:
                self.appendToOutputWindow(stderr_text)
            if not stdout_text and not stderr_text:
                break
        
    def OnUpperPageChange(self, event):
        sel = event.GetSelection()
        if sel == 2:
            # Selected the output window.
            self.OnStreamTimer(None, 1)
        event.Skip()
        
    def OnDebuggerOk(self, event):
        self.enableStepping()
        receiver_name = event.GetReceiverName()
        if receiver_name is not None:
            rcv = getattr(self, receiver_name)
            apply(rcv, (event.GetResult(),) + event.GetReceiverArgs())

    def OnDebuggerException(self, event):
        self.enableStepping()
        t, v = event.GetExc()
        if hasattr(t, '__name__'):
            t = t.__name__
        if (wxMessageDialog(
            self, '%s: %s.  Stop debugger?' % (t, v),
            'Debugger Communication Exception',
            wxYES_NO | wxYES_DEFAULT | wxICON_EXCLAMATION |
            wxCENTRE).ShowModal() == wxID_YES):
            # TODO: make sure the debugger doesn't pop up another
            # exception.
            self.killDebugger()
            self.clearViews()

    def runProcess(self, autocont=0):
        self.running = 1
        self.sb.writeError('Running...', 0)
        brks = bplist.getBreakpointList()
        add_paths = simplifyPathList(pyPath)
        filename = path.normcase(path.abspath(self.filename))
        self.invokeInDebugger(
            'runFileAndRequestStatus',
            (filename, self.params or [], autocont, add_paths, brks),
            'receiveDebuggerStatus')

        # InProcessClient TODO: setup the execution environment
        # the way it used to be done.

        #tmpApp = wxPython.wx.wxApp
        #wxPhonyApp.debugger = self
        #wxPython.wx.wxApp = wxPhonyApp

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

    def proceedAndRequestStatus(self, command, temp_breakpoint=None):
        # Non-blocking.
        self.sb.writeError('Running...', 0)
        if not temp_breakpoint:
            temp_breakpoint = 0
        self.invokeInDebugger('proceedAndRequestStatus',
                              (command, temp_breakpoint),
                              'receiveDebuggerStatus')

    def deleteBreakpoints(self, filename, lineno):
        filename = path.normcase(path.abspath(filename))
        self.invokeInDebugger('clearBreakpoints', (filename, lineno))
        self.breakpts.refreshList()

    def setBreakpoint(self, filename, lineno, tmp):
        filename = path.normcase(path.abspath(filename))
        self.invokeInDebugger('addBreakpoint', (filename, lineno, tmp))
        self.breakpts.refreshList()

    def receiveDebuggerStatus(self, info):
        # Get stdout and stderr if available.
        data = info.get('stdout', None)
        if data:
            self.appendToOutputWindow(data)
        data = info.get('stderr', None)
        if data:
            self.appendToOutputWindow(data)

        # Determine the current lineno, filename, and
        # funcname from the stack.
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

        # Show running status.
        if self.running:
            message = "%s:%s" % (base, lineno)
            if funcname != "?":
                message = "%s: %s()" % (message, funcname)
        else:
            message = 'Finished.'
        self.sb.status.SetLabel(message)

        # Show exception information.
        exc_type = info.get('exc_type', None)
        exc_value = info.get('exc_value', None)
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
        
        # Load the stack view.
        sv = self.stackView
        if sv:
            i = info['frame_stack_len']
            sv.load_stack(stack, i)
            sv.selectCurrentEntry()

        # If at a breakpoint, display status.
        if bplist.hasBreakpoint(filename, lineno):
            bplist.clearTemporaryBreakpoints(filename, lineno)
            self.sb.error.SetBackgroundColour(wxNamedColour('red'))
            self.sb.error.SetLabel('Breakpoint.')
            rect = self.sb.GetFieldRect(1)
            self.sb.error.SetDimensions(rect.x+2, rect.y+2, 
                                        rect.width-4, rect.height-4)

        # Update breakpoints view with stats.
        self.breakpts.stats = info['breaks']
        self.breakpts.refreshList()
        self.selectSourceLine(filename, lineno)

        # All info in watches, locals, and globals panes is now invalid.
        self.invalidatePanes()
        # Update the currently selected pane.
        self.updateSelectedPane()
        # Receive stream data even if the user isn't looking.
        self.updateOutputWindow()

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

    def ensureRunning(self, cont_if_running=0, cont_always=0,
                      temp_breakpoint=None):
        if self.isRunning():
            if cont_if_running or cont_always:
                self.doDebugStep('set_continue', temp_breakpoint)
        else:
            # Assume temp. breakpoint is already in bplist.
            self.runProcess(cont_always)

    def enableStepping(self):
        # FUTURE: enable the step buttons.
        self.stepping_enabled = 1

    def disableStepping(self):
        # FUTURE: disable the step buttons.
        self.stepping_enabled = 0

    def doDebugStep(self, method=None, temp_breakpoint=None):
        if self.stepping_enabled:
            self.disableStepping()
            self.clearStepPos()
            self.invalidatePanes()
            self.updateSelectedPane(do_request=0)
            if not self.running:
                self.runProcess()
            elif method:
                self.proceedAndRequestStatus(method, temp_breakpoint)
            return 1
        else:
            if temp_breakpoint:
                self.setBreakpoint(temp_breakpoint[0],
                                   temp_breakpoint[1], 1)
            return 0

    def OnDebug(self, event):
        self.doDebugStep('set_continue')

    def OnStep(self, event):
        self.doDebugStep('set_step')

    def OnOver(self, event):
        self.doDebugStep('set_step_over')

    def OnOut(self, event):
        self.doDebugStep('set_step_out')

    def OnPause(self, event):
        # Only meaningful when running.
        if not self.stepping_enabled:
            self.invokeInDebugger('set_pause')

    def OnStop(self, event):
        self.enableStepping()
        #wxPhonyApp.inMainLoop = false
        self.invalidatePanes()
        self.updateSelectedPane(do_request=0)
        self.proceedAndRequestStatus('set_quit')
    
    def OnSourceTrace(self, event):
        pass

    def clearViews(self):
        self.clearStepPos()
        self.stackView.load_stack([])
        self.watches.load_dict({})
        self.locs.load_dict({})
        self.globs.load_dict({})

    def OnCloseWindow(self, event):
        try:
            self.killDebugger()
            self.clearViews()
##            self.locs.destroy()
##            self.globs.destroy()
##            self.breakpts.destroy()
##            self.watches.destroy()
        finally:
##            self.Destroy()
            self.debug_client = None
            try: self.model.editor.debugger = None
            except: pass
            self.model = None
            self.Show(0)
            event.Skip()
