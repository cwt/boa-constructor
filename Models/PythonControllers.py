#-----------------------------------------------------------------------------
# Name:        PythonControllers.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2002/02/09
# RCS-ID:      $Id$
# Copyright:   (c) 2002
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Models.PythonControllers'

import os, string, sys, time
import marshal, stat

from wxPython.wx import *

import Preferences, Utils
from Preferences import keyDefs

import PaletteStore

import Controllers
from Controllers import SourceController, addTool
import EditorHelper, EditorModels, PythonEditorModels

from Views import EditorViews, AppViews, SourceViews, PySourceView, OGLViews, ProfileView

from ModRunner import ProcessModuleRunner
import ErrorStack

import methodparse, sourceconst

(wxID_MODULEPROFILE, wxID_MODULECHECKSOURCE, wxID_MODULERUNAPP, wxID_MODULERUN,
 wxID_MODULEDEBUGAPP, wxID_MODULEDEBUG,
 wxID_MODULEDEBUGSTEPIN, wxID_MODULEDEBUGSTEPOVER, wxID_MODULEDEBUGSTEPOUT,
 wxID_MODULECYCLOPSE, wxID_MODULEREINDENT, wxID_MODULETABNANNY,
 wxID_MODULEIMPORTINSHELL, wxID_MODULERELOADINSHELL,
 wxID_MODULEPYCHECK, wxID_MODULECONFPYCHECK,
 wxID_MODULEDIFF, wxID_MODULESWITCHAPP, wxID_MODULEADDTOAPP,
 wxID_MODULEATTACHTODEBUGGER, wxID_MODULEASSOSWITHAPP, wxID_MODULESETPARAMS,
) = Utils.wxNewIds(22)

# TODO: Profile, Cyclops and other file runners should use the command-line
# TODO: parameters whenever possible

class ModuleController(SourceController):
    activeApp = None

    runAppBmp = 'Images/Debug/RunApp.png'
    runBmp = 'Images/Debug/Run.png'
    compileBmp = 'Images/Debug/Compile.png'
    debugBmp = 'Images/Debug/Debug.png'
    profileBmp = 'Images/Debug/Profile.png'

    Model = PythonEditorModels.ModuleModel
    DefaultViews    = [PySourceView.PythonSourceView, EditorViews.ExploreView]
    AdditionalViews = [EditorViews.HierarchyView, EditorViews.ModuleDocView,
                       EditorViews.ToDoView, OGLViews.UMLView,
                       SourceViews.PythonDisView] + SourceController.AdditionalViews

    def addEvts(self):
        SourceController.addEvts(self)
        self.addEvt(wxID_MODULEPROFILE, self.OnProfile)
        self.addEvt(wxID_MODULECYCLOPSE, self.OnCyclops)
        self.addEvt(wxID_MODULECHECKSOURCE, self.OnCheckSource)
        self.addEvt(wxID_MODULESETPARAMS, self.OnSetRunParams)
        self.addEvt(wxID_MODULERUNAPP, self.OnRunApp)
        self.addEvt(wxID_MODULERUN, self.OnRun)
        self.addEvt(wxID_MODULEDEBUGAPP, self.OnDebugApp)
        self.addEvt(wxID_MODULEDEBUG, self.OnDebug)
        self.addEvt(wxID_MODULEDEBUGSTEPIN, self.OnDebugStepIn)
        self.addEvt(wxID_MODULEDEBUGSTEPOVER, self.OnDebugStepOver)
        self.addEvt(wxID_MODULEDEBUGSTEPOUT, self.OnDebugStepOut)
        self.addEvt(wxID_MODULEATTACHTODEBUGGER, self.OnAttachToDebugger)
        self.addEvt(wxID_MODULESWITCHAPP, self.OnSwitchApp)
        self.addEvt(wxID_MODULEADDTOAPP, self.OnAddToOpenApp)
        self.addEvt(wxID_MODULEASSOSWITHAPP, self.OnAssosiateWithOpenApp)
        self.addEvt(wxID_MODULEDIFF, self.OnDiffModules)
        self.addEvt(wxID_MODULEPYCHECK, self.OnRunPyChecker)
        self.addEvt(wxID_MODULECONFPYCHECK, self.OnConfigPyChecker)
        self.addEvt(wxID_MODULEREINDENT, self.OnReindent)
        self.addEvt(wxID_MODULETABNANNY, self.OnTabNanny)
        self.addEvt(wxID_MODULEIMPORTINSHELL, self.OnImportInShell)
        self.addEvt(wxID_MODULERELOADINSHELL, self.OnReloadInShell)

    def addTools(self, toolbar, model):
        SourceController.addTools(self, toolbar, model)
        toolbar.AddSeparator()
        addTool(self.editor, toolbar, self.profileBmp, 'Profile', self.OnProfile)
        addTool(self.editor, toolbar, self.compileBmp, 'Check source', self.OnCheckSource)
        if hasattr(model, 'app') and model.app:
            addTool(self.editor, toolbar, self.runAppBmp, 'Run application', self.OnRunApp)
        addTool(self.editor, toolbar, self.runBmp, 'Run module', self.OnRun)
        addTool(self.editor, toolbar, self.debugBmp, 'Debug application', self.OnDebugApp)

    def addMenus(self, menu, model):
        accls = SourceController.addMenus(self, menu, model)
        menu.Append(-1, '-')
        self.addMenu(menu, wxID_MODULEIMPORTINSHELL, 'Import module into Shell', accls, ())
        self.addMenu(menu, wxID_MODULERELOADINSHELL, 'Reload module in Shell', accls, ())
        menu.Append(-1, '-')
        self.addMenu(menu, wxID_MODULESETPARAMS, 'Set command-line parameters', accls, ())
        self.addMenu(menu, wxID_MODULERUNAPP, 'Run application', accls, (keyDefs['RunApp']))
        self.addMenu(menu, wxID_MODULERUN, 'Run module', accls, (keyDefs['RunMod']))
        self.addMenu(menu, wxID_MODULEDEBUGAPP, 'Debug application', accls, (keyDefs['Debug']))
        self.addMenu(menu, wxID_MODULEDEBUG, 'Debug module', accls, ())
        self.addMenu(menu, wxID_MODULEATTACHTODEBUGGER, 'Attach to debugger', accls, ())
        self.addMenu(menu, wxID_MODULEDEBUGSTEPIN, 'Step in', accls, (keyDefs['DebugStep']))
        self.addMenu(menu, wxID_MODULEDEBUGSTEPOVER, 'Step over', accls, (keyDefs['DebugOver']))
        self.addMenu(menu, wxID_MODULEDEBUGSTEPOUT, 'Step out', accls, (keyDefs['DebugOut']))
        menu.Append(-1, '-')
        self.addMenu(menu, wxID_MODULEPROFILE, 'Profile', accls, ())
        self.addMenu(menu, wxID_MODULECHECKSOURCE, 'Check source', accls, (keyDefs['CheckSource']))
        self.addMenu(menu, wxID_MODULECYCLOPSE, 'Cyclops', accls, ())
        menu.Append(-1, '-')
        self.addMenu(menu, wxID_MODULEREINDENT, 'Reindent whole file', accls, ())
        menu.Append(-1, '-')
        if hasattr(model, 'app') and model.app:
            self.addMenu(menu, wxID_MODULESWITCHAPP, 'Switch to app', accls, (keyDefs['SwitchToApp']))
        else:
            self.addMenu(menu, wxID_MODULEADDTOAPP, 'Add to an open application', accls, ())
            self.addMenu(menu, wxID_MODULEASSOSWITHAPP, 'Associate with an open application', accls, ())
        self.addMenu(menu, wxID_MODULEDIFF, 'NDiff modules...', accls, ())
        self.addMenu(menu, wxID_MODULEPYCHECK, 'Run PyChecker', accls, ())
        self.addMenu(menu, wxID_MODULECONFPYCHECK, 'Configure PyChecker', accls, ())
        return accls

    def createModel(self, source, filename, main, saved, modelParent=None):
        return self.Model(source, filename, self.editor, saved, modelParent)

    def createNewModel(self, modelParent=None):
        if modelParent:
            name = self.editor.getValidName(PythonEditorModels.ModuleModel, modelParent.absModulesPaths())
        else:
            name = self.editor.getValidName(PythonEditorModels.ModuleModel)

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
        if self.checkUnsaved(model): return

        statFile, modtime, profDir = model.profile()

        if modtime is not None:
            curmodtime = os.stat(statFile)[stat.ST_MTIME]
            if curmodtime == modtime:
                wxMessageBox('Stats file date unchanged!')
                return
        elif not os.path.exists(statFile):
            wxMessageBox('Stats file not found')
            return

        self.editor.setStatus('Loading stats...')
        stats = marshal.load(open(statFile, 'rb'))

        #stats, profDir = model.profile()
        resName = 'Profile stats: %s'%time.strftime('%H:%M:%S', time.gmtime(time.time()))
        if not model.views.has_key(resName):
            resultView = self.editor.addNewView(resName,
              ProfileView.ProfileStatsView)
        else:
            resultView = model.views[resName]
        resultView.tabName = resName
        resultView.stats = stats
        resultView.profDir = profDir
        self.editor.setStatus('Refreshing view...')
        resultView.refresh()
        resultView.focus()
        self.editor.setStatus('Profiling complete.')

    def OnCheckSource(self, event):
        model = self.getModel()
        self.editor.setStatus('Compiling...')
        if model.compile():
            self.editor.setStatus('There were errors', 'Warning')
        else:
            self.editor.setStatus('Compiled successfully')

        if Preferences.runPyLintOnCheckSource:
            self.editor.setStatus('Running lint...')
            warnings = model.runLint()
            if warnings and self.editor.erroutFrm:
                self.editor.erroutFrm.updateCtrls(warnings, [], 'Warning',
                    os.path.dirname(model.assertLocalFile()))
                self.editor.erroutFrm.display(len(warnings))
            self.editor.setStatus('Lint completed')

    def OnSetRunParams(self, event):
        model = self.getModel()
        dlg = wxTextEntryDialog(self.editor, 'Parameters:',
          'Command-line parameters', model.lastRunParams)
        try:
            if dlg.ShowModal() == wxID_OK:
                model.lastRunParams = dlg.GetValue()
                # update running debuggers debugging this module
                debugger = self.editor.debugger
                if debugger and debugger.filename == model.localFilename():
                    if model.lastRunParams:
                        params = methodparse.safesplitfields(model.lastRunParams, ' ')
                    else:
                        params = []
                    self.editor.debugger.setParams(params)


        finally:
            dlg.Destroy()

    def OnRun(self, event):
        self.OnRunApp(event, self.getModel())

    def OnRunApp(self, event=None, runModel=None):
        model = self.getModel()
        if self.checkUnsaved(model): return
        wxBeginBusyCursor()
        try:
            if runModel is None:
                if model.app:
                    runModel = model.app
                else:
                    runModel = model
            runModel.run(runModel.lastRunParams)
        finally:
            wxEndBusyCursor()

    def OnDebug(self, event):
        self.OnDebugApp(event, self.getModel())

    def OnDebugApp(self, event=None, debugModel=None):
        model = self.getModel()
        if self.checkUnsaved(model): return
        if debugModel is None:
            if model.app:
                debugModel = model.app
            else:
                debugModel = model

        if debugModel.lastRunParams:
            params = methodparse.safesplitfields(debugModel.lastRunParams, ' ')
        else:
            params = None
        debugModel.debug(params, cont_if_running=1)

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
        if model and isinstance(model, PythonEditorModels.ModuleModel) and model.app:
            # does this ensure correct app is reconnected?
            appmodel, controller = self.editor.openOrGotoModule(model.app.filename)

            if appmodel.prevSwitch and appmodel.prevSwitch.model:
                appmodel.prevSwitch.focus()
                appmodel.prevSwitch = None
            else:
                appmodel.views['Application'].focus()

    def OnDiffModules(self, event=None, filename=''):
        model = self.getModel()
        if model:
            if self.checkUnsaved(model): return
            if not filename:
                filename = self.editor.openFileDlg()
            if filename:
                filename = model.assertLocalFile(filename)
                tbName = 'Diff with : '+filename
                if not model.views.has_key(tbName):
                    from Views.DiffView import PythonSourceDiffView
                    resultView = self.editor.addNewView(tbName, PythonSourceDiffView)
                else:
                    resultView = model.views[tbName]

                resultView.tabName = tbName
                resultView.diffWith = filename
                resultView.refresh()
                resultView.focus()

    def OnRunPyChecker(self, event):
        model = self.getModel()
        if model:
            if self.checkUnsaved(model): return
            filename = model.assertLocalFile()
            cwd = os.path.abspath(os.getcwd())
            newCwd = os.path.dirname(filename)
            os.chdir(newCwd)
            oldErr = sys.stderr
            oldSysPath = sys.path[:]
            try:
                sys.path.append(Preferences.pyPath)
                cmd = '"%s" "%s" %s'%(sys.executable,
                      os.path.join(Preferences.pyPath, 'ExternalLib',
                      'PyChecker', 'checker_custom.py'),
                      os.path.basename(filename))

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
                filename = model.assertLocalFile()
                appDir = os.path.dirname(filename)
                appConfig = appDir+'/.pycheckrc'
            if not os.path.exists(appConfig):
                dlg = wxMessageDialog(self.editor, 'The PyChecker configuration file '
                  'can not be found. Copy the default file here?',
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
            if self.checkUnsaved(model): return
            self.editor.setStatus('Running Cyclopse on %s ...'%model.filename)
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

    def OnTabNanny(self, event):
        model = self.getModel()
        if model:
            model.tabnanny()

    def OnAttachToDebugger(self, event):
        # Attach dialog code here
        from Debugger.RemoteDialog import create
        rmtDlg = create(self.editor)
        rmtDlg.ShowModal()
        rmtDlg.Destroy()

    def chooseOpenApp(self, model, msg, capt):
        openApps = self.editor.getAppModules()
        if not openApps:
            wxMessageBox('No open applications.', style=wxICON_ERROR)
            return
        chooseApps = {}
        for app in openApps:
            chooseApps[os.path.basename(app.filename)] = app
        dlg = wxSingleChoiceDialog(self.editor, msg, capt, chooseApps.keys())
        try:
            if dlg.ShowModal() == wxID_OK:
                return chooseApps[dlg.GetStringSelection()]
            else:
                return None
        finally:
            dlg.Destroy()

    def OnAddToOpenApp(self, event):
        model = self.getModel()
        if model:
            app = self.chooseOpenApp(model,
                  'Select application to add the current file to',
                  'Add to Application')

            if model.savedAs: src = None
            else: src = model.getDataAsLines()

            app.addModule(model.filename, '', src)
            model.app = app
            self.editor.setupToolBar()

    def OnAssosiateWithOpenApp(self, event):
        model = self.getModel()
        if model:
            app = self.chooseOpenApp(model,
                  'Select application to associate the current file with',
                  'Associate with Application')

            model.app = app
            self.editor.setupToolBar()


    def OnSave(self, event):
        SourceController.OnSave(self, event)
        if Preferences.checkSourceOnSave:
            self.OnCheckSource(event)

    def OnSaveAs(self, event):
        SourceController.OnSaveAs(self, event)
        if Preferences.checkSourceOnSave:
            self.OnCheckSource(event)

    def OnImportInShell(self, event):
        model = self.getModel()
        if model:
            msg, status  = model.importInShell()
            self.editor.setStatus(msg, status)

    def OnReloadInShell(self, event):
        model = self.getModel()
        if model:
            msg, status  = model.reloadInShell()
            self.editor.setStatus(msg, status)


(wxID_APPSAVEALL, wxID_APPCMPAPPS, wxID_APPCRASHLOG) = Utils.wxNewIds(3)

class BaseAppController(ModuleController):
    saveAllBmp = 'Images/Editor/SaveAll.png'

    DefaultViews    = [AppViews.AppView] + ModuleController.DefaultViews
    AdditionalViews = [AppViews.AppModuleDocView, EditorViews.ToDoView,
                       OGLViews.ImportsView, EditorViews.CVSConflictsView,
                       AppViews.AppREADME_TIFView, AppViews.AppCHANGES_TIFView,
                       AppViews.AppTODO_TIFView, AppViews.AppBUGS_TIFView]

    def addEvts(self):
        ModuleController.addEvts(self)
        self.addEvt(wxID_APPSAVEALL, self.OnSaveAll)
        self.addEvt(wxID_APPCMPAPPS, self.OnCmpApps)
        self.addEvt(wxID_APPCRASHLOG, self.OnCrashLog)

    def addTools(self, toolbar, model):
        ModuleController.addTools(self, toolbar, model)
        toolbar.AddSeparator()
        addTool(self.editor, toolbar, self.saveAllBmp, 'Save modified modules', self.OnSaveAll)

    def addMenus(self, menu, model):
        accls = ModuleController.addMenus(self, menu, model)
        menu.Append(-1, '-')
        self.addMenu(menu, wxID_APPSAVEALL, 'Save modified modules', accls, ())
        self.addMenu(menu, wxID_APPCMPAPPS, 'Compare apps', accls, ())
        self.addMenu(menu, wxID_APPCRASHLOG, 'View crash log as traceback', accls, ())
        return accls

    def createModel(self, source, filename, main, saved, modelParent=None):
        return self.Model(source, filename, main, self.editor, saved,
           self.editor.modules)

    def createNewModel(self, modelParent=None):
        appName = self.editor.getValidName(self.Model)
        appModel = self.createModel('', appName, appName[:-3], false)
        appModel.transport = self.newFileTransport(appName[:-3], appName)

        return appModel, appName

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
                filename = model.assertLocalFile(fn)
                tbName = 'App. Compare : '+filename
                if not model.views.has_key(tbName):
                    from Views.AppViews import AppCompareView
                    resultView = self.editor.addNewView(tbName, AppCompareView)
                else:
                    resultView = model.views[tbName]

                resultView.tabName = tbName
                resultView.compareTo = filename
                resultView.refresh()
                resultView.focus()

    def OnCrashLog(self, event):
        model = self.getModel()
        if model:
            wxBeginBusyCursor()
            try:
                model.crashLog()
            finally:
                wxEndBusyCursor()

class PyAppController(BaseAppController):
    Model = PythonEditorModels.PyAppModel

    def afterAddModulePage(self, model):
        model.new()

class PackageController(ModuleController):
    Model = PythonEditorModels.PackageModel
    DefaultViews = [EditorViews.PackageView] + ModuleController.DefaultViews
    AdditionalViews = ModuleController.AdditionalViews + [OGLViews.ImportsView]

    def createModel(self, source, filename, main, saved, modelParent=None):
        return self.Model(source, filename, self.editor, saved)

    def createNewModel(self, modelParent=None):
        name = '__init__.py'
        filename, success = self.editor.saveAsDlg(name, dont_pop=1)
        if success:
            model = self.createModel(sourceconst.defPackageSrc, filename, '', false)
            model.transport = self.newFileTransport(name, filename)
            model.save()

            return model, filename
        else:
            return None, None

    def new(self):
        pass

    def afterAddModulePage(self, model):
        pass

(wxID_SETUPINSTALL, wxID_SETUPCLEAN, wxID_SETUPBUILD,
 wxID_SETUPSDIST, wxID_SETUPBDIST, wxID_SETUPBDIST_WININST, wxID_SETUPBDIST_RPM,
 wxID_SETUPPY2EXE, wxID_SETUPPARAMS,
) = Utils.wxNewIds(9)

class SetupController(ModuleController):
    Model = PythonEditorModels.SetupModuleModel

    DefaultViews = ModuleController.DefaultViews + [EditorViews.DistUtilManifestView]

    def addEvts(self):
        ModuleController.addEvts(self)
        self.addEvt(wxID_SETUPPARAMS, self.OnSetupParams)
        self.addEvt(wxID_SETUPBUILD, self.OnSetupBuild)
        self.addEvt(wxID_SETUPCLEAN, self.OnSetupClean)
        self.addEvt(wxID_SETUPINSTALL, self.OnSetupInstall)
        self.addEvt(wxID_SETUPSDIST, self.OnSetupSDist)
        self.addEvt(wxID_SETUPBDIST, self.OnSetupBDist)
        self.addEvt(wxID_SETUPBDIST_WININST, self.OnSetupBDist_WinInst)
        self.addEvt(wxID_SETUPBDIST_RPM, self.OnSetupBDist_RPM)

        # detect py2exe
        import imp
        try: imp.find_module('py2exe')
        except ImportError: self._py2exe = false
        else:
            self._py2exe = true
            self.addEvt(wxID_SETUPPY2EXE, self.OnSetupPy2Exe)

    def addMenus(self, menu, model):
        accls = ModuleController.addMenus(self, menu, model)
        menu.AppendSeparator()
        self.addMenu(menu, wxID_SETUPPARAMS, 'setup.py with parameters', accls, ())
        self.addMenu(menu, wxID_SETUPBUILD, 'setup.py build', accls, ())
        self.addMenu(menu, wxID_SETUPCLEAN, 'setup.py clean', accls, ())
        self.addMenu(menu, wxID_SETUPINSTALL, 'setup.py install', accls, ())
        self.addMenu(menu, wxID_SETUPSDIST, 'setup.py sdist', accls, ())
        self.addMenu(menu, wxID_SETUPBDIST, 'setup.py bdist', accls, ())
        if wxPlatform == '__WXGTK__':
            self.addMenu(menu, wxID_SETUPBDIST_RPM, 'setup.py bdist_rpm', accls, ())
        else:
            self.addMenu(menu, wxID_SETUPBDIST_WININST, 'setup.py bdist_wininst', accls, ())

        if self._py2exe:
            menu.AppendSeparator()
            self.addMenu(menu, wxID_SETUPPY2EXE, 'setup.py py2exe', accls, ())
        return accls

    def createNewModel(self, modelParent=None):
        name = 'setup.py'
        model = self.createModel(sourceconst.defSetup_py, name, '', false)
        model.transport = self.newFileTransport('', name)
        model.new()

        return model, name

    def runDistUtilsCmd(self, cmd):
        model = self.getModel()
        if not model.savedAs:
            wxLogError('Cannot run distutils on an unsaved module')
            return

        cwd = os.path.abspath(os.getcwd())
        filename = model.assertLocalFile()
        filedir = os.path.dirname(filename)
        os.chdir(filedir)
        try:
            ProcessModuleRunner(self.editor.erroutFrm, model.app, filedir).run(\
            '"%s" setup.py %s'%(`Preferences.pythonInterpreterPath`[1:-1], cmd),
            caption='Running distutil command...')
##            PD = ProcessProgressDlg.ProcessProgressDlg(self.editor,
##              '"%s" setup.py %s'%(`Preferences.pythonInterpreterPath`[1:-1], cmd),
##              'Running distutil command...',
##              autoClose = false)
##            try:
##                if PD.ShowModal() == wxOK:
##
##            finally: PD.Destroy()
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
    def OnSetupBDist_RPM(self, event):
        self.runDistUtilsCmd('bdist_rpm')
    def OnSetupParams(self, event):
        dlg = wxTextEntryDialog(self.editor, 'Edit setup.py arguments', 'Distutils setup', '')
        try:
            if dlg.ShowModal() == wxID_OK:
                self.runDistUtilsCmd(dlg.GetValue())
        finally:
            dlg.Destroy()

    def OnSetupPy2Exe(self, event):
        self.runDistUtilsCmd('py2exe')

#-------------------------------------------------------------------------------

Preferences.paletteTitle = Preferences.paletteTitle +' - Python IDE'
Controllers.headerStartChar['.py'] = '#'
Controllers.identifyHeader['.py'] = PythonEditorModels.identifyHeader
Controllers.identifySource['.py'] = PythonEditorModels.identifySource

Controllers.modelControllerReg.update({
      PythonEditorModels.PyAppModel: PyAppController,
      PythonEditorModels.ModuleModel: ModuleController,
      PythonEditorModels.PackageModel: PackageController,
      PythonEditorModels.SetupModuleModel: SetupController,
     })

PaletteStore.newControllers.update({'PythonApp': PyAppController,
                                    'Module': ModuleController,
                                    'Package': PackageController,
                                    'Setup': SetupController,
                                   })

PaletteStore.paletteLists['New'].extend(['PythonApp', 'Module', 'Package',
  'Setup'])
