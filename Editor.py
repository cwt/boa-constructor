#----------------------------------------------------------------------
# Name:        Editor.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2001 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
#Boa:Frame:EditorFrame

""" The main IDE frame containing the Shell, Explorer and the ability to host 
Models and their Views on ModulePages"""

# The focus of change
# the center of creation
# Alchemy

print 'importing Editor'

import os, sys, string, pprint
import threading, Queue, select

from wxPython.wx import *

import EditorModels, EditorHelper
from EditorUtils import EditorToolBar, EditorStatusBar, ModulePage

import Preferences, Utils
from Preferences import keyDefs, IS, wxFileDialog, flatTools
import About, Help, Browse

from Explorers import Explorer
from Explorers.ExplorerNodes import TransportSaveError, TransportLoadError
import Controllers
import ShellEditor
from ModRunner import EVT_EXEC_FINISH

addTool = Utils.AddToolButtonBmpIS

(mmFile, mmEdit, mmViews, mmWindows, mmHelp) = range(5)

[wxID_EDITORFRAME, wxID_EDITORFRAMESTATUSBAR, wxID_EDITORFRAMETABS, wxID_EDITORFRAMETOOLBAR] = map(lambda _init_ctrls: wxNewId(), range(4))

class EditorFrame(wxFrame, Utils.FrameRestorerMixin):
    """ Source code editor and Mode/View controller """

    openBmp = 'Images/Editor/Open.bmp'
    backBmp = 'Images/Shared/Previous.bmp'
    forwBmp = 'Images/Shared/Next.bmp'
    helpBmp = 'Images/Shared/Help.bmp'
    
    _custom_classes = {'wxToolBar': ['EditorToolBar'],
                       'wxStatusBar': ['EditorStatusBar']}  

    def _init_coll_mainMenu_Menus(self, parent):

        parent.Append(menu = wxMenu(), title = 'File')
        parent.Append(menu = wxMenu(), title = 'Edit')
        parent.Append(menu = wxMenu(), title = 'Views')

    def _init_utils(self):
        self.modelImageList = wxImageList(height = 16, width = 16)

        self.mainMenu = wxMenuBar()

        self.blankEditMenu = wxMenu(title = '')

        self.blankViewMenu = wxMenu(title = '')

        self.helpMenu = wxMenu(title = '')

        self._init_coll_mainMenu_Menus(self.mainMenu)

    def _init_ctrls(self, prnt):
        wxFrame.__init__(self, id = wxID_EDITORFRAME, name = '', parent = prnt, pos = wxPoint(182, 189), size = wxSize(810, 513), style = wxDEFAULT_FRAME_STYLE | Preferences.childFrameStyle, title = 'Editor')
        self._init_utils()
        self.SetMenuBar(self.mainMenu)
        self.SetClientSize(wxSize(802, 486))
        EVT_CLOSE(self, self.OnCloseWindow)

        self.statusBar = EditorStatusBar(id = wxID_EDITORFRAMESTATUSBAR, name = 'statusBar', parent = self, pos = wxPoint(0, 447), size = wxSize(802, 20), style = 0)
        self.SetStatusBar(self.statusBar)

        self.tabs = wxNotebook(id = wxID_EDITORFRAMETABS, name = 'tabs', parent = self, pos = wxPoint(0, 0), size = wxSize(802, 419), style = wxCLIP_CHILDREN)
        EVT_NOTEBOOK_PAGE_CHANGED(self.tabs, wxID_EDITORFRAMETABS, self.OnTabsNotebookPageChanged)

        self.toolBar = EditorToolBar(id = wxID_EDITORFRAMETOOLBAR, name = 'toolBar', parent = self, pos = wxPoint(0, -28), size = wxSize(802, 28), style = wxTB_HORIZONTAL | wxNO_BORDER)
        self.SetToolBar(self.toolBar)

    def __init__(self, parent, id, inspector, newMenu, componentPalette, app, palette):
	self._created = false
        self._init_ctrls(parent)
        self.SetDimensions(Preferences.inspWidth + Preferences.windowManagerSide*2,
              Preferences.paletteHeight + Preferences.windowManagerTop + \
              Preferences.windowManagerBottom, Preferences.edWidth,
              Preferences.bottomHeight)
        self.SetBackgroundColour(wxSystemSettings_GetSystemColour(wxSYS_COLOUR_BTNFACE))

        if wxPlatform == '__WXMSW__':
            self.SetIcon(IS.load('Images/Icons/Editor.ico'))

        self.app = app
        self.palette = palette
        self.modules = {}
        self.inspector = inspector
        self.compPalette = componentPalette
        self.debugger = None
        self.browser = Browse.Browser()
        self.controllers = {}

        # Build imagelist of all models
        for builtinImg in ('Images/Modules/FolderUp_s.bmp', 
              'Images/Modules/Folder_s.bmp', 
              'Images/Modules/Folder_green_s.bmp',
              'Images/Modules/Folder_cyan_s.bmp', 
              'Images/Zope/System_obj.bmp',
              'Images/Modules/ZopeConn_s.bmp', 
              'Images/Shared/BoaLogo.bmp',
              'Images/Modules/Drive_s.bmp',
              'Images/Modules/NetDrive_s.bmp',
              'Images/Modules/FolderBookmark_s.bmp',
              'Images/Modules/OpenEditorModels_s.bmp',
              'Images/Modules/PrefsFolder_s.bmp',
              'Images/Shared/PrefsSTCStyles.bmp', ):
            self.modelImageList.AddWithColourMask(IS.load(builtinImg), 
                  wxColour(255, 0, 255))
        orderedModList = []
        for mod in EditorModels.modelReg.values(): 
            orderedModList.append((mod.imgIdx, mod))
        orderedModList.sort()
        for mod in orderedModList:
            self.modelImageList.AddWithColourMask(\
                IS.load('Images/Modules/'+mod[1].bitmap), wxColour(255, 0, 255))

        if Utils.createAndReadConfig('Explorer').has_option('explorer', 'zope'):
            # Add Zoa Images
            import ZopeEditorModels
            for metatype, filename in ZopeEditorModels.ZOAImages:
                ZopeEditorModels.ZOAIcons[metatype] = \
                      self.modelImageList.AddWithColourMask(IS.load(filename), 
                      wxColour(255, 0, 255))

        if wxPlatform == '__WXMSW__':
            self.tabs.SetImageList(self.modelImageList)

        # Hook for shell and scripts
        sys.boa_ide = self

        # Shell
        self.shell = self.addShellPage()

        # Explorer
        self.explorer = Explorer.ExplorerSplitter (self.tabs,
              self.modelImageList, '', self)
        self.tabs.AddPage(self.explorer, 'Explorer')
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
        EVT_MENU(self, EditorHelper.wxID_EDITOREXITBOA, self.OnExitBoa)

        # Windows menu
        EVT_MENU(self, EditorHelper.wxID_EDITORSWITCHSHELL, self.OnSwitchShell)
        EVT_MENU(self, EditorHelper.wxID_EDITORSWITCHEXPLORER, self.OnSwitchExplorer)
        EVT_MENU(self, EditorHelper.wxID_EDITORSWITCHPALETTE, self.OnSwitchPalette)
        EVT_MENU(self, EditorHelper.wxID_EDITORSWITCHINSPECTOR, self.OnSwitchInspector)
        EVT_MENU(self, EditorHelper.wxID_EDITORPREVPAGE, self.OnPrevPage)
        EVT_MENU(self, EditorHelper.wxID_EDITORNEXTPAGE, self.OnNextPage)

        self.winMenu = wxMenu()
        self.winMenu.Append(EditorHelper.wxID_EDITORSWITCHPALETTE, 'Palette', 'Switch to the Palette frame.')
        self.winMenu.Append(EditorHelper.wxID_EDITORSWITCHINSPECTOR, 
              'Inspector\t%s'%keyDefs['Inspector'][2], 'Switch to the Inspector frame.')
        self.winMenu.Append(-1, '-')
        self.winMenu.Append(EditorHelper.wxID_EDITORSWITCHSHELL, 
              'Shell\t%s'%keyDefs['GotoShell'][2], 'Switch to the Shell page')
        self.winMenu.Append(EditorHelper.wxID_EDITORSWITCHEXPLORER, 
              'Explorer\t%s'%keyDefs['GotoExplorer'][2], 'Switch to the Explorer page')
        self.winMenu.Append(-1, '-')
        self.winMenu.Append(EditorHelper.wxID_EDITORPREVPAGE, 
              'Previous window\t%s'%keyDefs['PrevPage'][2], 'Switch to the previous page of the main notebook')
        self.winMenu.Append(EditorHelper.wxID_EDITORNEXTPAGE, 
              'Next window\t%s'%keyDefs['NextPage'][2], 'Switch to the next page of the main notebook')
        self.winMenu.Append(-1, '-')
        self.mainMenu.Append(self.winMenu, 'Windows')

        # Help menu
        self.helpMenu.Append(EditorHelper.wxID_EDITORHELP, 'Help', 'Opens help for the Editor')
        self.helpMenu.Append(EditorHelper.wxID_EDITORHELPGUIDE, 'Getting started guide', 'Opens the Getting started guide')
        self.helpMenu.AppendSeparator()
        self.helpMenu.Append(EditorHelper.wxID_EDITORHELPFIND, 'Find in index...\t%s'%keyDefs['HelpFind'][2], 'Pops up a text input for starting a search of the help indexes')
        self.helpMenu.Append(EditorHelper.wxID_EDITORHELPTIPS, 'Tips', 'Opens the "Tip of the Day" window')
        self.helpMenu.AppendSeparator()
        self.helpMenu.Append(EditorHelper.wxID_EDITORHELPABOUT, 'About', 'Opens the About box')

        EVT_MENU(self, EditorHelper.wxID_EDITORHELP, self.OnHelp)
        EVT_MENU(self, EditorHelper.wxID_EDITORHELPABOUT, self.OnHelpAbout)
        EVT_MENU(self, EditorHelper.wxID_EDITORHELPGUIDE, self.OnHelpGuide)
        EVT_MENU(self, EditorHelper.wxID_EDITORHELPTIPS, self.OnHelpTips)
        EVT_MENU(self, EditorHelper.wxID_EDITORHELPFIND, self.OnHelpFindIndex)

        self.mainMenu.Append(self.helpMenu, 'Help')

        # Start listening for requests to open files. Listener will run, putting
        # files to open into open_queue, until closed is set.
        self.open_queue = Queue.Queue(0)
        self.closed = threading.Event()
        self.listener = Listener(self.open_queue, self.closed).start()

        # create initial toolbar buttons and menus
        self._prevMod = None
        self._prevView = None
        self._created = true
##        self.defaultAdtViews = {}
        self.setupToolBar(viewIdx = 0)

# XXX Nothing works
##        tree = self.explorer.tree
##        if tree.defaultBookmarkItem:
##            ws = tree.getChildNamed(tree.GetRootItem(), 'Bookmarks')
###        self.defaultBookmarkItem = self.getChildNamed(ws, self.boaRoot.entries[1].getDefault())
###            self.getChildNamed(ws, tree.boaRoot.entries[1].getDefault())
##            tree.SelectItem(tree.getChildNamed(ws, tree.boaRoot.entries[1].getDefault()))
###            self.explorer.tree.defaultBookmarkItem)
##
###            print 'Setting default', self.explorer.tree.defaultBookmarkItem
###            self.explorer.tree.SelectItem(self.explorer.tree.defaultBookmarkItem)
###            print 'Set def', self.explorer.tree.GetSelection()
##
##            if self.explorer.list.GetItemCount():
##                item = self.explorer.list.GetItem(0)
##                item.SetState(wxLIST_STATE_SELECTED | wxLIST_STATE_FOCUSED)
##                self.explorer.list.SetItem(item)

        dt = Utils.BoaFileDropTarget(self)
        self.SetDropTarget(dt)

        self.explorer.list.SetFocus()

        # init (docked) error output frame
        import ErrorStackFrm
        self.erroutFrm = ErrorStackFrm.ErrorStackMF(self, self)
        
        if Preferences.showErrOutInInspector:
            panel, notebook = \
              Utils.wxProxyPanel(self.inspector.pages, self.erroutFrm.notebook1)
            self.inspector.pages.AddPage(panel, 'ErrOut')

        # Hack to feed BoaFileDialog images
        import FileDlg
        FileDlg.wxBoaFileDialog.modImages = self.modelImageList

        EVT_EXEC_FINISH(self, self.OnExecFinish)
        EVT_MENU_HIGHLIGHT_ALL(self, self.OnMenuHighlight)
        self.restoreEditorState()

        from FindReplaceEngine import FindReplaceEngine
        self.finder = FindReplaceEngine()

        # quit server mode flag not guaranteed to be set (yet) even if there is 
        # already a server running, but don't connect idle if not necessary
        if self.closed.isSet():
            print 'Not running in server mode'
        else:
            EVT_IDLE(self, self.poll_for_open)
    
    def __repr__(self):
        return '<EditorFrame (Boa IDE) instance at %d>'%id(self)

    def setupToolBar(self, modelIdx = None, viewIdx = None):
        """ Build toolbar and menus based on currently active IDE selection """
        if not self._created or self.palette.destroying:
            return

        # Release previous resources
        self.toolBar.ClearTools()
        if self._prevView:
            self._prevView.disconnectEvts()
            self._prevView = None
        if self._prevMod:
            self._prevMod.disconnectEvts()
            self._prevMod = None
                    
        accLst = []
        for (ctrlKey, key, code), wId in \
                ( (keyDefs['Inspector'], EditorHelper.wxID_EDITORSWITCHINSPECTOR),
                  (keyDefs['Open'], EditorHelper.wxID_EDITOROPEN),
                  (keyDefs['HelpFind'], EditorHelper.wxID_EDITORHELPFIND),
                  (keyDefs['GotoShell'], EditorHelper.wxID_EDITORSWITCHSHELL),
                  (keyDefs['GotoExplorer'], EditorHelper.wxID_EDITORSWITCHEXPLORER),
                  (keyDefs['PrevPage'], EditorHelper.wxID_EDITORPREVPAGE),
                  (keyDefs['NextPage'], EditorHelper.wxID_EDITORNEXTPAGE) ):
            accLst.append( (ctrlKey, key, wId) )

        # primary option: open a module
        fileMenu = wxMenu()
        if self.palette.palettePages:
            fileMenu.AppendMenu(wxNewId(), 'New', 
                  Utils.duplicateMenu(self.palette.palettePages[0].menu))
        fileMenu.Append(EditorHelper.wxID_EDITOROPEN, 
              'Open\t%s'%keyDefs['Open'][2], 'Open a module')

        addTool(self, self.toolBar, self.openBmp, 'Open a module', self.OnOpen)

        self.bbId = addTool(self, self.toolBar, self.backBmp, 'Browse back', self.OnBrowseBack)
        self.bfId = addTool(self, self.toolBar, self.forwBmp, 'Browse forward', self.OnBrowseForward)

        activeView = None
        actMod = self.getActiveModulePage(modelIdx)
        if actMod:
            actMod.connectEvts()
            self._prevMod = actMod

            if Controllers.modelControllerReg.has_key(actMod.model.__class__):
                Controller = Controllers.modelControllerReg[actMod.model.__class__]
                if self.controllers.has_key(Controller):
                    self.toolBar.AddSeparator()
                    ctrlr = self.controllers[Controller]
                    ctrlr.addTools(self.toolBar, actMod.model)
                    accls = ctrlr.addMenus(fileMenu, actMod.model)
                    accLst.extend(accls)

            fileMenu.AppendSeparator()
            fileMenu.Append(EditorHelper.wxID_EDITOREXITBOA, 'Exit Boa Constructor', 'Exit Boa Constructor')
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
                    self.mainMenu.Replace(mmEdit, Utils.duplicateMenu(menu), 'Edit').Destroy()
                else:
                    self.mainMenu.Replace(mmEdit, Utils.duplicateMenu(self.blankEditMenu), 'Edit').Destroy()
            else:
                self.mainMenu.Replace(mmEdit, Utils.duplicateMenu(self.blankEditMenu), 'Edit').Destroy()

            fileMenu.AppendSeparator()
            fileMenu.Append(EditorHelper.wxID_EDITOREXITBOA, 'Exit Boa Constructor', 'Exit Boa Constructor')
            self.mainMenu.Replace(mmFile, fileMenu, 'File').Destroy()

##            m = self.mainMenu.GetMenu(mmViews)
##            if m.GetMenuItemCount() > 0:
##                m.RemoveItem(m.FindItemById(wxID_DEFAULTVIEWS))

            self.mainMenu.Replace(mmViews, Utils.duplicateMenu(self.blankViewMenu), 'Views').Destroy()


        # Help button
        self.toolBar.AddSeparator()
        Utils.AddToolButtonBmpObject(self, self.toolBar, IS.load(self.helpBmp), 'Help', self.OnHelp)

        self.toolBar.Realize()

        self.updateBrowserBtns()

        if accLst:
            self.SetAcceleratorTable(wxAcceleratorTable(accLst))
##            if not activeView:
##                self.SetAcceleratorTable(wxAcceleratorTable(accLst))
##            else:
##                activeView.SetAcceleratorTable(wxAcceleratorTable(accLst))

    def updateBrowserBtns(self):
        self.toolBar.EnableTool(self.bbId, self.browser.canBack())
        self.toolBar.EnableTool(self.bfId, self.browser.canForward())

    def addShellPage(self):
        """ Adds the interactive interpreter to the editor """
        if wxPlatform == '__WXGTK__':
            # A panel between the STC and notebook reduces flicker
            tabPage, shellEdit = \
                  Utils.wxProxyPanel(self.tabs, ShellEditor.ShellEditor, -1)
        else:
            shellEdit = tabPage = ShellEditor.ShellEditor(self.tabs, -1)

        self.tabs.AddPage(tabPage, 'Shell')

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

    def editorUpdateNotify(self):
        self.explorer.editorUpdateNotify()
    
    def addModulePage(self, model, moduleName, defViews, views, imgIdx):
        spIdx = self.tabs.GetPageCount()
        modulePage = ModulePage(self.tabs, model, defViews, views, spIdx, self)
        self.modules[moduleName] = modulePage
        # Idx will be same as count after selection
        if wxPlatform == '__WXMSW__':
            self.tabs.AddPage(modulePage.notebook, modulePage.pageName, true, imgIdx)
        elif wxPlatform == '__WXGTK__':
            self.tabs.AddPage(modulePage.notebook, modulePage.pageName)
        ## wxYield()

        self.tabs.SetSelection(spIdx)
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
        if actMod and actMod.model.modelIdentifier in ('App', 'PyApp') \
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
            if modPage.model.modelIdentifier in ('App', 'PyApp'):
                apps.append(modPage.model)
        return apps

    def openOrGotoModule(self, name, app=None, transport=None):
        """ Main entrypoint to open a file in the editor.
        
        Defaults to 'file' if no protocol given.
        Optionally handles <filename>::<lineno> format to start on a given line
        Case insensitively find model if already open.
        """
        
        app = None
        
        if string.find(name, '://') == -1:
            name = 'file://'+name
        
        lineno = string.find(name, '::')
        if lineno != -1:
            try: name, lineno = name[:lineno], int(name[lineno+2:]) -1
            except: lineno = -1
        
        controller = None
        if self.modules.has_key(name):
            self.modules[name].focus()
            model = self.modules[name].model
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
            else:
                model, controller = self.openModule(name, app, transport)
        
        if lineno != -1 and model.views.has_key('Source'):
            model.views['Source'].GotoLine(lineno)

        if controller is None:
            controller = self.getController(Controllers.modelControllerReg.get(
                  model.__class__, Controllers.ModuleController))

        return model, controller
            
    def openModule(self, filename, app=None, transport=None):
        """ Open a Model in the IDE.
        
        Filename must be a valid URI.
        """
        # Get transport based on filename
        prot, category, respath, filename = Explorer.splitURI(filename)
        
        if prot == 'zope':
            return self.openZopeDocument(transport, filename)
        else:
# XXX commented for testing
##        elif not transport:
            transport = Explorer.getTransport(prot, category, respath, 
                self.explorer.tree.transports)
            # connect if not a stateless connection
            if transport.connection:
                wxBeginBusyCursor()
                try: transport.openList()
                finally: wxEndBusyCursor()

        assert transport, 'No transport defined'

        wxBeginBusyCursor()
        try: source = transport.load('r')
        finally: wxEndBusyCursor()

        # Get Model based on the file type
        modCls, main = EditorModels.identifyFile(filename, source)#, prot == 'file')

        # See if file is entry in an open app
        if app is None:
            for openApp in self.getAppModules():
                normedMods = []
                for pth in openApp.absModulesPaths():
                    normedMods.append(os.path.normcase(pth))
                if os.path.normcase(filename) in normedMods:
                    app = openApp
                    break
        
        # Get MVC objects
        controller = self.getController(Controllers.modelControllerReg.get(
              modCls, Controllers.ModuleController))
        model = controller.createModel(source, filename, main, true, app)
        defViews = controller.DefaultViews
        views = controller.AdditionalViews

        model.transport = transport
        
        # Add in IDE or display
        if controller.docked:
            self.addModulePage(model, filename, defViews, views, model.imgIdx)
        else:
            controller.display(model)

        model.notify()

##        if wxPlatform != '__WXGTK__':
##            self.updateTitle()

        return model, controller

    # XXX Unify with the rest of the explorers
    def openOrGotoZopeDocument(self, zopeObj):
        wholename=zopeObj.getURI()
        if self.modules.has_key(wholename):
            self.modules[wholename].focus()
            controller = self.getController(
                  Controllers.modelControllerReg[zopeObj.Model], zopeObj.Model)
            return self.modules[wholename].model, controller
        else:
            return self.openZopeDocument(zopeObj, wholename)

    # XXX Unify with the rest of the explorers
    def openZopeDocument(self, zopeObj, wholename):
        if zopeObj.Model:

            controller = self.getController(
                  Controllers.modelControllerReg[zopeObj.Model], zopeObj.Model)
            
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

    def openFileDlg(self):
        dlg = wxFileDialog(self, 'Choose a file', '.', '', 'Modules (*.py)|*.py|Text files (*.txt)|*.txt', wxOPEN)
        try:
            if dlg.ShowModal() == wxID_OK:
                return dlg.GetPath()
        finally:
            dlg.Destroy()
        return ''

    def saveAsDlg(self, filename, filter = '*.py'):
        dir, name = os.path.split(filename)
        if not dir:
            dir = Preferences.pyPath
        if dir[-1] == ':':
            dir = dir[:-1]
            
        dlg = wxFileDialog(self, 'Save as...', dir, name, filter,
          wxSAVE | wxOVERWRITE_PROMPT)

        try:
            if dlg.ShowModal() == wxID_OK:
                return dlg.GetPath(), true
            else:
                return '', false
        finally:
            dlg.Destroy()

    def closeModule(self, modulePage):
        # XXX most of this should move to ModulePage
        idx = modulePage.tIdx
        name = modulePage.model.filename
        if self.modules.has_key(name):
            if modulePage.model.views.has_key('Designer'):
                modulePage.model.views['Designer'].close()
            modulePage.model.refreshFromViews()
            if modulePage.model.modified:
                vis = self.tabs.IsShown()
                if not vis:
                    self.tabs.Show(true)

                dlg = wxMessageDialog(self, 'There are changes, do you want to save?',
                        'Close module', wxYES_NO | wxCANCEL |wxICON_QUESTION)
                try: res = dlg.ShowModal()
                finally: dlg.Destroy()
                if res == wxID_YES:
                    self.activeModSaveOrSaveAs()
                    name = modulePage.model.filename
                elif res == wxID_CANCEL:
                    raise 'Cancelled'

                if not vis:
                    self.tabs.Show(false)

            self.tabs.RemovePage(idx)
            del self.modules[name]
            modulePage.destroy()
            # notify pages for idx adjustments
            for modPge in self.modules.values():
                modPge.removedPage(idx)

        else: 
            print name, 'not found in OnClose', pprint.pprint(self.modules)

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
                pIdx = self.tabs.GetSelection()
            self.SetTitle('Editor - %s' % self.tabs.GetPageText(pageIdx))

    def updateModulePage(self, model, filename = ''):
        if filename:
            modPge = self.modules[filename]
        else:
            modPge = self.modules[model.filename]
        self.tabs.SetPageText(modPge.tIdx, modPge.updatePageName())

    def clearAllStepPoints(self):
        for mod in self.modules.values():
            if mod.model.views.has_key('Source'):
                mod.model.views['Source'].setStepPos(0)
    
    def setStatus(self, hint, msgType='Info', ringBell=false):
        self.statusBar.setHint(hint, msgType, ringBell)

    def OnOpen(self, event):
        fn = self.openFileDlg()
        if fn: self.openOrGotoModule(fn)

    def activeModSaveOrSaveAs(self, forceSaveAs=false):
        modulePage = self.getActiveModulePage()
        if modulePage:
            modulePage.model.refreshFromViews()
            modulePage.saveOrSaveAs(forceSaveAs)

    def OnTabsNotebookPageChanged(self, event):
        sel = event.GetSelection()
        if sel > -1:
            self.updateTitle(sel)
            if self._created: self.setupToolBar(sel)
        event.Skip()

    def OnCloseWindow(self, event):
        if not self.palette.destroying and not self.palette.IsShown(): 
            self.palette.Close()
            return
            
        if self.palette.destroying:
            if self.debugger:
                if Preferences.useDebugger == 'old' and self.debugger.interacting \
                  or Preferences.useDebugger == 'new' and self.debugger.running:
                    wxLogError('Please close the application running in the'
                    ' debugger before continuing.')
                    self.palette.destroying = false
                    return
                else:
                    self.debugger.Close()

            self.persistEditorState()

            self.tabs.Show(false)
            # hack to avoid core dump, first setting the notebook to anything but
            # the last page before setting it to the last page allows us to close
            # this window from the palette. Weird?
            self.tabs.SetSelection(0)
            pgeCnt = self.tabs.GetPageCount()
            self.tabs.SetSelection(pgeCnt -1)
            for p in range(pgeCnt):
                try:
                    self.closeModulePage(self.getActiveModulePage(), true)
                except 'Cancelled':
                    self.tabs.Show(true)
                    self.palette.destroying = false
                    return
                except TransportSaveError, error:
                    self.tabs.Show(true)
                    self.palette.destroying = false
                    wxLogError(str(error))
                    return

            # stop accepting files over socket
            self.closed.set()
            
            self.finder.saveOptions()

            self.palette.editor = None
            self.inspector = None
            self.explorer.destroy()
            self.newMenu.Destroy()
            self.blankEditMenu.Destroy()
            self.blankViewMenu.Destroy()

            self.erroutFrm.Destroy()
            self.erroutFrm = None

            self.shell.destroy()

            self.modelImageList = None
            import FileDlg
            FileDlg.wxBoaFileDialog.modImages = None
            
            self.Destroy()
            event.Skip()
        else:
            self.Show(false)

    def OnHelp(self, event):
        Help.showHelp('Editor.html')

    def OnHelpGuide(self, event):
        Help.showMainHelp('Boa Constructor Getting Started Guide')

    def OnHelpTips(self, event):
        Utils.showTip(self, true)

    def OnToggleView(self, event):
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
                            view.deleteFromNotebook(mod.default, viewName)

                            self.mainMenu.Check(evtId, false)
                            return
                        else:
                            print 'Remove: View already exists'
                    break
            else:
                print 'Menu Id not found'

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

    def OnSwitchedToView(self, event):
        # This is triggered twice, I'd love to know why
        event.Skip()

    def OnHelpAbout(self, event):
        abt = About.AboutBox(None)
        try:     abt.ShowModal()
        finally: abt.Destroy()

    def OnGotoModulePage(self, event):
        wId = event.GetId()
        for mod in self.modules.values():
            if mod.windowId == wId:
                self.tabs.SetSelection(mod.tIdx)

    def OnSwitchShell(self, event):
        self.tabs.SetSelection(0)

    def OnSwitchExplorer(self, event):
        if self.tabs.GetSelection() == 1:
            tree = self.explorer.tree
            cookie = 0
            child, cookie = tree.GetFirstChild(tree.GetRootItem(), cookie)
##            while child.IsOk() and tree.GetItemText(child) != 'Editor':
##                child, cookie = tree.GetNextChild(node, cookie)
            tree.SelectItem(child)
        else:
            self.tabs.SetSelection(1)

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
            page = Browse.BrowsePage(modulePage, activeView.viewName, marker)
            self.browser.add(page)
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
            files = eval(conf.get('editor', 'openfiles'))
            for file in files:
                try:
                    print 'Opening in Editor: %s' % string.split(
                          os.path.basename(file), '::')[0]
                    self.openOrGotoModule(file)

                except Exception, error:
                    # Swallow exceptions
                    wxLogError(str(error))

            try: self.tabs.SetSelection(conf.getint('editor', 'activepage'))
            except: pass


    def persistEditorState(self, ):
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

            try:
                conf = Utils.createAndReadConfig('Explorer')
                conf.set('editor', 'openfiles', pprint.pformat(mods))
                conf.set('editor', 'activepage', self.tabs.GetSelection())
                conf.write(open(conf.confFile, 'w'))
            except Exception, error:
                wxLogError('Could not save open file list: '+str(error))

    def OnExecFinish(self, event):
        event.runner.init(self.erroutFrm, event.runner.app)
        errs = event.runner.recheck()
        if errs:
            self.statusBar.setHint('Finished execution, there were errors', 'Warning')
        else:
            self.statusBar.setHint('Finished execution.')
        self.palette.restore()
        self.restore()

    def OnHelpFindIndex(self, event):
        dlg = wxTextEntryDialog(self, 'Enter term to search for in the index', 
              'Help - Find in index', '')
        try:
            if dlg.ShowModal() == wxID_OK:
                Help.showContextHelp(None, None, dlg.GetValue())
        finally:
            dlg.Destroy()

    def OnExitBoa(self, event):
        self.palette.Close()

    def OnMenuHighlight(self, event):
        item = self.mainMenu.FindItemById(event.GetMenuId())
        if item:
            self.statusBar.setHint(item.GetHelp())

    # svr
    def poll_for_open(self, event=None):
        opened = 0
        while 1:
            try:
                name = self.open_queue.get(0)
                self.openOrGotoModule(name)
                opened = 1
            except Queue.Empty:
                break
        if opened:
            self.palette.restore()

class Listener(threading.Thread):
    def __init__(self, queue, closed):
        self.queue = queue
        self.closed = closed
        threading.Thread.__init__(self)
        
    def run(self, host='127.0.0.1', port=50007):
        import socket 
        from select import select
        # Open a socket and listen.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((host, port))
        except socket.error, err:
            # printing from thread not useful because it's async
            ##if err[0] == 10048: # Address already in use
            ##    print 'Already a Boa running as a server'
            ##else:
            ##    print 'Server mode not started:', err
            self.closed.set() 
            return 
        s.listen(5)
        while 1:
            while 1:
                # Listen for 0.5 s, then check if closed is set. In that case,
                # end thread by returning.
                ready, dummy, dummy = select([s],[],[], 0.5)
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
            self.queue.put(name)
            conn.close()

