# Controllers 
import os, sys, time

from wxPython.wx import *

import EditorModels, ZopeEditorModels, EditorHelper, PaletteStore
from Views import EditorViews, AppViews, SourceViews, PySourceView, OGLViews, DataView, Designer, ProfileView
from Explorers import CVSExplorer, ExplorerNodes
import Preferences, Utils
import methodparse, sourceconst
from Preferences import keyDefs
from ModRunner import ProcessModuleRunner
import ErrorStack

addTool = Utils.AddToolButtonBmpIS

true=1;false=0

# XXX Controller should handle transport attachment

class BaseEditorController:
    """ Between user and model operations 
    
    Provides interface to add new and open existing models
    Manages toolbar and menu actions
    Custom classes should define Model operations as events
    """
    def __init__(self, editor, Model, DefaultViews, AdditionalViews):
        self.editor = editor
        self.Model = Model
        self.DefaultViews = DefaultViews
        self.AdditionalViews = AdditionalViews
        
        self.docked = true
    
    def getModel(self):
        return self.editor.getActiveModulePage().model

    def createModel(self, source, filename, name, editor, saved, modelParent=None):
        pass
        
    def createNewModel(self, modelParent=None):
        pass

    def afterAddModulePage(self, model):
        pass    

    def addMenu(self, menu, wId, label, accls, code = ()):
        menu.Append(wId, label + (code and '\t'+code[2] or ''))
        if code:
            accls.append((code[0], code[1], wId),)

    def addMenus(self, menu, model):
        return []

    def addTools(self, toolbar, model):
        pass

    def newFileTransport(self, name, filename):
        from Explorers.FileExplorer import PyFileNode
        return PyFileNode(name, filename, None, -1, None, None,
              properties = {})

class EditorController(BaseEditorController):
    closeBmp = 'Images/Editor/Close.bmp'
    def __init__(self, editor, Model, DefaultViews, AdditionalViews):
        BaseEditorController.__init__(self, editor, Model, DefaultViews, AdditionalViews)

        EVT_MENU(self.editor, EditorHelper.wxID_EDITORCLOSEPAGE, self.OnClose)

    def addTools(self, toolbar, model):
        addTool(self.editor, toolbar, self.closeBmp, 'Close', self.OnClose)

    def addMenus(self, menu, model):
        accls = []
        self.addMenu(menu, EditorHelper.wxID_EDITORCLOSEPAGE, 'Close', accls, (keyDefs['Close']))
        return accls

    def OnClose(self, event):
        self.editor.closeModulePage(self.editor.getActiveModulePage())
    
class PersistentController(EditorController):
    saveBmp = 'Images/Editor/Save.bmp'
    saveAsBmp = 'Images/Editor/SaveAs.bmp'
    def __init__(self, editor, Model, DefaultViews, AdditionalViews):
        EditorController.__init__(self, editor, Model, DefaultViews, AdditionalViews)

        EVT_MENU(self.editor, EditorHelper.wxID_EDITORSAVE, self.OnSave)
        EVT_MENU(self.editor, EditorHelper.wxID_EDITORSAVEAS, self.OnSaveAs)
        EVT_MENU(self.editor, EditorHelper.wxID_EDITORRELOAD, self.OnReload)

    def addTools(self, toolbar, model):
        EditorController.addTools(self, toolbar, model)
        addTool(self.editor, toolbar, self.saveBmp, 'Save', self.OnSave)
        addTool(self.editor, toolbar, self.saveAsBmp, 'Save as...', self.OnSaveAs)

    def addMenus(self, menu, model):
        accls = EditorController.addMenus(self, menu, model)
        self.addMenu(menu, EditorHelper.wxID_EDITORRELOAD, 'Reload', accls, ())
        self.addMenu(menu, EditorHelper.wxID_EDITORSAVE, 'Save', accls, (keyDefs['Save']))
        self.addMenu(menu, EditorHelper.wxID_EDITORSAVEAS, 'Save as...', accls, (keyDefs['SaveAs']))
        return accls

    def createModel(self, source, filename, main, saved, modelParent=None):
        return self.Model(source, filename, self.editor, saved)

    def createNewModel(self, modelParent=None):
        name = self.editor.getValidName(self.Model)
        model = self.createModel('', name, '', false)
        model.transport = self.newFileTransport('', name)
        model.new()

        return model, name

    def OnSave(self, event):
        #print 'save'
        try:
            self.editor.activeModSaveOrSaveAs()
        except ExplorerNodes.TransportSaveError, error:
            wxLogError(str(error))

    def OnSaveAs(self, event):
        try:
            self.editor.activeModSaveOrSaveAs(forceSaveAs=true)
        except ExplorerNodes.TransportSaveError, error:
            wxLogError(str(error))

    def OnReload(self, event):
        model = self.getModel()
        if model:
            try:
                model.load()
            except ExplorerNodes.TransportLoadError, error:
                wxLogError(str(error))
        
class ModuleController(PersistentController):
    runAppBmp = 'Images/Debug/RunApp.bmp'
    runBmp = 'Images/Debug/Run.bmp'
    compileBmp = 'Images/Debug/Compile.bmp'
    debugBmp = 'Images/Debug/Debug.bmp'
    profileBmp = 'Images/Debug/Profile.bmp'
    def __init__(self, editor):
        PersistentController.__init__(self, editor, EditorModels.ModuleModel,
            DefaultViews=(PySourceView.PythonSourceView, EditorViews.ExploreView),
            AdditionalViews=(EditorViews.HierarchyView, 
                             EditorViews.ModuleDocView, EditorViews.ToDoView, 
                             OGLViews.UMLView, CVSExplorer.CVSConflictsView, 
                             SourceViews.PythonDisView) )

        self.activeApp = None

        EVT_MENU(self.editor, EditorHelper.wxID_MODULEPROFILE, self.OnProfile)
        EVT_MENU(self.editor, EditorHelper.wxID_MODULECHECKSOURCE, self.OnCheckSource)
        EVT_MENU(self.editor, EditorHelper.wxID_MODULERUNAPP, self.OnRunApp)
        EVT_MENU(self.editor, EditorHelper.wxID_MODULERUN, self.OnRun)
        EVT_MENU(self.editor, EditorHelper.wxID_MODULERUNPARAMS, self.OnRunParams)
        EVT_MENU(self.editor, EditorHelper.wxID_MODULEDEBUG, self.OnDebug)
        EVT_MENU(self.editor, EditorHelper.wxID_MODULEDEBUGPARAMS, self.OnDebugParams)
        EVT_MENU(self.editor, EditorHelper.wxID_MODULEDEBUGSTEPIN, self.OnDebugStepIn)
        EVT_MENU(self.editor, EditorHelper.wxID_MODULEDEBUGSTEPOVER, self.OnDebugStepOver)
        EVT_MENU(self.editor, EditorHelper.wxID_MODULEDEBUGSTEPOUT, self.OnDebugStepOut)
        EVT_MENU(self.editor, EditorHelper.wxID_EDITORATTACHTODEBUGGER, self.OnAttachToDebugger)
        EVT_MENU(self.editor, EditorHelper.wxID_EDITORSWITCHAPP, self.OnSwitchApp)
        EVT_MENU(self.editor, EditorHelper.wxID_EDITORDIFF, self.OnDiffModules)
        EVT_MENU(self.editor, EditorHelper.wxID_EDITORPYCHECK, self.OnRunPyChecker)
        EVT_MENU(self.editor, EditorHelper.wxID_EDITORCONFPYCHECK, self.OnConfigPyChecker)
        EVT_MENU(self.editor, EditorHelper.wxID_MODULEREINDENT, self.OnReindent)

    def addTools(self, toolbar, model):
        PersistentController.addTools(self, toolbar, model)
        toolbar.AddSeparator()
        addTool(self.editor, toolbar, self.profileBmp, 'Profile', self.OnProfile)
        addTool(self.editor, toolbar, self.compileBmp, 'Check source', self.OnCheckSource)
        if hasattr(model, 'app') and model.app:
            addTool(self.editor, toolbar, self.runAppBmp, 'Run application', self.OnRunApp)
        addTool(self.editor, toolbar, self.runBmp, 'Run module', self.OnRun)
        addTool(self.editor, toolbar, self.debugBmp, 'Debug module', self.OnDebug)

    def addMenus(self, menu, model):
        accls = PersistentController.addMenus(self, menu, model)
        menu.Append(-1, '-')
        if hasattr(model, 'app') and model.app:
            self.addMenu(menu, EditorHelper.wxID_MODULERUNAPP, 'Run application', accls, (keyDefs['RunApp']))
        self.addMenu(menu, EditorHelper.wxID_MODULERUN, 'Run module', accls, (keyDefs['RunMod']))
        self.addMenu(menu, EditorHelper.wxID_MODULERUNPARAMS, 'Run module with parameters', accls, ())
        self.addMenu(menu, EditorHelper.wxID_MODULEDEBUG, 'Debug module', accls, (keyDefs['Debug']))
        self.addMenu(menu, EditorHelper.wxID_MODULEDEBUGPARAMS, 'Debug module with parameters', accls, ())
        if Preferences.useDebugger == 'new':
            self.addMenu(menu, EditorHelper.wxID_EDITORATTACHTODEBUGGER, 'Attach to debugger', accls, ())
        self.addMenu(menu, EditorHelper.wxID_MODULEDEBUGSTEPIN, 'Step in', accls, (keyDefs['DebugStep']))
        self.addMenu(menu, EditorHelper.wxID_MODULEDEBUGSTEPOVER, 'Step over', accls, (keyDefs['DebugOver']))
        self.addMenu(menu, EditorHelper.wxID_MODULEDEBUGSTEPOUT, 'Step out', accls, (keyDefs['DebugOut']))
        menu.Append(-1, '-')
        self.addMenu(menu, EditorHelper.wxID_MODULEPROFILE, 'Profile', accls, ())
        self.addMenu(menu, EditorHelper.wxID_MODULECHECKSOURCE, 'Check source', accls, (keyDefs['CheckSource']))
        self.addMenu(menu, EditorHelper.wxID_MODULECYCLOPSE, 'Cyclops', accls, ())
        menu.Append(-1, '-')
        self.addMenu(menu, EditorHelper.wxID_MODULEREINDENT, 'Reindent whole file', accls, ())
        menu.Append(-1, '-')
        if hasattr(model, 'app') and model.app:
            self.addMenu(menu, EditorHelper.wxID_EDITORSWITCHAPP, 'Switch to app', accls, (keyDefs['SwitchToApp']))
        self.addMenu(menu, EditorHelper.wxID_EDITORDIFF, 'Diff modules...', accls, ())
        self.addMenu(menu, EditorHelper.wxID_EDITORPYCHECK, 'Run PyChecker', accls, ())
        self.addMenu(menu, EditorHelper.wxID_EDITORCONFPYCHECK, 'Configure PyChecker', accls, ())
        return accls

    def createModel(self, source, filename, main, saved, modelParent=None):
        return self.Model(source, filename, self.editor, saved, modelParent)

    def createNewModel(self, modelParent=None):
        if modelParent:
            name = self.editor.getValidName(EditorModels.ModuleModel, modelParent.absModulesPaths())
        else:
            name = self.editor.getValidName(EditorModels.ModuleModel)

        model = self.createModel('', name, '', false, modelParent)
        model.transport = self.newFileTransport('', name)
        self.activeApp = modelParent
        
        return model, name

    def afterAddModulePage(self, model):
        if self.activeApp and Preferences.autoAddToApplication:
            self.activeApp.addModule(model.filename, '')

        model.new()

    def OnProfile(self, event):
        model = self.getModel()
        stats, profDir = model.profile()
        resName = 'Profile stats: %s'%time.strftime('%H:%M:%S', time.gmtime(time.time()))
        if not model.views.has_key(resName):
            resultView = self.editor.addNewView(resName,
              ProfileView.ProfileStatsView)
        else:
            resultView = model.views[resName]
        resultView.tabName = resName
        resultView.stats = stats
        resultView.profDir = profDir
        resultView.refresh()
        resultView.focus()

    def OnCheckSource(self, event):
        model = self.getModel()
        if not model.savedAs or model.modified or \
          len(model.viewsModified):
            wxMessageBox('Cannot compile an unsaved or modified module.')
            return
        model.compile()

    def OnRun(self, event):
        model = self.getModel()
        if not model.savedAs: #modified or len(self.model.viewsModified):
            wxMessageBox('Cannot run an unsaved module.')
            return
        model.run()

    def OnRunParams(self, event):
        model = self.getModel()
        if not model.savedAs: #modified or len(self.model.viewsModified):
            wxMessageBox('Cannot run an unsaved module.')
            return
        dlg = wxTextEntryDialog(self.editor, 'Parameters:',
          'Run with parameters', model.lastRunParams)
        try:
            if dlg.ShowModal() == wxID_OK:
                model.lastRunParams = dlg.GetValue()
                model.run(model.lastRunParams)
        finally:
            dlg.Destroy()

    def OnRunApp(self, event):
        model = self.getModel()
        if not model.app.savedAs: #modified or len(self.model.viewsModified):
            wxMessageBox('Cannot run an unsaved application.')
            return
        wxBeginBusyCursor()
        try:
            model.app.run()
        finally:
            wxEndBusyCursor()

    def OnDebug(self, event):
        model = self.getModel()
        if Preferences.useDebugger == 'new':
            model.debug(cont_if_running=1, cont_always=0, temp_breakpoint=None)
        elif Preferences.useDebugger == 'old':
            if not model.savedAs or model.modified or \
              len(model.viewsModified):
                wxMessageBox('Cannot debug an unsaved or modified module.')
                return
            model.debug()
            
            if not self.model.savedAs or self.model.modified or \
              len(self.model.viewsModified):
                wxMessageBox('Cannot debug an unsaved or modified module.')
                return
        

    def OnDebugParams(self, event):
        model = self.getModel()
        if not model.savedAs or model.modified or \
          len(model.viewsModified):
            wxMessageBox('Cannot debug an unsaved or modified module.')
            return
        dlg = wxTextEntryDialog(self.editor, 'Parameters:',
          'Debug with parameters', model.lastDebugParams)
        try:
            if dlg.ShowModal() == wxID_OK:
                model.lastDebugParams = dlg.GetValue()
                model.debug(methodparse.safesplitfields(model.lastDebugParams, ' '))
        finally:
            dlg.Destroy()

    def OnDebugStepIn(self, event):
        if self.editor.debugger:
            self.editor.debugger.OnStep(event)

    def OnDebugStepOver(self, event):
        if self.editor.debugger:
            self.editor.debugger.OnOver(event)

    def OnDebugStepOut(self, event):
        if self.editor.debugger:
            self.editor.debugger.OnOut(event)

    def OnSwitchApp(self, event):
        model = self.getModel()
        if model and isinstance(model, EditorModels.ModuleModel) and model.app:
            # does this ensure correct app is reconnected?
            appmodel = self.editor.openOrGotoModule(model.app.filename)
            appmodel.views['Application'].focus()

    def OnDiffModules(self, event):
        model = self.getModel()
        if model:
            fn = self.editor.openFileDlg()
            if fn:
                model.diff(fn)

    def OnRunPyChecker(self, event):
        model = self.getModel()
        if model:
            cwd = os.path.abspath(os.getcwd())
            newCwd = os.path.dirname(model.filename)
            os.chdir(newCwd)
            oldErr = sys.stderr
            oldSysPath = sys.path[:]
            try:
                sys.path.append(Preferences.pyPath)
                cmd = '"%s" "%s" %s'%(sys.executable,
                      os.path.join(Preferences.pyPath, 'ExternalLib',
                      'PyChecker', 'checker_custom.py'),
                      os.path.basename(model.filename))

                ProcessModuleRunner(self.editor.erroutFrm, model.app,
                      newCwd).run(cmd, ErrorStack.PyCheckerErrorParser,
                      'PyChecker', 'Warning', true)
            finally:
                sys.path = oldSysPath
                sys.stderr = oldErr
                os.chdir(cwd)

    def OnConfigPyChecker(self, event):
        model = self.getModel()
        if model:
            home = os.environ.get('HOME')
            if home:
                appDir = home
                appConfig = home+'/.pycheckrc'
            else:
                appDir = os.path.dirname(model.filename)
                appConfig = appDir+'/.pycheckrc'
            if not os.path.exists(appConfig):
                dlg = wxMessageDialog(self.editor, 'The PyChecker configuration file '
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
            SourceBasedPrefColNode('PyChecker', ('*',), appConfig, -1, None).open(self.editor)

    def OnCyclops(self, event):
        model = self.getModel()
        if model:
            wxBeginBusyCursor()
            try:
                report = model.cyclops()
            finally:
                wxEndBusyCursor()
    
            resName = 'Cyclops report: %s'%time.strftime('%H:%M:%S', time.gmtime(time.time()))
            if not model.views.has_key(resName):
                resultView = self.editor.addNewView(resName, EditorViews.CyclopsView)
            else:
                resultView = model.views[resName]
            resultView.tabName = resName
            resultView.report = report
            resultView.refresh()
            resultView.focus()

    def OnReindent(self, event):
        model = self.getModel()
        if model:
            model.reindent()

    def OnAttachToDebugger(self, event):
        # Attach dialog code here
        from Debugger.RemoteDialog import create
        create(self.editor).ShowModal()



class AppController(ModuleController):
    saveAllBmp = 'Images/Editor/SaveAll.bmp'
    def __init__(self, editor):
        ModuleController.__init__(self, editor)
        self.Model = EditorModels.AppModel, 
        self.DefaultViews = (AppViews.AppView,) + self.DefaultViews
        self.AdditionalViews = (AppViews.AppModuleDocView, EditorViews.ToDoView, 
                                OGLViews.ImportsView, 
                                CVSExplorer.CVSConflictsView, 
                                AppViews.AppTimeTrackView, 
                                AppViews.AppREADME_TIFView, 
                                AppViews.AppCHANGES_TIFView, 
                                AppViews.AppTODO_TIFView, 
                                AppViews.AppBUGS_TIFView)

        EVT_MENU(self.editor, EditorHelper.wxID_APPSAVEALL, self.OnSaveAll)
        EVT_MENU(self.editor, EditorHelper.wxID_APPCMPAPPS, self.OnCmpApps)
        EVT_MENU(self.editor, EditorHelper.wxID_APPCRASHLOG, self.OnCrashLog)

    def addTools(self, toolbar, model):
        ModuleController.addTools(self, toolbar, model)
        toolbar.AddSeparator()
        addTool(self.editor, toolbar, self.saveAllBmp, 'Save modified modules', self.OnSaveAll)

    def addMenus(self, menu, model):
        accls = ModuleController.addMenus(self, menu, model)
        menu.Append(-1, '-')
        self.addMenu(menu, EditorHelper.wxID_APPCMPAPPS, 'Compare apps', accls, ())
        self.addMenu(menu, EditorHelper.wxID_APPCRASHLOG, 'View crash log as traceback', accls, ())
        return accls

    def createModel(self, source, filename, main, saved, modelParent=None):
        return EditorModels.AppModel(source, filename, main, self.editor, 
              saved, self.editor.modules)

    def createNewModel(self, modelParent=None):
        appName = self.editor.getValidName(EditorModels.AppModel)
        appModel = self.createModel('', appName, appName[:-3], false)
        appModel.transport = self.newFileTransport(appName[:-3], appName)

        return appModel, appName

    def afterAddModulePage(self, model):
        frmMod = self.editor.addNewPage('Frame', FrameController, model)

        frmNme = os.path.splitext(os.path.basename(frmMod.filename))[0]
        model.new(frmNme)

    def OnSaveAll(self, event):
        model = self.getModel()
        if model:
            for modulePage in self.editor.modules.values():
                mod = modulePage.model
                if mod != model:
                    if hasattr(mod, 'app') and mod.app == model and \
                      (mod.modified or len(mod.viewsModified)):
                        if len(mod.viewsModified):
                            mod.refreshFromViews()
                        modulePage.saveOrSaveAs()
                else:
                    appModPage = modulePage
            appModPage.saveOrSaveAs()


    def OnCmpApps(self, event):
        model = self.getModel()
        if model:
            fn = self.editor.openFileDlg()
            if fn:
                model.compareApp(fn)

    def OnCrashLog(self, event):
        model = self.getModel()
        if model:
            wxBeginBusyCursor()
            try:
                model.crashLog()
            finally:
                wxEndBusyCursor()

class BaseFrameController(ModuleController):
    designerBmp = 'Images/Shared/Designer.bmp'
    def __init__(self, editor, Model):
        ModuleController.__init__(self, editor)
        self.Model = Model
        EVT_MENU(self.editor, EditorHelper.wxID_EDITORDESIGNER, self.OnDesigner)

    def addTools(self, toolbar, model):
        ModuleController.addTools(self, toolbar, model)
        toolbar.AddSeparator()
        addTool(self.editor, toolbar, self.designerBmp, 'Frame Designer', self.OnDesigner)

    def addMenus(self, menu, model):
        accls = ModuleController.addMenus(self, menu, model)
        self.addMenu(menu, EditorHelper.wxID_EDITORDESIGNER, 'Frame Designer', accls, (keyDefs['Designer']))
        return accls
    
    def createModel(self, source, filename, main, saved, modelParent=None):
        return self.Model(source, filename, main, self.editor, saved, modelParent)

    def createNewModel(self, modelParent=None):
        if modelParent:
            name = self.editor.getValidName(self.Model, modelParent.absModulesPaths())
        else:
            name = self.editor.getValidName(self.Model)

        model = self.createModel('', name, name[:-3], false, modelParent)
        model.transport = self.newFileTransport('', model.filename)

        self.activeApp = modelParent

        return model, name

    def afterAddModulePage(self, model):
        tempComp = self.Model.companion('', None, None)
        params = tempComp.designTimeSource()
        params['parent'] = 'prnt'
        params['id'] = Utils.windowIdentifier(model.main, '')
        params['title'] = `model.main`

        model.new(params)

        if self.activeApp and self.activeApp.data and Preferences.autoAddToApplication:
            self.activeApp.addModule(model.filename, '')

    def OnDesigner(self, event):
        self.showDesigner()

    def showDesigner(self):
        # Just show if already opened
        modulePage = self.editor.getActiveModulePage()
        model = modulePage.model
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
                    dataView = DataView.DataView(modulePage.notebook, 
                         self.editor.inspector, model, self.editor.compPalette)
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
                    designer = Designer.DesignerView(self.editor, 
                          self.editor.inspector, model, self.editor.compPalette, 
                          model.companion, dataView)
                    model.views['Designer'] = designer
                    designer.refreshCtrl()
                model.views['Designer'].Show(true)
            except:
                if model.views.has_key('Designer'):
                    model.views['Designer'].saveOnClose = false
                    model.views['Designer'].close()

                # If designer got exception before actually being created
                if model.views.has_key('Data'):
                    model.views['Data'].focus()
                    model.views['Data'].saveOnClose = false
                    model.views['Data'].deleteFromNotebook('Source', 'Data')
                raise

            # Make source read only
            model.views['Source'].disableSource(true)

            self.editor.statusBar.setHint('Designer session started.')

        except Exception, error:
            self.editor.statusBar.setHint(\
                'An error occured while opening the Designer: %s'%str(error),
                'Error')
            self.editor.statusBar.progress.SetValue(0)
            raise

class FrameController(BaseFrameController):
    def __init__(self, editor):
        BaseFrameController.__init__(self, editor, EditorModels.FrameModel)
class DialogController(BaseFrameController):
    def __init__(self, editor):
        BaseFrameController.__init__(self, editor, EditorModels.DialogModel)
class MiniFrameController(BaseFrameController):
    def __init__(self, editor):
        BaseFrameController.__init__(self, editor, EditorModels.MiniFrameModel)
class MDIParentController(BaseFrameController):
    def __init__(self, editor):
        BaseFrameController.__init__(self, editor, EditorModels.MDIParentModel)
class MDIChildController(BaseFrameController):
    def __init__(self, editor):
        BaseFrameController.__init__(self, editor, EditorModels.MDIChildModel)

class PackageController(ModuleController):
    def __init__(self, editor):
        ModuleController.__init__(self, editor)
        self.Model = EditorModels.PackageModel
        self.DefaultViews = (EditorViews.PackageView,) + self.DefaultViews

    def createModel(self, source, filename, main, saved, modelParent=None):
        return self.Model(source, filename, self.editor, saved)

    def createNewModel(self, modelParent=None):
        name = '__init__.py'
        filename, success = self.editor.saveAsDlg(name)
        if success:
            model = self.createModel(sourceconst.defPackageSrc, filename, '',
                  false)
            model.transport = self.newFileTransport(name, filename)
            model.save()
            
            return model, filename
        else:
            return None, None

    def new(self):
        pass

    def afterAddModulePage(self, model):
        pass

class SetupController(ModuleController):
    def __init__(self, editor):
        ModuleController.__init__(self, editor)
        self.Model = EditorModels.SetupModuleModel

        EVT_MENU(self.editor, EditorHelper.wxID_SETUPBUILD, self.OnSetupBuild)
        EVT_MENU(self.editor, EditorHelper.wxID_SETUPCLEAN, self.OnSetupClean)
        EVT_MENU(self.editor, EditorHelper.wxID_SETUPINSTALL, self.OnSetupInstall)
        EVT_MENU(self.editor, EditorHelper.wxID_SETUPSDIST, self.OnSetupSDist)
        EVT_MENU(self.editor, EditorHelper.wxID_SETUPBDIST, self.OnSetupBDist)
        EVT_MENU(self.editor, EditorHelper.wxID_SETUPBDIST_WININST, self.OnSetupBDist_WinInst)
        EVT_MENU(self.editor, EditorHelper.wxID_SETUPPY2EXE, self.OnSetupPy2Exe)

    def addMenus(self, menu, model):
        accls = ModuleController.addMenus(self, menu, model)
        menu.AppendSeparator()
        self.addMenu(menu, EditorHelper.wxID_SETUPBUILD, 'setup.py build', accls, ())
        self.addMenu(menu, EditorHelper.wxID_SETUPCLEAN, 'setup.py clean', accls, ())
        self.addMenu(menu, EditorHelper.wxID_SETUPINSTALL, 'setup.py install', accls, ())
        self.addMenu(menu, EditorHelper.wxID_SETUPSDIST, 'setup.py sdist', accls, ())
        self.addMenu(menu, EditorHelper.wxID_SETUPBDIST, 'setup.py bdist', accls, ())
        self.addMenu(menu, EditorHelper.wxID_SETUPBDIST_WININST, 'setup.py bdist_wininst', accls, ())
        menu.AppendSeparator()
        self.addMenu(menu, EditorHelper.wxID_SETUPPY2EXE, 'setup.py py2exe', accls, ())
        return accls

    def createNewModel(self, modelParent=None):
        name = 'setup.py'
        model = self.createModel(sourceconst.defSetup_py, name, '', false)
        model.transport = self.newFileTransport('', name)
        model.new()
        
        return model, name

    def runDistUtilsCmd(self, cmd):
        import ProcessProgressDlg
        cwd = os.path.abspath(os.getcwd())
        os.chdir(os.path.dirname(self.getModel().filename))
        try:
            PD = ProcessProgressDlg.ProcessProgressDlg(self.editor,
              'python setup.py %s'%cmd, 'Running distutil command...', 
              autoClose = false)
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


class TextController(PersistentController):
    def __init__(self, editor):
        PersistentController.__init__(self, editor, EditorModels.TextModel,
            DefaultViews=(SourceViews.TextView,),
            AdditionalViews=() )

class ConfigFileController(TextController):
    def __init__(self, editor):
        TextController.__init__(self, editor)
        self.Model = EditorModels.ConfigFileModel

class CPPController(PersistentController):
    def __init__(self, editor):
        PersistentController.__init__(self, editor, EditorModels.CPPModel,
            DefaultViews=(SourceViews.CPPSourceView, SourceViews.HPPSourceView),
            AdditionalViews=(CVSExplorer.CVSConflictsView,) )

class HTMLFileController(PersistentController):
    def __init__(self, editor):
        PersistentController.__init__(self, editor, EditorModels.HTMLFileModel,
            DefaultViews=(SourceViews.HTMLSourceView,),
            AdditionalViews=(EditorViews.HTMLFileView,) )

class XMLFileController(PersistentController):
    def __init__(self, editor):
        try:
            from Views.XMLView import XMLTreeView
            adtViews = (XMLTreeView,)
        except ImportError:
            adtViews = ()
        PersistentController.__init__(self, editor, EditorModels.XMLFileModel,
            DefaultViews=(XMLSourceView,),
            AdditionalViews=adtViews )

class BitmapFileController(BaseEditorController):
    def __init__(self, editor):
        BaseEditorController.__init__(self, editor, 
            EditorModels.BitmapFileModel, (), ())
        self.docked = false

    def display(self, model):
        from ZopeLib import ImageViewer
        ImageViewer.create(self.editor).showImage(model.filename, model.transport)

class ZopeExportFileController(BaseEditorController):
    def __init__(self, editor):
        BaseEditorController.__init__(self, editor, 
            ZopeEditorModels.ZopeExportFileModel, (), ())
        self.docked = false

    def display(self, model):
        wxMessageBox('This file cannot be opened and must be imported by Zope')
        
# XXX Zope Controllers should create from the palette, Zope Companions should 
# XXX manage only inspection

class ZopeController(PersistentController):
    def __init__(self, editor, Model):
        PersistentController.__init__(self, editor, Model,
            DefaultViews=(), AdditionalViews=() )
    def createModel(self, source, filename, main, saved, transport):
        return self.Model(filename, main, self.editor, saved, transport)

    def createNewModel(self, modelParent=None):
        pass

class MakePyController(BaseEditorController):
    def __init__(self, editor):
        BaseEditorController.__init__(self, editor, None, (), ())
        self.docked = false

    def createNewModel(self, modelParent=None):
        return None, None

    def display(self, model):
        import makepydialog
        dlg = makepydialog.create(self.editor)
        try:
            if dlg.ShowModal() == wxID_OK and dlg.generatedFilename:
                self.editor.openOrGotoModule(dlg.generatedFilename)
        finally:
            dlg.Destroy()

modelControllerReg = {EditorModels.AppModel: AppController,
                      EditorModels.FrameModel: FrameController,
                      EditorModels.DialogModel: DialogController,
                      EditorModels.MiniFrameModel: MiniFrameController,
                      EditorModels.MDIParentModel: MDIParentController,
                      EditorModels.MDIChildModel: MDIChildController,
                      EditorModels.ModuleModel: ModuleController,
                      EditorModels.PackageModel: PackageController,
                      EditorModels.SetupModuleModel: SetupController,
                      EditorModels.TextModel: TextController,
                      EditorModels.ConfigFileModel: ConfigFileController,
                      EditorModels.CPPModel: CPPController,
                      EditorModels.HTMLFileModel: HTMLFileController,
                      EditorModels.XMLFileModel: XMLFileController,
                      ZopeEditorModels.ZopeExportFileModel: ZopeExportFileController,
                      ZopeEditorModels.ZopeBlankEditorModel: ZopeController,
                      ZopeEditorModels.ZopeDocumentModel: ZopeController,
                      ZopeEditorModels.ZopeDTMLDocumentModel: ZopeController,
                      ZopeEditorModels.ZopeDTMLMethodModel: ZopeController,
                      ZopeEditorModels.ZopeSQLMethodModel: ZopeController,
                      ZopeEditorModels.ZopePythonSourceModel: ZopeController,
                      ZopeEditorModels.ZopePythonScriptModel: ZopeController,
                      ZopeEditorModels.ZopePythonMethodModel: ZopeController,
                      ZopeEditorModels.ZopeExternalMethodModel: ZopeController,
                      ZopeEditorModels.ZopeExportFileModel: ZopeController,
                      }

# Register controllers on the New palette
PaletteStore.paletteLists['New'].extend(['wxApp', 'wxFrame', 'wxDialog',
  'wxMiniFrame', 'wxMDIParentFrame', 'wxMDIChildFrame', 'Module', 'Package',
  'Setup', 'Text'])
  
if Utils.IsComEnabled():
    PaletteStore.paletteLists['New'].append('MakePy Dialog')

PaletteStore.newControllers.update({'wxApp': AppController,
                                    'wxFrame': FrameController,
                                    'wxDialog': DialogController,
                                    'wxMiniFrame': MiniFrameController,
                                    'wxMDIParentFrame': MDIParentController,
                                    'wxMDIChildFrame': MDIChildController,
                                    'Module': ModuleController,
                                    'Package': PackageController,
                                    'Setup': SetupController,
                                    'Text': TextController})

if Utils.IsComEnabled():
    PaletteStore.newControllers['MakePy Dialog'] = MakePyController
            