#----------------------------------------------------------------------------
# Name:         Debugger.py
# Purpose:      wxPython debugger, a port of IDLE's debugger written by Guido
#
# Author:       Riaan Booysen
#
# Created:      2000/01/11
# RCS-ID:       $Id$
# Copyright:    (c) 2000 - 2001
# Licence:      dual GPL & Python
#----------------------------------------------------------------------------

import string, sys, os
from os import path
from repr import Repr
import bdb, traceback, linecache, imp, pprint

from wxPython.wx import *
import wxPython

import Preferences, Utils
from Preferences import pyPath, IS, flatTools
#from PhonyApp import wxPhonyApp

wxID_STACKVIEW = wxNewId()
class StackViewCtrl(wxListCtrl):
    def __init__(self, parent, flist, debugger):
        wxListCtrl.__init__(self, parent, wxID_STACKVIEW, style = wxLC_REPORT | wxLC_SINGLE_SEL )
        self.InsertColumn(0, 'Frame', wxLIST_FORMAT_LEFT, 150)
        self.InsertColumn(1, 'Line', wxLIST_FORMAT_LEFT, 35)
        self.InsertColumn(2, 'Code', wxLIST_FORMAT_LEFT, 300)
        EVT_LIST_ITEM_SELECTED(self, wxID_STACKVIEW, self.OnStackItemSelected)
        EVT_LIST_ITEM_DESELECTED(self, wxID_STACKVIEW, self.OnStackItemDeselected)
        EVT_LEFT_DCLICK(self, self.OnGotoSource)

        self.flist = flist
        self.debugger = debugger
        self.stack = []
        self.selection = -1

    def load_stack(self, stack, index=None):
        self.stack = stack
        self.DeleteAllItems()

        for i in range(len(stack)):
            frame, lineno = stack[i]
            try:
                modname = frame.f_globals['__name__']
            except:
                modname = "?"
            code = frame.f_code
            filename = code.co_filename
            funcname = code.co_name
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

        if 0 <= self.selection < len(self.stack):
            self.debugger.show_frame(self.stack[self.selection])

    def OnStackItemDeselected(self, event):
        self.selection = -1

    def OnGotoSource(self, event):
        if self.selection != -1:
            frame, lineno = self.stack[self.selection]
            try:
                modname = frame.f_globals['__name__']
            except:
                return
#                modname = "?"
            code = frame.f_code
            filename = code.co_filename

            if filename[0] != '<' and filename[-1] != '>':
                filename = self.debugger.resolvePath(filename)
                if not filename: return

                self.debugger.model.editor.SetFocus()
                self.debugger.model.editor.openOrGotoModule(filename)
                model = self.debugger.model.editor.getActiveModulePage().model
                model.views['Source'].focus()
                model.views['Source'].SetFocus()
                model.views['Source'].selectLine(lineno - 1)

def get_stack(t=None, f=None):
    if t is None:
        t = sys.last_traceback
    stack = []
    if t and t.tb_frame is f:
        t = t.tb_next
    while f is not None:
        stack.append((f, f.f_lineno))
        if f is self.botframe:
            break
        f = f.f_back
    stack.reverse()
    while t is not None:
        stack.append((t.tb_frame, t.tb_lineno))
        t = t.tb_next
    return stack


def getexception(type=None, value=None):
    if type is None:
        type = sys.last_type
        value = sys.last_value
    if hasattr(type, "__name__"):
        type = type.__name__
    s = str(type)
    if value is not None:
        s = s + ": " + str(value)
    return s

[wxID_BREAKVIEW, wxID_BREAKSOURCE, wxID_BREAKEDIT, wxID_BREAKDELETE,
  wxID_BREAKENABLED, wxID_BREAKREFRESH] = Utils.wxNewIds(6)

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
        self.brkImgLst.Add(IS.load('Images/Debug/Breakpoint-red.png'))
        self.brkImgLst.Add(IS.load('Images/Debug/Breakpoint-yellow.png'))
        self.brkImgLst.Add(IS.load('Images/Debug/Breakpoint-gray.png'))
        self.brkImgLst.Add(IS.load('Images/Debug/Breakpoint-blue.png'))

        EVT_LIST_ITEM_SELECTED(self, wxID_BREAKVIEW, self.OnBreakpointSelected)
        EVT_LIST_ITEM_DESELECTED(self, wxID_BREAKVIEW, self.OnBreakpointDeselected)
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

        for file, lineno in bdb.Breakpoint.bplist.keys():
            self.debugger.set_internal_breakpoint(file, lineno)

    def destroy(self):
        self.menu.Destroy()

    def bpList(self):
        bpl = []
        for bp in bdb.Breakpoint.bpbynumber:
            if bp: bpl.append(bp)
        return bpl

    def refreshList(self):
        self.selection = -1
        self.DeleteAllItems()
        for bp in self.bpList():
            p = self.GetItemCount()
            imgIdx = 0
            if not bp.enabled:
                imgIdx = 2
            elif bp.temporary: imgIdx = 3

            self.InsertImageStringItem(p, path.basename(bp.file), imgIdx)
            self.SetStringItem(p, 1, `bp.line`)
            if bp.enabled: self.SetStringItem(p, 3, '*')
            self.SetStringItem(p, 2, `bp.ignore`)
            self.SetStringItem(p, 3, `bp.hits`)
            try: self.SetStringItem(p, 4, bp.condition)
            except: pass

    def addBreakpoint(self, filename, lineno):
        self.refreshList()

    def OnBreakpointSelected(self, event):
        self.selection = event.m_itemIndex

    def OnBreakpointDeselected(self, event):
        self.selection = -1

    def OnGotoSource(self, event):
        if self.selection != -1:
            bp = self.bpList()[self.selection]

            filename = self.debugger.resolvePath(bp.file)
            if not filename: return

            self.debugger.model.editor.SetFocus()
            self.debugger.model.editor.openOrGotoModule(filename)
            model = self.debugger.model.editor.getActiveModulePage().model
            model.views['Source'].focus()
            model.views['Source'].SetFocus()
            model.views['Source'].selectLine(bp.line - 1)

    def OnEdit(self, event):
        pass

    def OnDelete(self, event):
        if self.selection != -1:
            bp = self.bpList()[self.selection]
            self.debugger.clear_break(bp.file, bp.line)

            self.refreshList()

    def OnRefresh(self, event):
        self.refreshList()

    def OnToggleEnabled(self, event):
        if self.selection != -1:
            bp = self.bpList()[self.selection]
            bp.enabled = not bp.enabled
            self.refreshList()

    def OnRightDown(self, event):
        self.x = event.GetX()
        self.y = event.GetY()

    def OnRightClick(self, event):
        if self.selection != -1:
            self.menu.Check(wxID_BREAKENABLED,
              self.bpList()[self.selection].enabled)
            self.PopupMenu(self.menu, wxPoint(self.x, self.y))


# XXX Expose classes' dicts as indented items
wxID_NSVIEW = wxNewId()
class NamespaceViewCtrl(wxListCtrl):
    def __init__(self, parent, add_watch, is_local, name, dict=None):
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

        idAs = wxNewId()
        idA = wxNewId()
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

        self.load_dict(dict)

    def destroy(self):
        self.menu.Destroy()

    dict = -1

    def load_dict(self, dict, force=0):
        if dict is self.dict and not force:
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
                value = dict[name]
                svalue = self.repr.repr(value) # repr(value)

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

wxID_WATCHVIEW = wxNewId()
class WatchViewCtrl(wxListCtrl):

    def __init__(self, parent, images, debugger):
        wxListCtrl.__init__(self, parent, wxID_WATCHVIEW,
          style = wxLC_REPORT)# | wxLC_SINGLE_SEL )
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

        EVT_LEFT_DCLICK(self, self.OnDoubleClick)
        self.menu = wxMenu()

        id = wxNewId()
        self.menu.Append(id, 'Add')
        EVT_MENU(self, id, self.OnAdd)
        id = wxNewId()
        self.menu.Append(id, 'Edit')
        EVT_MENU(self, id, self.OnEdit)
        id = wxNewId()
        self.menu.Append(id, 'Delete')
        EVT_MENU(self, id, self.OnDelete)
        id = wxNewId()
        self.menu.Append(id, 'Expand')
        EVT_MENU(self, id, self.OnExpand)
        self.menu.AppendSeparator()
        self.localId = wxNewId()
        self.menu.Append(self.localId, 'Local', checkable = true)
        EVT_MENU(self, self.localId, self.OnEvalLocal)
        self.globalId = wxNewId()
        self.menu.Append(self.globalId, 'Global', checkable = true)
        EVT_MENU(self, self.globalId, self.OnEvalGlobal)

        self.x = self.y = 0

    def destroy(self):
        self.menu.Destroy()

    def getSelection(self):
        res = []
        for idx in range(self.GetItemCount()):
            item = self.GetItem(idx)
            if item.GetState() & wxLIST_STATE_SELECTED:
                res.append(idx)
        return res

    dict = -1

    def add_watch(self, name, local):
        if name:
            self.watches.append([name, local])
        else:
            dlg = wxTextEntryDialog(self, 'Enter name:', 'Add a watch:', '')
            try:
                if dlg.ShowModal() == wxID_OK:
                    self.watches.append([dlg.GetValue(), local])
            finally:
                dlg.Destroy()

    def load_dict(self, localsDict, globalsDict, force=0):
        self.DeleteAllItems()
        row = 0
        for name, local in self.watches:
            if local:
                try:
                    value = self.repr.repr(localsDict[name])
                except:
                    try:
                        value = eval(name, globalsDict, localsDict)
                    except Exception, message:
                        value = '??? (%s)' % message
                idx = 3
            else:
                try:
                    value = self.repr.repr(globalsDict[name])
                except:
                    try:
                        value = eval(name, globalsDict)
                    except Exception, message:
                        value = '??? (%s)' % message
                idx = 4

            svalue = self.repr.repr(value) # repr(value)

            self.InsertImageStringItem(row, name, idx)
            self.SetStringItem(row, 1, svalue, idx)

            row = row + 1

    def OnDelete(self, event):
        if self.selected != -1:
            selItems = self.getSelection()
            selItems.sort()
            selItems.reverse()
            for idx in selItems:
                del self.watches[idx]
                self.DeleteItem(idx)

    def OnExpand(self, event):
        if self.selected != -1:
            name, local = self.watches[self.selected]
            self.debugger.expand_watch(name, local)

    def OnEdit(self, event):
        watch = self.watches[self.selected]
        dlg = wxTextEntryDialog(self, 'Current expression:', 'Edit watch:', watch[0])
        try:
            if dlg.ShowModal() == wxID_OK:
                del self.watches[self.selected]
                self.watches.insert(self.selected, [dlg.GetValue(), watch[1]] )
                self.debugger.show_variables()
        finally:
            dlg.Destroy()

    def OnItemSelect(self, event):
        self.selected = event.m_itemIndex

    def OnItemDeselect(self, event):
        self.selected = -1

    def OnRightDown(self, event):
        self.x = event.GetX()
        self.y = event.GetY()

    def OnRightClick(self, event):
        if self.selected != -1:
            local = self.watches[self.selected][1]
            self.menu.Check(self.localId, local)
            self.menu.Check(self.globalId, not local)

            self.PopupMenu(self.menu, wxPoint(self.x, self.y))

    def OnEvalLocal(self, event):
        if self.selected != -1:
            for idx in self.getSelection():
                self.watches[idx][1] = true
        self.debugger.show_variables()

    def OnEvalGlobal(self, event):
        if self.selected != -1:
            for idx in self.getSelection():
                self.watches[idx][1] = false
        self.debugger.show_variables()

    def OnAdd(self, event):
        self.add_watch('', true)
        self.debugger.show_variables()

    def OnDoubleClick(self, event):
        if self.selected != -1:
            self.OnEdit(event)
        else:
            self.OnAdd(event)

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
        self.error.SetToolTipString(message)

        rect = self.GetFieldRect(1)
        self.error.SetDimensions(rect.x+2, rect.y+2, rect.width-4, rect.height-4)

    def OnSize(self, event):
        rect = self.GetFieldRect(0)
        self.status.SetDimensions(rect.x+2, rect.y+2, rect.width-4, rect.height-4)

        rect = self.GetFieldRect(1)
        self.error.SetDimensions(rect.x+2, rect.y+2, rect.width-4, rect.height-4)

class DebuggerFrame(wxFrame, bdb.Bdb, Utils.FrameRestorerMixin):
    def __init__(self, model, stack = None):
        try:
            self.filename = model.assertLocalFile()
        except AssertionError:
            raise Exception('Can only debug local files.')

        bdb.Bdb.__init__(self)
        wxFrame.__init__(self, model.editor, -1, 'Debugger - %s - %s' \
          % (path.basename(model.filename), model.filename))

        self.winConfOption = 'debugger'
        self.loadDims()

        self.SetIcon(IS.load('Images/Icons/Debug.ico'))

        self.viewsImgLst = wxImageList(16, 16)
        self.viewsImgLst.Add(IS.load('Images/Debug/Stack.png'))
        self.viewsImgLst.Add(IS.load('Images/Debug/Breakpoints.png'))
        self.viewsImgLst.Add(IS.load('Images/Debug/Watches.png'))
        self.viewsImgLst.Add(IS.load('Images/Debug/Locals.png'))
        self.viewsImgLst.Add(IS.load('Images/Debug/Globals.png'))
        self.viewsImgLst.Add(IS.load('Images/Debug/Output.png'))

        self.interacting = 0
#        self.app = app
        self.model = model
        self.app = self.model.editor.app
        self.sb = DebugStatusBar(self)
        self.SetStatusBar(self.sb)

        self.toolbar = wxToolBar(self, -1, style = wxTB_HORIZONTAL|wxNO_BORDER|flatTools)
        self.SetToolBar(self.toolbar)

        self.runId = Utils.AddToolButtonBmpIS(self, self.toolbar,
          'Images/Debug/Debug.png', 'Debug', self.OnDebug)
        self.stepId = Utils.AddToolButtonBmpIS(self, self.toolbar,
          'Images/Debug/Step.png', 'Step', self.OnStep)
        self.overId = Utils.AddToolButtonBmpIS(self, self.toolbar,
          'Images/Debug/Over.png', 'Over', self.OnOver)
        self.outId = Utils.AddToolButtonBmpIS(self, self.toolbar,
          'Images/Debug/Out.png', 'Out', self.OnOut)
        self.stopId = Utils.AddToolButtonBmpIS(self, self.toolbar,
          'Images/Debug/Stop.png',  'Stop', self.OnStop)
        self.toolbar.AddSeparator()
        self.sourceTraceId = Utils.AddToolButtonBmpIS(self, self.toolbar,
          'Images/Debug/SourceTrace-Off.png',  'Trace in source',
          self.OnSourceTrace, '1')
        self.debugBrowseId = Utils.AddToolButtonBmpIS(self, self.toolbar,
          'Images/Debug/DebugBrowse.png',  'Debug browsing',
          self.OnDebugBrowse, '1')
        self.shellNamespaceId = Utils.AddToolButtonBmpIS(self, self.toolbar,
          'Images/Debug/ShellDebug.png',  'Eval in shell',
          self.OnDebugNamespace, '1')

        self.toolbar.Realize()

        self.toolbar.ToggleTool(self.sourceTraceId, true)
        self.toolbar.ToggleTool(self.debugBrowseId, true)

        self.splitter = wxSplitterWindow(self, -1, style = wxSP_NOBORDER| wxSP_3DSASH | wxSP_FULLSASH)

        # Create a Notebook
        self.nbTop = wxNotebook(self.splitter, -1)
        if wxPlatform == '__WXMSW__':
            self.nbTop.SetImageList(self.viewsImgLst)

        self.stackView = StackViewCtrl(self.nbTop, None, self)
        if stack is None:
            try:
                stack = get_stack()
                self.stackView.load_stack(stack)
            except:
                pass
        else:
            self.stackView.load_stack(stack)

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
##        self.outp.SetBackgroundColour(wxBLACK)
##        self.outp.SetForegroundColour(wxWHITE)
        if wxPlatform == '__WXMSW__':
            self.outp.SetFont(wxFont(7, wxDEFAULT, wxNORMAL, wxNORMAL, false))
            self.nbTop.AddPage(self.outp, 'Output', imageId = 5)
        elif wxPlatform == '__WXGTK__':
            self.outp.SetFont(wxFont(9, wxDEFAULT, wxNORMAL, wxNORMAL, false))
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

        self.locs = NamespaceViewCtrl(self.nbBottom, self.add_watch, 1, 'local')
        if wxPlatform == '__WXMSW__':
            self.nbBottom.AddPage(self.locs, 'Locals', imageId = 3)
        elif wxPlatform == '__WXGTK__':
            self.nbBottom.AddPage(self.locs, 'Locals')

        self.globs = NamespaceViewCtrl(self.nbBottom, self.add_watch, 0, 'global')

        if wxPlatform == '__WXMSW__':
            self.nbBottom.AddPage(self.globs, 'Globals', imageId = 4)
        elif wxPlatform == '__WXGTK__':
            self.nbBottom.AddPage(self.globs, 'Globals')

        self.splitter.SetMinimumPaneSize(40)
        #self.splitter.SplitVertically(self.nbTop, self.nbBottom, 200)
        self.splitter.SplitHorizontally(self.nbTop, self.nbBottom)
        self.splitter.SetSashPosition(200)


        self.mlc = 0
        self.frame = None

        EVT_CLOSE(self, self.OnCloseWindow)

    def setDefaultDimensions(self):
        self.SetDimensions(0, Preferences.paletteHeight + \
              Preferences.windowManagerTop + Preferences.windowManagerBottom,
              Preferences.inspWidth, Preferences.bottomHeight)

    def add_watch(self, name, local):
        self.watches.add_watch(name, local)
        self.nbBottom.SetSelection(0)
        self.show_variables()

    def expand_watch(self, name, local):
        inst_items = dir(eval(name, self.frame.f_globals, self.frame.f_locals))
        clss_items = dir(eval(name, self.frame.f_globals,
          self.frame.f_locals).__class__)
        for item in inst_items + clss_items:
            self.watches.add_watch('%s.%s' %(name, item), local)
        self.nbBottom.SetSelection(0)
        self.show_variables()

    def show_variables(self, force=0):
        frame = self.frame
        if not frame:
            ldict = gdict = None
        else:
            ldict = frame.f_locals
            gdict = frame.f_globals
            if self.locs and self.globs and ldict is gdict:
                ldict = None
        if self.locs:
            self.locs.load_dict(ldict, force)
        if self.globs:
            self.globs.load_dict(gdict, force)

        self.watches.load_dict(ldict, gdict, force)

    def show_frame(self, (frame, lineno)):
        self.frame = frame
        self.show_variables()

    def getVarValue(self, name):
        if self.frame:
            try:
                return pprint.pformat(eval(name, self.frame.f_globals, self.frame.f_locals))
            except Exception, message:
                return pprint.pformat(str(message))
        else:
            return '(No current frame)'

    def startMainLoop(self):
        self.app.MainLoop()
        self.mlc = self.mlc + 1

    def stopMainLoop(self):
        self.app.ExitMainLoop()
        self.mlc = self.mlc - 1

#---------------------------------------------------------------------------

##    def trace_dispatch(self, frame, event, arg):
##        print event, arg
##        return bdb.Bdb.trace_dispatch(self, frame, event, arg)

    def canonic(self, filename):
        # Canonicalize filename -- called by Bdb
        return os.path.normcase(os.path.abspath(filename))

    def do_clear(self, arg):
        self.clear_bpbynumber(arg)

    def debug_file(self, filename, params = None):
        filename = path.join(pyPath, filename)
        saveout = sys.stdout
        saveerr = sys.stderr
        if params is None: params = []

        owin = self.outp
        editor = self.model.editor
        tmpApp = wxPython.wx.wxApp
        tmpSimpleApp = wxPython.wx.wxPySimpleApp
        tmpArgs = sys.argv[:]
        wxPython.wx.wxApp.debugger = self
##        wxPhonyApp.debugger = self
##        wxPython.wx.wxApp = wxPhonyApp
##        wxPython.wx.wxPySimpleApp = wxPhonyApp

        self.modpath = os.path.dirname(filename)
        sys.argv = [filename] + params
        tmpPaths = sys.path[:]
        sys.path.insert(0, self.modpath)
        sys.path.append(Preferences.pyPath)
        sysMods = sys.modules.keys()
        cwd = path.abspath(os.getcwd())
        os.chdir(path.dirname(filename))
        try:
            sys.stderr = PseudoFileErrTC(owin)
            try:
                sys.stdout = PseudoFileOutTC(owin)
                try:
                    editor.app.saveStdio = sys.stdout, sys.stderr

                    modname, ext = os.path.splitext(os.path.basename(filename))
                    if sys.modules.has_key(modname):
                        mod = sys.modules[modname]
                    else:
                        mod = imp.new_module(modname)
                        sys.modules[modname] = mod

                    try:
                        mod.__file__ = filename
                    except AttributeError:
                        print "I'm frozen!"

                    self.run("execfile(%s)" % `filename`, mod.__dict__)
                except:
                    (sys.last_type, sys.last_value,
                     sys.last_traceback) = sys.exc_info()
                    linecache.checkcache()
                    traceback.print_exc()
            finally:
                pass
                sys.stdout = saveout
        finally:
            sys.stderr = saveerr
            editor.app.saveStdio = sys.stdout, sys.stderr
            del wxPython.wx.wxApp.debugger
##            wxPython.wx.wxApp = tmpApp
##            wxPython.wx.wxPySimpleApp = tmpSimpleApp
            sys.path = tmpPaths
            sys.argv = tmpArgs
            os.chdir(cwd)

##            for mod in sys.modules.keys():
##                if mod in sysMods:
##                    sysMods.remove(mod)
##            if len(sysMods):
##                wxLogMessage('sys.modules changed '+string.join(sysMods, ', '))

##            if len(sysMods) and wxMessageBox('The following modules were introduced during '
##                'Debug:\n'+string.join(sysMods, ', '), 'Delete from sys.modules',
##                wxYES_NO) == wxYES:
##                if mod in sysMods:
##                    del sys.modules[mod]

##            else:
##                wxLogMessage('sys.modules not changed')

    def set_breakpoint_here(self, filename, lineno, tmp):
        #wxLogMessage('SetBreak %s %d'%(filename, lineno))
        self.nbTop.SetSelection(1)
        filename = self.canonic(filename)
        brpt = self.set_break(filename, lineno, tmp)
        self.breakpts.refreshList()
        return brpt

    def set_internal_breakpoint(self, filename, lineno, temporary=0, cond = None):
        if not self.breaks.has_key(filename):
            self.breaks[filename] = []
        list = self.breaks[filename]
        if not lineno in list:
            list.append(lineno)
    # A literal copy of Bdb.set_break() without the print statement at the end,
    # returning the breakpoint
    def set_break(self, filename, lineno, temporary=0, cond = None):
        import linecache # Import as late as possible
        line = linecache.getline(filename, lineno)
        if not line:
            return 'That line does not exist!'
        self.set_internal_breakpoint(filename, lineno, temporary, cond)
        return bdb.Breakpoint(filename, lineno, temporary, cond)

    def set_continue(self):
        self.stopframe = self.botframe
        self.returnframe = None
        self.quitting = 0
##        if not self.breaks:
##            # no breakpoints; run without debugger overhead
##            sys.settrace(None)
##            try:
##                1 + ''  # raise an exception
##            except:
##                frame = sys.exc_info()[2].tb_frame.f_back
##            while frame and frame is not self.botframe:
##                del frame.f_trace
##                frame = frame.f_back


    def run(self, *args):
#        print args
        try:
            self.sb.status.SetLabel('Running.')
            self.interacting = 1
            return apply(bdb.Bdb.run, (self,) + args)
        finally:
            self.interacting = 0
            self.sb.status.SetLabel('Finished.')

    def user_line(self, frame):
        self.interaction(frame)

    def user_return(self, frame, rv):
        # XXX show rv?
        ##self.interaction(frame)
        pass

    def user_exception(self, frame, info):
        self.interaction(frame, info)

    def interaction(self, frame, info=None):
        self.frame = frame
        code = frame.f_code
        file = code.co_filename
        base = os.path.basename(file)
        lineno = frame.f_lineno

        message = "%s:%s" % (base, lineno)
        if code.co_name != "?":
            message = "%s: %s()" % (message, code.co_name)

        self.sb.status.SetLabel(message)

        if info:
            type, value, tb = info
            try:
                m1 = type.__name__
            except AttributeError:
                m1 = "%s" % str(type)
            if value is not None:
                try:
                    m1 = "%s: %s" % (m1, str(value))
                except:
                    pass
            bg = wxNamedColour('yellow')
        else:
            m1 = ''
            tb = None
            bg = wxNamedColour('white')#self.errorbg

        self.sb.writeError(m1)

        sv = self.stackView
        if sv:
            stack, i = self.get_stack(self.frame, tb)
            sv.load_stack(stack, i)

        if (string.lower(file), lineno) in bdb.Breakpoint.bplist.keys():
            self.sb.error.SetBackgroundColour(wxNamedColour('red'))
            self.sb.error.SetLabel('Breakpoint.')

            rect = self.sb.GetFieldRect(1)
            self.sb.error.SetDimensions(rect.x+2, rect.y+2,
                                        rect.width-4, rect.height-4)

        self.breakpts.refreshList()
        self.selectSourceLine()

        self.sb.status.SetLabel('Paused')

        # process debugger events
        self.startMainLoop()

        self.sb.status.SetLabel('Running')
        self.sb.writeError('')

        self.frame = None

    def resolvePath(self, filename):
        # Try to find file in Main module directory, Boa directory and Current directory
        fn = os.path.normpath(os.path.join(self.modpath, filename))
        if not os.path.exists(fn):
            fn = os.path.join(Preferences.pyPath, filename)
            if not os.path.exists(fn):
                fn = os.path.abspath(filename)
                if not os.path.exists(fn):
                    return ''
        return fn

    def selectSourceLine(self):
        if self.stackView.stack and self.isSourceTracing():
            stack = self.stackView.stack
            frame, lineno = stack[len(stack)-1]
            try:
                modname = frame.f_globals['__name__']
            except:
                return
            code = frame.f_code
            filename = code.co_filename
    #            funcname = code.co_name

            if filename[0] != '<' and filename[-1] != '>':
                filename = self.resolvePath(filename)
                if not filename: return

                self.model.editor.SetFocus()
                self.model.editor.openOrGotoModule(filename)
                model = self.model.editor.getActiveModulePage().model
                model.views['Source'].focus(false)
                model.views['Source'].SetFocus()
                model.views['Source'].selectLine(lineno -1)
                model.views['Source'].setStepPos(lineno -1)

    def enableTools(self, enable = true):
        self.toolbar.EnableTool(self.runId, enable)
        self.toolbar.EnableTool(self.stepId, enable)
        self.toolbar.EnableTool(self.overId, enable)
        self.toolbar.EnableTool(self.outId, enable)
        self.toolbar.EnableTool(self.stopId, enable)

    def isSourceTracing(self):
        return self.toolbar.GetToolState(self.sourceTraceId)

    def isDebugBrowsing(self):
        return self.toolbar.GetToolState(self.debugBrowseId)

    def isInShellNamepace(self):
        return self.toolbar.GetToolState(self.shellNamespaceId)

    def OnDebug(self, event):
        if self.interacting:
            self.set_continue()
        else:
            self.debug_file(self.filename)
        self.show_variables()
        self.stopMainLoop()

    def OnStep(self, event):
        self.set_step()
        self.show_variables()
        self.stopMainLoop()

    def OnOver(self, event):
        self.set_next(self.frame)
        self.show_variables()
        self.stopMainLoop()

    def OnOut(self, event):
        self.set_return(self.frame)
        self.show_variables()
        self.stopMainLoop()

    def OnStop(self, event):
        ##wxPhonyApp.inMainLoop = false
        self.set_quit()
        if hasattr(self.model, 'editor'):
            self.model.editor.clearAllStepPoints()
            self.stackView.load_stack([])
        self.frame = None
        self.show_variables()
        self.stopMainLoop()

    def OnSourceTrace(self, event):
        pass

    def OnDebugBrowse(self, event):
        pass

    def OnCloseWindow(self, event):
        try:
            if self.interacting:
                # XXX mmm
                self.OnStop(None)
            self.app.quit = true
            self.locs.destroy()
            self.globs.destroy()
            self.breakpts.destroy()
            self.watches.destroy()
            if hasattr(self.model, 'editor'):
                self.model.editor.debugger = None
        finally:
            self.Destroy()
            event.Skip()

    def OnDebugNamespace(self, event):
##        try:
        self.model.editor.OnSwitchShell(None)
        self.model.editor.shell.debugShell(self.isInShellNamepace(), self)
##        except Exception, error:
##            wxLogError(str(error))

echo = true
class PseudoFileOutTC(Utils.PseudoFile):
    tags = 'stderr'
    def write(self, s):
        self.output.AppendText(s)
        if echo: sys.__stdout__.write(s)

class PseudoFileErrTC(Utils.PseudoFile):
    tags = 'stdout'
    def write(self, s):
        self.output.AppendText(s)
        if echo: sys.__stderr__.write(s)
