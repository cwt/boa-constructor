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

from wxPython.wx import *
from wxPython.stc import *

import sys, string, time
import Preferences, About, Help
from os import path
import Utils, Browse

from Views.EditorViews import *
from Views.AppViews import AppView, AppFindResults, AppModuleDocView
from Views.AppViews import AppREADME_TIFView, AppTODO_TIFView, AppBUGS_TIFView
from Views.Designer import DesignerView
from Views.OGLViews import UMLView, ImportsView
from Views.DataView import DataView
from Views.PySourceView import PythonSourceView, HTMLSourceView, TextView, CPPSourceView, HPPSourceView
from Explorers.CVSExplorer import CVSConflictsView
from Explorers import Explorer

from EditorModels import *
from PrefsKeys import keyDefs
import ShellEditor
from Preferences import IS, wxFileDialog, flatTools

defAppModelViews = (AppView, PythonSourceView)
adtAppModelViews = (AppModuleDocView, ToDoView, ImportsView, CVSConflictsView, 
                    AppREADME_TIFView, AppREADME_TIFView, AppTODO_TIFView, 
                    AppBUGS_TIFView)

defModModelViews = (PythonSourceView, ExploreView)
adtModModelViews = (HierarchyView, ModuleDocView, ToDoView, UMLView, CVSConflictsView)

defBaseFrameModelViews = (PythonSourceView, ExploreView)
adtBaseFrameModelViews = (HierarchyView, ModuleDocView, ToDoView, UMLView, CVSConflictsView)

defPackageModelViews = (PackageView, PythonSourceView)
adtPackageModelViews = (CVSConflictsView,)

defTextModelViews = (TextView,)
adtTextModelViews = ()

defZopeDocModelViews = (HTMLSourceView,)
adtZopeDocModelViews = ()

defCPPModelViews = (CPPSourceView, HPPSourceView)
adtCPPModelViews = (CVSConflictsView,)

(mmFile, mmEdit, mmViews, mmWindows, mmHelp) = range(5)

[wxID_EDITOROPEN, wxID_EDITORSAVE, wxID_EDITORSAVEAS, wxID_EDITORCLOSEPAGE,
 wxID_EDITORREFRESH, wxID_EDITORDESIGNER, wxID_EDITORDEBUG, wxID_EDITORHELP,
 wxID_EDITORSWITCHAPP, wxID_DEFAULTVIEWS, wxID_EDITORSWITCHTO, 
 wxID_EDITORTOGGLEVIEW, wxID_EDITORSWITCHEXPLORER, wxID_EDITORSWITCHSHELL,
 wxID_EDITORSWITCHPALETTE, wxID_EDITORSWITCHINSPECTOR, wxID_EDITORDIFF,
 wxID_EDITORCMPAPPS, wxID_EDITORHELPABOUT, wxID_EDITORPREVPAGE, 
 wxID_EDITORNEXTPAGE, wxID_EDITORBROWSEFORW, wxID_EDITORBROWSEBACK] = \
 map(lambda _editor_menus: wxNewId(), range(23))
               
[wxID_EDITORFRAME, wxID_PAGECHANGED] = map(lambda _init_ctrls: wxNewId(), range(2))

##
## This class is used to merge paint reqeusts. Each paint is 
## captured and saved. Later on the idle envent, the non-duplicated
## paints are executed. The code attempts to be efficient by determining
## the enclosing rectangle where multiple rectangles intersect.
## This is required only on GTK systems.
##
class NoteBookPanelPaintEventHandler(wxEvtHandler):
    def __init__(self, window):
        wxEvtHandler.__init__(self)
        self.dirty=0
        self.updates=[]
        self.window = window
        window.PushEventHandler(self)
        EVT_PAINT(self, self.OnPaint)
        EVT_IDLE(self, self.OnIdle)
    def OnPaint(self, event):
        self.Id = event.GetId()
        if self.dirty==2:
            ### Clear everything out of our update queue
            ### which is covered by this rectangle. Then
            ### pass it on.
            paintRect = self.window.GetUpdateRegion().GetBox()
            newList=[]
            for rect in self.updates:
                if not self.RectangleIncludes(paintRect, rect):
                    newList.append(rect)
            self.updates = newList
            event.Skip()
            return
        self.dirty=1
        newRect = self.window.GetUpdateRegion().GetBox()
        newList=[]
        for rect in self.updates:
            if self.RectanglesOverlap(rect, newRect):
                newRect = self.MergeRectangles(rect,newRect)
            else:
                newList.append(rect)
        self.updates = newList
        self.updates.append(newRect)
    def OnIdle(self, event):
        if self.dirty != 1:
            return
        self.dirty=2
        for i in range(len(self.updates)):
            try:
                rect = self.updates[i]
                self.window.Refresh(0, rect)
            except:
                pass
        self.updates=[]
        self.dirty=0
    def RectangleIncludes(self, rect1, rect2):
        "Returns 1 if rectangle 2 is included in rectangle 1"
        if rect1.x > rect2.x : return 0
        if rect1.y > rect2.y : return 0
        if rect1.x + rect1.width < rect2.x + rect2.width : return 0
        if rect1.y + rect1.height < rect2.y + rect2.height : return 0
        return 1
    def RectanglesOverlap(self, rect1, rect2):
        " Returns 1 if Rectangles overlap, 0 otherwise "
        if rect1.x > rect2.x + rect2.width : return 0
        if rect1.y > rect2.y + rect2.height : return 0
        if rect1.x + rect1.width < rect2.x : return 0
        if rect1.y + rect1.height < rect2.y : return 0
        return 1
    def MergeRectangles(self, rect1, rect2):
        " Returns a rectangle containing both rect1 and rect2"
        if rect1.x < rect2.x:
            x=rect1.x
            width = rect1.width + rect2.width + (rect2.x -(rect1.x + rect1.width))
        else:
            x=rect2.x
            width = rect1.width + rect2.width + (rect1.x -(rect2.x + rect2.width))
        if rect1.y < rect2.y:
            y=rect1.y
            height = rect1.height + rect2.height + (rect2.y -(rect1.y + rect1.height))
        else:
            y=rect2.y
            height = rect1.height + rect2.height + (rect1.y -(rect2.y + rect2.height))
        return (wxRect(x, y, width, height))

                    
class EditorFrame(wxFrame):
    """ Source code editor and Mode/View controller"""

    openBmp = 'Images/Editor/Open.bmp'
    helpBmp = 'Images/Shared/Help.bmp'
        
    def _init_utils(self): 
        pass

    def _init_ctrls(self, prnt): 
        wxFrame.__init__(self, size = (-1, -1), id = wxID_EDITORFRAME, title = 'Editor', parent = prnt, name = '', style = wxDEFAULT_FRAME_STYLE | wxCLIP_CHILDREN, pos = (-1, -1))

    def __init__(self, parent, id, inspector, newMenu, componentPalette, app):
        self._init_ctrls(parent)
        self._init_utils()
        self.SetDimensions(Preferences.inspWidth, Preferences.paletteHeight + Preferences.windowManagerTop + Preferences.windowManagerBottom, 
          Preferences.edWidth, Preferences.bottomHeight)
        EVT_CLOSE(self, self.OnCloseWindow)

        if wxPlatform == '__WXMSW__':
            self.SetIcon(wxIcon(Preferences.toPyPath('Images/Icons/Editor.ico'), wxBITMAP_TYPE_ICO))
        
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
        
        # Build imagelist of all models
        orderedModList = []
        for mod in modelReg.values(): orderedModList.append((mod.imgIdx, mod))
        orderedModList.sort()
        for mod in orderedModList:
            self.modelImageList.Add(IS.load('Images/Modules/'+mod[1].bitmap))

        self.modelImageList.Add(IS.load('Images/Modules/Folder_s.bmp'))
        self.modelImageList.Add(IS.load('Images/Modules/Folder_green_s.bmp'))
        self.modelImageList.Add(IS.load('Images/Modules/Folder_cyan_s.bmp'))
        self.modelImageList.Add(IS.load('Images/Zope/Folder_icon.bmp'))
        self.modelImageList.Add(IS.load('Images/Zope/ControlPanel_icon.bmp'))
        self.modelImageList.Add(IS.load('Images/Zope/ProductFolder_icon.bmp'))
        self.modelImageList.Add(IS.load('Images/Zope/InstalledProduct_icon.bmp'))
        self.modelImageList.Add(IS.load('Images/Zope/UserFolder_icon.bmp'))
        self.modelImageList.Add(IS.load('Images/Zope/dtmldoc.bmp'))
        self.modelImageList.Add(IS.load('Images/Zope/Image_icon.bmp'))
        self.modelImageList.Add(IS.load('Images/Zope/System_obj.bmp'))
        self.modelImageList.Add(IS.load('Images/Zope/Zope_connection.bmp'))
        self.modelImageList.Add(IS.load('Images/Shared/BoaLogo.bmp'))
        self.modelImageList.Add(IS.load('Images/Modules/FolderUp_s.bmp'))
        self.modelImageList.Add(IS.load('Images/Modules/Drive_s.bmp'))
        self.modelImageList.Add(IS.load('Images/Modules/FolderBookmark_s.bmp'))
                                        
        if wxPlatform == '__WXMSW__':
            self.tabs.SetImageList(self.modelImageList)

        # Shell
        self.addShellPage()

        # Explorer
        self.explorer = Explorer.ExplorerSplitter (self.tabs, 
          self.modelImageList, '', self)
        self.tabs.AddPage(self.explorer, 'Explorer')
        self.tabs.SetSelection(1)
        
        # Menus
        self.newMenu = newMenu
        
        self.blankEditMenu = wxMenu()
        self.blankViewMenu = wxMenu()
        self.helpMenu = wxMenu()
        self.helpMenu.Append(wxID_EDITORHELP, 'Help')
        self.helpMenu.AppendSeparator()
        self.helpMenu.Append(wxID_EDITORHELPABOUT, 'About')

        EVT_MENU(self, wxID_EDITORHELP, self.OnHelp)
        EVT_MENU(self, wxID_EDITORHELPABOUT, self.OnHelpAbout)
        EVT_MENU(self, wxID_EDITOROPEN, self.OnOpen)
        EVT_MENU(self, wxID_EDITORSAVE, self.OnSave)
        EVT_MENU(self, wxID_EDITORSAVEAS, self.OnSaveAs)
        EVT_MENU(self, wxID_EDITORCLOSEPAGE, self.OnClosePage)
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
        EVT_MENU(self, wxID_EDITORPREVPAGE, self.OnPrevPage)
        EVT_MENU(self, wxID_EDITORNEXTPAGE, self.OnNextPage)
        
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
        
        self.defaultAdtViews = {AppModel: [], BaseFrameModel: [], 
                                ModuleModel: [], PackageModel: [], TextModel: [],
                                ZopeDocumentModel: [], CPPModel: []}

        # Toolbar
        self.toolBar = EditorToolBar(self, -1)#, style = wxTB_HORIZONTAL|wxNO_BORDER|wxTB_FLAT)#|wxTB_FLAT
        self.SetToolBar(self.toolBar)
        self.setupToolBar(viewIdx = 0)
        
        tree = self.explorer.tree
        if tree.defaultBookmarkItem:
            ws = tree.getChildNamed(tree.GetRootItem(), 'Bookmarks')
#        self.defaultBookmarkItem = self.getChildNamed(ws, self.boaRoot.entries[1].getDefault())
#            self.getChildNamed(ws, tree.boaRoot.entries[1].getDefault())
            tree.SelectItem(tree.getChildNamed(ws, tree.boaRoot.entries[1].getDefault()))
#            self.explorer.tree.defaultBookmarkItem)		
            
#            print 'Setting default', self.explorer.tree.defaultBookmarkItem
#            self.explorer.tree.SelectItem(self.explorer.tree.defaultBookmarkItem)		
#            print 'Set def', self.explorer.tree.GetSelection()

            if self.explorer.list.GetItemCount():
                item = self.explorer.list.GetItem(0)
                item.SetState(wxLIST_STATE_SELECTED | wxLIST_STATE_FOCUSED)
                self.explorer.list.SetItem(item)

        dt = Utils.BoaFileDropTarget(self)
        self.SetDropTarget(dt)

        self.explorer.list.SetFocus()
        
        # Hack to feed BoaFileDialog images
        import FileDlg
        FileDlg.wxBoaFileDialog.modImages = self.modelImageList
    
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
        if self.palette.destroying:
            return
        
        self.toolBar.ClearTools()
        
        accLst = []
        for (ctrlKey, key), wId in \
                ( (keyDefs['Inspector'], wxID_EDITORSWITCHINSPECTOR),
                  (keyDefs['Open'], wxID_EDITOROPEN),
                  (keyDefs['PrevPage'], wxID_EDITORPREVPAGE),
                  (keyDefs['NextPage'], wxID_EDITORNEXTPAGE) ):
            accLst.append( (ctrlKey, key, wId) ) 
            
        # primary option: open a module
        fileMenu = wxMenu()
        fileMenu.Append(wxID_EDITOROPEN, 'Open', 'Open a module')

        Utils.AddToolButtonBmpObject(self, self.toolBar, IS.load(self.openBmp), 'Open a module', self.OnOpen)
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
            self.mainMenu.Replace(mmFile, fileMenu, 'File').Destroy()
            self.mainMenu.Replace(mmEdit, Utils.duplicateMenu(self.blankEditMenu), 'Edit').Destroy()
#            self.mainMenu.Replace(mmEdit, self.blankEditMenu, 'Edit')

##            m = self.mainMenu.GetMenu(mmViews)
##            if m.GetMenuItemCount() > 0:
##                m.RemoveItem(m.FindItemById(wxID_DEFAULTVIEWS))

            self.mainMenu.Replace(mmViews, Utils.duplicateMenu(self.blankViewMenu), 'Views').Destroy()

        # Help button  
        self.toolBar.AddSeparator() 
        Utils.AddToolButtonBmpObject(self, self.toolBar, IS.load(self.helpBmp), 'Help', self.OnHelp)
            
        self.toolBar.Realize()

        if accLst: self.SetAcceleratorTable(wxAcceleratorTable(accLst))
#        print 'end setup toolbar',
    
    def addShellPage(self):
        """ Adds the interactive interpreter to the editor """
        self.tabs.AddPage(ShellEditor.ShellEditor(self.tabs, -1), 'Shell')

    def getValidName(self, modelClass):
        def tryName(modelClass, n): return '%s%d%s' %(modelClass.defaultName, n, modelClass.ext)
        n = 1
        #Obfuscated one-liner to check if such a name exists as a basename 
        #in a the dict keys of self.module
        while filter(lambda key, name=tryName(modelClass, n): \
          path.basename(key) == name, self.modules.keys()): n = n + 1
            
        return tryName(modelClass, n)
    
    def addModulePage(self, model, moduleName, defViews, views, imgIdx):
        spIdx = self.tabs.GetPageCount()
        modulePage = ModulePage(self.tabs, model, defViews, views, spIdx, self)
        self.modules[moduleName] = modulePage
        # Idx will be same as count after selection
        if wxPlatform == '__WXMSW__':
            self.tabs.AddPage(modulePage.notebook, modulePage.pageName, true, imgIdx)
        elif wxPlatform == '__WXGTK__':
            self.tabs.AddPage(modulePage.notebook, modulePage.pageName)
        wxYield()

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
        self.addModulePage(model, name, defTextModelViews, adtTextModelViews, 
          TextModel.imgIdx)
        model.new()

        self.tabs.Refresh()
        self.updateTitle()

    def addNewPackage(self):
        filename, success = self.saveAsDlg('__init__.py')
        if success:
            model = PackageModel('# Package initialisation', filename, self, false)
            self.addModulePage(model, model.packageName, defPackageModelViews, 
              adtPackageModelViews, PackageModel.imgIdx)
            model.save()
            model.notify()

            self.tabs.Refresh()
            self.updateTitle()

    def addNewAppPage(self):

        appname = self.getValidName(AppModel)
        appmodel = AppModel('', appname, appname[:-3], self, false)

        self.addModulePage(appmodel, appname, defAppModelViews, adtAppModelViews, 
          AppModel.imgIdx)

        frmMod = self.addNewFramePage('Frame', appmodel)
        frmNme = path.splitext(path.basename(frmMod.filename))[0]
        appmodel.new(frmNme)

        self.tabs.Refresh()
        self.updateTitle()

    def addNewModulePage(self):
        name = self.getValidName(ModuleModel)
        activeApp = self.activeApp()
        if activeApp: activeApp = activeApp.model

        model = ModuleModel('', name, self, false, activeApp)
        self.addModulePage(model, name, defModModelViews, adtModModelViews, 
          ModuleModel.imgIdx)
        model.new()
        if activeApp: activeApp.addModule(model.filename, '')

        self.tabs.Refresh()
        self.updateTitle()

    def addNewFramePage(self, modId, app = None):
        frmMod = modelReg[modId]
        name = self.getValidName(frmMod)
        if app: 
            activeAppMod = app
        else: 
            activeAppMod = self.activeApp()
            if activeAppMod: 
                activeAppMod = activeAppMod.model

        model = frmMod('', name, name[:-3], self, false, activeAppMod)

        activeApp = self.activeApp()

        self.addModulePage(model, name, defBaseFrameModelViews, 
          adtBaseFrameModelViews, frmMod.imgIdx)
        tempComp = frmMod.companion('', None, None)
        params = tempComp.designTimeSource()
        params['parent'] = 'prnt'
        params['id'] = Utils.windowIdentifier(model.main, '')

        model.new(params)
        if activeApp: activeApp.model.addModule(model.filename, '')

        self.tabs.Refresh()
        self.updateTitle()
        
        return model

    def addNewDialog(self, dlgClass, dlgCompanion):
        module = self.getActiveModulePage()
        if module:
            view = module.getActiveView() 
            if view and view.viewName == 'Source':
                compn = dlgCompanion('dlg', None)
                view.insertCodeBlock(compn.body())
         
    
    def openOrGotoModule(self, name, app = None):
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
                return self.openModule(name, app)
        
    def openModule(self, filename, app = None):
        name = filename
        try:
            modCls, main = identifyFile(filename)
            f = open(filename, 'r')
        except IOError, err:
            Utils.ShowMessage(self, 'File error', err.strerror, wxICON_EXCLAMATION)
            raise
        try:
            dirname, name = path.split(filename)
            name, ext = path.splitext(name)
            source = f.read()
            imgIdx = modCls.imgIdx

            if modCls is PackageModel:
                model = PackageModel(source, filename, self, true)
                defViews = defPackageModelViews
                views = adtPackageModelViews
                name = model.packageName
            elif modCls is AppModel:
                model = AppModel(source, filename, '', self, true)
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
                print 'Identified CPP'
                model = CPPModel(source, filename, self, true)
                defViews = defCPPModelViews
                views = adtCPPModelViews
            else:
                model = ModuleModel(source, filename, self, true, app)
                defViews = defModModelViews
                views = adtModModelViews
        finally:
            f.close()

        self.addModulePage(model, filename, defViews, views, model.imgIdx)

        model.notify()

        if wxPlatform != '__WXGTK__':
            self.tabs.Refresh()
            self.updateTitle()

        return model
    
    def openOrGotoZopeDocument(self, zopeConn, zopeObj):
        if self.modules.has_key(zopeObj.whole_name()):
            self.modules[zopeObj.whole_name()].focus()
            return self.modules[zopeObj.whole_name()].model
        else:
            self.openZopeDocument(zopeConn, zopeObj)
            
    def openZopeDocument(self, zopeConn, zopeObj):

        model = ZopeDocumentModel(zopeObj.whole_name(), '', 
          self, false, zopeConn, zopeObj)
        model.load()

        self.addModulePage(
            model, zopeObj.whole_name(), defZopeDocModelViews,
            adtZopeDocModelViews, ZopeDocumentModel.imgIdx)

        model.save()
        model.notify()

        self.tabs.Refresh()

        self.updateTitle()
        
    def showDesigner(self):
        # XXX Disable source control as editing source with the designer
        # XXX will loose code in certain cases
        modulePage = self.getActiveModulePage()
        if modulePage:
            model = modulePage.model

            # Just show if already opened
            if model.views.has_key('Designer'):
                model.views['Data'].focus()
                model.views['Designer'].Show(true)
                model.views['Designer'].Raise()
                return

            # update any view modifications
            model.refreshFromViews()

            model.initModule()
            model.readComponents()  

            # add or focus data view
            if not model.views.has_key('Data'):
                dataView = DataView(modulePage.notebook, self.inspector, 
                  model, self.compPalette)
                dataView.addToNotebook(modulePage.notebook)
                model.views['Data'] = dataView
                dataView.initialize()
            else:
                dataView = model.views['Data']
                dataView.focus()
            
            modulePage.notebook.SetSelection(modulePage.notebook.GetPageCount()-1)
            dataView.refreshCtrl()

            # add or focus frame designer
            if not model.views.has_key('Designer'):
                designer = DesignerView(self, self.inspector, 
                  model, self.compPalette, model.companion, dataView)
                model.views['Designer'] = designer
                designer.refreshCtrl()
            model.views['Designer'].Show(true)
            
            # Make source read only
            model.views['Source'].SetReadOnly(true)
                
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
                if Utils.yesNoDialog(self, 'Close module', 'There are changes, do you want to save?'):
                    self.saveOrSaveAs()
                    name = modulePage.model.filename
                if not vis:
                    self.Show(false)

            self.tabs.RemovePage(idx)
            del self.modules[name]
            modulePage.destroy()
            # notify pages for idx adjustments
            for modPge in self.modules.values():
                modPge.removedPage(idx)
            
        else: print name, 'not found in OnClose'

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
        self.tabs.Refresh()
    
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
        modulePage.model.refreshFromViews()
        if modulePage:
            model = modulePage.model
            oldName = model.filename
            
            if self.saveAs(oldName) and (oldName != model.filename):
                del self.modules[oldName]
                self.modules[model.filename] = modulePage

    def OnClosePage(self, event):
        # Replace view's edit menu with editor managed blankEditMenu
        # so editor can free it without fear of mainMenu freeing it
#        self.mainMenu.Replace(mmEdit, self.blankEditMenu, 'Edit')
        self.mainMenu.Replace(mmEdit, wxMenu(), 'Edit').Destroy()

        modulePage = self.getActiveModulePage()
        actPge = self.tabs.GetSelection()
        numPgs = self.tabs.GetPageCount()
        if modulePage:
            self.closeModule(modulePage)
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
            # hack to avoid core dump, first setting the notebook to anything but
            # the last page before setting it to the last page allows us to close
            # this window from the palette. Weird?
            self.tabs.SetSelection(0)
            pgeCnt = self.tabs.GetPageCount()
            self.tabs.SetSelection(pgeCnt -1)
            for p in range(pgeCnt):
                self.OnClosePage(None)
            self.palette.editor = None
            self.inspector = None
            self.explorer.destroy()
            self.newMenu.Destroy()#
##            self.mainMenu.Replace(1, self.blankEditMenu, 'Edit')
##            self.mainMenu.Replace(2, self.blankViewMenu, 'View')
            self.mainMenu.Replace(1, wxMenu(), 'Edit').Destroy()
            self.mainMenu.Replace(2, wxMenu(), 'View').Destroy()
            self.mainMenu = None
            self.Destroy()
            event.Skip()
##        else:
##            self.Show(false) 

    def OnHelp(self, event):
        Help.showHelp(self, Help.BoaHelpFrame, 'Editor.html')

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
            if view not in self.defaultAdtViews[model]:
                self.defaultAdtViews[model].append(view)
        else:
            if view in self.defaultAdtViews[model]:
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
        a = About.AboutBox(None)
        a.ShowModal()
        a.Destroy()
    
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

#-----Toolbar-------------------------------------------------------------------

class MyToolBar(wxToolBar):
    def __init__(self, parent, winid):
        wxToolBar.__init__(self, parent, winid, 
          style = wxTB_HORIZONTAL|wxNO_BORDER|flatTools)#wxDOUBLE_BORDER|
        self.toolLst = []
        self.toolCount = 0

    def AddTool(self, id, bitmap, toggleBitmap = wxNullBitmap, shortHelpString = '', isToggle = false):
        from Views.StyledTextCtrls import new_stc
        if new_stc:
            wxToolBar.AddTool(self, id, bitmap, toggleBitmap, isToggle = isToggle, 
                shortHelpString = shortHelpString)
        else:
            wxToolBar.AddTool(self, id, bitmap, toggleBitmap, toggle = isToggle, 
                shortHelpString = shortHelpString)
   
        self.toolLst.append(id)
        self.toolCount = self.toolCount + 1

    def AddSeparator(self):
        wxToolBar.AddSeparator(self)
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
            self.GetParent().Disconnect(wid),
        self.toolLst = []
        self.toolCount = 0

class EditorToolBar(MyToolBar):
    pass

class EditorStatusBar(wxStatusBar):
    """ Displays information about the current view. Also global stats/ 
        progress bar etc. """
    def __init__(self, parent):
        wxStatusBar.__init__(self, parent, -1, style = wxST_SIZEGRIP)
        self.SetFieldsCount(5)
        self.SetStatusWidths([30, 30, 300, 150, -1])
        wID = NewId()

        dc = wxClientDC(self)
        dc.SetFont(self.GetFont())
        w, h = dc.GetTextExtent('X')
        self.h = int(h * 1.8)
        self.SetSize(wxSize(100, self.h-1))

        self.col = wxStaticText(self, -1, '0   ', wxPoint(3, 4))
        self.row = wxStaticText(self, -1, '0   ', wxPoint(37, 4))
        self.hint = wxStaticText(self, -1, ' ', wxPoint(72, 4), 
          wxSize(290, self.h -8), style = wxST_NO_AUTORESIZE | wxALIGN_LEFT)
        self.progress = wxGauge(self, -1, 100, 
          pos = wxPoint(368+Preferences.editorProgressFudgePosX, 2), 
          size = wxSize(150, self.h -5 + Preferences.editorProgressFudgeSizeY))
    
    def setHint(self, hint):
        self.hint.SetLabel(hint)
        self.hint.SetSize(wxSize(290, self.h -8))
        self.hint.SetToolTipString(hint)

#-----Model hoster--------------------------------------------------------------

wxID_MODULEPAGEVIEWCHANGE = wxNewId()

class ModulePage:
    """ Represents a notebook on a page of the top level notebook hosting 
        model instances. """  
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
        if not editor.defaultAdtViews.has_key(cls):
            cls = model.__class__.__bases__[0]
            
        tot = len(defViews) + len(editor.defaultAdtViews[cls])
        if tot:
            stepsDone = 50.0
            editor.statusBar.progress.SetValue(int(stepsDone))
            step = (100 - stepsDone) / tot
            for view in defViews:
                self.addView(view)
                stepsDone = stepsDone + step
                editor.statusBar.progress.SetValue(int(stepsDone))
            
            for view in editor.defaultAdtViews[cls]:
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
            view.close()
        self.notebook.DeleteAllPages()

        self.model.destroy()    
        self.notebook.Destroy()
    
    def __del__(self):
        print '__del__', self.__class__.__name__        

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
        if name[0] == '~': name = name[1:-1]
        return self.model.views[name]

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
        if wxPlatform == '__WXGTK__':
            panel = wxPanel(self.notebook, -1, style=wxTAB_TRAVERSAL | wxCLIP_CHILDREN)
        
        if not viewName: viewName = view.viewName
        if wxPlatform == '__WXGTK__':
            self.model.views[viewName] = apply(view, (panel, self.model))
            self.model.nb_handler = NoteBookPanelPaintEventHandler(self.model.views[viewName])
        else:
            self.model.views[viewName] = apply(view, (self.notebook, self.model))

        if wxPlatform == '__WXGTK__':
            def OnWinSize(evt, win=self.model.views[viewName]):
                win.SetSize(evt.GetSize())
            EVT_SIZE(panel, OnWinSize)

        if view.docked:
            if wxPlatform == '__WXGTK__':
                self.model.views[viewName].addToNotebook(self.notebook, viewName,
                    panel=panel)
            else:
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
    
    def OnPageChange(self, event):
        viewIdx = event.GetSelection()
        if event.GetOldSelection() != viewIdx:
            self.editor.setupToolBar(viewIdx=viewIdx)
            view = self.getActiveView(viewIdx)
            if hasattr(view, 'OnPageActivated'):
                view.OnPageActivated(event)
        event.Skip()
