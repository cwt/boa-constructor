import os, time, threading, socket

from wxPython.wx import *
import Preferences, Utils

#-----Toolbar-------------------------------------------------------------------

class MyToolBar(wxToolBar):
    def __init__(self, *_args, **_kwargs):
        wxToolBar.__init__(self, _kwargs['parent'], _kwargs['id'],
          style = wxTB_HORIZONTAL|wxNO_BORDER|Preferences.flatTools)
        self.toolLst = []
        self.toolCount = 0

    def AddTool(self, id, bitmap, toggleBitmap=wxNullBitmap, shortHelpString='', isToggle=false):
        wxToolBar.AddTool(self, id, bitmap, toggleBitmap, isToggle=isToggle,
            shortHelpString=shortHelpString)

        self.toolLst.append(id)
        self.toolCount = self.toolCount + 1

    def AddTool2(self, id, bitmapname, shortHelpString='', toggleBitmap=wxNullBitmap, isToggle=false):
        self.AddTool(id, Preferences.IS.load(bitmapname), toggleBitmap, shortHelpString, isToggle)

    def AddSeparator(self):
        wxToolBar.AddSeparator(self)
        self.toolLst.append(-1)
        self.toolCount = self.toolCount + 1

    def DeleteTool(self, id):
        wxToolBar.DeleteTool(self, id)
        self.toolLst.remove(id)
        self.toolCount = self.toolCount - 1

    def ClearTools(self):
        posLst = range(self.toolCount)
        posLst.reverse()
        for pos in posLst:
            self.DeleteToolByPos(pos)

        self.DisconnectToolIds()

        self.toolLst = []
        self.toolCount = 0

    def GetToolPopupPosition(self, id):
        margins = self.GetToolMargins()
        toolSize = self.GetToolSize()
        xPos = margins.x
        for tId in self.toolLst:
            if tId == id:
                return wxPoint(xPos, margins.y + toolSize.y)

            if tId == -1:
                xPos = xPos + self.GetToolSeparation()
            else:
                xPos = xPos + toolSize.x

        return wxPoint(0, 0)

    def PopupToolMenu(self, toolId, menu):
        self.PopupMenu(menu, self.GetToolPopupPosition(toolId))

    def DisconnectToolIds(self):
        for wid in self.toolLst:
            if wid != -1:
                self.GetParent().Disconnect(wid)

class EditorToolBar(MyToolBar):
    pass


# fields
sbfIcon, sbfBrwsBtns, sbfStatus, sbfCrsInfo, sbfProgress = range(5)

class EditorStatusBar(wxStatusBar):
    """ Displays information about the current view. Also global stats/
        progress bar etc. """
    maxHistorySize = 250
    def __init__(self, *_args, **_kwargs):
        wxStatusBar.__init__(self, _kwargs['parent'], _kwargs['id'], style=wxST_SIZEGRIP)
        self.SetFieldsCount(6)
        if wxPlatform == '__WXGTK__':
            imgWidth = 21
        else:
            imgWidth = 16

        self.SetStatusWidths([imgWidth, 36, 400, 25, 150, -1])

        rect = self.GetFieldRect(sbfIcon)
        self.img = wxStaticBitmap(self, -1,
            Preferences.IS.load('Images/Shared/BoaLogo.png'),
            (rect.x+1, rect.y+1), (16, 16))
        EVT_LEFT_DCLICK(self.img, self.OnShowHistory)

        rect = self.GetFieldRect(sbfBrwsBtns)
        self.historyBtns = wxSpinButton(self, -1, (rect.x+1, rect.y+1),
                                                  (rect.width-2, rect.height-2))
        self.historyBtns.SetToolTipString('Browse the Traceback/Error/Output window history.')
        EVT_SPIN_DOWN(self.historyBtns, self.historyBtns.GetId(), self.OnErrOutHistoryBack)
        EVT_SPIN_UP(self.historyBtns, self.historyBtns.GetId(), self.OnErrOutHistoryFwd)
        self.erroutFrm = None

        self.progress = wxGauge(self, -1, 100)
        self.linkProgressToStatusBar()

        self.images = {'Info': Preferences.IS.load('Images/Shared/Info.png'),
                       'Warning': Preferences.IS.load('Images/Shared/Warning.png'),
                       'Error': Preferences.IS.load('Images/Shared/Error.png')}
        self.history = []
        self._histcnt = 0

    def destroy(self):
        self.images = None

    def setHint(self, hint, msgType='Info', ringBell=false):
        """ Show a status message in the statusbar, optionally rings a bell.

        msgType can be 'Info', 'Warning' or 'Error'
        """
        if not self.images:
            return
        self._histcnt = self._histcnt - 1
        if hint.strip():
            self.history.append( (msgType, time.strftime('%H:%M:%S',
              time.gmtime(time.time())), hint, ringBell) )
        if len(self.history) > self.maxHistorySize:
            del self.history[0]

        self.SetStatusText(hint, sbfStatus)
        self.img.SetToolTipString(hint)
        self.img.SetBitmap(self.images[msgType])
        if ringBell: wxBell()

    def OnEditorNotification(self, event):
        self.setHint(event.message)

    logDlgs = {'Info': wxLogMessage,
               'Warning': wxLogWarning,
               'Error': wxLogError}
    def OnShowHistory(self, event):
        hist = self.history[:]
        hp = HistoryPopup(self.GetParent(), hist, self.images)

    def linkProgressToStatusBar(self):
        rect = self.GetFieldRect(sbfProgress)
        self.progress.SetDimensions(rect.x+1, rect.y+1, rect.width -2, rect.height -2)

    def setColumnPos(self, value):
        self.SetStatusText(str(value), sbfCrsInfo)

    def OnErrOutHistoryBack(self, event):
        if self.erroutFrm:
             self.erroutFrm.stepBackInHistory()

    def OnErrOutHistoryFwd(self, event):
        if self.erroutFrm:
            self.erroutFrm.stepFwdInHistory()


def HistoryPopup(parent, hist, imgs):
    f = wxMiniFrame(parent, -1, 'Editor status history', size = (350, 200))
    lc = wxListCtrl(f, style=wxLC_REPORT | wxLC_VRULES | wxLC_NO_HEADER)
    lc.il = wxImageList(16, 16)
    idxs = {}
    for tpe, img in imgs.items():
        idxs[tpe] = lc.il.Add(img)
    lc.SetImageList(lc.il, wxIMAGE_LIST_SMALL)
    lc.InsertColumn(0, 'Time')
    lc.InsertColumn(1, 'Message')
    lc.SetColumnWidth(0, 75)
    lc.SetColumnWidth(1, 750)
    for tpe, tme, msg, _bell in hist:
        lc.InsertImageStringItem(0, tme, idxs[tpe])
        lc.SetStringItem(0, 1, msg)
    f.Center()
    f.Show()
    wxPostEvent(f, wxSizeEvent(f.GetSize()))
    return f


#-----Model hoster--------------------------------------------------------------


wxID_MODULEPAGEVIEWCHANGE, wxID_MODULEPAGECLOSEVIEW = Utils.wxNewIds(2)

class ModulePage:
    """ Represents a notebook on a page of the top level notebook hosting
        the model instance. """
    def __init__(self, parent, model, defViews, views, idx, editor):
        self.editor = editor
        self.defViews = map(lambda x: (x, wxNewId()), defViews)
        self.adtViews = map(lambda x: (x, wxNewId()), views)
        self.viewIds = []
        self.model = model
        self.parent = parent
        self.notebook = wxNotebook(parent, -1, style = wxWANTS_CHARS | wxCLIP_CHILDREN)
        EVT_NOTEBOOK_PAGE_CHANGED(self.notebook, self.notebook.GetId(), self.OnPageChange)
        self.tIdx = idx
        self.updatePageName()

        self.windowId = wxNewId()
        self.editor.winMenu.Append(self.windowId, self.getMenuLabel(),
              'Switch to highlighted file')
        EVT_MENU(self.editor, self.windowId, self.editor.OnGotoModulePage)
        EVT_MENU(self.notebook, wxID_MODULEPAGECLOSEVIEW, self.OnDirectActionClose)
        EVT_RIGHT_DOWN(self.notebook, self.OnRightDown)

        Class = model.__class__
##        if not editor.defaultAdtViews.has_key(cls):
##            cls = model.__class__.__bases__[0]

        tot = len(defViews) ##+ len(editor.defaultAdtViews.get(Class, []))
        if tot:
            stepsDone = 50.0
            editor.statusBar.progress.SetValue(int(stepsDone))
            step = (100 - stepsDone) / tot
            for View in defViews:
                self.addView(View)
                stepsDone = stepsDone + step
                editor.statusBar.progress.SetValue(int(stepsDone))

##            for View in editor.defaultAdtViews.get(Class, []):
##                self.addView(View)
##                stepsDone = stepsDone + step
##                editor.statusBar.progress.SetValue(int(stepsDone))

        if defViews:
            self.default = defViews[0].viewName
        else:
            self.default = None

        self.viewMenu = self.viewSelectionMenu()

        editor.statusBar.progress.SetValue(0)

    def destroy(self):
        """ Destroy all views, notepad pages and the view notebook."""
        self.disconnectEvts()
        self.editor.Disconnect(self.windowId)

        self.editor.winMenu.Delete(self.windowId)

        self.viewMenu.Destroy()

        for view in self.model.views.values():
            if view:
                view.close()
        self.notebook.DeleteAllPages()

        self.model.destroy()
        self.model = None

        self.notebook.Destroy()

##    def __del__(self):
##        print '__del__', self.__class__.__name__

    def __repr__(self):
        return '<%s: %s, %d>' %(self.__class__.__name__, os.path.basename(self.model.filename), self.tIdx)

    def updatePageName(self):
        """ Return a name that is decorated with () meaning never been saved
            and/or * meaning model modified ~ meaning view modified. """

        pageName = self.model.getPageName()

        if not self.model.savedAs: sa1, sa2 = '(', ')'
        else: sa1 = sa2 = ''

        if len(self.model.viewsModified): vm = '~'
        else: vm = ''

        if self.model.modified: m = '*'
        else: m = ''

        if self.model.transport and self.model.transport.stdAttrs['read-only']:
            ro = ' (read only)'
        else: ro = ''

        self.pageName = '%s%s%s%s%s%s%s%s' % (m, vm, sa1, pageName, ro, sa2, vm, m)

        return self.pageName

### decl getActiveView(self, idx : int) -> EditorView
    def getActiveView(self, idx=None):
        if idx is None: idx = self.notebook.GetSelection()
        if idx == -1: return None
        name = self.notebook.GetPageText(idx)
        if name and name[0] == '~': name = name[1:-1]
        try:
            return self.model.views[name]
        except KeyError:
            return None

### decl viewSelectionMenu(self) -> wxMenu
    def viewSelectionMenu(self):
        menu = wxMenu()
        for View, wId in self.defViews:
            menu.Append(wId, View.viewName)
        menu.AppendSeparator()
        for View, wId in self.adtViews:
            menu.Append(wId, View.viewName, '', View not in self.adtViews)

        return menu

    def connectEvts(self):
        for view, wId in self.defViews:
            EVT_MENU(self.editor, wId, self.editor.OnSwitchedToView)
        for view, wId in self.adtViews:
            EVT_MENU(self.editor, wId, self.editor.OnToggleView)

    def disconnectEvts(self):
        if self.model:
            for view, wId in self.defViews + self.adtViews:
                self.editor.Disconnect(wId)

    def setActiveViewsMenu(self):
        viewClss = map(lambda x: x.__class__, self.model.views.values())
        for view, wId in self.adtViews:
            self.viewMenu.Check(wId, view in viewClss)

    def addView(self, View, viewName=''):
        """ Add a view to the model and display it as a page in the notebook
            of view instances."""
        if not viewName: viewName = View.viewName
        if wxPlatform == '__WXGTK__':
            panel, view = Utils.wxProxyPanel(self.notebook, View, self.model)
            self.model.views[viewName] = view
            if View.docked:
                self.model.views[viewName].addToNotebook(self.notebook, viewName,
                        panel=panel)
        else:
            view = View(self.notebook, self.model)
            self.model.views[viewName] = view
            if View.docked:
                self.model.views[viewName].addToNotebook(self.notebook, viewName)

        return self.model.views[viewName]

    def refresh(self):
        pass
        # self.notebook.Refresh()

    def focus(self):
        """ Make this model page the currently selected page. """
        self.parent.SetSelection(self.tIdx)

    def removedPage(self, idx):
        """ Called on all ModulePages after a sibling ModulePage deletion.
            Decrements tIdx if bigger than idx. """
        if idx < self.tIdx:
            self.tIdx = self.tIdx - 1

    def addedPage(self, idx):
        if idx <= self.tIdx:
            self.tIdx = self.tIdx + 1

    def saveAs(self, filename):
        newFilename, success = self.editor.saveAsDlg(filename)
        if success:
            self.model.saveAs(newFilename)
            self.editor.updateModulePage(self.model, filename)
            self.editor.updateTitle()
        return success

    def saveOrSaveAs(self, forceSaveAs=false):
        model = self.model
        editor = self.editor
        if forceSaveAs or not model.savedAs:
            oldName = model.filename
            if self.saveAs(oldName) and (oldName != model.filename):
                self.rename(oldName, model.filename)

                editor.statusBar.setHint('%s saved.'%\
                      os.path.basename(model.filename))
        else:
            from Explorers.ExplorerNodes import TransportModifiedSaveError
            try:
                model.save()
            except TransportModifiedSaveError, err:
                choice = wxMessageBox(str(err)+'\nDo you want to overwrite these '
                  'changes (Yes), reload your file (No) or cancel this operation '
                  '(Cancel)?', 'Overwrite newer file warning',
                  wxYES_NO | wxCANCEL | wxICON_WARNING)
                if choice == wxYES:
                    model.save(overwriteNewer=true)
                elif choice == wxNO:
                    raise TransportModifiedSaveError('Reload')
                elif choice == wxCANCEL:
                    raise TransportModifiedSaveError('Cancel')

            editor.updateModulePage(model)
            editor.updateTitle()

            editor.statusBar.setHint('%s saved.'%\
                  os.path.basename(model.filename))

    def OnPageChange(self, event):
        viewIdx = event.GetSelection()
        if event.GetOldSelection() != viewIdx or wxPlatform == '__WXGTK__':
            self.editor.setupToolBar(viewIdx=viewIdx)
            view = self.getActiveView(viewIdx)
            if hasattr(view, 'OnPageActivated'):
                view.OnPageActivated(event)
        event.Skip()

    def OnRightDown(self, event):
        actView = self.getActiveView()

        doDirectMenuPopup = false
        for View, wid in self.adtViews:
            if isinstance(actView, View):
                doDirectMenuPopup = true
                break

        if not doDirectMenuPopup:
            from Views.EditorViews import CloseableViewMix
            if isinstance(actView, CloseableViewMix):
                doDirectMenuPopup = true

        if doDirectMenuPopup:
            directMenu = wxMenu()
            directMenu.Append(wxID_MODULEPAGECLOSEVIEW, 'Close active view')

            self.notebook.PopupMenu(directMenu, event.GetPosition())
            directMenu.Destroy()
            return

    def OnDirectActionClose(self, event):
        actView = self.getActiveView()

        for View, wid in self.adtViews:
            if isinstance(actView, View):
                actView.deleteFromNotebook(self.default, actView.viewName)

                self.editor.mainMenu.Check(wid, false)
                return

        from Views.EditorViews import CloseableViewMix
        if isinstance(actView, CloseableViewMix):
            actView.OnClose(None)

    def rename(self, oldName, newName):
        del self.editor.modules[oldName]
        self.editor.modules[newName] = self

        item = self.editor.winMenu.FindItemById(self.windowId)
        item.SetText(self.getMenuLabel())
        self.editor.editorUpdateNotify()

    def getMenuLabel(self):
        return '%s (%s)'%(os.path.basename(self.model.filename),
                          self.model.filename)


socketPort = 50007
selectTimeout = 0.25
class Listener(threading.Thread):
    def __init__(self, editor, closed):
        #self.queue = queue
        self.editor = editor
        self.closed = closed
        threading.Thread.__init__(self)

    def run(self, host='127.0.0.1', port=socketPort):
        import socket
        from select import select
        # Open a socket and listen.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((host, port))
        except socket.error, err:
            self.closed.set()
            return

        s.listen(5)
        while 1:
            while 1:
                # Listen for 0.25 s, then check if closed is set. In that case,
                # end thread by returning.
                ready, dummy, dummy = select([s],[],[], selectTimeout)
                if self.closed.isSet():
                    return
                if ready:
                    break

            # Accept a connection, read the data and put it into the queue.
            conn, addr = s.accept()
            l = []
            while 1:
                data = conn.recv(1024)
                if not data: break
                l.append(data)
            name = ''.join(l)
            if name.strip():
                Utils.wxCallAfter(self.editor.openOrGotoModule, name)
            conn.close()


def socketFileOpenServerListen(editor):
    closed = threading.Event()
    return closed, Listener(editor, closed).start()


if __name__ == '__main__':
    app = wxPySimpleApp()
    frame = HistoryPopup(None, (), {})
    app.MainLoop()
