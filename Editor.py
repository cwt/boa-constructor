#----------------------------------------------------------------------
# Name:        Editor.py
# Purpose:     The main IDE frame containing the Shell, Explorer and
#              opened objects
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2002 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
#Boa:Frame:EditorFrame

""" The main IDE frame containing the Shell, Explorer and the ability to host
Models and their Views on ModulePages"""

# The focus of change
# the center of creation
# Alchemy

print 'importing Editor'

# XXX The Editor should support the following event API
# XXX It is event based to allow threads to access the Editor
# XXX   wxOpenURIEvent
# XXX   wxStatusUpdateEvent
# XXX   wxRunURIEvent (ModRunner.EVT_EXEC_FINISH)
# XXX   wxAddBrowseMarker

# XXX Add a wxPython Class Browser entry to Windows menu

import os, sys, string, pprint
import Queue

from wxPython.wx import *
from wxPython.help import *

from Models import EditorHelper, Controllers

from EditorUtils import EditorToolBar, EditorStatusBar, ModulePage, socketFileOpenServerListen

import Preferences, Utils
from Preferences import keyDefs, IS, flatTools
from Utils import BottomAligningSplitterWindow

import About, Help, Browse

from Explorers import Explorer
from Explorers.ExplorerNodes import TransportSaveError, TransportLoadError
import ShellEditor
from ModRunner import EVT_EXEC_FINISH

addTool = Utils.AddToolButtonBmpIS

(mmFile, mmEdit, mmViews, mmWindows, mmHelp) = range(5)

[wxID_EDITORFRAME, wxID_EDITORFRAMESTATUSBAR, wxID_EDITORFRAMETABS, 
 wxID_EDITORFRAMETABSSPLITTER, wxID_EDITORFRAMETOOLBAR, 
] = map(lambda _init_ctrls: wxNewId(), range(5))

class EditorFrame(wxFrame, Utils.FrameRestorerMixin):
    """ Source code editor and host for the Model/View/Controller classes"""

    openBmp = 'Images/Editor/Open.png'
    backBmp = 'Images/Shared/Previous.png'
    forwBmp = 'Images/Shared/Next.png'
    helpBmp = 'Images/Shared/Help.png'
    ctxHelpBmp = 'Images/Shared/ContextHelp.png'
    shellBmp = 'Images/Editor/Shell.png'
    explBmp = 'Images/Editor/Explorer.png'
    inspBmp = 'Images/Shared/Inspector.png'
    prefsBmp = 'Images/Modules/PrefsFolder_s.png'
    
    _custom_classes = {'wxToolBar': ['EditorToolBar'],
                       'wxStatusBar': ['EditorStatusBar'],
                       'wxSplitterWindow': ['BottomAligningSplitterWindow']}
    def _init_coll_mainMenu_Menus(self, parent):
        # generated method, don't edit

        parent.Append(menu=wxMenu(), title='File')
        parent.Append(menu=wxMenu(), title='Edit')
        parent.Append(menu=wxMenu(), title='Views')

    def _init_utils(self):
        # generated method, don't edit
        self.modelImageList = wxImageList(height=16, width=16)

        self.mainMenu = wxMenuBar()

        self.blankEditMenu = wxMenu(title='')

        self.blankViewMenu = wxMenu(title='')

        self.helpMenu = wxMenu(title='')

        self._init_coll_mainMenu_Menus(self.mainMenu)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxFrame.__init__(self, id=wxID_EDITORFRAME, name='', parent=prnt,
              pos=wxPoint(182, 189), size=wxSize(810, 515),
              style=wxDEFAULT_FRAME_STYLE | Preferences.childFrameStyle,
              title='Editor')
        self._init_utils()
        self.SetMenuBar(self.mainMenu)
        self.SetClientSize(wxSize(802, 488))
        EVT_CLOSE(self, self.OnCloseWindow)

        self.statusBar = EditorStatusBar(id=wxID_EDITORFRAMESTATUSBAR,
              name='statusBar', parent=self, style=0)
        self.SetStatusBar(self.statusBar)

        self.toolBar = EditorToolBar(id=wxID_EDITORFRAMETOOLBAR, name='toolBar',
              parent=self, pos=wxPoint(0, 0), size=wxSize(802, 28),
              style=wxTB_HORIZONTAL | wxNO_BORDER)
        self.SetToolBar(self.toolBar)

        self.tabsSplitter = BottomAligningSplitterWindow(id=wxID_EDITORFRAMETABSSPLITTER,
              name='tabsSplitter', parent=self, point=wxPoint(0, 0),
              size=wxSize(802, 421),
              style=wxCLIP_CHILDREN | wxSP_LIVE_UPDATE | wxSP_3DSASH | wxSP_FULLSASH)

        self.tabs = wxNotebook(id=wxID_EDITORFRAMETABS, name='tabs',
              parent=self.tabsSplitter, pos=wxPoint(2, 2), size=wxSize(798,
              417), style=wxCLIP_CHILDREN)
        EVT_NOTEBOOK_PAGE_CHANGED(self.tabs, wxID_EDITORFRAMETABS,
              self.OnTabsNotebookPageChanged)

    def __init__(self, parent, id, inspector, newMenu, componentPalette, app, palette):
        self._created = false
        self._init_ctrls(parent)

        self.palette = palette
        self.winConfOption = 'editor'
        self.loadDims()

        self.SetBackgroundColour(wxSystemSettings_GetSystemColour(wxSYS_COLOUR_BTNFACE))

        self.SetIcon(IS.load('Images/Icons/Editor.ico'))

        self.app = app
        self.modules = {}
        self.inspector = inspector
        self.compPalette = componentPalette
        self.debugger = None
        self.browser = Browse.HistoryBrowser()
        self.controllers = {}

        self.initImages()

        # Hook for shell and scripts
        if not hasattr(sys, 'boa_ide'):
            sys.boa_ide = self

        # Shell
        self.shell = self.addShellPage()

        # Explorer
        self.explorer = Explorer.ExplorerSplitter(self.tabs,
              self.modelImageList, self)
        self.tabs.AddPage(self.explorer, 'Explorer', imageId=EditorHelper.imgExplorer)
        self.tabs.SetSelection(1)

        # Add open editor models to explorer
        from Explorers import EditorExplorer
        root = self.explorer.tree.boaRoot
        root.entries.insert(0, EditorExplorer.OpenModelsNode(self, root))
        # Connect it's controller
        self.explorer.controllers[EditorExplorer.OpenModelsNode.protocol] = \
              EditorExplorer.EditorController(self, self.explorer.list)

        self.explorer.tree.openDefaultNodes()

        # Menus
        self.newMenu = newMenu
        EVT_MENU(self, EditorHelper.wxID_EDITOROPEN, self.OnOpen)
        EVT_MENU(self, EditorHelper.wxID_EDITOROPENRECENT, self.OnOpenRecent)
        EVT_MENU(self, EditorHelper.wxID_EDITOREXITBOA, self.OnExitBoa)

        # Windows menu
        EVT_MENU(self, EditorHelper.wxID_EDITORSWITCHSHELL, self.OnSwitchShell)
        EVT_MENU(self, EditorHelper.wxID_EDITORSWITCHEXPLORER, self.OnSwitchExplorer)
        EVT_MENU(self, EditorHelper.wxID_EDITORSWITCHPREFS, self.OnSwitchPrefs)
        EVT_MENU(self, EditorHelper.wxID_EDITORSWITCHPALETTE, self.OnSwitchPalette)
        EVT_MENU(self, EditorHelper.wxID_EDITORSWITCHINSPECTOR, self.OnSwitchInspector)
        EVT_MENU(self, EditorHelper.wxID_EDITORBROWSEFWD, self.OnBrowseForward)
        EVT_MENU(self, EditorHelper.wxID_EDITORBROWSEBACK, self.OnBrowseBack)
        EVT_MENU(self, EditorHelper.wxID_EDITORPREVPAGE, self.OnPrevPage)
        EVT_MENU(self, EditorHelper.wxID_EDITORNEXTPAGE, self.OnNextPage)
        EVT_MENU(self, EditorHelper.wxID_EDITORHIDEPALETTE, self.OnHidePalette)
        EVT_MENU(self, EditorHelper.wxID_EDITORWINDIMSLOAD, self.OnWinDimsLoad)
        EVT_MENU(self, EditorHelper.wxID_EDITORWINDIMSSAVE, self.OnWinDimsSave)
        EVT_MENU(self, EditorHelper.wxID_EDITORWINDIMSRESDEFS, self.OnWinDimsRestoreDefs)

        self.winDimsMenu = wxMenu()
        self.winDimsMenu.Append(EditorHelper.wxID_EDITORWINDIMSLOAD, 'Load',
              'Load window dimensions from the config.')
        self.winDimsMenu.Append(EditorHelper.wxID_EDITORWINDIMSSAVE, 'Save',
              'Save window dimensions to the config.')
        self.winDimsMenu.Append(EditorHelper.wxID_EDITORWINDIMSRESDEFS,
              'Restore defaults', 'Restore dimensions to defaults')

        self.winMenu = wxMenu()
        self.winMenu.Append(EditorHelper.wxID_EDITORSWITCHPALETTE, 'Palette',
              'Switch to the Palette frame.')
        Utils.appendMenuItem(self.winMenu, EditorHelper.wxID_EDITORSWITCHINSPECTOR, 
              'Inspector', keyDefs['Inspector'], self.inspBmp, 
              'Switch to the Inspector frame.')
        self.winMenu.Append(-1, '-')
        Utils.appendMenuItem(self.winMenu, EditorHelper.wxID_EDITORSWITCHSHELL,
              'Shell', keyDefs['GotoShell'], self.shellBmp, 
              'Switch to the Shell page')
        Utils.appendMenuItem(self.winMenu, EditorHelper.wxID_EDITORSWITCHEXPLORER,
              'Explorer', keyDefs['GotoExplorer'], self.explBmp, 
              'Switch to the Explorer page')
        Utils.appendMenuItem(self.winMenu, EditorHelper.wxID_EDITORSWITCHPREFS,
              'Preferences', (), self.prefsBmp, 
              'Switch to the Preferences in the Explorer')
        self.winMenu.Append(-1, '-')
        Utils.appendMenuItem(self.winMenu, EditorHelper.wxID_EDITORBROWSEBACK,
              'Browse back', (), self.backBmp, #\t%s'%keyDefs['BrowseBack'][2],
              'Go back in browsing history stack')
        Utils.appendMenuItem(self.winMenu, EditorHelper.wxID_EDITORBROWSEFWD,
              'Browse forward', (), self.forwBmp, #\t%s'%keyDefs['BrowseFwd'][2],
              'Go forward in browsing history stack')
        Utils.appendMenuItem(self.winMenu, EditorHelper.wxID_EDITORPREVPAGE,
              'Previous page', keyDefs['PrevPage'], '-',
              'Switch to the previous page of the main notebook')
        Utils.appendMenuItem(self.winMenu, EditorHelper.wxID_EDITORNEXTPAGE,
              'Next page', keyDefs['NextPage'], '-',
              'Switch to the next page of the main notebook')
        self.winMenu.Append(-1, '-')
        self.winMenu.AppendMenu(EditorHelper.wxID_EDITORWINDIMS,
              'All window dimensions', self.winDimsMenu,
              'Load, save or restore IDE windows dimensions')
        self.winMenu.Append(EditorHelper.wxID_EDITORHIDEPALETTE,
              'Hide Palette', 'Hide the Palette frame')
        self.winMenu.Append(-1, '-')
        self.mainMenu.Append(self.winMenu, 'Windows')

        # Help menu
        Utils.appendMenuItem(self.helpMenu, EditorHelper.wxID_EDITORHELP, 'Help',
              (), self.helpBmp, 'Opens help for the Editor')
        self.helpMenu.Append(EditorHelper.wxID_EDITORHELPGUIDE,
              'Getting started guide', 'Opens the Getting started guide')
        self.helpMenu.AppendSeparator()
        self.helpMenu.Append(EditorHelper.wxID_EDITORHELPFIND,
              'Find in index...\t%s'%keyDefs['HelpFind'][2],
              'Pops up a text input for starting a search of the help indexes')
        self.helpMenu.Append(EditorHelper.wxID_EDITORHELPTIPS, 'Tips',
              'Opens the "Tip of the Day" window')
        self.helpMenu.AppendSeparator()
        self.helpMenu.Append(EditorHelper.wxID_EDITORHELPABOUT, 'About',
              'Opens the About box')

        EVT_MENU(self, EditorHelper.wxID_EDITORHELP, self.OnHelp)
        EVT_MENU(self, EditorHelper.wxID_EDITORHELPABOUT, self.OnHelpAbout)
        EVT_MENU(self, EditorHelper.wxID_EDITORHELPGUIDE, self.OnHelpGuide)
        EVT_MENU(self, EditorHelper.wxID_EDITORHELPTIPS, self.OnHelpTips)
        EVT_MENU(self, EditorHelper.wxID_EDITORHELPFIND, self.OnHelpFindIndex)

        self.mainMenu.Append(self.helpMenu, 'Help')

        if Preferences.suSocketFileOpenServer:
            # Start listening for requests to open files. Listener will run, putting
            # files to open into open_queue, until closed is set.
            self.open_queue, self.closed, self.listener = socketFileOpenServerListen()
        else:
            self.closed = None

        # create initial toolbar buttons and menus
        self._prevMod = None
        self._prevView = None
        self._prevContrl = None
        self._created = true
        self._blockToolbar = false
##        self.defaultAdtViews = {}
        self.setupToolBar(viewIdx = 0)

        dt = Utils.BoaFileDropTarget(self)
        self.SetDropTarget(dt)

        # init (docked) error output frame
        import ErrorStackFrm
        self.erroutFrm = ErrorStackFrm.ErrorStackMF(self, self)

        if Preferences.eoErrOutDockWindow == 'editor':
            self.erroutFrm.notebook1.Reparent(self.tabsSplitter)
            self.tabsSplitter.SplitHorizontally(self.tabs, self.erroutFrm.notebook1,
              self.tabsSplitter.GetClientSize().y - self.tabsSplitter.GetSashSize())
        else:
            if Preferences.eoErrOutDockWindow == 'inspector':
                panel, notebook = \
                  Utils.wxProxyPanel(self.inspector.pages, self.erroutFrm.notebook1)
                self.inspector.pages.AddPage(panel, 'ErrOut')
            self.tabsSplitter.Initialize(self.tabs)
            wxPostEvent(self.tabsSplitter, wxSizeEvent(self.tabsSplitter.GetSize()))
        #self.tabsSplitter.Layout()

        # Hack to feed BoaFileDialog images
        import FileDlg
        FileDlg.wxBoaFileDialog.modImages = self.modelImageList

        EVT_EXEC_FINISH(self, self.OnExecFinish)
        EVT_MENU_HIGHLIGHT_ALL(self, self.OnMenuHighlight)

        from FindReplaceEngine import FindReplaceEngine
        self.finder = FindReplaceEngine()

        # quit server mode flag not guaranteed to be set (yet) even if there is
        # already a server running, but don't connect idle if not necessary
        if self.closed:
            if self.closed.isSet():
                print 'Not running in server mode'
            elif self.closed:
                EVT_IDLE(self, self.pollForOpen)

    def __repr__(self):
        return '<EditorFrame (Boa IDE) instance at %d>'%id(self)

    def setDefaultDimensions(self):
        self.SetDimensions(Preferences.inspWidth + Preferences.windowManagerSide*2,
              Preferences.paletteHeight + Preferences.windowManagerTop + \
              Preferences.windowManagerBottom, Preferences.edWidth,
              Preferences.bottomHeight)
        #if not self.palette.IsShown():
        #    self.Center()

    def releasePrevResources(self):
        self.toolBar.ClearTools()
        if self._prevView:
            self._prevView.disconnectEvts()
            self._prevView = None
        if self._prevMod:
            self._prevMod.disconnectEvts()
            self._prevMod = None
        if self._prevContrl:
            self._prevContrl.disconnectEvts()
            self._prevContrl = None

    def initImages(self):
        # Build imageidx: filename list of all Editor images
        allImages = {}
        for img in EditorHelper.builtinImgs:
            allImages[len(allImages)] = img
        for mod in EditorHelper.modelReg.values():
            allImages[mod.imgIdx] = 'Images/Modules/'+mod.bitmap
        # XXX move ZOAImages/Icons into EditorHelper.extraImages updated from ZopeEditorModels
        if Utils.transportInstalled('ZopeLib.ZopeExplorer'):
            from ZopeLib import ZopeEditorModels
            for metatype, filename in ZopeEditorModels.ZOAImages:
                idx = ZopeEditorModels.ZOAIcons[metatype]
                if allImages.has_key(idx) and filename != allImages[idx]:
                    print idx, filename, 'clash with ', allImages[idx]
                allImages[idx] = filename

        # Populate imagelist
        imgIdxs = allImages.keys()
        imgIdxs.sort()
        for idx in imgIdxs:
            midx = self.modelImageList.Add(IS.load(allImages[idx]))
            if idx != midx:
                print 'Image index mismatch', idx, midx, allImages[idx]

        self.tabs.SetImageList(self.modelImageList)

    def setupToolBar(self, modelIdx = None, viewIdx = None):
        """ Build toolbar and menus based on currently active IDE selection """
        if not self._created or self._blockToolbar or self.palette.destroying:
            return

        self.releasePrevResources()

        accLst = []
        for (ctrlKey, key, code), wId in \
                ( (keyDefs['Inspector'], EditorHelper.wxID_EDITORSWITCHINSPECTOR),
                  (keyDefs['Open'], EditorHelper.wxID_EDITOROPEN),
                  (keyDefs['HelpFind'], EditorHelper.wxID_EDITORHELPFIND),
                  (keyDefs['GotoShell'], EditorHelper.wxID_EDITORSWITCHSHELL),
                  (keyDefs['GotoExplorer'], EditorHelper.wxID_EDITORSWITCHEXPLORER),
                  (keyDefs['BrowseBack'], EditorHelper.wxID_EDITORBROWSEBACK),
                  (keyDefs['BrowseFwd'], EditorHelper.wxID_EDITORBROWSEFWD),
                  (keyDefs['PrevPage'], EditorHelper.wxID_EDITORPREVPAGE),
                  (keyDefs['NextPage'], EditorHelper.wxID_EDITORNEXTPAGE) ):
            accLst.append( (ctrlKey, key, wId) )

        # primary option: open a module
        fileMenu = wxMenu()
        if self.palette.palettePages and Preferences.edShowFileNewMenu:
            fileMenu.AppendMenu(wxNewId(), 'New',
                  Utils.duplicateMenu(self.palette.palettePages[0].menu))
        Utils.appendMenuItem(fileMenu, EditorHelper.wxID_EDITOROPEN, 'Open',
              keyDefs['Open'], self.openBmp, 'Open a module')
        Utils.appendMenuItem(fileMenu, EditorHelper.wxID_EDITOROPENRECENT,
              'Open recent files')

        addTool(self, self.toolBar, self.openBmp, 'Open a module', self.OnOpen)

        self.bbId = addTool(self, self.toolBar, self.backBmp, 'Browse back', self.OnBrowseBack)
        self.bfId = addTool(self, self.toolBar, self.forwBmp, 'Browse forward', self.OnBrowseForward)

        activeView = None
        actMod = self.getActiveModulePage(modelIdx)
        #print actMod
        if actMod:
            actMod.connectEvts()
            self._prevMod = actMod

            ModClass = actMod.model.__class__
            ctrlr = self.getControllerFromModel(actMod.model)
            if ctrlr:
                self.toolBar.AddSeparator()
                accls = ctrlr.addActions(self.toolBar, fileMenu, actMod.model)
                self._prevContrl = ctrlr
                accLst.extend(accls)

            fileMenu.AppendSeparator()
            fileMenu.Append(EditorHelper.wxID_EDITOREXITBOA, 
                  'Exit Boa Constructor', 'Exit Boa Constructor')
            self.mainMenu.Replace(mmFile, fileMenu, 'File').Destroy()
            # Edit menu
            self.toolBar.AddSeparator()

            activeView = actMod.getActiveView(viewIdx)
            if activeView:
                activeView.connectEvts()
                self._prevView = activeView

                activeView.addViewTools(self.toolBar)
                menu, accls = activeView.addViewMenus()
                self.mainMenu.Replace(mmEdit, menu, 'Edit').Destroy()
                accLst.extend(accls)

                # Views menu
                # XXX Should only recalculate when module switches
                actMod.setActiveViewsMenu()

##                menu.AppendSeparator()
##                menu.AppendMenu(wxID_DEFAULTVIEWS, 'Defaults', self.viewDefaults)
##                m = self.mainMenu.GetMenu(mmViews)
##                if m.GetMenuItemCount() > 0:
##                    m.RemoveItem(m.FindItemById(wxID_DEFAULTVIEWS))

                menu = Utils.duplicateMenu(actMod.viewMenu)
                self.mainMenu.Replace(mmViews, menu, 'Views').Destroy()
        else:
            if modelIdx == 1:
                self.explorer.addTools(self.toolBar)
                menu = self.explorer.getMenu()
                if menu:
                    self.mainMenu.Replace(mmEdit, Utils.duplicateMenu(menu),
                          'Edit').Destroy()
                else:
                    self.mainMenu.Replace(mmEdit,
                      Utils.duplicateMenu(self.blankEditMenu), 'Edit').Destroy()
            else:
                self.mainMenu.Replace(mmEdit,
                  Utils.duplicateMenu(self.blankEditMenu), 'Edit').Destroy()

            fileMenu.AppendSeparator()
            fileMenu.Append(EditorHelper.wxID_EDITOREXITBOA,
                  'Exit Boa Constructor', 'Exit Boa Constructor')
            self.mainMenu.Replace(mmFile, fileMenu, 'File').Destroy()

##            m = self.mainMenu.GetMenu(mmViews)
##            if m.GetMenuItemCount() > 0:
##                m.RemoveItem(m.FindItemById(wxID_DEFAULTVIEWS))

            self.mainMenu.Replace(mmViews,
                  Utils.duplicateMenu(self.blankViewMenu), 'Views').Destroy()


        # Help button
        self.toolBar.AddSeparator()
        Utils.AddToolButtonBmpObject(self, self.toolBar, IS.load(self.helpBmp),
              'Help', self.OnHelp)
        #Utils.AddToolButtonBmpObject(self, self.toolBar, IS.load(self.ctxHelpBmp), 'Context Help', self.OnContextHelp)

        self.toolBar.Realize()

        self.updateBrowserBtns()

        if accLst:
            self.SetAcceleratorTable(wxAcceleratorTable(accLst))

    def updateStaticMenuShortcuts(self):
        wm, hm = self.winMenu, self.helpMenu
        for menu, mId, label in ( (wm, EditorHelper.wxID_EDITORSWITCHINSPECTOR,
               'Inspector\t%s'%keyDefs['Inspector'][2]),
              (wm, EditorHelper.wxID_EDITORSWITCHSHELL,
               'Shell\t%s'%keyDefs['GotoShell'][2]),
              (wm, EditorHelper.wxID_EDITORSWITCHEXPLORER,
               'Explorer\t%s'%keyDefs['GotoExplorer'][2]),
              (wm, EditorHelper.wxID_EDITORPREVPAGE,
               'Previous window\t%s'%keyDefs['PrevPage'][2]),
              (wm, EditorHelper.wxID_EDITORNEXTPAGE,
               'Next window\t%s'%keyDefs['NextPage'][2]),
              (hm, EditorHelper.wxID_EDITORHELPFIND,
               'Find in index...\t%s'%keyDefs['HelpFind'][2]) ):
            menu.SetLabel(mId, label)

    def updateBrowserBtns(self):
        self.toolBar.EnableTool(self.bbId, self.browser.canBack())
        self.toolBar.EnableTool(self.bfId, self.browser.canForward())

    def doAfterShownActions(self):
        self.statusBar.linkProgressToStatusBar()
        tree = self.explorer.tree
        #tree.SetFocus()
        if tree.defaultBookmarkItem:
            tree.SelectItem(tree.defaultBookmarkItem)
            self.explorer.list.SetFocus()

    def addShellPage(self):
        """ Adds the interactive interpreter to the editor """
        if wxPlatform == '__WXGTK__':
            # A panel between the STC and notebook reduces flicker
            tabPage, shellEdit = \
                  Utils.wxProxyPanel(self.tabs, ShellEditor.ShellEditor, -1)
        else:
            shellEdit = tabPage = ShellEditor.ShellEditor(self.tabs, -1)

        self.tabs.AddPage(tabPage, 'Shell', imageId=EditorHelper.imgShell)

        return shellEdit

    def getValidName(self, modelClass, moreUsedNames = None):
        if moreUsedNames is None:
            moreUsedNames = []
        def tryName(modelClass, n):
            return '%s%d%s' %(modelClass.defaultName, n, modelClass.ext)
        n = 1
        #Obfuscated one-liner to check if such a name exists as a basename
        #in a the dict keys of self.module
        while filter(lambda key, name=tryName(modelClass, n): \
          os.path.basename(key) == name, self.modules.keys() + moreUsedNames):
            n = n + 1

        return tryName(modelClass, n)

    def addModulePage(self, model, moduleName, defViews, views, imgIdx, notebook=None):
        if notebook is None:
            notebook = self.tabs

        if Preferences.editorNotebookOpenPos == 'current':
            spIdx = max(notebook.GetSelection() + 1, 2)

            modulePage = ModulePage(notebook, model, defViews, views, spIdx, self)

            # notify pages for idx adjustments
            for modPge in self.modules.values():
                modPge.addedPage(spIdx)

            if self.modules.has_key(moduleName):
                print 'module %s exists'%moduleName
            self.modules[moduleName] = modulePage
            notebook.InsertPage(spIdx, modulePage.notebook, modulePage.pageName, true, imgIdx)

        elif Preferences.editorNotebookOpenPos == 'append':
            spIdx = notebook.GetPageCount()

            modulePage = ModulePage(notebook, model, defViews, views, spIdx, self)
            self.modules[moduleName] = modulePage
            notebook.AddPage(modulePage.notebook, modulePage.pageName, true, imgIdx)


        # XXX wxGTK does not trigger an AfterPageChangeEvent
        if wxPlatform == '__WXGTK__':
            self.OnTabsNotebookPageChanged(None, spIdx)

        notebook.SetSelection(spIdx)
        modulePage.refresh()
        self.editorUpdateNotify()

    def closeModulePage(self, modulePage, shutdown=false):
        actPge = self.tabs.GetSelection()
        numPgs = self.tabs.GetPageCount()
        if modulePage:
            try:
                self.closeModule(modulePage)
            except 'Cancelled':
                if shutdown: raise
                else: return
            except TransportSaveError, error:
                if shutdown: raise
                else:
                    wxLogError(str(error))
                    return

            self.mainMenu.Replace(mmEdit, wxMenu(), 'Edit').Destroy()
            if actPge == numPgs - 1:
                self.tabs.SetSelection(numPgs - 2)
            else:
                self.tabs.SetSelection(actPge)
            self.editorUpdateNotify()

            # XXX Work around bug where notebook change event differs between
            # XXX 2.3.2 and 2.3.3
            # XXX This overrides the wrong title and toolbar/menus set by the
            # XXX notebook change event
            sel = self.tabs.GetSelection()
            self.updateTitle(sel)
            self.setupToolBar(sel)

    def getActiveModulePage(self, page = None):
        if page is None: page = self.tabs.GetSelection()
        # this excludes shell
        if page:
            for mod in self.modules.values():
                if mod.tIdx == page:
                    return mod
        # XXX raise on not found ?
        return None

    def activeApp(self):
        actMod = self.getActiveModulePage()
        if actMod and actMod.model.modelIdentifier in Controllers.appModelIdReg \
              and actMod.model.data <> '':
            return actMod
        else:
            return None

    def getController(self, Controller, *args):
        if not self.controllers.has_key(Controller):
            self.controllers[Controller] = apply(Controller, (self,) + args)

        return self.controllers[Controller]

    def addNewPage(self, metatype, Controller, modelParent=None):
        controller = self.getController(Controller)

        if modelParent is None:
            modelParent = self.activeApp()
            if modelParent:
                modelParent = modelParent.model

        model, name = controller.createNewModel(modelParent)
        if controller.docked:
            if model:
                self.addModulePage(model, name, controller.DefaultViews,
                                   controller.AdditionalViews, model.imgIdx)

                controller.afterAddModulePage(model)
                model.notify()
                self.updateTitle()
        else:
            controller.display(model)

        return model

    def getAppModules(self):
        """ Return a list of all open Application modules """
        apps = []
        for modPage in self.modules.values():
            if modPage.model.modelIdentifier in Controllers.appModelIdReg:
                apps.append(modPage.model)
        return apps

    def getControllerFromModel(self, model):
        ModClass = model.__class__
        if Controllers.modelControllerReg.has_key(ModClass):
            Controller = Controllers.modelControllerReg[ModClass]
            if self.controllers.has_key(Controller):
                return self.controllers[Controller]
            elif self.controllers.has_key(ModClass):
                return self.controllers[ModClass]
        return None

#---Opening and closing items in the IDE----------------------------------------
    def openOrGotoModule(self, name, app=None, transport=None, notebook=None):
        """ Main entrypoint to open a file in the editor.

        Defaults to 'file' if no protocol given.
        Optionally handles <filename>::<lineno> format to start on a given line
        Case insensitively find model if already open.
        """

        app = None

        if string.find(name, '://') == -1:
            name = 'file://'+name

        lineno = string.rfind(name, '::')
        if lineno != -1:
            try: name, lineno = name[:lineno], int(name[lineno+2:]) -1
            except: lineno = -1

        controller = None
        name = Explorer.splitURI(name)[-1]
        if self.modules.has_key(name):
            self.modules[name].focus()
            model = self.modules[name].model
            controller = self.getControllerFromModel(model)
        else:
            # Check non case sensitive (fix for breakpoints)
            lst = self.modules.keys()
            assos = {}
            for keyIdx in range(len(lst)):
                assos[os.path.normcase(os.path.abspath(lst[keyIdx]))] = lst[keyIdx]

            a_name = os.path.normcase(os.path.abspath(name))
            if assos.has_key(a_name):
                self.modules[assos[a_name]].focus()
                model = self.modules[assos[a_name]].model
                controller = self.getControllerFromModel(model)
            else:
                model, controller = self.openModule(name, app, transport, notebook)

        if lineno != -1 and model.views.has_key('Source'):
            model.views['Source'].GotoLine(lineno)

        if controller is None:
            # XXX Use default controller class
            # XXX This path broken for Zope because of Model keys
            controller = self.getController(Controllers.modelControllerReg.get(
                  model.__class__, Controllers.DefaultController))

        return model, controller

    def openModule(self, filename, app=None, transport=None, notebook=None):
        """ Open a Model in the IDE.

        Filename must be a valid URI.
        """
        # Get transport based on filename
        prot, category, respath, filename = Explorer.splitURI(filename)
        
        assert not self.modules.has_key(filename), 'File already open.'

        if prot == 'zope':
            if transport is None:
                transport = Explorer.getTransport(prot, category, respath,
                      self.explorer.tree.transports)
            return self.openZopeDocument(transport, filename)
        else:
        # XXX commented for testing
        #elif not transport:
            transport = Explorer.getTransport(prot, category, respath,
                self.explorer.tree.transports)
            # connect if not a stateless connection
            if transport.connection:
                wxBeginBusyCursor()
                try: transport.openList()
                finally: wxEndBusyCursor()

        assert transport, 'Cannot open, no transport defined.'

        if os.path.splitext(filename)[1] in EditorHelper.getBinaryFiles():
            mode = 'rb'
        else:
            mode = 'r'

        wxBeginBusyCursor()
        try: source = transport.load(mode)
        finally: wxEndBusyCursor()

        # Get Model based on the file type
        modCls, main = Controllers.identifyFile(filename, source)#, prot == 'file')

        # See if file is entry in an open app
        if modCls.modelIdentifier not in Controllers.appModelIdReg and app is None:
            for openApp in self.getAppModules():
                normedMods = []
                for pth in openApp.absModulesPaths():
                    normedMods.append(os.path.normcase(pth))
                if os.path.normcase(filename) in normedMods:
                    app = openApp
                    break

        # Get MVC objects
        controller = self.getController(Controllers.modelControllerReg.get(
              modCls, Controllers.DefaultController))
        model = controller.createModel(source, filename, main, true, app)
        defViews = controller.DefaultViews
        views = controller.AdditionalViews

        model.transport = transport

        # Add in IDE or display
        if controller.docked:
            self.addModulePage(model, filename, defViews, views, model.imgIdx, notebook)
        else:
            controller.display(model)

        model.notify()

        return model, controller

    def getZopeController(self, Model):
        if not self.controllers.has_key(Model):
            self.controllers[Model] = \
                  Controllers.modelControllerReg[Model](self, Model)
        return self.controllers[Model]

    # XXX Unify with the rest of the explorers
    def openOrGotoZopeDocument(self, zopeObj):
        wholename=zopeObj.getURI()
        if self.modules.has_key(wholename):
            self.modules[wholename].focus()
            controller = self.getZopeController(zopeObj.Model)
            return self.modules[wholename].model, controller
        else:
            return self.openZopeDocument(zopeObj, wholename)

    # XXX Unify with the rest of the explorers
    def openZopeDocument(self, zopeObj, wholename):
        if zopeObj and zopeObj.Model:
            controller = self.getZopeController(zopeObj.Model)

            model = controller.createModel('', wholename, '', false, zopeObj)

            model.transport = zopeObj
            model.load()

            self.addModulePage(
                model, wholename, zopeObj.defaultViews,
                zopeObj.additionalViews, zopeObj.Model.imgIdx)
            model.notify()

            self.updateTitle()
            return model, controller
        else:
            wxLogWarning('Zope Object %s not supported' % `zopeObj`)
            return None, None

    def addNewView(self, name, viewClass):
        module = self.getActiveModulePage()
        if module:
            if not module.model.views.has_key(name):
                return module.addView(viewClass, name)
            else:
                return module.model.views[name]

    def addNewDialog(self, dlgClass, dlgCompanion):
        module = self.getActiveModulePage()
        if module:
            view = module.getActiveView()
            if view and view.viewName == 'Source':
                compn = dlgCompanion('dlg', None)
                view.insertCodeBlock(compn.body())

    def openFileDlg(self, filter='*.py', curdir='.'):
        if filter == '*.py': filter = Preferences.exDefaultFilter

        if curdir=='.' and getattr(Preferences, 'exOpenFromHere', 1):
            # Open relative to the file in the active module page.
            actMod = self.getActiveModulePage()
            if actMod:
                filename = actMod.model.filename
                if filename:
                    curdir = os.path.dirname(filename)
                    if not curdir:
                        curdir = '.'

        from FileDlg import wxFileDialog
        dlg = wxFileDialog(self, 'Choose a file', curdir, '', filter, wxOPEN)
        try:
            if dlg.ShowModal() == wxID_OK:
                return dlg.GetPath()
        finally:
            dlg.Destroy()
        return ''

    def saveAsDlg(self, filename, filter = '*.py', dont_pop=0):
        if filter == '*.py': filter = Preferences.exDefaultFilter

        dir, name = os.path.split(filename)
        if not dir:
            dir = Preferences.pyPath
        if dir[-1] == ':':
            dir = dir[:-1]

        from FileDlg import wxFileDialog
        dlg = wxFileDialog(self, 'Save as...', dir, name, filter,
              wxSAVE | wxOVERWRITE_PROMPT)
        dlg.dont_pop = dont_pop
        try:
            if dlg.ShowModal() == wxID_OK:
                return dlg.GetPath(), true
            else:
                return '', false
        finally:
            dlg.Destroy()

    def activeModSaveOrSaveAs(self, forceSaveAs=false):
        modulePage = self.getActiveModulePage()
        if modulePage:
            modulePage.model.refreshFromViews()
            modulePage.saveOrSaveAs(forceSaveAs)

    def prepareForCloseModule(self, modulePage, focusPromptingPages=false):
        # XXX most of this should move to ModulePage
        idx = modulePage.tIdx
        model = modulePage.model
        name = model.filename
        if self.modules.has_key(name):
            if model.views.has_key('Designer'):
                model.views['Designer'].close()

            insp = self.inspector
            try:
                if insp.selCmp and insp.sessionHandler and \
                  hasattr(insp.selCmp, 'model') and model is insp.selCmp.model:
                    insp.sessionHandler.promptPostOrCancel(insp)
            except:
                if focusPromptingPages:
                    self.tabs.SetSelection(modulePage.tIdx)

                raise 'Cancelled'

            model.refreshFromViews()
            if model.modified:
                if focusPromptingPages:
                    self.tabs.SetSelection(modulePage.tIdx)

                dlg = wxMessageDialog(self, 'There are changes, do you want to save?',
                        'Close module', wxYES_NO | wxCANCEL |wxICON_QUESTION)
                try: res = dlg.ShowModal()
                finally: dlg.Destroy()
                if res == wxID_YES:
                    self.activeModSaveOrSaveAs()
                    name = model.filename
                elif res == wxID_CANCEL:
                    raise 'Cancelled'
            return idx, name
        else:
            return -1, None


    def closeModule(self, modulePage):
        idx, name = self.prepareForCloseModule(modulePage)
        
        if idx != -1:
            self.browser.checkRemoval(modulePage)
            self.tabs.RemovePage(idx)
            del self.modules[name]
            modulePage.destroy()

            # notify pages for idx adjustments
            for modPge in self.modules.values():
                modPge.removedPage(idx)

##        else:
##            print name, 'not found in OnClose', pprint.pprint(self.modules)

#---Visual updating methods-----------------------------------------------------
    def updateModuleState(self, model, filename = '', pageIdx=None):
        self.updateModulePage(model, filename)
        self.updateTitle(pageIdx)

    def updateTitle(self, pageIdx = None):
        """ Updates the title of the Editor to reflect changes in selection,
            filename or model state.
        """

        # XXX Do decorations here
        modulePage = self.getActiveModulePage(pageIdx)
        if modulePage:
            self.SetTitle('Editor - %s - %s' %(modulePage.pageName,
              modulePage.model.filename))
              # modulePage.model.getDisplayName()))
        else:
            if pageIdx is None:
                pageIdx = self.tabs.GetSelection()
            self.SetTitle('Editor - %s' % self.tabs.GetPageText(pageIdx))

    def updateModulePage(self, model, filename = ''):
        if filename:
            modPge = self.modules[filename]
        else:
            modPge = self.modules[model.filename]
        self.tabs.SetPageText(modPge.tIdx, modPge.updatePageName())

    def assureRefreshed(self):
        sel = self.tabs.GetSelection()
        page = self.tabs.GetPage(sel)
        if page:
            page.SetFocus()

        self.updateTitle(sel)
        self.setupToolBar(sel)

    # XXX this looks like overkill
    def clearAllStepPoints(self):
        for mod in self.modules.values():
            if mod.model.views.has_key('Source'):
                mod.model.views['Source'].setStepPos(0)

    def setStatus(self, hint, msgType='Info', ringBell=false):
        self.statusBar.setHint(hint, msgType, ringBell)

    def getMainFrame(self):
        if self.palette.IsShown():
            return self.palette
        else:
            return self

    def minimizeBoa(self):
        if self.palette.IsShown() and not self.palette.IsIconized():
            self.palette.Iconize(true)
        elif not self.IsIconized():
            self.Iconize(true)

    def editorUpdateNotify(self):
        self.explorer.editorUpdateNotify()

    def explorerRenameNotify(self, oldURI, newNode):
        if self.modules.has_key(oldURI):
            modulePage = self.modules[oldURI]
            modulePage.model.transport = newNode
            modulePage.model.updateNameFromTransport()
            newURI = newNode.getURI()
            modulePage.rename(oldURI, newURI)

            self.updateModulePage(modulePage.model, newURI)

    def explorerDeleteNotify(self, URI):
        if self.modules.has_key(URI):
            self.closeModulePage(self.modules[URI])

    def OnOpen(self, event, curdir='.'):
        fn = self.openFileDlg(curdir=curdir)
        if fn:
            tree = self.explorer.tree
            self.openOrGotoModule(fn)
            tree.recentFiles.add(fn)

            node = tree.GetPyData(tree.GetSelection())
            if node.protocol == 'recent.files':
                self.explorer.list.refreshCurrent()

    def OnOpenRecent(self, event, curdir='.'):
        self.OnOpen(event, 'recent.files://')

    def OnTabsNotebookPageChanged(self, event, sel=None):
        if sel is None:
            sel = event.GetSelection()
##            print sel
##        else:
##            if event is not None:
##                print sel, event.GetSelection()
##            else:
##                print 'force %s'%sel
        if sel > -1:
            self.updateTitle(sel)
            if self._created:
                self.setupToolBar(sel)
                if sel == 1:
                    self.editorUpdateNotify()

        if event: event.Skip()

#---Help events-----------------------------------------------------------------
    def OnHelp(self, event):
        Help.showHelp('Editor.html')

    def OnHelpGuide(self, event):
        Help.showMainHelp('Boa Constructor Getting Started Guide')

    def OnHelpTips(self, event):
        Utils.showTip(self, true)

    def OnHelpAbout(self, event):
        abt = About.DefAboutBox(None)
        try:     abt.ShowModal()
        finally: abt.Destroy()

    def OnHelpFindIndex(self, event):
        dlg = wxTextEntryDialog(self, 'Enter term to search for in the index',
              'Help - Find in index', '')
        try:
            if dlg.ShowModal() == wxID_OK:
                Help.showContextHelp(dlg.GetValue())
        finally:
            dlg.Destroy()

    def OnContextHelp(self, event):
        wxContextHelp(self)

##    def defsMenu(self, model, viewClss):
##        """ Default menus specifying which views are opened by default when a
##            certain type of model is opened.
##        """
##
##        menu = wxMenu()
##        for view in viewClss:
##            wId = wxNewId()
##            self.viewDefaultIds[wId] = view, model
##            menu.Append(wId, view.viewName, checkable = true)
##            menu.Check(wId, false)
##            EVT_MENU(self, wId, self.OnDefaultsToggle)
##        return menu
##
##    def OnDefaultsToggle(self, event):
##        evtId = event.GetId()
##        view, model = self.viewDefaultIds[event.GetId()]
##        if self.mainMenu.IsChecked(evtId):
##            if view not in self.defaultAdtViews.get(model, []):
##                self.defaultAdtViews[model].append(view)
##        else:
##            if view in self.defaultAdtViews.get(model, []):
##                self.defaultAdtViews[model].remove(view)

##        self.viewDefaultIds = {}
##        self.viewDefaults = wxMenu()
##        self.viewDefaults.AppendMenu(wxNewId(), AppModel.modelIdentifier,
##          self.defsMenu(AppModel, adtAppModelViews))
##        self.viewDefaults.AppendMenu(wxNewId(), BaseFrameModel.modelIdentifier,
##          self.defsMenu(BaseFrameModel, adtBaseFrameModelViews))
##        self.viewDefaults.AppendMenu(wxNewId(), ModuleModel.modelIdentifier,
##          self.defsMenu(ModuleModel, adtModModelViews))
##        self.viewDefaults.AppendMenu(wxNewId(), PackageModel.modelIdentifier,
##          self.defsMenu(PackageModel, adtPackageModelViews))
##        self.viewDefaults.AppendMenu(wxNewId(), TextModel.modelIdentifier,
##          self.defsMenu(TextModel, adtTextModelViews))
##        self.blankViewMenu.AppendMenu(wxID_DEFAULTVIEWS, 'Defaults', self.viewDefaults)
##

    def OnToggleView(self, event, evtId=None):
        if evtId is None:
            evtId = event.GetId()
        mod = self.getActiveModulePage()
        if mod:
            modVwClss = map(lambda x: x.__class__, mod.model.views.values())
            #Find view class associated with this id
            for viewCls, wId in mod.adtViews:
                if wId == evtId:
                    if self.mainMenu.IsChecked(evtId):
                        #Should be added, but check that it doesn't exist
                        if viewCls not in modVwClss:
                            view = mod.addView(viewCls)
                            view.refreshCtrl()
                            view.focus()
                        else:
                            print 'Add: View already exists'
                    else:
                        #Should be removed, but check that it does exist
                        if viewCls in modVwClss:
                            viewName = viewCls.viewName
                            view = mod.model.views[viewName]
                            if view.modified:
                                view.refreshModel()
                            view.deleteFromNotebook(mod.default, viewName)

                            self.mainMenu.Check(evtId, false)
                            return
                        else:
                            print 'Remove: View already exists'
                    break

    def OnSwitchedToView(self, event):
        # This is triggered twice, I'd love to know why
        pass

#---Switching to different windows----------------------------------------------
    def OnGotoModulePage(self, event):
        wId = event.GetId()
        for mod in self.modules.values():
            if mod.windowId == wId:
                self.tabs.SetSelection(mod.tIdx)

    def OnSwitchShell(self, event=None):
        self.tabs.SetSelection(0)

    def OnSwitchExplorer(self, event):
        if self.tabs.GetSelection() == 1:
            tree = self.explorer.tree
            cookie = 0
            child, cookie = tree.GetFirstChild(tree.GetRootItem(), cookie)
            tree.SelectItem(child)
            self.explorer.list.SetFocus()
            STATE = wxLIST_STATE_FOCUSED|wxLIST_STATE_SELECTED
            self.explorer.list.SetItemState(0, STATE, STATE)

        else:
            self.tabs.SetSelection(1)

    def OnSwitchPrefs(self, event):
        self.tabs.SetSelection(1)
        tree = self.explorer.tree
        cookie = 0
        child = tree.GetLastChild(tree.GetRootItem())
        tree.SelectItem(child)
        tree.EnsureVisible(child)
        self.explorer.list.SetFocus()
        STATE = wxLIST_STATE_FOCUSED|wxLIST_STATE_SELECTED
        self.explorer.list.SetItemState(1, STATE, STATE)

    def OnSwitchPalette(self, event):
        self.palette.restore()

    def OnSwitchInspector(self, event):
        self.inspector.restore()

    def OnNextPage(self, event):
        pc = self.tabs.GetPageCount()
        idx = self.tabs.GetSelection() + 1
        if idx >= pc: idx = 0
        self.tabs.SetSelection(idx)

    def OnPrevPage(self, event):
        pc = self.tabs.GetPageCount()
        idx = self.tabs.GetSelection() - 1
        if idx < 0: idx = pc - 1
        self.tabs.SetSelection(idx)

#---Code Browsing---------------------------------------------------------------
    def addBrowseMarker(self, marker):
        """ Add marker to browse stack associated with the currently open module
            and view
        """
        modulePage = self.getActiveModulePage()
        if modulePage:
            activeView = modulePage.getActiveView()
            self.browser.add(modulePage, activeView.viewName, marker)
            self.updateBrowserBtns()

    def OnBrowseBack(self, event):
        self.browser.back()
        self.updateBrowserBtns()

    def OnBrowseForward(self, event):
        self.browser.forward()
        self.updateBrowserBtns()

#---State methods---------------------------------------------------------------
    def restoreEditorState(self):
        # Open previously opened files
        if Preferences.rememberOpenFiles:
            conf = Utils.createAndReadConfig('Explorer')
            if conf.has_section('editor'):
                files = eval(conf.get('editor', 'openfiles'))
                self._blockToolbar = true
                try:
                    cnt = 0
                    for file in files:
                        try:
                            print 'opening in Editor: %s <<%d/%d>>' % (string.split(
                                  os.path.basename(file), '::')[0], cnt, len(files))

                            self.openOrGotoModule(file)
                            cnt = cnt + 1

                        except Exception, error:
                            # Swallow exceptions
                            wxLogError(str(error))

                    try:
                        actPage = conf.getint('editor', 'activepage')
                        if actPage < self.tabs.GetPageCount():
                            self.tabs.SetSelection(actPage)
                    except:
                        pass
                finally:
                    self._blockToolbar = false

    def persistEditorState(self):
        # Save list of open files to config
        if Preferences.rememberOpenFiles:
            modOrder = []
            for mod, modPage in self.modules.items():
                if modPage.model.savedAs:
                    if modPage.model.views.has_key('Source'):
                        mod = '%s::%d' %(mod,
                              modPage.model.views['Source'].GetCurrentLine()+1)
                    modOrder.append( (modPage.tIdx, mod) )
            modOrder.sort()

            mods = []
            for idx, mod in modOrder:
                mods.append(mod)

            conf = Utils.createAndReadConfig('Explorer')
            if not conf.has_section('editor'): conf.add_section('editor')
            conf.set('editor', 'openfiles', pprint.pformat(mods))
            conf.set('editor', 'activepage', self.tabs.GetSelection())
            try:
                Utils.writeConfig(conf)
            except Exception, error:
                wxLogError('Could not save open file list: '+str(error))

#---Misc events-----------------------------------------------------------------
    def OnExecFinish(self, event):
        if self.erroutFrm:
            if self.palette.IsShown():
                self.palette.restore()
            self.restore()

            event.runner.init(self.erroutFrm, event.runner.app)
            errs = event.runner.recheck()
            if errs:
                self.statusBar.setHint('Finished execution, there were errors', 'Warning')
            else:
                self.statusBar.setHint('Finished execution.')

    def OnExitBoa(self, event):
        self.palette.Close()

    def OnMenuHighlight(self, event):
        item = self.mainMenu.FindItemById(event.GetMenuId())
        if item:
            self.statusBar.setHint(item.GetHelp())

    def OnHidePalette(self, event):
        self.palette.Show(false)

    def OnCloseWindow(self, event):
        if not self.palette.destroying and not self.palette.IsShown():
            self.palette.Close()
            return

        if self.palette.destroying:
            if self.debugger:
                if self.debugger.running:
                    wxLogError('Please close the application running in the'
                    ' debugger before continuing.')
                    self.palette.destroying = false
                    return
                else:
                    self.debugger.Close(true)

            self.persistEditorState()
            self.finder.saveOptions()

            modPageList = []
            for name, modPage in self.modules.items():
                modPageList.append( (modPage.tIdx, name, modPage) )
            modPageList.sort()
            for idx, name, modPage in modPageList:
                try:
                    self.prepareForCloseModule(modPage, true)
                except 'Cancelled':
                    self.palette.destroying = false
                    return
                except TransportSaveError, error:
                    self.palette.destroying = false
                    wxLogError(str(error))
                    return

##            # Close open items
##            # hack to avoid core dump, first setting the notebook to anything but
##            # the last page before setting it to the last page allows us to close
##            # this window from the palette. Weird?
##            self.tabs.SetSelection(0)
##            pgeCnt = self.tabs.GetPageCount()
##            self.tabs.SetSelection(pgeCnt -1)
##            for p in range(pgeCnt):
##                try:
##                    self.closeModulePage(self.getActiveModulePage(), true)
##                except 'Cancelled':
##                    self.palette.destroying = false
##                    return
##                except TransportSaveError, error:
##                    self.palette.destroying = false
##                    wxLogError(str(error))
##                    return

            # stop accepting files over socket
            if self.closed:
                self.closed.set()
                # This caused problems when Boa closes 'too quickly', by sleeping
                # for half the select time-out, seems to work although sleeping for
                # the exactly the time-out would be safest (but starts to be noticeable)
                import time
                time.sleep(0.125)

            self.palette.editor = None
            self.inspector = None
            self.controllers = None
            self.explorer.Hide()
            self.explorer.destroy()

            self.newMenu.Destroy()
            self.blankEditMenu.Destroy()
            self.blankViewMenu.Destroy()

            self.erroutFrm.Destroy()
            self.erroutFrm = None

            self.shell.destroy()

            if sys.boa_ide == self:
                del sys.boa_ide

            self._prevMod = None
            self._prevView = None
            self._prevContrl = None

            self.modelImageList = None
            import FileDlg
            FileDlg.wxBoaFileDialog.modImages = None

            self.statusBar.destroy()

            self.Destroy()
            event.Skip()
        else:
            self.Show(false)

#---Window dimensions maintenance-----------------------------------------------
    def callOnIDEWindows(self, meth):
        for window in (self.palette, self.inspector, self, self.erroutFrm,
                       self.debugger, self.palette.browser):
            if window: meth(window)

    def OnWinDimsLoad(self, event):
        self.callOnIDEWindows(Utils.FrameRestorerMixin.loadDims)
        self.setStatus('Window dimensions loaded')

    def OnWinDimsSave(self, event):
        self.callOnIDEWindows(Utils.FrameRestorerMixin.saveDims)
        self.setStatus('Window dimensions saved')

    def OnWinDimsRestoreDefs(self, event):
        self.callOnIDEWindows(Utils.FrameRestorerMixin.restoreDefDims)
        self.setStatus('Window dimensions restored to defaults')

#---Server idle polling method--------------------------------------------------
    def pollForOpen(self, event=None):
        opened = 0
        while 1:
            try:
                name = self.open_queue.get(0)
                self.openOrGotoModule(name)
                opened = 1
            except Queue.Empty:
                break
        if opened:
            if self.palette.IsShown():
                self.palette.restore()
            else:
                self.restore()



if __name__ == '__main__':
    app = wxPySimpleApp()
    wxInitAllImageHandlers()

    import Palette
    palette = Palette.BoaFrame(None, -1, app)

    frame = EditorFrame(None, -1, None, None, None, app, palette)
    frame.Show()
    app.MainLoop()
