import os

from wxPython.wx import *
import Preferences

#-----Toolbar-------------------------------------------------------------------

class MyToolBar(wxToolBar):
    def __init__(self, *_args, **_kwargs):
        wxToolBar.__init__(self, _kwargs['parent'], _kwargs['id'],
          style = wxTB_HORIZONTAL|wxNO_BORDER|Preferences.flatTools)
        self.toolLst = []
        self.toolCount = 0

    def AddTool(self, id, bitmap, toggleBitmap = wxNullBitmap, shortHelpString = '', isToggle = false):
        wxToolBar.AddTool(self, id, bitmap, toggleBitmap, isToggle = isToggle,
            shortHelpString = shortHelpString)

        self.toolLst.append(id)
        self.toolCount = self.toolCount + 1

    def AddTool2(self, id, bitmapname, shortHelpString = '', toggleBitmap = wxNullBitmap, isToggle = false):
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

        for wid in self.toolLst:
            if wid != -1:
                self.GetParent().Disconnect(wid),
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

class EditorToolBar(MyToolBar):
    pass

class EditorStatusBar(wxStatusBar):
    """ Displays information about the current view. Also global stats/
        progress bar etc. """
    def __init__(self, *_args, **_kwargs):
        wxStatusBar.__init__(self, _kwargs['parent'], _kwargs['id'], style = wxST_SIZEGRIP)
        self.SetFieldsCount(4)
        if wxPlatform == '__WXGTK__':
            imgWidth = 21
        else:
            imgWidth = 16
            
        self.SetStatusWidths([imgWidth, 400, 150, -1])

        rect = self.GetFieldRect(0)
        self.img = wxStaticBitmap(self, -1, wxNullBitmap, 
            (rect.x+1, rect.y+1), (16, 16))

        rect = self.GetFieldRect(2)
        self.progress = wxGauge(self, -1, 100, rect.GetPosition(), rect.GetSize())
        
        self.images = {'Info': Preferences.IS.load('Images/Shared/Info.bmp'),
                       'Warning': Preferences.IS.load('Images/Shared/Warning.bmp'),
                       'Error': Preferences.IS.load('Images/Shared/Error.bmp')}
        
    def setHint(self, hint, msgType = 'Info'):
        self.SetStatusText(hint, 1)
        self.img.SetToolTipString(hint)
        self.img.SetBitmap(self.images[msgType])

    def OnEditorNotification(self, event):
        self.setHint(event.message)


#-----Model hoster--------------------------------------------------------------

wxID_MODULEPAGEVIEWCHANGE = wxNewId()

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
        self.editor.winMenu.Append(self.windowId, self.model.filename)
        EVT_MENU(self.editor, self.windowId, self.editor.OnGotoModulePage)

        Class = model.__class__
#        if not editor.defaultAdtViews.has_key(cls):
#            cls = model.__class__.__bases__[0]

        tot = len(defViews) + len(editor.defaultAdtViews.get(Class, []))
        if tot:
            stepsDone = 50.0
            editor.statusBar.progress.SetValue(int(stepsDone))
            step = (100 - stepsDone) / tot
            for view in defViews:
                self.addView(view)
                stepsDone = stepsDone + step
                editor.statusBar.progress.SetValue(int(stepsDone))

            for view in editor.defaultAdtViews.get(Class, []):
                self.addView(view)
                stepsDone = stepsDone + step
                editor.statusBar.progress.SetValue(int(stepsDone))

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
        return '<%s: %s, %d>' %(self.__class__.__name__, self.model.defaultName, self.tIdx)

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

        self.pageName = '%s%s%s%s%s%s%s' % (m, vm, sa1, pageName, sa2, vm, m)

        return self.pageName

### decl getActiveView(self, idx : int) -> EditorView
    def getActiveView(self, idx = None):
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
        for view, wId in self.defViews:
            menu.Append(wId, view.viewName)
        menu.AppendSeparator()
        for view, wId in self.adtViews:
            menu.Append(wId, view.viewName, checkable = view not in self.adtViews)

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

    def addView(self, view, viewName = ''):
        """ Add a view to the model and display it as a page in the notebook
            of view instances."""
        if not viewName: viewName = view.viewName
        if wxPlatform == '__WXGTK__':
            panel, self.model.views[viewName] = Utils.wxProxyPanel(self.notebook, view, self.model)
            if view.docked:
                self.model.views[viewName].addToNotebook(self.notebook, viewName,
                        panel=panel)
        else:
            self.model.views[viewName] = apply(view, (self.notebook, self.model))
            if view.docked:
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
                del editor.modules[oldName]
                editor.modules[model.filename] = self

                editor.statusBar.setHint('%s saved.'%\
                      os.path.basename(model.filename))
        else:
            model.save()
            editor.updateModulePage(model)
            editor.updateTitle()

            editor.statusBar.setHint('%s saved.'%\
                  os.path.basename(model.filename))

    def OnPageChange(self, event):
        viewIdx = event.GetSelection()
        if event.GetOldSelection() != viewIdx:
            self.editor.setupToolBar(viewIdx=viewIdx)
            view = self.getActiveView(viewIdx)
            if hasattr(view, 'OnPageActivated'):
                view.OnPageActivated(event)
        event.Skip()
