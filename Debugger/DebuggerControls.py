import os, pprint
from repr import Repr

from wxPython.wx import *
from wxPython.lib.stattext import wxGenStaticText

import Preferences, Utils
from Preferences import IS

from Breakpoint import bplist

SEL_STATE = wxLIST_STATE_SELECTED | wxLIST_STATE_FOCUSED

class DebuggerListCtrl(wxListCtrl, Utils.ListCtrlSelectionManagerMix):
    def __init__(self, parent, wId):
        wxListCtrl.__init__(self, parent, wId,
              style=wxLC_REPORT|wxLC_SINGLE_SEL|wxLC_VRULES|wxCLIP_CHILDREN)
        Utils.ListCtrlSelectionManagerMix.__init__(self)

wxID_STACKVIEW = wxNewId()
class StackViewCtrl(DebuggerListCtrl):
    def __init__(self, parent, flist, debugger):
        DebuggerListCtrl.__init__(self, parent, wxID_STACKVIEW)

        self.InsertColumn(0, 'Frame', wxLIST_FORMAT_LEFT, 150)
        self.InsertColumn(1, 'Line', wxLIST_FORMAT_LEFT, 35)
        self.InsertColumn(2, 'Code', wxLIST_FORMAT_LEFT, 300)

        EVT_LIST_ITEM_SELECTED(self, wxID_STACKVIEW, self.OnStackItemSelected)
        EVT_LEFT_DCLICK(self, self.OnGotoSource)

        self.flist = flist
        self.debugger = debugger
        self.stack = []

    def load_stack(self, stack, index=None):
        import linecache

        self.stack = stack
        data = []

        pos = 0
        count = self.GetItemCount()
        for entry in stack:
            lineno = entry['lineno']
            modname = entry['modname']
            filename = entry['client_filename']
            funcname = entry['funcname']
            sourceline = linecache.getline(filename, lineno)
            sourceline = sourceline.strip()
            if funcname in ("?", "", None):
                #item = "%s, line %d: %s" % (modname, lineno, sourceline)
                attrib = modname
            else:
                #item = "%s.%s(), line %d: %s" % (modname, funcname,
                #                                 lineno, sourceline)
                # XXX methods will be shown as "module.function"
                # when maybe they ought to be shown as "module.class.method".
                attrib = modname + '.' + funcname
            #if pos == index:
            #    item = "> " + item
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

    def OnStackItemSelected(self, event):
        selection = self.getSelection()
        stacklen = len(self.stack)
        if 0 <= selection < stacklen:
            self.debugger.invalidatePanes()
            self.debugger.updateSelectedPane()

    def selectCurrentEntry(self):
        selection = self.getSelection()
        newsel = self.GetItemCount() - 1
        if newsel != selection:
            if selection >= 0:
                item = self.GetItem(selection)
                item.m_state = item.m_state & ~wxLIST_STATE_SELECTED
                self.SetItem(item)
            if newsel >= 0:
                item = self.GetItem(newsel)
                item.m_state = item.m_state | wxLIST_STATE_SELECTED
                self.SetItem(item)
        if newsel >= 0:
            self.EnsureVisible(newsel)

    def OnGotoSource(self, event):
        selection = self.getSelection()
        if selection != -1:
            entry = self.stack[selection]
            lineno = entry['lineno']
            modname = entry['modname']
            filename = entry['client_filename']
            if not filename:
                return

            editor = self.debugger.editor
            editor.SetFocus()
            editor.openOrGotoModule(filename)
            model = editor.getActiveModulePage().model
            view = model.getSourceView()
            if view is not None:
                view.focus()
                view.SetFocus()
                view.selectLine(lineno - 1)


[wxID_BREAKVIEW, wxID_BREAKSOURCE, wxID_BREAKEDIT, wxID_BREAKDELETE,
 wxID_BREAKENABLED, wxID_BREAKREFRESH, wxID_BREAKIGNORE] = Utils.wxNewIds(7)

class BreakViewCtrl(DebuggerListCtrl):
    def __init__(self, parent, debugger):
        DebuggerListCtrl.__init__(self, parent, wxID_BREAKVIEW)

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

        EVT_LEFT_DCLICK(self, self.OnGotoSource)

        self.debugger = debugger

        self.menu = wxMenu()

        self.menu.Append(wxID_BREAKSOURCE, 'Goto source')
        self.menu.Append(wxID_BREAKREFRESH, 'Refresh')
        self.menu.Append(-1, '-')
        self.menu.Append(wxID_BREAKIGNORE, 'Edit ignore count')
        self.menu.Append(wxID_BREAKEDIT, 'Edit condition')
        self.menu.Append(wxID_BREAKDELETE, 'Delete')
        self.menu.Append(-1, '-')
        self.menu.Append(wxID_BREAKENABLED, 'Enabled', '', true)

        self.menu.Check(wxID_BREAKENABLED, true)

        EVT_MENU(self, wxID_BREAKSOURCE, self.OnGotoSourceRight)
        EVT_MENU(self, wxID_BREAKREFRESH, self.OnRefresh)
        EVT_MENU(self, wxID_BREAKIGNORE, self.OnEditIgnore)
        EVT_MENU(self, wxID_BREAKEDIT, self.OnEditCondition)
        EVT_MENU(self, wxID_BREAKDELETE, self.OnDelete)
        EVT_MENU(self, wxID_BREAKENABLED, self.OnToggleEnabled)
        self.pos = None

        self.setPopupMenu(self.menu)

        self.AssignImageList(self.brkImgLst, wxIMAGE_LIST_SMALL)

        self.bps = []
        self.stats_map = {}

    def destroy(self):
        self.menu.Destroy()
        self.brkImgLst = None

    def updateBreakpointStats(self, stats):
        """Received from debugger.

        stats is a list of mappings."""
        stats_map = {}
        for item in stats:
            fn = item['client_filename']
            lineno = item['lineno']
            stats_map[(fn, lineno)] = item
            if not bplist.hasBreakpoint(fn, lineno):
                # A hard breakpoint was hit and a new breakpoint was created.
                bplist.addBreakpoint(fn, lineno)
        self.stats_map = stats_map

    def refreshList(self):
        self.DeleteAllItems()
        bps = bplist.getBreakpointList()
        # Sort by filename and lineno.
        bps.sort(lambda a, b:
                 cmp((a['filename'], a['lineno']),
                     (b['filename'], b['lineno'])))
        self.bps = bps
        for p in range(len(bps)):
            bp = bps[p]
            # setup prelim image
            imgIdx = 0
            if not bp['enabled']: imgIdx = 2
            elif bp['temporary']: imgIdx = 3

            self.InsertImageStringItem(
                p, os.path.basename(bp['filename']), imgIdx)
            self.SetStringItem(p, 1, str(bp['lineno']))

            hits = ''
            ignore = ''
            cond = ''
            if self.stats_map:
                item = self.stats_map.get((bp['filename'], bp['lineno']), None)
                if item is not None:
                    hits = str(item['hits'])
                    ignore = str(item['ignore'])
                    cond = item['cond'] or ''

            self.SetStringItem(p, 2, ignore)
            self.SetStringItem(p, 3, hits)
            self.SetStringItem(p, 4, cond)

    def addBreakpoint(self, filename, lineno):
        self.refreshList()

    def selectBreakpoint(self, filename, lineno):
        idx = 0
        for bp in self.bps:
            if bp['filename']==filename and bp['lineno']==lineno:
                self.SetItemState(idx, SEL_STATE, SEL_STATE)
                self.EnsureVisible(idx)
                return
            idx = idx + 1

    def OnGotoSource(self, event):
        sel = self.getSelection()
        if sel != -1:
            self.gotoSourceForItem(sel)

    def OnGotoSourceRight(self, event):
        sel = self.getSelection()
        if sel != -1:
            self.gotoSourceForItem(sel)

    def gotoSourceForItem(self, sel):
        bp = self.bps[sel]
        filename = bp['filename']
        if not filename:
            return
        editor = self.debugger.editor
        editor.SetFocus()
        model, ctrlr = editor.openOrGotoModule(filename)
        view = model.getSourceView()
        if view is not None:
            view.focus()
            view.GotoLine(bp['lineno'] - 1)

    def OnDelete(self, event):
        sel = self.getSelection()
        if sel != -1:
            bp = self.bps[sel]
            filename = bp['filename']
            bplist.deleteBreakpoints(filename, bp['lineno'])

            # Delete in debug server
            server_fn = self.debugger.clientFNToServerFN(filename)
            self.debugger.invokeInDebugger(
                'clearBreakpoints', (server_fn, bp['lineno']))

            # Unmark the breakpoint in the editor (if open)
            sourceView = self.debugger.getEditorSourceView(filename)
            if sourceView:
                sourceView.deleteBreakMarkers(bp['lineno'])

            #self.debugger.requestDebuggerStatus()
            self.refreshList()

    def OnRefresh(self, event):
        self.refreshList()

    def OnToggleEnabled(self, event):
        sel = self.getSelection()
        if sel != -1:
            bp = self.bps[sel]
            filename = bp['filename']
            lineno = bp['lineno']
            enabled = bp['enabled'] = not bp['enabled']
            bplist.enableBreakpoints(filename, lineno, enabled)
            server_fn = self.debugger.clientFNToServerFN(filename)
            self.debugger.invokeInDebugger(
                'enableBreakpoints', (server_fn, lineno, enabled))
            self.refreshList()

            sourceView = self.debugger.getEditorSourceView(filename)
            if sourceView:
                sourceView.deleteBreakMarkers(bp['lineno'])
                sourceView.setBreakMarker(bp)

    def getPopupMenu(self):
        wxYield()
        sel = self.getSelection()

        self.menu.Enable(wxID_BREAKSOURCE, sel != -1)
        self.menu.Enable(wxID_BREAKIGNORE, sel != -1)
        self.menu.Enable(wxID_BREAKEDIT, sel != -1)
        self.menu.Enable(wxID_BREAKDELETE, sel != -1)
        self.menu.Enable(wxID_BREAKENABLED, sel != -1)

        if sel != -1:
            bp = self.bps[sel]
            self.menu.Check(wxID_BREAKENABLED, bp['enabled'])

        return DebuggerListCtrl.getPopupMenu(self)

    def OnEditCondition(self, event):
        sel = self.getSelection()
        if sel != -1:
            bp = self.bps[sel]
            filename = bp['filename']
            lineno = bp['lineno']
            cond = bp['cond']

            dlg = wxTextEntryDialog(self, 'Condition to break on:',
                  'Change condition', cond)
            try:
                if dlg.ShowModal() == wxID_OK:
                    cond = dlg.GetValue().strip()

                    bplist.conditionalBreakpoints(filename, lineno, cond)
                    # Update debug server
                    server_fn = self.debugger.clientFNToServerFN(filename)
                    self.debugger.invokeInDebugger(
                        'conditionalBreakpoints', (server_fn, lineno, cond))

                    self.debugger.requestDebuggerStatus()
                    #self.refreshList()
            finally:
                dlg.Destroy()

    def OnEditIgnore(self, event):
        sel = self.getSelection()
        if sel != -1:
            bp = self.bps[sel]
            filename = bp['filename']
            lineno = bp['lineno']
            ignore = bp['ignore']

            dlg = wxTextEntryDialog(self, 'Number of hits to ignore:',
                  'Change ignore count', `ignore`)
            try:
                if dlg.ShowModal() == wxID_OK:
                    ignore = int(dlg.GetValue())
                    # Update debugger list and debug server
                    bplist.ignoreBreakpoints(filename, lineno, ignore)
                    server_fn = self.debugger.clientFNToServerFN(filename)
                    self.debugger.invokeInDebugger(
                        'ignoreBreakpoints', (server_fn, lineno, ignore))

                    self.debugger.requestDebuggerStatus()
                    #self.refreshList()
            finally:
                dlg.Destroy()

# XXX Expose classes' dicts as indented items

wxID_NSVIEW = wxNewId()
class NamespaceViewCtrl(DebuggerListCtrl):
    def __init__(self, parent, debugger, is_local, name):
        DebuggerListCtrl.__init__(self, parent, wxID_NSVIEW)

        self.InsertColumn(0, 'Attribute', wxLIST_FORMAT_LEFT, 125)
        self.InsertColumn(1, 'Value', wxLIST_FORMAT_LEFT, 200)

        self.is_local = is_local

        self.menu = wxMenu()

        idAs = wxNewId()
        idA = wxNewId()
        self.menu.Append(idAs, 'Add as watch')
        self.menu.Append(idA, 'Add a %s watch' % name)
        EVT_MENU(self, idAs, self.OnAddAsWatch)
        EVT_MENU(self, idA, self.OnAddAWatch)
        outputId = wxNewId()
        self.menu.Append(outputId, 'Write value to Output')
        EVT_MENU(self, outputId, self.OnValueToOutput)

        EVT_LEFT_DCLICK(self, self.OnDoubleClick)

        self.pos = None

        self.setPopupMenu(self.menu)

        self.repr = Repr()
        self.repr.maxstring = 100
        self.repr.maxother = 100
        self.names = []

        self.debugger = debugger

    def destroy(self):
        self.menu.Destroy()

    def showLoading(self):
        self.DeleteAllItems()
        self.InsertStringItem(0, '...')

    def load_dict(self, nsdict, force=0):
        self.DeleteAllItems()

        if not nsdict:
            pass
        else:
            self.names = nsdict.keys()
            self.names.sort()
            row = 0
            for name in self.names:
                svalue = nsdict[name]

                self.InsertStringItem(row, name)
                self.SetStringItem(row, 1, svalue, -1)

                row = row + 1

    def OnAddAsWatch(self, event):
        selected = self.getSelection()
        if selected != -1:
            name = self.names[selected]
            self.debugger.add_watch(name, self.is_local)

    def OnAddAWatch(self, event):
        self.debugger.add_watch('', self.is_local)

    def OnValueToOutput(self, event):
        selected = self.getSelection()
        if selected != -1:
            name = self.names[selected]
            self.debugger.valueToOutput(name)

    def OnDoubleClick(self, event):
        if event.ControlDown():
            self.OnValueToOutput(event)
        else:
            self.OnAddAsWatch(event)


wxID_WATCHVIEW = wxNewId()
class WatchViewCtrl(DebuggerListCtrl):
    def __init__(self, parent, images, debugger):
        DebuggerListCtrl.__init__(self, parent, wxID_WATCHVIEW)

        self.InsertColumn(0, 'Attribute', wxLIST_FORMAT_LEFT, 125)
        self.InsertColumn(1, 'Value', wxLIST_FORMAT_LEFT, 200)

        self.repr = Repr()
        self.repr.maxstring = 60
        self.repr.maxother = 60
        self.debugger = debugger

        self.watches = []

        self.AssignImageList(images, wxIMAGE_LIST_SMALL)

        self.menu = wxMenu()

        wid = wxNewId()
        self.menu.Append(wid, 'Add local watch')
        EVT_MENU(self, wid, self.OnAddLocal)
        wid = wxNewId()
        self.menu.Append(wid, 'Add global watch')
        EVT_MENU(self, wid, self.OnAddGlobal)
        self.editId = wxNewId()
        self.menu.Append(self.editId, 'Edit watch')
        EVT_MENU(self, self.editId, self.OnEdit)
        self.outputId = wxNewId()
        self.menu.Append(self.outputId, 'Write value to Output')
        EVT_MENU(self, self.outputId, self.OnValueToOutput)
        self.deleteId = wxNewId()
        self.menu.Append(self.deleteId, 'Delete')
        EVT_MENU(self, self.deleteId, self.OnDelete)
        self.expandId = wxNewId()
        self.menu.Append(self.expandId, 'Expand')
        EVT_MENU(self, self.expandId, self.OnExpand)
        wid = wxNewId()
        self.menu.Append(wid, 'Delete All')
        EVT_MENU(self, wid, self.OnDeleteAll)

        EVT_LEFT_DCLICK(self, self.OnDoubleClick)

        self.pos = None

        self.setPopupMenu(self.menu)

    def destroy(self):
        self.menu.Destroy()

    def add_watch(self, name, local, pos=-1):
        if name:
            if pos < 0 or pos >= len(self.watches):
                self.watches.append((name, local))
                pos = len(self.watches)-1
            else:
                self.watches.insert(pos, (name, local))
        else:
            dlg = wxTextEntryDialog(
                self, 'Expression:', 'Add a watch:', '')
            try:
                if dlg.ShowModal() == wxID_OK:
                    self.watches.append((dlg.GetValue(), local))
                    pos = len(self.watches)-1
            finally:
                dlg.Destroy()
        #self.SetItemState(pos, SEL_STATE, SEL_STATE)
        #self.EnsureVisible(pos)

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

    def OnAddLocal(self, event):
        self.add_watch('', true)
        self.debugger.updateSelectedPane(force=1)

    def OnAddGlobal(self, event):
        self.add_watch('', false)
        self.debugger.updateSelectedPane(force=1)

    def OnEdit(self, event):
        selected = self.getSelection()

        if selected != -1:
            name, local = self.watches[selected]
            dlg = wxTextEntryDialog(
                self, 'Expression:', 'Edit watch:', name)
            try:
                if dlg.ShowModal() == wxID_OK:
                    self.watches[selected] = (dlg.GetValue(), local)
                    self.debugger.updateSelectedPane(force=1)
            finally:
                dlg.Destroy()

    def OnDelete(self, event):
        selected = self.getSelection()
        if selected != -1:
            del self.watches[selected]
            self.DeleteItem(selected)
            self.debugger.updateSelectedPane(force=1)

    def OnDeleteAll(self, event):
        del self.watches[:]
        self.DeleteAllItems()

    def OnExpand(self, event):
        selected = self.getSelection()
        if selected != -1:
            name, local = self.watches[selected]
            self.debugger.requestWatchSubobjects(name, local, selected + 1)

    def getPopupMenu(self):
        sel = self.getSelection()

        self.menu.Enable(self.editId, sel != -1)
        self.menu.Enable(self.deleteId, sel != -1)
        self.menu.Enable(self.expandId, sel != -1)

        return DebuggerListCtrl.getPopupMenu(self)

    def OnValueToOutput(self, event):
        selected = self.getSelection()

        if selected != -1:
            name = self.watches[selected][0]
            self.debugger.valueToOutput(name)

    def OnDoubleClick(self, event):
        if event.ControlDown():
            self.OnValueToOutput(event)
        else:
            self.OnEdit(event)


class DebugStatusBar(wxStatusBar):
    def __init__(self, parent):
        wxStatusBar.__init__(self, parent, -1, style=0)
        self.SetFieldsCount(2)
        self.SetMinHeight(30)
        #self.SetStatusWidths([-1, -1, 16])

        self.stateCols = {'except': wxColour(0xFF, 0xFF, 0x44),#wxNamedColour('yellow'),
                          'info':   wxNamedColour('white'),
                          'break':  wxColour(0xFF, 0x44, 0x44),#wxNamedColour('red'),
                          'busy':   wxColour(0xBB, 0xE0, 0xFF)}

        self.instr_ptr = wxGenStaticText(self, -1, ' ',
              style=wxALIGN_CENTER|wxST_NO_AUTORESIZE)
        self.instr_ptr.SetBackgroundColour(wxColour(0xEE, 0xEE, 0xEE))
        self._setCtrlDims(self.instr_ptr, self.GetFieldRect(0))

        self.state = wxGenStaticText(self, -1, 'Ready.',
              style=wxALIGN_CENTER|wxST_NO_AUTORESIZE)
        self.state.SetBackgroundColour(self.stateCols['info'])
        self._setCtrlDims(self.state, self.GetFieldRect(1))

        dc = wxClientDC(self)
        dc.SetFont(self.GetFont())
        (w,h) = dc.GetTextExtent('X')
        h = int(h * 1.8)
        self.SetSize(wxSize(100, h))

        EVT_SIZE(self, self.OnSize)

    def _setCtrlDims(self, ctrl, rect):
        ctrl.SetDimensions(rect.x+2, rect.y+2, rect.width-4, rect.height-4)

    def updateState(self, message, sts_type='except'):
        if message:
            self.state.SetBackgroundColour(self.stateCols[sts_type])
        else:
            self.state.SetBackgroundColour(self.stateCols['info'])
        self.state.SetLabel(message)
        self.state.SetToolTipString(message)

        self._setCtrlDims(self.state, self.GetFieldRect(1))

    def updateInstructionPtr(self, status):
        self.instr_ptr.SetLabel(status)
        self._setCtrlDims(self.instr_ptr, self.GetFieldRect(0))

    def OnSize(self, event):
        self._setCtrlDims(self.instr_ptr, self.GetFieldRect(0))
        self._setCtrlDims(self.state, self.GetFieldRect(1))
