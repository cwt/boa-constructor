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

import sys, string, time
import Preferences
from PythonInterpreter import *
from os import path
from Utils import AddToolButtonBmpObject

from EditorViews import *
from Designer import DesignerView
from UMLView import UMLView, ImportsView
from DataView import DataView
from EditorModels import *
from wxPython.wx import *
import Explorer

ps1 = '>>> '
ps2 = '... '
#nl = chr(13)+chr(10)

AppModelViews = (AppView, SourceView, AppModuleDocView, ToDoView)
#ModModelViews = (TestView,) 
ModModelViews = (SourceView, HierarchyView, ExploreView, ModuleDocView, ToDoView, UMLView) #PyDEView, InfoView, 
BaseFrameModelViews = (SourceView, HierarchyView, ExploreView, ModuleDocView, ToDoView)#, UMLView) ExploreView, 
PackageModelViews = (PackageView, SourceView)
TextModelViews = (TextView,)
                    
class EditorFrame(wxFrame):#, ImageListed):
    """ Source code editor and Mode/View controller"""

    openBmp = wxBitmap('Images/Editor/Open.bmp', wxBITMAP_TYPE_BMP)
    helpBmp = wxBitmap('Images/Shared/Help.bmp', wxBITMAP_TYPE_BMP)
#    closeBmp = wxBitmap('Images/Editor/Close.bmp', wxBITMAP_TYPE_BMP)
#    saveBmp = wxBitmap('Images/Editor/Save.bmp', wxBITMAP_TYPE_BMP)
#    saveAsBmp = wxBitmap('Images/Editor/SaveAs.bmp', wxBITMAP_TYPE_BMP)
#    designerBmp = wxBitmap('Images/Shared/Designer.bmp', wxBITMAP_TYPE_BMP)
        
    def __init__(self, parent, id, title, inspector, componentPalette, app):
        wxFrame.__init__(self, parent, -1, title,
            wxPoint(Preferences.inspWidth, Preferences.paletteHeight + \
            Preferences.windowManagerTop + Preferences.windowManagerBottom), 
            wxSize(Preferences.edWidth, Preferences.bottomHeight))
        if wxPlatform == '__WXMSW__':
            self.icon = wxIcon('Images/Icons/Editor.ico', wxBITMAP_TYPE_ICO)
            self.SetIcon(self.icon)

        self.app = app
        self.palette = parent
        self.modules = {}
        self.inspector = inspector
        self.compPalette = componentPalette
        self.debugger = None

        self.statusBar = EditorStatusBar(self)
        self.SetStatusBar(self.statusBar)
        
        idNotebookChange = NewId()

        self.tabs = wxNotebook(self, idNotebookChange)#, style = wxTC_MULTILINE)

        EVT_NOTEBOOK_PAGE_CHANGED(self.tabs, idNotebookChange, self.OnPageChange)

        self.modelImageList = wxImageList(16, 16)

        orderedModList = []
        for mod in modelReg.values(): orderedModList.append((mod.imgIdx, mod))
        orderedModList.sort()
        for mod in orderedModList:
            self.modelImageList.Add(wxBitmap('Images/Modules/'+mod[1].bitmap,
                                              wxBITMAP_TYPE_BMP))
        self.modelImageList.Add(wxBitmap('Images/Modules/Folder_s.bmp',
                                          wxBITMAP_TYPE_BMP))
                                        
        if wxPlatform == '__WXMSW__':
            self.tabs.SetImageList(self.modelImageList)

        self.addShellPage()

        self.explorer = Explorer.PackageFolderExplorer(self.tabs, 
          self.modelImageList, '', self)#'D:\\Program Files\\Python', self)
        self.tabs.AddPage(self.explorer, 'Explorer')
        self.tabs.SetSelection(0)
		
        self.interp = PythonInterpreter()
        self.toolBar = None

        self.toolBar = EditorToolBar(self, -1)#, style = wxTB_HORIZONTAL|wxNO_BORDER|wxTB_FLAT)#|wxTB_FLAT
        self.SetToolBar(self.toolBar)
        self.setupToolBar(viewIdx = 0)

    def setupToolBar(self, modelIdx = None, viewIdx = None):

        self.toolBar.ClearTools()
            
        # primary option: open a module
        AddToolButtonBmpObject(self, self.toolBar, self.openBmp, 'Open a module', self.OnOpen)
#        self.toolBar.AddSeparator()
           
        am = self.getActiveModulePage(modelIdx) 
        if am: 
            am.model.addTools(self.toolBar)
            activeView = am.getActiveView(viewIdx)
            self.toolBar.AddSeparator() 
            activeView.addViewTools(self.toolBar)

        # Help button  
        self.toolBar.AddSeparator() 
        AddToolButtonBmpObject(self, self.toolBar, self.helpBmp, 'Help', self.OnHelp)
            
        self.toolBar.Realize()
        self.toolBar.Refresh()

                
    def write(self, s):
    	self.editor.WriteText(s)
	
    def addPage(self, caption, content):
        mID = NewId()
        editor = wxTextCtrl(self.tabs, mID, content, wxPoint(80, 75), wxSize(200, 150), wxTE_MULTILINE)
        editor.SetFont(wxFont(9, wxMODERN, wxNORMAL, wxNORMAL, false))
        self.tabs.AddPage(editor, caption)
        wxYield()
        self.tabs.SetSelection(self.tabs.GetPageCount() -1)
        self.tabs.Refresh()
        self.tabs.ResizeChildren();
        return editor

    def addShellPage(self):
        """ Adds the interactive interpreter to the editor """
        self.shell = self.addPage('Shell', 'Python '+ sys.version+ " (Boa) " + sys.copyright+chr(13)+chr(10)+ps1)
        wxYield()
        self.shell.SetInsertionPointEnd()
        self.shell.interp = PythonInterpreter()
        EVT_CHAR(self.shell, self.OnShellEnter)

    def getValidName(self, modelClass):
        def tryName(modelClass, n): return '%s%d%s' %(modelClass.defaultName, n, modelClass.ext)
        n = 1
        #Obfuscated one-liner to check if such a name exists as a basename 
        #in a the dict keys of self.module
        while filter(lambda key, name=tryName(modelClass, n): \
          path.basename(key) == name, self.modules.keys()): n = n + 1
            
        return tryName(modelClass, n)
    
    def addModulePage(self, model, moduleName, views, imgIdx):
        spIdx = self.tabs.GetPageCount()
        modulePage = ModulePage(self.tabs, model, views, spIdx, self)
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
        self.addModulePage(model, name, TextModelViews, TextModel.imgIdx)
        model.new()

        self.tabs.ResizeChildren()
        self.tabs.Refresh()

        self.updateTitle()

    def addNewPackage(self):
        filename, success = self.saveAsDlg('__init__.py')
        if success:
            model = PackageModel('# Package initialisation', filename, self, false)
#            self.addIfAppActive(model.filename)
            self.addModulePage(model, model.packageName, PackageModelViews, 
              PackageModel.imgIdx)
            model.save()
            model.notify()

            self.tabs.ResizeChildren()
            self.tabs.Refresh()

            self.updateTitle()

    def addNewAppPage(self):

        appname = self.getValidName(AppModel)
        appmodel = AppModel('', appname, appname[:-3], self, false)

        self.addModulePage(appmodel, appname, AppModelViews, AppModel.imgIdx)

        frmMod = self.addNewFramePage('Frame')
        frmMod.app = appmodel
        frmNme = path.splitext(path.basename(frmMod.filename))[0]
        appmodel.new(frmNme)

        self.tabs.ResizeChildren()
        self.tabs.Refresh()

        self.updateTitle()

    def addNewModulePage(self):
        name = self.getValidName(ModuleModel)
        model = ModuleModel('', name, self, false)
        activeApp = self.activeApp()
        self.addModulePage(model, name, ModModelViews, ModuleModel.imgIdx)
        model.new()
        if activeApp: activeApp.model.addModule(model.filename, '')

        self.tabs.ResizeChildren()
        self.tabs.Refresh()

        self.updateTitle()

    def addNewFramePage(self, modId):
        frmMod = modelReg[modId]
        name = self.getValidName(frmMod)
        model = frmMod('', name, name[:-3], self, false)
        activeApp = self.activeApp()

        self.addModulePage(model, name, BaseFrameModelViews, frmMod.imgIdx)
        tempComp = frmMod.companion('', None, None)
        params = tempComp.designTimeSource()
        params['parent'] = 'prnt'
        params['id'] = Utils.windowIdentifier(model.main, '')

        model.new(params)
        if activeApp: activeApp.model.addModule(model.filename, '')

        self.tabs.ResizeChildren()
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
         
    
    def openOrGotoModule(self, name):
        if self.modules.has_key(name):
            self.modules[name].focus()
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
                return self.openModule(name)
        
    def openModule(self, filename):
        name = filename
        modCls, main = identifyFile(filename)
        f = open(filename, 'r')
        try:
            dirname, name = path.split(filename)
            name, ext = path.splitext(name)
            source = f.read()
            imgIdx = modCls.imgIdx

            if modCls is PackageModel:
                model = PackageModel(source, filename, self, true)
                views = PackageModelViews
                name = model.packageName
            elif modCls is AppModel:
                model = AppModel(source, filename, '', self, true)
                views = AppModelViews
            elif modCls in (FrameModel, DialogModel, MiniFrameModel, 
              MDIParentModel, MDIChildModel):
                model = modCls(source, filename, main, self, true)
                views = BaseFrameModelViews
            elif modCls is TextModel:
                model = TextModel(source, filename, self, true)
                views = TextModelViews
            else:
                model = ModuleModel(source, filename, self, true)
                views = ModModelViews
        finally:
            f.close()

        self.addModulePage(model, filename, views, model.imgIdx)

        model.notify()

        self.tabs.ResizeChildren()
        self.tabs.Refresh()

        self.updateTitle()

        return model
            
    def showDesigner(self):
        # XXX Disable source control as editing source with the designer
        # XXX will loose code in certain cases
        module = self.getActiveModulePage()
        if module:
            # update any view modifications
            module.model.refreshFromViews()

            # add or focus data view
            if not module.model.views.has_key('Data'):
                dataView = DataView(module.notebook, self.inspector, 
                  module.model, self.compPalette, module.model.companion)
                dataView.addToNotebook(module.notebook)
                module.model.views['Data'] = dataView
                dataView.initialize()
            else:
                dataView = module.model.views['Data']
                dataView.focus()
            
            module.notebook.SetSelection(module.notebook.GetPageCount()-1)
            dataView.refreshCtrl()

            # add or focus frame designer
            if not module.model.views.has_key('Designer'):
                module.model.initModule()
                module.model.readComponents()  
                module.model.views['Designer'] = DesignerView(self, self.inspector, 
                  module.model, self.compPalette, module.model.companion, dataView)
                module.model.views['Designer'].refreshCtrl()
            module.model.views['Designer'].Show(true)

            designer = module.model.views['Designer']
            if designer.selection:
                designer.selection.selectCtrl(designer, designer.companion)
#                self.inspector.selectObject(designer, designer.companion)
                
                
    def showImportsView(self):
        module = self.getActiveModulePage()
        if module:
            if not module.model.views.has_key('Imports'):
                module.addView(ImportsView)

            module.model.views['Imports'].Show(true)
                                
    def openFileDlg(self):
        dlg = wxFileDialog(self, 'Choose a file', '.', '', 'Text files (*.txt)|*.txt|Modules (*.py)|*.py', wxOPEN)
        if dlg.ShowModal() == wxID_OK:
            return dlg.GetPath()
        dlg.Destroy()
        return '' 
        
    def saveAsDlg(self, filename):
        dir, name = path.split(filename)
        dlg = wxFileDialog(self, 'Save as...', dir, name, "*.py", wxSAVE)
        
        try:
            if dlg.ShowModal() == wxID_OK:
                destFile = dlg.GetPath()
                result = true
            else:
                destFile = ''
                result = false
        finally: dlg.Destroy()
        
        return destFile, result

    def closeModule(self, modulePage):
        idx = modulePage.tIdx
        name = modulePage.model.filename
        if self.modules.has_key(name):
            if modulePage.model.views.has_key('Designer'):
#                if yesNoDialog(parent, 'Close module', 'Do you want to save?'):
                modulePage.model.views['Designer'].close()
            modulePage.model.refreshFromViews()
            if modulePage.model.modified:
                if Utils.yesNoDialog(self, 'Close module', 'There are changes, do you want to save?'):
                    self.saveOrSaveAs()
            modulePage.destroy()
            self.tabs.RemovePage(idx)
            del self.modules[name]
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
    
#    def 
    
    def updateTitle(self, pageIdx = None):
        """ Updates the title of the Editor to reflect changes in selection,
            filename or model state. """
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
        self.tabs.ResizeChildren();
    
    def updateStatusRowCol(self, row, col):
        self.statusBar.row.SetLabel(`row`)
        self.statusBar.col.SetLabel(`col`)
	            
    def OnOpen(self, event):
        fn = self.openFileDlg()
        if fn: self.openOrGotoModule(fn)

    def saveOrSaveAs(self):
        modulePage = self.getActiveModulePage()
        if modulePage:
            model = modulePage.model
            if not model.savedAs:
                oldName = model.filename
                if self.saveAs(oldName) and (oldName != model.filename):
                    del self.modules[oldName]
                    self.modules[model.filename] = modulePage
            else:
                model.save()                
                self.updateModulePage(model)
                self.updateTitle()

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

    def OnClose(self, event):
        modulePage = self.getActiveModulePage()
        actPge = self.tabs.GetSelection()
        numPgs = self.tabs.GetPageCount()
        if modulePage:
            self.closeModule(modulePage)
            if actPge == numPgs - 1:
                self.tabs.SetSelection(numPgs - 2)
            else:
                self.tabs.SetSelection(actPge)
                
            
#            self.tabs.AdvanceSelection( 
#              self.tabs.GetSelection() == (self.tabs.GetPageCount() - 1))

##            if self.tabs.GetSelection() != (self.tabs.GetPageCount()):
##                self.tabs.AdvanceSelection(false)
##                print 'advanced selection'
##            else:
##                self.tabs.SetSelection(self.tabs.GetPageCount()-1)
##                print 'selected last'

    def OnRefresh(self, event):
        modulePage = self.getActiveModulePage()
        if modulePage and modulePage.model.views.has_key('Source'):
            modulePage.model.views['Source'].refreshModel()
            self.updateModulePage(modulePage.model)
            self.updateTitle()

		
    def OnPageChange(self, event):
        self.updateTitle(event.GetSelection())
        if hasattr(self, 'toolBar'): self.setupToolBar(event.GetSelection())
        event.Skip()

    def OnDesigner(self, event):
        self.showDesigner()

    def OnShellEnter(self, event):
        if event.KeyCode() == 13:
            self.shell.AppendText(nl)
            try:
                tmpstdout = sys.stdout
                tmpstderr = sys.stderr
                line = string.strip(self.shell.GetLineText(self.shell.GetNumberOfLines() -2)[3:])

                sys.stdout = PseudoFileOut(self.shell)
                sys.stderr = PseudoFileErr(self.shell)

                if self.shell.interp.push(line):
                    self.shell.AppendText(nl + ps2)
                else:
                    self.shell.AppendText(ps1)
            finally:                
                sys.stdout = tmpstdout
                sys.stderr = tmpstderr
	else: event.Skip()

    def OnDebug(self, event):
        print self.modules
    
    def OnCloseWindow(self, event):
        # hack to avoid core dump, first setting the notebook to anything but
        # the last page before setting it to the last page allows us to close
        # this window from the palette. Weird?
        self.tabs.SetSelection(0)
        pgeCnt = self.tabs.GetPageCount()
        self.tabs.SetSelection(pgeCnt -1)
        for p in range(pgeCnt):
            self.OnClose(None)
        self.palette.editor = None
        event.Skip()

    def OnHelp(self, event):
       pass

class MyToolBar(wxToolBar):
    def __init__(self, parent, winid):
        wxToolBar.__init__(self, parent, winid)
#        self.toolLst = []
        self.toolCount = 0

    def AddTool(self, id, bitmap, shortHelpString):
        wxToolBar.AddTool(self, id, bitmap, shortHelpString = shortHelpString)
#        self.toolLst.append(id)
        self.toolCount = self.toolCount + 1

    def AddSeparator(self):
        wxToolBar.AddSeparator(self)
#        self.toolLst.append(-1)
        self.toolCount = self.toolCount + 1
        
    def DeleteTool(self, id):
        wxToolBar.DeleteTool(self, id) 
#        self.toolLst.remove(id)
        self.toolCount = self.toolCount - 1

    def ClearTools(self):
#        posLst = range(len(self.toolLst))
        posLst = range(self.toolCount)
        posLst.reverse()
        for pos in posLst:
            self.DeleteToolByPos(pos)
#        self.toolLst = []
        self.toolCount = 0

class EditorToolBar(MyToolBar):
    pass

class EditorStatusBar(wxStatusBar):
    """ Displays information about the current view. Also global stats/ 
        progress bar etc. """
    def __init__(self, parent):
        wxStatusBar.__init__(self, parent, -1, style = wxST_SIZEGRIP)
        self.SetFieldsCount(5)
        self.SetStatusWidths([30, 30, 200, 150, -1])
        wID = NewId()

        dc = wxClientDC(self)
        dc.SetFont(self.GetFont())
        w, h = dc.GetTextExtent('X')
        h = int(h * 1.8)
        self.SetSize(wxSize(100, h-1))

        self.col = wxStaticText(self, -1, '0   ', wxPoint(3, 4))
        self.row = wxStaticText(self, -1, '0   ', wxPoint(34, 4))
        self.hint = wxStaticText(self, -1, ' ', wxPoint(67, 4), wxSize(190, h -8))
        self.progress = wxGauge(self, -1, 100, pos = wxPoint(262, 2), size = wxSize(147, h -4))

idViewChange = NewId()

class ModulePage:
    """ Represents a notebook on a page of the top level notebook hosting 
        model instances. """
    def __init__(self, parent, model, views, idx, editor):
        """ Constructor """
        # this must be refreshed before it looks right
        self.editor = editor
        self.model = model
        self.parent = parent
        self.notebook = wxNotebook(parent, -1)
        EVT_NOTEBOOK_PAGE_CHANGED(self.notebook, self.notebook.GetId(), self.OnPageChange) 
        self.tIdx = idx
        self.updatePageName()
        stepsDone = 50.0
        editor.statusBar.progress.SetValue(int(stepsDone))
        step = (100 - stepsDone) / len(views)
	# construct the views
        for view in views:
            self.addView(view)
            stepsDone = stepsDone + step
            editor.statusBar.progress.SetValue(int(stepsDone))

        editor.statusBar.progress.SetValue(0)

    def __repr__(self):
        return '(%s, %d)' %(self.model.defaultName, self.tIdx)

    def updatePageName(self):
        """ Return a name that is decorated with () meaning never been saved
            and/or * meaning model modified ~ meaning view modified. """
        
        # XXX Nasty special checking package!!!
        if self.model.__class__ == PackageModel:
            self.pageName = self.model.packageName
        else:
            self.pageName, dummy = path.splitext(path.basename(self.model.filename))
        
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
        
        return self.pageName

    def getActiveView(self, idx = None):
#        wxYield()
        if idx is None: idx = self.notebook.GetSelection()
        name = self.notebook.GetPageText(idx)
        if name[0] == '~': name = name[1:-1]
        return self.model.views[name]
            
    def addView(self, view):
        """ Add a view to the model and display it as a page in the notebook
            of view instances."""
        self.model.views[view.viewName] = apply(view, (self.notebook, self.model))

        if view.docked:
            self.model.views[view.viewName].addToNotebook(self.notebook)
        
        return self.model.views[view.viewName]
        
    def refresh(self):
        self.notebook.Refresh()
        self.notebook.ResizeChildren()
    
    def focus(self):
        """ Make this model page the currently selected page. """
        self.parent.SetSelection(self.tIdx)
    
    def destroy(self):
        """ Destroy all views, notepad pages and the view notebook."""
        for view in self.model.views.values():
            view.close()
        self.notebook.DeleteAllPages()

        self.model.views = {}    
        self.notebook.Destroy()
    
    def removedPage(self, idx):
        """ Called on all ModulePages after a sibling ModulePage deletion. 
            Decrements tIdx if bigger than idx. """
        if idx < self.tIdx:
            self.tIdx = self.tIdx - 1
    
    def OnPageChange(self, event):
        self.editor.setupToolBar(viewIdx = event.GetSelection())
        event.Skip()
        

class PseudoFile:
    """ Base class for file like objects to facilitate StdOut for the Shell."""
    def __init__(self, output):
        self.output = output

    def writelines(self, l):
        map(self.write, l)
    
    def write(s):
        pass

    def flush(self):
        pass

class PseudoFileOut(PseudoFile):
    tags = 'stderr'
    def write(self, s):
        self.output.AppendText(s)

class PseudoFileErr(PseudoFile):
    tags = 'stdout'
    def write(self, s):
        self.output.AppendText(s)

