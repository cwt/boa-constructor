#----------------------------------------------------------------------
# Name:        Editor.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
#Boa:Frame:EditorFrame

# The focus of change
# the center of creation
# Alchemy

from os import path
import sys, string, time

from wxPython.wx import *
from wxPython.stc import *

import Preferences, About, Help
import Utils, Browse

print 'importing Views.EditorViews'
from Views.EditorViews import *
print 'importing Views.AppViews'
from Views.AppViews import AppView, AppFindResults, AppModuleDocView, AppTimeTrackView
from Views.AppViews import AppREADME_TIFView, AppTODO_TIFView, AppBUGS_TIFView, AppCHANGES_TIFView
print 'importing Views.DesignerViews'
from Views.Designer import DesignerView
from Views.DataView import DataView
print 'importing Views.UMLViews'
from Views.OGLViews import UMLView, ImportsView
print 'importing Views.SourceViews'
from Views.PySourceView import PythonSourceView
from Views.SourceViews import HTMLSourceView, XMLSourceView, TextView, CPPSourceView, HPPSourceView, PythonDisView
print 'importing ZopeViews'
from Views.ZopeViews import ZopeHTMLView, ZopeUndoView, ZopeSecurityView
print 'importing Explorers'
from Explorers.CVSExplorer import CVSConflictsView
from Explorers import Explorer
from ZopeLib import ImageViewer

print 'importing Models'
from EditorModels import *
from PrefsKeys import keyDefs
import ShellEditor, PaletteStore, ErrorStack
from Preferences import IS, wxFileDialog, flatTools
from EditorHelper import *
from ModRunner import EVT_EXEC_FINISH

from EditorUtils import EditorToolBar, EditorStatusBar

# Models available on the 'New' palette page
PaletteStore.paletteLists['New'].extend(['wxApp', 'wxFrame', 'wxDialog',
    'wxMiniFrame', 'wxMDIParentFrame', 'wxMDIChildFrame', 'Module', 'Package',
    'Setup', 'Text'])

if Utils.IsComEnabled():
    PaletteStore.paletteLists['New'].append('MakePy Dialog')

# Views associated with a model, default views and additional views
defAppModelViews = (AppView, PythonSourceView)
adtAppModelViews = (AppModuleDocView, ToDoView, ImportsView, CVSConflictsView,
                    AppTimeTrackView, AppREADME_TIFView, AppCHANGES_TIFView,
                    AppTODO_TIFView, AppBUGS_TIFView)

defModModelViews = (PythonSourceView, ExploreView)
adtModModelViews = (HierarchyView, ModuleDocView, ToDoView, UMLView,
                    CVSConflictsView, PythonDisView)

defBaseFrameModelViews = (PythonSourceView, ExploreView)
adtBaseFrameModelViews = (HierarchyView, ModuleDocView, ToDoView, UMLView,
                          CVSConflictsView, PythonDisView)

defPackageModelViews = (PackageView, PythonSourceView)
adtPackageModelViews = (CVSConflictsView,)

defTextModelViews = (TextView,)
adtTextModelViews = ()

defHTMLFileModelViews = (HTMLSourceView,)
adtHTMLFileModelViews = (HTMLFileView,)

defXMLFileModelViews = (XMLSourceView,)
try:
    from Views.XMLView import XMLTreeView
    adtXMLFileModelViews = (XMLTreeView,)
except ImportError:
    adtXMLFileModelViews = ()

defZopeDocModelViews = (HTMLSourceView,)
adtZopeDocModelViews = (ZopeHTMLView,)

defCPPModelViews = (CPPSourceView, HPPSourceView)
adtCPPModelViews = (CVSConflictsView,)

defSetupModelViews = (PythonSourceView, )
adtSetupModelViews = ()

(mmFile, mmEdit, mmViews, mmWindows, mmHelp) = range(5)

[wxID_EDITORFRAME, wxID_PAGECHANGED,
] = map(lambda _init_ctrls: wxNewId(), range(2))

class EditorFrame(wxFrame):
    """ Source code editor and Mode/View controller"""

    openBmp = 'Images/Editor/Open.bmp'
    backBmp = 'Images/Shared/Previous.bmp'
    forwBmp = 'Images/Shared/Next.bmp'
    helpBmp = 'Images/Shared/Help.bmp'

    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxFrame.__init__(self, size = (-1, -1), id = wxID_EDITORFRAME, title = 'Editor', parent = prnt, name = '', style = wxDEFAULT_FRAME_STYLE | wxCLIP_CHILDREN, pos = (-1, -1))

    def __init__(self, parent, id, inspector, newMenu, componentPalette, app):
        self._init_ctrls(parent)
        self._init_utils()
        self.SetDimensions(Preferences.inspWidth + Preferences.windowManagerSide*2,
              Preferences.paletteHeight + Preferences.windowManagerTop + \
              Preferences.windowManagerBottom, Preferences.edWidth,
              Preferences.bottomHeight)
        EVT_CLOSE(self, self.OnCloseWindow)

        if wxPlatform == '__WXMSW__':
            self.SetIcon(IS.load('Images/Icons/Editor.ico'))

        self.app = app
        self.palette = parent
        self.modules = {}
        self.inspector = inspector
        self.compPalette = componentPalette
        self.debugger = None
        self.browser = Browse.Browser()

        self.statusBar = EditorStatusBar(self)
        self.SetStatusBar(self.statusBar)

        # 16 (FxdWdth), 32 (lft), 64 (rght), 128 (btm)
        self.tabs = wxNotebook(self, wxID_PAGECHANGED, style = wxCLIP_CHILDREN)#, style = wxTC_MULTILINE)
        EVT_NOTEBOOK_PAGE_CHANGED(self.tabs, wxID_PAGECHANGED, self.OnPageChange)

        self.modelImageList = wxImageList(16, 16)

        # System images
        self.modelImageList.Add(IS.load('Images/Modules/Folder_s.bmp'))
        self.modelImageList.Add(IS.load('Images/Modules/Folder_green_s.bmp'))
        self.modelImageList.Add(IS.load('Images/Modules/Folder_cyan_s.bmp'))
        self.modelImageList.Add(IS.load('Images/Zope/System_obj.bmp'))
        self.modelImageList.Add(IS.load('Images/Zope/Zope_connection.bmp'))
        self.modelImageList.Add(IS.load('Images/Shared/BoaLogo.bmp'))
        self.modelImageList.Add(IS.load('Images/Modules/FolderUp_s.bmp'))
        self.modelImageList.Add(IS.load('Images/Modules/Drive_s.bmp'))
        self.modelImageList.Add(IS.load('Images/Modules/FolderBookmark_s.bmp'))

        # Build imagelist of all models
        print 'Editor (loading images)'
        orderedModList = []
        for mod in modelReg.values(): orderedModList.append((mod.imgIdx, mod))
        orderedModList.sort()
        for mod in orderedModList:
            self.modelImageList.Add(IS.load('Images/Modules/'+mod[1].bitmap))

        # Add Zoa Images
        import ZopeEditorModels
        for metatype, filename in ZopeEditorModels.ZOAImages:
            ZopeEditorModels.ZOAIcons[metatype] = \
                  self.modelImageList.Add(IS.load(filename))

        if wxPlatform == '__WXMSW__':
            self.tabs.SetImageList(self.modelImageList)

        # Shell
        self.shell = self.addShellPage()

        # Explorer
        self.explorer = Explorer.ExplorerSplitter (self.tabs,
          self.modelImageList, '', self)
        self.tabs.AddPage(self.explorer, 'Explorer')
        self.tabs.SetSelection(1)
        
        from Explorers import EditorExplorer
        root = self.explorer.tree.boaRoot
        root.entries.insert(0, EditorExplorer.OpenModelsNode(self, root))
        
        self.explorer.tree.openDefaultNodes()

        # Menus
        self.newMenu = newMenu

        self.blankEditMenu = wxMenu()
        self.blankViewMenu = wxMenu()
        self.helpMenu = wxMenu()
        self.helpMenu.Append(wxID_EDITORHELP, 'Help')
        self.helpMenu.Append(wxID_EDITORHELPGUIDE, 'Getting started guide')
        self.helpMenu.Append(wxID_EDITORHELPTIPS, 'Tips')
        self.helpMenu.AppendSeparator()
        self.helpMenu.Append(wxID_EDITORHELPABOUT, 'About')

        EVT_MENU(self, wxID_EDITORHELP, self.OnHelp)
        EVT_MENU(self, wxID_EDITORHELPABOUT, self.OnHelpAbout)
        EVT_MENU(self, wxID_EDITORHELPGUIDE, self.OnHelpGuide)
        EVT_MENU(self, wxID_EDITORHELPTIPS, self.OnHelpTips)

        EVT_MENU(self, wxID_EDITOROPEN, self.OnOpen)

        # XXX These methods and events should be refactored into controllers
        # XXX that can link to certain models

        EVT_MENU(self, wxID_EDITORSAVE, self.OnSave)
        EVT_MENU(self, wxID_EDITORSAVEAS, self.OnSaveAs)
        EVT_MENU(self, wxID_EDITORCLOSEPAGE, self.OnClosePage)
        EVT_MENU(self, wxID_EDITORRELOAD, self.OnReload)

        EVT_MENU(self, wxID_EDITORREFRESH, self.OnRefresh)
        EVT_MENU(self, wxID_EDITORDESIGNER, self.OnDesigner)
        EVT_MENU(self, wxID_EDITORDEBUG, self.OnDebug)

        EVT_MENU(self, wxID_EDITORSWITCHAPP, self.OnSwitchApp)
        EVT_MENU(self, wxID_EDITORSWITCHSHELL, self.OnSwitchShell)
        EVT_MENU(self, wxID_EDITORSWITCHEXPLORER, self.OnSwitchExplorer)
        EVT_MENU(self, wxID_EDITORSWITCHPALETTE, self.OnSwitchPalette)
        EVT_MENU(self, wxID_EDITORSWITCHINSPECTOR, self.OnSwitchInspector)

        EVT_MENU(self, wxID_EDITORDIFF, self.OnDiff)
        EVT_MENU(self, wxID_EDITORCMPAPPS, self.OnCmpApps)
        EVT_MENU(self, wxID_EDITORPYCHECK, self.OnPyChecker)
        EVT_MENU(self, wxID_EDITORCONFPYCHECK, self.OnConfPyChecker)

        EVT_MENU(self, wxID_EDITORPREVPAGE, self.OnPrevPage)
        EVT_MENU(self, wxID_EDITORNEXTPAGE, self.OnNextPage)

        EVT_MENU(self, wxID_SETUPBUILD, self.OnSetupBuild)
        EVT_MENU(self, wxID_SETUPCLEAN, self.OnSetupClean)
        EVT_MENU(self, wxID_SETUPINSTALL, self.OnSetupInstall)
        EVT_MENU(self, wxID_SETUPSDIST, self.OnSetupSDist)
        EVT_MENU(self, wxID_SETUPBDIST, self.OnSetupBDist)
        EVT_MENU(self, wxID_SETUPBDIST_WININST, self.OnSetupBDist_WinInst)
        EVT_MENU(self, wxID_SETUPPY2EXE, self.OnSetupPy2Exe)

        self.mainMenu = wxMenuBar()
        self.SetMenuBar(self.mainMenu)
        self.mainMenu.Append(wxMenu(), 'File')
#        self.mainMenu.Append(self.blankEditMenu, 'Edit')
        self.mainMenu.Append(wxMenu(), 'Edit')

        # Views menu
        self.viewDefaultIds = {}
        self.viewDefaults = wxMenu()
        self.viewDefaults.AppendMenu(wxNewId(), AppModel.modelIdentifier,
          self.defsMenu(AppModel, adtAppModelViews))
        self.viewDefaults.AppendMenu(wxNewId(), BaseFrameModel.modelIdentifier,
          self.defsMenu(BaseFrameModel, adtBaseFrameModelViews))
        self.viewDefaults.AppendMenu(wxNewId(), ModuleModel.modelIdentifier,
          self.defsMenu(ModuleModel, adtModModelViews))
        self.viewDefaults.AppendMenu(wxNewId(), PackageModel.modelIdentifier,
          self.defsMenu(PackageModel, adtPackageModelViews))
        self.viewDefaults.AppendMenu(wxNewId(), TextModel.modelIdentifier,
          self.defsMenu(TextModel, adtTextModelViews))

        self.blankViewMenu.AppendMenu(wxID_DEFAULTVIEWS, 'Defaults', self.viewDefaults)

        self.mainMenu.Append(wxMenu(), 'Views')
#        self.mainMenu.Append(self.blankViewMenu, 'Views')

        # Windows menu
        self.winMenu = wxMenu()
        self.winMenu.Append(wxID_EDITORSWITCHPALETTE, 'Palette')
        self.winMenu.Append(wxID_EDITORSWITCHINSPECTOR, 'Inspector')
        self.winMenu.Append(-1, '-')
        self.winMenu.Append(wxID_EDITORSWITCHSHELL, 'Shell')
        self.winMenu.Append(wxID_EDITORSWITCHEXPLORER, 'Explorer')
        self.winMenu.Append(-1, '-')
        self.mainMenu.Append(self.winMenu, 'Windows')

        self.mainMenu.Append(self.helpMenu, 'Help')

        self.defaultAdtViews = {}
##        {AppModel: [], BaseFrameModel: [],
##                                ModuleModel: [], PackageModel: [], TextModel: [],
##                                ZopeDocumentModel: [], CPPModel: [],
##                                HTMLFileModel: []}

        # Toolbar
        self.toolBar = EditorToolBar(self, -1)#, style = wxTB_HORIZONTAL|wxNO_BORDER|wxTB_FLAT)#|wxTB_FLAT
        self.SetToolBar(self.toolBar)
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

        import ErrorStackFrm
        self.erroutFrm = ErrorStackFrm.ErrorStackMF(self, self)

        # Hack to feed BoaFileDialog images
        import FileDlg
        FileDlg.wxBoaFileDialog.modImages = self.modelImageList

        EVT_EXEC_FINISH(self, self.OnExecFinish)

        self.restoreEditorState()
    
    def __repr__(self):
        return '<EditorFrame instance at %d>'%id(self)

    def defsMenu(self, model, viewClss):
        """ Default menus specifying which views are opened by default when a
            certain type of model is opened.
        """

        menu = wxMenu()
        for view in viewClss:
            wId = wxNewId()
            self.viewDefaultIds[wId] = view, model
            menu.Append(wId, view.viewName, checkable = true)
            menu.Check(wId, false)
            EVT_MENU(self, wId, self.OnDefaultsToggle)
        return menu

    def setupToolBar(self, modelIdx = None, viewIdx = None):
        if not hasattr(self, 'toolBar') or self.palette.destroying:
            return

        self.toolBar.ClearTools()

        accLst = []
        for (ctrlKey, key, code), wId in \
                ( (keyDefs['Inspector'], wxID_EDITORSWITCHINSPECTOR),
                  (keyDefs['Open'], wxID_EDITOROPEN),
                  (keyDefs['PrevPage'], wxID_EDITORPREVPAGE),
                  (keyDefs['NextPage'], wxID_EDITORNEXTPAGE) ):
            accLst.append( (ctrlKey, key, wId) )

        # primary option: open a module
        fileMenu = wxMenu()
        fileMenu.Append(wxID_EDITOROPEN, 'Open', 'Open a module')

        Utils.AddToolButtonBmpObject(self, self.toolBar, IS.load(self.openBmp), 'Open a module', self.OnOpen)
        self.bbId = Utils.AddToolButtonBmpObject(self, self.toolBar, IS.load(self.backBmp), 'Browse back', self.OnBrowseBack)
        self.bfId = Utils.AddToolButtonBmpObject(self, self.toolBar, IS.load(self.forwBmp), 'Browse forward', self.OnBrowseForward)
        actMod = self.getActiveModulePage(modelIdx)
        if actMod:
            activeView = actMod.getActiveView(viewIdx)
            if activeView:
                # File menu
                actMod.model.addTools(self.toolBar)
                accls = actMod.model.addMenus(fileMenu)
                accLst.extend(accls)
                self.mainMenu.Replace(mmFile, fileMenu, 'File').Destroy()
                # Edit menu
                self.toolBar.AddSeparator()
                activeView = actMod.getActiveView(viewIdx)
                activeView.addViewTools(self.toolBar)
                menu, accls = activeView.editorMenu, activeView.accelLst
                menu = Utils.duplicateMenu(menu)
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
#                self.mainMenu.Replace(mmViews, actMod.viewMenu, 'Views')
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
            self.mainMenu.Replace(mmFile, fileMenu, 'File').Destroy()
#            self.mainMenu.Replace(mmEdit, self.blankEditMenu, 'Edit')

##            m = self.mainMenu.GetMenu(mmViews)
##            if m.GetMenuItemCount() > 0:
##                m.RemoveItem(m.FindItemById(wxID_DEFAULTVIEWS))

            self.mainMenu.Replace(mmViews, Utils.duplicateMenu(self.blankViewMenu), 'Views').Destroy()

        # Help button
        self.toolBar.AddSeparator()
        Utils.AddToolButtonBmpObject(self, self.toolBar, IS.load(self.helpBmp), 'Help', self.OnHelp)

        self.toolBar.Realize()

        self.updateBrowserBtns()

        if accLst: self.SetAcceleratorTable(wxAcceleratorTable(accLst))
#        print 'end setup toolbar',

    def updateBrowserBtns(self):
        self.toolBar.EnableTool(self.bbId, self.browser.canBack())
        self.toolBar.EnableTool(self.bfId, self.browser.canForward())

    def addShellPage(self):
        """ Adds the interactive interpreter to the editor """
        if wxPlatform == '__WXGTK__':
            # A panel between the STC and notebook reduces flicker
            shellEdit, dummy = Utils.wxProxyPanel(self.tabs, ShellEditor.ShellEditor, -1)

##            panel = wxPanel(self.tabs, -1, style=wxTAB_TRAVERSAL | wxCLIP_CHILDREN)
##            shellEdit = ShellEditor.ShellEditor(panel, -1)
##            def OnWinSize(evt, win=shellEdit):
##                win.SetSize(evt.GetSize())
##            EVT_SIZE(panel, OnWinSize)
##            self.tabs.AddPage(panel, 'Shell')
        else:
            shellEdit = ShellEditor.ShellEditor(self.tabs, -1)

        self.tabs.AddPage(shellEdit, 'Shell')

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
          path.basename(key) == name, self.modules.keys() + moreUsedNames):
            n = n + 1

        return tryName(modelClass, n)

    def newFileTransport(self, name, filename):
        from Explorers.FileExplorer import PyFileNode
        return PyFileNode(name, filename, None, -1, None, None,
              properties = {})

    def addModulePage(self, model, moduleName, defViews, views, imgIdx):
        spIdx = self.tabs.GetPageCount()
        modulePage = ModulePage(self.tabs, model, defViews, views, spIdx, self)
        self.modules[moduleName] = modulePage
        # Idx will be same as count after selection
        if wxPlatform == '__WXMSW__':
            self.tabs.AddPage(modulePage.notebook, modulePage.pageName, true, imgIdx)
        elif wxPlatform == '__WXGTK__':
            self.tabs.AddPage(modulePage.notebook, modulePage.pageName)
#        wxYield()

        self.tabs.SetSelection(spIdx)
        modulePage.refresh()

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
        if actMod and actMod.model.__class__ == AppModel and actMod.model.data <> '':
            return actMod
        else:
            return None

    def addNewTextPage(self):
        name = self.getValidName(TextModel)
        model = TextModel('', name, self, false)
        model.transport = self.newFileTransport('', name)
        self.addModulePage(model, name, defTextModelViews, adtTextModelViews,
          TextModel.imgIdx)
        model.new()

        self.updateTitle()

    def addNewSetupPage(self):
        name = 'setup.py'
        model = SetupModuleModel(defSetup_py, name, self, false)
        model.transport = self.newFileTransport('', name)
        self.addModulePage(model, name, defSetupModelViews, adtSetupModelViews,
          SetupModuleModel.imgIdx)
        model.new()

        self.updateTitle()

    def addNewPage(self, metatype):
        
        # Choose controller
        
        # Create controller
        
        # Create model
        
        # Add ModulePage
        self.addModulePage(model, name, defViews, adtViews, imgIdx)
        
        # Update title
        self.updateTitle()
        
##        name = 'setup.py'
##        model = SetupModuleModel(defSetup_py, name, self, false)
##        model.transport = self.newFileTransport('', name)
##        self.addModulePage(model, name, defSetupModelViews, adtSetupModelViews,
##          SetupModuleModel.imgIdx)
##        model.new()


    def addNewPackage(self):
        filename, success = self.saveAsDlg('__init__.py')
        if success:
            model = PackageModel('# Package initialisation', filename, self, false)
            model.transport = self.newFileTransport('', filename)
            self.addModulePage(model, model.packageName, defPackageModelViews,
              adtPackageModelViews, PackageModel.imgIdx)
            model.save()
            model.notify()

            self.updateTitle()

    def addNewAppPage(self):
        appName = self.getValidName(AppModel)
        appModel = AppModel('', appName, appName[:-3], self, false, self.modules)
        appModel.transport = self.newFileTransport(appName[:-3], appName)

        self.addModulePage(appModel, appName, defAppModelViews, adtAppModelViews,
          AppModel.imgIdx)

        frmMod = self.addNewFramePage('Frame', appModel)
        frmNme = path.splitext(path.basename(frmMod.filename))[0]
        appModel.new(frmNme)

        self.updateTitle()

    def addNewModulePage(self):
        activeApp = self.activeApp()
        if activeApp:
            activeApp = activeApp.model
            name = self.getValidName(ModuleModel, activeApp.absModulesPaths())
        else:
            name = self.getValidName(ModuleModel)

        model = ModuleModel('', name, self, false, activeApp)
        model.transport = self.newFileTransport('', name)
        self.addModulePage(model, name, defModModelViews, adtModModelViews,
          ModuleModel.imgIdx)
        model.new()
        if activeApp and Preferences.autoAddToApplication:
            activeApp.addModule(model.filename, '')

        self.updateTitle()

    def addNewFramePage(self, modId, app = None):
        FrmMod = modelReg[modId]
        if app:
            activeAppMod = app
            name = self.getValidName(FrmMod, app.absModulesPaths())
        else:
            activeAppMod = self.activeApp()
            if activeAppMod:
                activeAppMod = activeAppMod.model
                name = self.getValidName(FrmMod, activeAppMod.absModulesPaths())
            else:
                name = self.getValidName(FrmMod)

        model = FrmMod('', name, name[:-3], self, false, activeAppMod)
        model.transport = self.newFileTransport('', model.filename)

        activeApp = self.activeApp()

        self.addModulePage(model, name, defBaseFrameModelViews,
          adtBaseFrameModelViews, FrmMod.imgIdx)
        tempComp = FrmMod.companion('', None, None)
        params = tempComp.designTimeSource()
        params['parent'] = 'prnt'
        params['id'] = Utils.windowIdentifier(model.main, '')
        params['title'] = `model.main`

        model.new(params)
        if activeApp and Preferences.autoAddToApplication:
            activeApp.model.addModule(model.filename, '')

        self.updateTitle()

        return model

    def addNewDialog(self, dlgClass, dlgCompanion):
        module = self.getActiveModulePage()
        if module:
            view = module.getActiveView()
            if view and view.viewName == 'Source':
                compn = dlgCompanion('dlg', None)
                view.insertCodeBlock(compn.body())

    def getAppModules(self):
        """ Return a list of all open Application modules """
        apps = []
        for modPage in self.modules.values():
            if modPage.model.modelIdentifier == 'App':
                apps.append(modPage.model)
        return apps

    def openOrGotoModule(self, name, app=None, transport=None):
        if self.modules.has_key(name):
            self.modules[name].focus()
            return self.modules[name].model
        else:
            # Check non case sensitive (fix for breakpoints)
            lst = self.modules.keys()
            assos = {}
            for keyIdx in range(len(lst)):
                assos[path.normcase(path.abspath(lst[keyIdx]))] = lst[keyIdx]

            if assos.has_key(name):
                self.modules[assos[name]].focus()
                return self.modules[assos[name]].model
            else:
                return self.openModule(name, app, transport)

    def openModule(self, filename, app=None, transport=None):
        name = filename
        dirname, name = path.split(filename)
        name, ext = path.splitext(name)

        if not transport:
            from Explorers.FileExplorer import PyFileNode
            transport = PyFileNode(name, filename, None, -1, None, None,
                  properties = {})

        source = transport.load()
        modCls, main = identifyFile(filename, source, true)

        imgIdx = modCls.imgIdx

        if modCls is PackageModel:
            model = PackageModel(source, filename, self, true)
            defViews = defPackageModelViews
            views = adtPackageModelViews
            name = model.packageName
        elif modCls is AppModel:
            model = AppModel(source, filename, '', self, true, self.modules)
            defViews = defAppModelViews
            views = adtAppModelViews
        elif modCls in (FrameModel, DialogModel, MiniFrameModel,
          MDIParentModel, MDIChildModel):
            model = modCls(source, filename, main, self, true, app)
            defViews = defBaseFrameModelViews
            views = adtBaseFrameModelViews
        elif modCls is TextModel:
            model = TextModel(source, filename, self, true)
            defViews = defTextModelViews
            views = adtTextModelViews
        elif modCls is CPPModel:
            model = CPPModel(source, filename, self, true)
            defViews = defCPPModelViews
            views = adtCPPModelViews
        elif modCls is HTMLFileModel:
            model = HTMLFileModel(source, filename, self, true)
            defViews = defHTMLFileModelViews
            views = adtHTMLFileModelViews
        elif modCls is XMLFileModel:
            model = XMLFileModel(source, filename, self, true)
            defViews = defXMLFileModelViews
            views = adtXMLFileModelViews
        elif modCls is ConfigFileModel:
            model = ConfigFileModel(source, filename, self, true)
            defViews = defTextModelViews
            views = adtTextModelViews
        elif modCls is BitmapFileModel:
            model = BitmapFileModel(source, filename, self, true)
            ImageViewer.create(self).showImage(filename, transport)
            return model
        elif modCls is SetupModuleModel:
            model = SetupModuleModel(source, filename, self, true)
            defViews = defSetupModelViews
            views = adtSetupModelViews
        else:
            model = ModuleModel(source, filename, self, true, app)
            defViews = defModModelViews
            views = adtModModelViews

        model.transport = transport
        self.addModulePage(model, filename, defViews, views, model.imgIdx)

        model.notify()

        if wxPlatform != '__WXGTK__':
#            self.tabs.Refresh()
            self.updateTitle()

        return model

    def openOrGotoZopeDocument(self, zopeObj):
        wholename=zopeObj.whole_name()
        if self.modules.has_key(wholename):
            self.modules[wholename].focus()
            return self.modules[wholename].model
        else:
            return self.openZopeDocument(zopeObj,wholename)

    def openZopeDocument(self, zopeObj, wholename):
        if zopeObj.Model:
            model = zopeObj.Model(wholename, '', self, false, zopeObj) #zopeObj.whole_name(), '', self, false, zopeConn, zopeObj
            model.transport = zopeObj
            model.load()

            self.addModulePage(
                model, wholename, zopeObj.defaultViews,
                zopeObj.additionalViews, zopeObj.Model.imgIdx)
            model.notify()

            self.updateTitle()
            return model
        else:
            wxLogWarning('Zope Object %s not supported' % `zopeObj`)

    def showDesigner(self):
        modulePage = self.getActiveModulePage()
        if modulePage:
            model = modulePage.model

            # Just show if already opened
            if model.views.has_key('Designer'):
                model.views['Data'].focus()
                model.views['Designer'].Show(true)
                model.views['Designer'].Raise()
                return

            dataView = None
            try:
                # update any view modifications
                model.refreshFromViews()
    
                model.initModule()
                model.readComponents()
    
                try:
                    # add or focus data view
                    if not model.views.has_key('Data'):
                        dataView = DataView(modulePage.notebook, self.inspector,
                          model, self.compPalette)
                        dataView.addToNotebook(modulePage.notebook)
                        model.views['Data'] = dataView
                        dataView.initialize()
                    else:
                        dataView = model.views['Data']
                except:
                    if model.views.has_key('Data'):
                        model.views['Data'].focus()
                        model.views['Data'].saveOnClose = false
                        model.views['Data'].deleteFromNotebook('Source', 'Data')
                    raise
        
                dataView.focus()
                #modulePage.notebook.SetSelection(modulePage.notebook.GetPageCount()-1)
                dataView.refreshCtrl()
                
                try:
                    # add or focus frame designer
                    if not model.views.has_key('Designer'):
                        designer = DesignerView(self, self.inspector,
                          model, self.compPalette, model.companion, dataView)
                        model.views['Designer'] = designer
                        designer.refreshCtrl()
                    model.views['Designer'].Show(true)
                except:
                    if model.views.has_key('Designer'):
                        model.views['Designer'].saveOnClose = false
                        model.views['Designer'].close()
                    raise
    
                # Make source read only
                model.views['Source'].disableSource(true)

                self.statusBar.setHint('Designer session started.')

            except Exception, error:
                self.statusBar.setHint(\
                    'An error occured while opening the Designer: %s'%str(error),
                    'Error')
                self.statusBar.progress.SetValue(0)
                raise

    def showImportsView(self):
        self.addNewView('Imports', ImportsView)

    def addNewView(self, name, viewClass):
        module = self.getActiveModulePage()
        if module:
            if not module.model.views.has_key(name):
                return module.addView(viewClass, name)
            else:
                return module.model.views[name]
            module.model.views[name].Show(true)

    def openFileDlg(self):
#        return wxFileSelector('Choose a file', '.', '', 'Modules (*.py)|*.py|Text files (*.txt)|*.txt', '.py', wxOPEN)
        dlg = wxFileDialog(self, 'Choose a file', '.', '', 'Modules (*.py)|*.py|Text files (*.txt)|*.txt', wxOPEN)
        try:
            if dlg.ShowModal() == wxID_OK:
                return dlg.GetPath()
        finally:
            dlg.Destroy()
        return ''

    def saveAsDlg(self, filename, filter = '*.py'):
        dir, name = path.split(filename)
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
        idx = modulePage.tIdx
        name = modulePage.model.filename
        if self.modules.has_key(name):
            if modulePage.model.views.has_key('Designer'):
                modulePage.model.views['Designer'].close()
            modulePage.model.refreshFromViews()
            if modulePage.model.modified:
                vis = self.IsShown()
                if not vis:
                    self.Show(true)

                dlg = wxMessageDialog(self, 'There are changes, do you want to save?',
                        'Close module', wxYES_NO | wxCANCEL |wxICON_QUESTION)
                try: res = dlg.ShowModal()
                finally: dlg.Destroy()
                if res == wxID_YES:
#                if Utils.yesNoDialog(self, 'Close module', 'There are changes, do you want to save?'):
                    self.saveOrSaveAs()
                    name = modulePage.model.filename
                elif res == wxID_CANCEL:
                    raise 'Cancelled'

                if not vis:
                    self.Show(false)

            self.tabs.RemovePage(idx)
            del self.modules[name]
            modulePage.destroy()
            # notify pages for idx adjustments
            for modPge in self.modules.values():
                modPge.removedPage(idx)

        else: print name, 'not found in OnClose', self.modules

    def saveAs(self, filename):
        """ Brings up a save as file dialog with filename as initial name """
        model = self.modules[filename].model

        newFilename, success = self.saveAsDlg(filename)
        if success:
            # XXX Check for renaming and update models
            model.saveAs(newFilename)
            self.updateModulePage(model, filename)
            self.updateTitle()
        return success

    def updateTitle(self, pageIdx = None):
        """ Updates the title of the Editor to reflect changes in selection,
            filename or model state.
        """

        # XXX Do decorations here
        modulePage = self.getActiveModulePage(pageIdx)
        if modulePage:
            self.SetTitle('Editor - %s - %s' %(modulePage.pageName,
              modulePage.model.filename))
        else:
            self.SetTitle('Editor')

    def updateModulePage(self, model, filename = ''):
        if filename:
            modPge = self.modules[filename]
        else:
            modPge = self.modules[model.filename]
        self.tabs.SetPageText(modPge.tIdx, modPge.updatePageName())
#        self.tabs.Refresh()

    def updateStatusRowCol(self, row, col):
        self.statusBar.row.SetLabel(`row`)
        self.statusBar.col.SetLabel(`col`)

    def clearAllStepPoints(self):
        for mod in self.modules.values():
            if mod.model.views.has_key('Source'):
                mod.model.views['Source'].setStepPos(0)

    def OnOpen(self, event):
        fn = self.openFileDlg()
        if fn: self.openOrGotoModule(fn)

    def saveOrSaveAs(self):
        modulePage = self.getActiveModulePage()
        if modulePage:
            modulePage.saveOrSaveAs()

    def OnSave(self, event):
        modulePage = self.getActiveModulePage()
        modulePage.model.refreshFromViews()
        self.saveOrSaveAs()

    def OnSaveAs(self, event):
        modulePage = self.getActiveModulePage()
        if modulePage:
            modulePage.model.refreshFromViews()
            model = modulePage.model
            oldName = model.filename

            if self.saveAs(oldName) and (oldName != model.filename):
                del self.modules[oldName]
                self.modules[model.filename] = modulePage

    def OnReload(self, event):
        modulePage = self.getActiveModulePage()
        if modulePage:
            modulePage.model.load()

    def OnClosePage(self, event):
        # Replace view's edit menu with editor managed blankEditMenu
        # so editor can free it without fear of mainMenu freeing it
#        self.mainMenu.Replace(mmEdit, self.blankEditMenu, 'Edit')

#        self.mainMenu.Replace(mmEdit, wxMenu(), 'Edit').Destroy()
        # XXX This might cause crash !!!!
        modulePage = self.getActiveModulePage()
        actPge = self.tabs.GetSelection()
        numPgs = self.tabs.GetPageCount()
        if modulePage:
            try:
                self.closeModule(modulePage)
            except 'Cancelled':
                if not event:
                    raise
                else:
                    return

            self.mainMenu.Replace(mmEdit, wxMenu(), 'Edit').Destroy()
            if actPge == numPgs - 1:
                self.tabs.SetSelection(numPgs - 2)
            else:
                self.tabs.SetSelection(actPge)


    def OnRefresh(self, event):
        modulePage = self.getActiveModulePage()
        if modulePage and modulePage.model.views.has_key('Source'):
            modulePage.model.views['Source'].refreshModel()
            self.updateModulePage(modulePage.model)
            self.updateTitle()

    def OnPageChange(self, event):
        sel = event.GetSelection()
        if sel > -1:
            self.updateTitle(sel)
            if hasattr(self, 'toolBar'): self.setupToolBar(sel)
        event.Skip()

    def OnDesigner(self, event):
        self.showDesigner()

    def OnDebug(self, event):
        print self.modules

    def OnCloseWindow(self, event):
        self.Show(false)
        if self.palette.destroying:
            self.persistEditorState()

            # hack to avoid core dump, first setting the notebook to anything but
            # the last page before setting it to the last page allows us to close
            # this window from the palette. Weird?
            self.tabs.SetSelection(0)
            pgeCnt = self.tabs.GetPageCount()
            self.tabs.SetSelection(pgeCnt -1)
            for p in range(pgeCnt):
                try:
                    self.OnClosePage(None)
                except 'Cancelled':
                    self.Show(true)
                    self.palette.destroying = false
                    return

            if self.debugger:
                self.debugger.Close()

            self.palette.editor = None
            self.inspector = None
            self.explorer.destroy()
            self.newMenu.Destroy()#
##            self.mainMenu.Replace(1, self.blankEditMenu, 'Edit')
##            self.mainMenu.Replace(2, self.blankViewMenu, 'View')
            self.mainMenu.Replace(1, wxMenu(), 'Edit').Destroy()
            self.mainMenu.Replace(2, wxMenu(), 'View').Destroy()
            self.mainMenu = None

            self.erroutFrm.Destroy()
            self.erroutFrm = None

            self.shell.destroy()

            self.Destroy()
            event.Skip()

    def OnHelp(self, event):
        Help.showHelp(self, Help.BoaHelpFrame, 'Editor.html')

    def OnHelpGuide(self, event):
        Help.showHelp(self, Help.BoaHelpFrame, 'Guide/index.html')

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

    def OnDefaultsToggle(self, event):
        evtId = event.GetId()
        view, model = self.viewDefaultIds[event.GetId()]
        if self.mainMenu.IsChecked(evtId):
            if view not in self.defaultAdtViews.get(model, []):
                self.defaultAdtViews[model].append(view)
        else:
            if view in self.defaultAdtViews.get(model, []):
                self.defaultAdtViews[model].remove(view)


    def OnSwitchedToView(self, event):
        # This is triggered twice, I'd love to know why
        event.Skip()

    def OnSwitchApp(self, event):
        actMod = self.getActiveModulePage()
        if actMod and isinstance(actMod.model, ModuleModel) and actMod.model.app:
            model = self.openOrGotoModule(actMod.model.app.filename)
            model.views['Application'].focus()

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
        self.tabs.SetSelection(1)

    def OnSwitchPalette(self, event):
        self.palette.Show(true)
        self.palette.Raise()

    def OnSwitchInspector(self, event):
        self.inspector.Show(true)
        if self.inspector.IsIconized():
            self.inspector.Iconize(false)
        self.inspector.Raise()

    def OnDiff(self, event):
        actMod = self.getActiveModulePage()
        if actMod:
            fn = self.openFileDlg()
            if fn:
                actMod.model.diff(fn)

    def OnPyChecker(self, event):
        actMod = self.getActiveModulePage()
        if actMod:
            cwd = os.path.abspath(os.getcwd())
            newCwd = os.path.dirname(actMod.model.filename)
            os.chdir(newCwd)
            oldErr = sys.stderr
            oldSysPath = sys.path[:]
            try:
                sys.path.append(Preferences.pyPath)
                cmd = '"%s" "%s" %s'%(sys.executable,
                      os.path.join(Preferences.pyPath, 'ExternalLib',
                      'PyChecker', 'checker_custom.py'),
                      os.path.basename(actMod.model.filename))

                from ModRunner import ProcessModuleRunner
                ProcessModuleRunner(self.erroutFrm, actMod.model.app,
                      newCwd).run(cmd, ErrorStack.PyCheckerErrorParser,
                      'PyChecker', 'Warning', true)
            finally:
                sys.path = oldSysPath
                sys.stderr = oldErr
                os.chdir(cwd)

    def OnConfPyChecker(self, event):
        actMod = self.getActiveModulePage()
        if actMod:
            home = os.environ.get('HOME')
            if home:
                appDir = home
                appConfig = home+'/.pycheckrc'
            else:
                appDir = os.path.dirname(actMod.model.filename)
                appConfig = appDir+'/.pycheckrc'
            if not os.path.exists(appConfig):
                dlg = wxMessageDialog(self, 'The PyChecker configuration file '
                  "can not be found. Copy the default file here?",
                  'Config file not found', wxYES_NO | wxICON_QUESTION)
                try:
                    if dlg.ShowModal() == wxID_YES:
                        import shutil
                        shutil.copyfile(os.path.join(Preferences.pyPath,
                            'ExternalLib', 'PyChecker', 'pycheckrc'), appConfig)
                    else:
                        return
                finally:
                    dlg.Destroy()

            from Explorers.PrefsExplorer import SourceBasedPrefColNode
            SourceBasedPrefColNode('PyChecker', ('*',), appConfig, -1, None).open(self)

    def OnCmpApps(self, event):
        actMod = self.getActiveModulePage()
        if actMod:
            fn = self.openFileDlg()
            if fn:
                actMod.model.compareApp(fn)

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

#---DistUtils-------------------------------------------------------------------
    def runDistUtilsCmd(self, cmd):
        import ProcessProgressDlg
        cwd = path.abspath(os.getcwd())
        modulePage = self.getActiveModulePage()
        os.chdir(path.dirname(modulePage.model.filename))
        try:
            PD = ProcessProgressDlg.ProcessProgressDlg(self,
              'python setup.py %s'%cmd, 'Running distutil command...', autoClose = false)
            try:
                PD.ShowModal()
            finally:
                PD.Destroy()
        finally:
            os.chdir(cwd)

    def OnSetupBuild(self, event):
        self.runDistUtilsCmd('build')
    def OnSetupClean(self, event):
        self.runDistUtilsCmd('clean')
    def OnSetupInstall(self, event):
        self.runDistUtilsCmd('install')
    def OnSetupSDist(self, event):
        self.runDistUtilsCmd('sdist')
    def OnSetupBDist(self, event):
        self.runDistUtilsCmd('bdist')
    def OnSetupBDist_WinInst(self, event):
        self.runDistUtilsCmd('bdist_wininst')

    def OnSetupPy2Exe(self, event):
        self.runDistUtilsCmd('py2exe')

#---State methods---------------------------------------------------------------
    def restoreEditorState(self):
        # Open previously opened files if necessary
        if Preferences.rememberOpenFiles:
            conf = Utils.createAndReadConfig('Explorer')
            files = eval(conf.get('editor', 'openfiles'))
            apps = []
            for file in files:
                try:
                    print 'Opening in Editor: %s' % os.path.basename(file)
                    for app in apps:
                        if app.hasModule(file): break
                    else:
                        app = None
                    model = self.openModule(file, app)
                    if model.modelIdentifier == 'App':
                        apps.append(model)

                except Exception, error:
                    # Swallow exceptions, ignore non FS modules
                    wxLogError(str(error))

    def persistEditorState(self, ):
        # Save list of open files to config if necessary
        if Preferences.rememberOpenFiles:
            modOrder = []
            for mod, modPage in self.modules.items():
                if modPage.model.savedAs:
                    modOrder.append( (modPage.tIdx, mod) )
            modOrder.sort()

            mods = []
            for idx, mod in modOrder:
                mods.append(mod)

            try:
                conf = Utils.createAndReadConfig('Explorer')
                conf.set('editor', 'openfiles', `mods`)
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
        #print 'OnExecFinish', event.runner


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

        cls = model.__class__
#        if not editor.defaultAdtViews.has_key(cls):
#            cls = model.__class__.__bases__[0]

        tot = len(defViews) + len(editor.defaultAdtViews.get(cls, []))
        if tot:
            stepsDone = 50.0
            editor.statusBar.progress.SetValue(int(stepsDone))
            step = (100 - stepsDone) / tot
            for view in defViews:
                self.addView(view)
                stepsDone = stepsDone + step
                editor.statusBar.progress.SetValue(int(stepsDone))

            for view in editor.defaultAdtViews.get(cls, []):
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
        for view, wId in self.defViews + self.adtViews:
            if wId != -1:
                self.model.editor.Disconnect(wId)

        self.editor.winMenu.Delete(self.windowId)
        self.editor.Disconnect(self.windowId)

        self.viewMenu.Destroy()

        for view in self.model.views.values():
            if view:
                view.close()
        self.notebook.DeleteAllPages()

        self.model.destroy()
        self.notebook.Destroy()

##    def __del__(self):
##        print '__del__', self.__class__.__name__

    def __repr__(self):
        return '<%s: %s, %d>' %(self.__class__.__name__, self.model.defaultName, self.tIdx)

    def updatePageName(self):
        """ Return a name that is decorated with () meaning never been saved
            and/or * meaning model modified ~ meaning view modified. """

        self.pageName = self.model.getPageName()

        if not self.model.savedAs:
            sa1 = '('
            sa2 = ')'
        else: sa1 = sa2 = ''

        if len(self.model.viewsModified):
            vm = '~'
        else: vm = ''

        if self.model.modified: m = '*'
        else: m = ''

        self.pageName = '%s%s%s%s%s%s%s' % (m, vm, sa1, self.pageName, sa2, vm, m)

##        self.pageName = '%s%s%s%s%s%s%s' % (self.model.modified and '*' or '',
##                                            len(self.model.viewsModified) and '~' or '',
##                                            self.model.savedAs and '(' or '',
##                                            self.model.getPageName(),
##                                            self.model.savedAs and ')' or '',
##                                            len(self.model.viewsModified) and '~' or '',
##                                            self.model.modified and '*' or '')

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
            EVT_MENU(self.model.editor, wId, self.model.editor.OnSwitchedToView)
        menu.AppendSeparator()
        for view, wId in self.adtViews:
            menu.Append(wId, view.viewName, checkable = view not in self.adtViews)
            EVT_MENU(self.model.editor, wId, self.model.editor.OnToggleView)

        return menu

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

    def saveOrSaveAs(self):
        model = self.model
        if not model.savedAs:
            oldName = model.filename
            if model.editor.saveAs(oldName) and (oldName != model.filename):
                del model.editor.modules[oldName]
                model.editor.modules[model.filename] = self
        else:
            model.save()
            model.editor.updateModulePage(model)
            model.editor.updateTitle()

        model.editor.statusBar.setHint('%s saved.'%os.path.basename(model.filename))

    def OnPageChange(self, event):
        viewIdx = event.GetSelection()
        if event.GetOldSelection() != viewIdx:
            self.editor.setupToolBar(viewIdx=viewIdx)
            view = self.getActiveView(viewIdx)
            if hasattr(view, 'OnPageActivated'):
                view.OnPageActivated(event)
        event.Skip()
