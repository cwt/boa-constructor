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

from os import path
import sys, string, time, pprint

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
from Explorers import Explorer
from Explorers.CVSExplorer import CVSConflictsView
from Explorers.ExplorerNodes import TransportSaveError, TransportLoadError
from ZopeLib import ImageViewer

print 'importing Models'
from EditorModels import *
from PrefsKeys import keyDefs
import ShellEditor, PaletteStore, ErrorStack
from Preferences import IS, wxFileDialog, flatTools
from EditorHelper import *
from ModRunner import EVT_EXEC_FINISH

from EditorUtils import EditorToolBar, EditorStatusBar, ModulePage

import Controllers

addTool = Utils.AddToolButtonBmpIS

(mmFile, mmEdit, mmViews, mmWindows, mmHelp) = range(5)

[wxID_EDITORFRAME, wxID_EDITORFRAMESTATUSBAR, wxID_EDITORFRAMETABS, wxID_EDITORFRAMETOOLBAR] = map(lambda _init_ctrls: wxNewId(), range(4))

class EditorFrame(wxFrame):
    """ Source code editor and Mode/View controller"""

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

    def _init_coll_modelImageList_Images(self, parent):

        parent.Add(bitmap = IS.load('Images/Modules/FolderUp_s.bmp'), mask = wxNullBitmap)
        parent.Add(bitmap = IS.load('Images/Modules/Folder_s.bmp'), mask = wxNullBitmap)
        parent.Add(bitmap = IS.load('Images/Modules/Folder_green_s.bmp'), mask = wxNullBitmap)
        parent.Add(bitmap = IS.load('Images/Modules/Folder_cyan_s.bmp'), mask = wxNullBitmap)
        parent.Add(bitmap = IS.load('Images/Zope/System_obj.bmp'), mask = wxNullBitmap)
        parent.Add(bitmap = IS.load('Images/Zope/Zope_connection.bmp'), mask = wxNullBitmap)
        parent.Add(bitmap = IS.load('Images/Shared/BoaLogo.bmp'), mask = wxNullBitmap)
        parent.Add(bitmap = IS.load('Images/Modules/Drive_s.bmp'), mask = wxNullBitmap)
        parent.Add(bitmap = IS.load('Images/Modules/FolderBookmark_s.bmp'), mask = wxNullBitmap)

    def _init_utils(self):
        self.modelImageList = wxImageList(height = 16, width = 16)
        self._init_coll_modelImageList_Images(self.modelImageList)

        self.mainMenu = wxMenuBar()

        self.blankEditMenu = wxMenu(title = '')

        self.blankViewMenu = wxMenu(title = '')

        self.helpMenu = wxMenu(title = '')

        self._init_coll_mainMenu_Menus(self.mainMenu)

    def _init_ctrls(self, prnt):
        wxFrame.__init__(self, id = wxID_EDITORFRAME, name = '', parent = prnt, pos = wxPoint(182, 189), size = wxSize(810, 513), style = wxDEFAULT_FRAME_STYLE | Preferences.childFrameStyle, title = 'Editor')
        self._init_utils()
        self.SetMenuBar(self.mainMenu)
        EVT_CLOSE(self, self.OnCloseWindow)

        self.statusBar = EditorStatusBar(id = wxID_EDITORFRAMESTATUSBAR, name = 'statusBar', parent = self, pos = wxPoint(0, 419), size = wxSize(802, 20), style = 0)
        self.SetStatusBar(self.statusBar)

        self.tabs = wxNotebook(id = wxID_EDITORFRAMETABS, name = 'tabs', parent = self, pos = wxPoint(0, 0), size = wxSize(802, 419), style = wxCLIP_CHILDREN)
        EVT_NOTEBOOK_PAGE_CHANGED(self.tabs, wxID_EDITORFRAMETABS, self.OnTabsNotebookPageChanged)

        self.toolBar = EditorToolBar(id = wxID_EDITORFRAMETOOLBAR, name = 'toolBar', parent = self, pos = wxPoint(0, -28), size = wxSize(802, 28), style = wxTB_HORIZONTAL | wxNO_BORDER)
        self.SetToolBar(self.toolBar)

    def __init__(self, parent, id, inspector, newMenu, componentPalette, app):
	self._created = false
        self._init_ctrls(parent)
        self.SetDimensions(Preferences.inspWidth + Preferences.windowManagerSide*2,
              Preferences.paletteHeight + Preferences.windowManagerTop + \
              Preferences.windowManagerBottom, Preferences.edWidth,
              Preferences.bottomHeight)

        if wxPlatform == '__WXMSW__':
            self.SetIcon(IS.load('Images/Icons/Editor.ico'))

        self.app = app
        self.palette = parent
        self.modules = {}
        self.inspector = inspector
        self.compPalette = componentPalette
        self.debugger = None
        self.browser = Browse.Browser()
        self.controllers = {}

        # System images are defined in the designer,
        # Note that it's a slight cheat as it takes advantage of the fact that
        # IS (ImageStore) is in the Boa evaluation namespace

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

        # Hook for shell and scripts
        sys.boa_ide = self

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
        EVT_MENU(self, EditorHelper.wxID_EDITOROPEN, self.OnOpen)

        # Windows menu
        EVT_MENU(self, EditorHelper.wxID_EDITORSWITCHSHELL, self.OnSwitchShell)
        EVT_MENU(self, EditorHelper.wxID_EDITORSWITCHEXPLORER, self.OnSwitchExplorer)
        EVT_MENU(self, EditorHelper.wxID_EDITORSWITCHPALETTE, self.OnSwitchPalette)
        EVT_MENU(self, EditorHelper.wxID_EDITORSWITCHINSPECTOR, self.OnSwitchInspector)
        EVT_MENU(self, EditorHelper.wxID_EDITORPREVPAGE, self.OnPrevPage)
        EVT_MENU(self, EditorHelper.wxID_EDITORNEXTPAGE, self.OnNextPage)

        self.winMenu = wxMenu()
        self.winMenu.Append(EditorHelper.wxID_EDITORSWITCHPALETTE, 'Palette')
        self.winMenu.Append(EditorHelper.wxID_EDITORSWITCHINSPECTOR, 
              'Inspector\t%s'%keyDefs['Inspector'][2])
        self.winMenu.Append(-1, '-')
        self.winMenu.Append(EditorHelper.wxID_EDITORSWITCHSHELL, 'Shell')
        self.winMenu.Append(EditorHelper.wxID_EDITORSWITCHEXPLORER, 'Explorer')
        self.winMenu.Append(-1, '-')
        self.winMenu.Append(EditorHelper.wxID_EDITORPREVPAGE, 
              'Previous window\t%s'%keyDefs['PrevPage'][2])
        self.winMenu.Append(EditorHelper.wxID_EDITORNEXTPAGE, 
              'Next window\t%s'%keyDefs['NextPage'][2])
        self.winMenu.Append(-1, '-')
        self.mainMenu.Append(self.winMenu, 'Windows')

        # Help menu
        self.helpMenu.Append(EditorHelper.wxID_EDITORHELP, 'Help')
        self.helpMenu.Append(EditorHelper.wxID_EDITORHELPGUIDE, 'Getting started guide')
        self.helpMenu.Append(EditorHelper.wxID_EDITORHELPTIPS, 'Tips')
        self.helpMenu.AppendSeparator()
        self.helpMenu.Append(EditorHelper.wxID_EDITORHELPABOUT, 'About')

        EVT_MENU(self, EditorHelper.wxID_EDITORHELP, self.OnHelp)
        EVT_MENU(self, EditorHelper.wxID_EDITORHELPABOUT, self.OnHelpAbout)
        EVT_MENU(self, EditorHelper.wxID_EDITORHELPGUIDE, self.OnHelpGuide)
        EVT_MENU(self, EditorHelper.wxID_EDITORHELPTIPS, self.OnHelpTips)

        self.mainMenu.Append(self.helpMenu, 'Help')

        self.defaultAdtViews = {}

        self._prevMod = None
        self._prevView = None
        self._created = true
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

        self.restoreEditorState()
    
    def __repr__(self):
        return '<EditorFrame (Boa IDE) instance at %d>'%id(self)

    def setupToolBar(self, modelIdx = None, viewIdx = None):
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
                ( (keyDefs['Inspector'], wxID_EDITORSWITCHINSPECTOR),
                  (keyDefs['Open'], wxID_EDITOROPEN),
                  (keyDefs['PrevPage'], wxID_EDITORPREVPAGE),
                  (keyDefs['NextPage'], wxID_EDITORNEXTPAGE) ):
            accLst.append( (ctrlKey, key, wId) )

        # primary option: open a module
        fileMenu = wxMenu()
        if self.palette.palettePages:
            fileMenu.AppendMenu(wxNewId(), 'New', Utils.duplicateMenu(self.palette.palettePages[0].menu))
        fileMenu.Append(EditorHelper.wxID_EDITOROPEN, 'Open\t%s'%keyDefs['Open'][2], 'Open a module')

        #self.toolBar.AddTool2(EditorHelper.wxID_EDITOROPEN, self.openBmp, 'Open a module')
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

            self.mainMenu.Replace(mmFile, fileMenu, 'File').Destroy()
            # Edit menu
            self.toolBar.AddSeparator()
            
            activeView = actMod.getActiveView(viewIdx)
            if activeView:
                activeView.connectEvts()
                self._prevView = activeView
                
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
        ## wxYield()

        self.tabs.SetSelection(spIdx)
        modulePage.refresh()
    
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
            transport = self.newFileTransport(name, filename)

        source = transport.load('r')
        modCls, main = identifyFile(filename, source, true)

        imgIdx = modCls.imgIdx
        
        controller = self.getController(Controllers.modelControllerReg.get(
              modCls, Controllers.ModuleController))
        model = controller.createModel(source, filename, main, true, app)
        defViews = controller.DefaultViews
        views = controller.AdditionalViews

        model.transport = transport
        
        if controller.docked:
            self.addModulePage(model, filename, defViews, views, model.imgIdx)
        else:
            controller.display(model)

        model.notify()

        if wxPlatform != '__WXGTK__':
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

            controller = Controllers.ZopeController(self, zopeObj.Model)
            
            model = controller.createModel('', wholename, '', false, zopeObj)
            
            # Add generic controller for model operations
            if not self.controllers.has_key(Controllers.ZopeController):
                self.controllers[Controllers.ZopeController] = \
                    Controllers.ZopeController(self, None)
                
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
        # XXX most of this should move to ModulePage
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
                    self.activeModSaveOrSaveAs()
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
        else:
            self.SetTitle('Editor')

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
                    self.closeModulePage(self.getActiveModulePage(), true)
                except 'Cancelled':
                    self.Show(true)
                    self.palette.destroying = false
                    return
                except TransportSaveError, error:
                    self.Show(true)
                    self.palette.destroying = false
                    wxLogError(str(error))
                    return

            if self.debugger:
                self.debugger.Close()

            self.palette.editor = None
            self.inspector = None
            self.explorer.destroy()
            self.newMenu.Destroy()
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
        self.tabs.SetSelection(1)

    def OnSwitchPalette(self, event):
        self.palette.Show(true)
        self.palette.Raise()

    def OnSwitchInspector(self, event):
        self.inspector.Show(true)
        if self.inspector.IsIconized():
            self.inspector.Iconize(false)
        self.inspector.Raise()

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
        if Preferences.minimizeOnRun and self.palette.IsIconized():
            self.palette.Iconize(false)
        event.runner.init(self.erroutFrm, event.runner.app)
        errs = event.runner.recheck()
        if errs:
            self.statusBar.setHint('Finished execution, there were errors', 'Warning')
        else:
            self.statusBar.setHint('Finished execution.')
                    