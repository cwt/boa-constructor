#----------------------------------------------------------------------
# Name:        EditorModels.py
# Purpose:     Model classes usually representing different types of
#              source code
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

# Behind the screen
# beyond interpretation
# essence

""" The model classes represent different types of source code files,
    Different views can be connected to a model  """

# XXX form inheritance

import string, os, sys, re, pprint
from time import time, gmtime, strftime
from stat import *
import profile
from thread import start_new_thread

from wxPython import wx

# XXX
import PaletteMapping

import Preferences, Utils, EditorHelper, ErrorStack
from Companions import Companions
from Views.DiffView import PythonSourceDiffView
from Views.AppViews import AppCompareView
from Views import ObjCollection
from PrefsKeys import keyDefs
from Debugger import Debugger
from Utils import AddToolButtonBmpIS
import moduleparse, relpath
from sourceconst import *

# Special import for the profiler
import wxPython
from PhonyApp import wxProfilerPhonyApp
from EditorHelper import *

true = 1;false = 0

class EditorModel:
    defaultName = 'abstract'
    bitmap = 'None'
    imgIdx = -1
    closeBmp = 'Images/Editor/Close.bmp'
    objCnt = 0
    def     __init__(self, name, data, editor, saved):
        self.active = false
        self.data = data
        self.savedAs = saved
        self.filename = name
        self.editor = editor
        self.transport = None

        self.views = {}
        self.modified = not saved
        self.viewsModified = []

##        self.objCnt = self.objCnt + 1

##    def __del__(self):
##        self.objCnt = self.objCnt - 1
##        print '__del__', self.__class__.__name__

    def destroy(self):
#        print 'destroy', self.__class__.__name__
#        for i in self.views.values():
#            print sys.getrefcount(i)

        del self.views
        del self.viewsModified
        del self.editor

    def addTools(self, toolbar):
        AddToolButtonBmpIS(self.editor, toolbar, self.closeBmp, 'Close', self.editor.OnClosePage)

    def addMenu(self, menu, wId, label, accls, code = ()):
        menu.Append(wId, label + (code and '     <'+code[2]+'>' or ''))
        if code:
            accls.append((code[0], code[1], wId),)

    def addMenus(self, menu):
        accls = []
        self.addMenu(menu, EditorHelper.wxID_EDITORCLOSEPAGE, 'Close', accls, (keyDefs['Close']))
        self.addMenu(menu, EditorHelper.wxID_EDITORRELOAD, 'Reload', accls, ())
        return accls

    def reorderFollowingViewIdxs(self, idx):
        for view in self.views.values():
            if view.pageIdx > idx:
                view.pageIdx = view.pageIdx - 1

    def getDataAsLines(self):
        return string.split(self.data, '\012')
    def setDataFromLines(self, lines):
        self.data = string.join(lines, '\012')

    def load(self, notify = true):
        """ Loads contents of data from file specified by self.filename.
            Note: Load not really used currently objects are constructed
                  with their data as parameter """
        if not self.transport:
            raise 'No transport for loading'

        self.data = self.transport.load()
##        f = open(self.filename, 'r')
##        self.data = f.read()
##        f.close()
        self.modified = false
        self.saved = false
        self.update()
        if notify: self.notify()

    def save(self):
        """ Saves contents of data to file specified by self.filename. """
        if not self.transport:
            raise 'No transport for saving'

        if self.filename:
            self.transport.save(self.filename, self.data)
            self.modified = false
            self.saved = true

        else:
            raise 'No filename'

    def saveAs(self, filename):
        """ Saves contents of data to file specified by filename.
            Override this to catch name changes. """
        self.filename = filename
        self.save()
        self.savedAs = true

    def notify(self):
        """ Update all views connected to this model.
            This method must be called after changes were made to the model """
        for view in self.views.values():
            view.update()

    def update(self):
        """ Rebuild additional derived structure, called when data is changed """

    def refreshFromViews(self):
        for view in self.viewsModified:
            self.views[view].refreshModel()

    def getPageName(self):
        return os.path.splitext(os.path.basename(self.filename))[0]

class FolderModel(EditorModel):
    modelIdentifier = 'Folder'
    defaultName = 'folder'
    bitmap = 'Folder_s.bmp'
    imgIdx = imgFolder

    def __init__(self, data, name, editor, filepath):
        EditorModel.__init__(self, name, data, editor, true)
        self.filepath = filepath

class SysPathFolderModel(FolderModel):
    modelIdentifier = 'SysPathFolder'
    defaultName = 'syspathfolder'
    bitmap = 'Folder_green.bmp'
    imgIdx = imgPathFolder

class CVSFolderModel(FolderModel):
    modelIdentifier = 'CVS Folder'
    defaultName = 'cvsfolder'
    bitmap = 'Folder_cyan_s.bmp'
    imgIdx = imgCVSFolder

    def __init__(self, data, name, editor, filepath):
        FolderModel.__init__(self, data, name, editor, filepath)
        self.readFiles()

    def readFile(self, filename):
        f = open(filename, 'r')
        try: return string.strip(f.read())
        finally: f.close()

    def readFiles(self):
        self.root = self.readFile(os.path.join(self.filepath, 'Root'))
        self.repository = self.readFile(os.path.join(self.filepath, 'Repository'))
        self.entries = []

        f = open(os.path.join(self.filepath, 'Entries'), 'r')
        dirpos = 0
        try:
            txtEntries = f.readlines()
            for txtEntry in txtEntries:
                txtEntry = string.strip(txtEntry)
                if txtEntry:
                    if txtEntry == 'D':
                        pass
                        # maybe add all dirs?
                    elif txtEntry[0] == 'D':
                        self.entries.insert(dirpos, CVSDir(txtEntry))
                        dirpos = dirpos + 1
                    else:
                        try:
                            self.entries.append(CVSFile(txtEntry, self.filepath))
                        except IOError: pass
        finally:
            f.close()

class BitmapFileModel(EditorModel):
    modelIdentifier = 'Bitmap'
    defaultName = 'bmp'
    bitmap = 'Bitmap_s.bmp'
    imgIdx = imgBitmapFileModel
    ext = '.bmp'

class UnknownFileModel(EditorModel):
    modelIdentifier = 'Unknown'
    defaultName = '*'
    bitmap = 'Unknown_s.bmp'
    imgIdx = imgUnknownFileModel
    ext = '.*'


class ZipFileModel(EditorModel):
    modelIdentifier = 'ZipFile'
    defaultName = 'zip'
    bitmap = 'ZipFile_s.bmp'
    imgIdx = imgZipFileModel
    ext = '.zip'

class PackageModel(EditorModel):
    """ Must be constructed in a valid path, name being filename, actual
        name will be derived from path """

    modelIdentifier = 'Package'
    defaultName = 'package'
    bitmap = 'Package_s.bmp'
    imgIdx = imgPackageModel
    pckgIdnt = '__init__.py'
    ext = '.py'

    saveBmp = 'Images/Editor/Save.bmp'
    saveAsBmp = 'Images/Editor/SaveAs.bmp'

    def __init__(self, data, name, editor, saved):
        EditorModel.__init__(self, name, data, editor, saved)
        self.packagePath, dummy = os.path.split(self.filename)
        dummy, self.packageName = os.path.split(self.packagePath)
        self.savedAs = true
        self.modified = false

    def addTools(self, toolbar):
        EditorModel.addTools(self, toolbar)
        AddToolButtonBmpIS(self.editor, toolbar, self.saveBmp, 'Save', self.editor.OnSave)
        AddToolButtonBmpIS(self.editor, toolbar, self.saveAsBmp, 'Save as...', self.editor.OnSaveAs)

    def addMenus(self, menu):
        accls = EditorModel.addMenus(self, menu)
        self.addMenu(menu, EditorHelper.wxID_EDITORSAVE, 'Save', accls, (keyDefs['Save']))
        self.addMenu(menu, EditorHelper.wxID_EDITORSAVEAS, 'Save as...', accls, (keyDefs['SaveAs']))
        return accls

    def openPackage(self, name):
        self.editor.openModule(os.path.join(self.packagePath, name, self.pckgIdnt))

    def openFile(self, name):
        self.editor.openModule(os.path.join(self.packagePath, name + self.ext))

    def generateFileList(self):
        """ Generate a list of modules and packages in the package path """
        files = os.listdir(self.packagePath)
        packages = []
        modules = []
        for file in files:
            filename = os.path.join(self.packagePath, file)
            mod, ext = os.path.splitext(file)
            if file == self.pckgIdnt: continue
            elif (ext == self.ext) and os.path.isfile(filename):
                modules.append((mod, identifyFile(filename)[0]))
            elif os.path.isdir(filename) and \
              os.path.exists(os.path.join(filename, self.pckgIdnt)):
                packages.append((file, PackageModel))

        return packages + modules

    def getPageName(self):
        return self.packageName

class BasePersistentModel(EditorModel):
    saveBmp = 'Images/Editor/Save.bmp'
    saveAsBmp = 'Images/Editor/SaveAs.bmp'

    def addTools(self, toolbar):
        EditorModel.addTools(self, toolbar)
        AddToolButtonBmpIS(self.editor, toolbar, self.saveBmp, 'Save', self.editor.OnSave)
        AddToolButtonBmpIS(self.editor, toolbar, self.saveAsBmp, 'Save as...', self.editor.OnSaveAs)

    def addMenus(self, menu):
        accls = EditorModel.addMenus(self, menu)
        self.addMenu(menu, EditorHelper.wxID_EDITORSAVE, 'Save', accls, (keyDefs['Save']))
        self.addMenu(menu, EditorHelper.wxID_EDITORSAVEAS, 'Save as...', accls, (keyDefs['SaveAs']))
        return accls

    def new(self):
        self.data = ''
        self.savedAs = false
        self.modified = true
        self.update()
        self.notify()

class PersistentModel(BasePersistentModel):
    def __init__(self, data, name, editor, saved):
        BasePersistentModel.__init__(self, name, data, editor, saved)
        if data: self.update()

    def load(self, notify = true):
        BasePersistentModel.load(self, false)
        self.update()
        if notify: self.notify()
        
class SourceModel(BasePersistentModel):
    modelIdentifier = 'Source'
    def getCVSConflicts(self):
        # needless obscurity
        # numedLines = apply(map, (None,) + (lines, range(len(lines))) )

        # use model.module.source
        conflictStart = -1
        confCnt = 0
        lineNo = 0
        conflicts =[]
        for line in self.getDataAsLines():
            if line[:8] == '<<<<<<< ' and \
                  string.strip(line[8:]) == os.path.basename(self.filename):
                conflictStart = lineNo
            if line[:8] == '>>>>>>> ':
                rev = line[8:]
                conflicts.append( (rev, conflictStart, lineNo - conflictStart) )
                confCnt = confCnt + 1
            lineNo = lineNo + 1
        return conflicts

    def applyChangeBlock(self, conflict, blockIdx):
        rev, start, size = conflict
        lines = self.getDataAsLines()

        blocks = Utils.split_seq(lines[start+1 : start+size], '=======')
        lines[start:start+size+1] = blocks[blockIdx]
        self.data = self.setDataFromLines(lines)

        self.update()
        self.notify()

    def acceptConflictChange(self, conflict):
        self.applyChangeBlock(conflict, 1)

    def rejectConflictChange(self, conflict):
        self.applyChangeBlock(conflict, 0)

class ModuleModel(SourceModel):

    modelIdentifier = 'Module'
    defaultName = 'module'
    bitmap = 'Module_s.bmp'
    imgIdx = imgModuleModel
    ext = '.py'

##    saveBmp = 'Images/Editor/Save.bmp'
##    saveAsBmp = 'Images/Editor/SaveAs.bmp'

    def __init__(self, data, name, editor, saved, app = None):
        SourceModel.__init__(self, name, data, editor, saved)
        self.moduleName = os.path.split(self.filename)[1]
        self.app = app
        self.debugger = None
        if data:
            if Preferences.autoReindent:
                if not self.reindent(false):
                    self.update()
            else:
                self.update()

    def destroy(self):
        SourceModel.destroy(self)
        del self.app
        del self.debugger

##    def addTools(self, toolbar):
##        SourceModel.addTools(self, toolbar)
##        AddToolButtonBmpIS(self.editor, toolbar, self.saveBmp, 'Save', self.editor.OnSave)
##        AddToolButtonBmpIS(self.editor, toolbar, self.saveAsBmp, 'Save as...', self.editor.OnSaveAs)

    def addMenus(self, menu):
        accls = SourceModel.addMenus(self, menu)
##        self.addMenu(menu, EditorHelper.wxID_EDITORSAVE, 'Save', accls, (keyDefs['Save']))
##        self.addMenu(menu, EditorHelper.wxID_EDITORSAVEAS, 'Save as...', accls, (keyDefs['SaveAs']))
        menu.Append(-1, '-')
        self.addMenu(menu, EditorHelper.wxID_EDITORSWITCHAPP, 'Switch to app', accls, (keyDefs['SwitchToApp']))
        self.addMenu(menu, EditorHelper.wxID_EDITORDIFF, 'Diff modules...', accls, ())
        self.addMenu(menu, EditorHelper.wxID_EDITORPYCHECK, 'Run PyChecker', accls, ())
        self.addMenu(menu, EditorHelper.wxID_EDITORCONFPYCHECK, 'Configure PyChecker', accls, ())
        return accls

    def new(self):
        self.data = ''
        self.savedAs = false
        self.modified = true
        self.update()
        self.notify()

    def load(self, notify = true):
        SourceModel.load(self, false)
        if Preferences.autoReindent:
            if not self.reindent():
                self.update()
        else:
            self.update()
        if notify: self.notify()

    def save(self):
        if Preferences.autoReindent:
            self.reindent(false)
        SourceModel.save(self)

    def getModule(self):
        if self._module is None:
            wx.wxBeginBusyCursor()
            try:
                self._module = moduleparse.Module(
                    self.moduleName, self.getDataAsLines())
            finally:
                wx.wxEndBusyCursor()
        return self._module

    def initModule(self):
        # Don't parse the module until it's needed.
        self._module = None

    def refreshFromModule(self):
        """ Must call this method to apply changes made
        to the module object. """
        self.data = string.join(self.getModule().source, '\012')#os.linesep)
        self.notify()

    def renameClass(self, oldname, newname):
        pass

    def update(self):
        EditorModel.update(self)
        self.initModule()

    def runInThread(self, filename, args, app, interpreterPath):
        cwd = os.path.abspath(os.getcwd())
        newCwd = os.path.dirname(filename)
        os.chdir(newCwd)
        try:
            cmd = '"%s" %s %s'%(interpreterPath,
                  os.path.basename(filename), args)

            from ModRunner import PopenModuleRunner, ExecFinishEvent

            runner = PopenModuleRunner(None, app, newCwd)
            runner.run(cmd)
            wx.wxPostEvent(self.editor, ExecFinishEvent(runner))
        finally:
            os.chdir(cwd)

    def run(self, args = ''):
        """ Excecute the current saved image of the application. """
        if self.savedAs:
            if not Preferences.pythonInterpreterPath:
                pythonIntPath = sys.executable
            else:
                pythonIntPath = Preferences.pythonInterpreterPath

            self.editor.statusBar.setHint('Running %s...' % self.filename)
            start_new_thread(self.runInThread, (self.filename, args,
                  self.app, pythonIntPath))

##        if self.savedAs:
##            cwd = os.path.abspath(os.getcwd())
##            newCwd = os.path.dirname(self.filename)
##            os.chdir(newCwd)
##            oldErr = sys.stderr
##            oldSysPath = sys.path[:]
##            try:
##                sys.path.append(Preferences.pyPath)
##                if not Preferences.pythonInterpreterPath:
##                    pythonIntPath = sys.executable
##                else:
##                    pythonIntPath = Preferences.pythonInterpreterPath
##                cmd = '"%s" %s %s'%(pythonIntPath,
##                      os.path.basename(self.filename), args)
##
##                from ModRunner import PreferredRunner
##                if Preferences.minimizeOnRun:
##                    self.editor.palette.Iconize(true)
##                try:
##                    PreferredRunner(self.editor.erroutFrm, self.app, newCwd).run(cmd)
##                finally:
##                    pass
##                    if Preferences.minimizeOnRun:
##                        self.editor.palette.Iconize(false)
##                        if self.editor.erroutFrm:
##                            self.editor.erroutFrm.Raise()
##
##            finally:
##                sys.path = oldSysPath
##                sys.stderr = oldErr
##                os.chdir(cwd)

    def runAsScript(self):
        execfile(self.filename)

    def compile(self):
        if self.savedAs:
            import ModRunner
            oldErr = sys.stderr
            sys.stderr = ErrorStack.RecFile()
            try:
                cmr = ModRunner.CompileModuleRunner(self.editor.erroutFrm, self.app)
                cmr.run(self.filename)

                serr = ErrorStack.errorList(sys.stderr)

                cmr.checkError(serr, 'Compiled')
            finally:
                sys.stderr = oldErr

    def cyclops(self):
        """ Run the saved application thru Cyclops """
        if self.savedAs:
            cwd = os.path.abspath(os.getcwd())
            os.chdir(os.path.dirname(self.filename))
            page = ''
            try:
                name = os.path.basename(self.filename)

                # excecute Cyclops in Python with module as parameter
                command = '"%s" "%s" "%s"'%(sys.executable,
                  Preferences.toPyPath('RunCyclops.py'), name)
                wx.wxExecute(command, true)

                # read report that Cyclops generated
                f = open(name[:-3]+'.cycles', 'r')
                page = f.read()
                f.close()
            finally:
                os.chdir(cwd)
                return page
        else:
            wx.wxLogWarning('Save before running Cyclops')
            raise 'Not saved yet!'

    def debug(self, params = None):
        if self.savedAs:
            if self.editor.debugger:
                self.editor.debugger.Show(true)
            else:
                self.editor.debugger = Debugger.DebuggerFrame(self)
                self.editor.debugger.Show(true)
                if params is None: params = []
                self.editor.debugger.debug_file(self.editor.debugger.filename, params)

    def profile(self):
        # XXX Should change to the profile file directory
        if self.savedAs:
            cwd = os.path.abspath(os.getcwd())
            os.chdir(os.path.dirname(self.filename))

            tmpApp = wxPython.wx.wxApp
            wxProfilerPhonyApp.realApp = self.editor.app
            wxPython.wx.wxApp = wxProfilerPhonyApp
            try:
                sys.path.insert(0, os.path.dirname(self.filename))
                prof = profile.Profile()
                try:
                    prof = prof.run('execfile("%s")'% os.path.basename(self.filename))
                except SystemExit, error:
                    wxLogError('Error: '+str(error))
                prof.create_stats()
                return prof.stats, os.path.dirname(self.filename)

            finally:
                del sys.path[0]
                wxPython.wx.wxApp = tmpApp
                del wxProfilerPhonyApp.realApp
                os.chdir(cwd)

    def addModuleInfo(self, prefs):
        # XXX Check that module doesn't already have an info block

        dollar = '$' # has to be obscured from CVS :)
        prefs['Name'] = self.moduleName
        prefs['Created'] = strftime('%Y/%d/%m', gmtime(time()))
        prefs['RCS-ID'] = '%sId: %s %s' % (dollar, self.moduleName , dollar)

        self.data = defInfoBlock % (prefs['Name'], prefs['Purpose'], prefs['Author'],
          prefs['Created'], prefs['RCS-ID'], prefs['Copyright'], prefs['Licence']) + self.data
        self.modified = true
        self.update()
        self.notify()

    def saveAs(self, filename):
        oldFilename = self.filename
        EditorModel.saveAs(self, filename)
        if self.app:
            self.app.moduleSaveAsNotify(self, oldFilename, filename)
        self.moduleName = os.path.basename(filename)
        self.notify()

    def diff(self, filename):
        tbName = 'Diff with : '+filename
        if not self.views.has_key(tbName):
            resultView = self.editor.addNewView(tbName, PythonSourceDiffView)
        else:
            resultView = self.views[tbName]

        resultView.tabName = tbName
        resultView.diffWith = filename
        resultView.refresh()
        resultView.focus()

    def reindent(self, updateModulePage = true):
        from ExternalLib import reindent
        self.refreshFromViews()
        file = SourcePseudoFile(self.getDataAsLines())
        ri = reindent.Reindenter(file)
        try:
            if ri.run():
                file.output = []
                ri.write(file)

                newData = string.join(file.output, '')
                modified = self.data != newData
                self.modified = self.modified or modified

                if modified:
                    self.data = newData
                    if updateModulePage:
                        self.editor.updateModulePage(self)
                    self.update()
                    self.notify()

                    self.editor.statusBar.setHint(\
                          'Code reformatted (indents and or EOL characters fixed)')
                    return true
        except Exception, error:
            self.editor.statusBar.setHint(\
                  'Reindent failed - %s : %s' % (error.__class__, str(error)) , 'Error')

        return false

    def getSimpleRunnerSrc(self):
        return simpleModuleRunSrc

class SourcePseudoFile(Utils.PseudoFileOutStore):
    def readlines(self):
        return self.output

class TextModel(PersistentModel):

    modelIdentifier = 'Text'
    defaultName = 'text'
    bitmap = 'Text_s.bmp'
    imgIdx = imgTextModel
    ext = '.txt'


class CPPModel(SourceModel):

    modelIdentifier = 'CPP'
    defaultName = 'cpp'
    bitmap = 'Cpp_s.bmp'
    imgIdx = imgCPPModel
    ext = '.cxx'

    def __init__(self, data, name, editor, saved):
        SourceModel.__init__(self, name, data, editor, saved)
        self.loadHeader()
        if data: self.update()

    def loadHeader(self):
        header = os.path.splitext(self.filename)[0]+'.h'
        if os.path.exists(header):
            # This should open a BasicFileModel instead of a file directly
            self.headerData = open(header).read()
        else:
            self.headerData = ''

    def load(self, notify = true):
        SourceModel.load(self, false)
        self.loadHeader()
        self.update()
        if notify: self.notify()

##class HPPModel(CPPModel):
##    modelIdentifier = 'HPP'
##    defaultName = 'hpp'
##    bitmap = 'Cpp_s.bmp'
##    imgIdx = 13
##    ext = '.h'

class ConfigFileModel(PersistentModel):
    modelIdentifier = 'Config'
    defaultName = 'config'
    bitmap = 'Config_s.bmp'
    imgIdx = imgConfigFileModel
    ext = '.cfg'

class HTMLFileModel(PersistentModel):
    modelIdentifier = 'HTML'
    defaultName = 'html'
    bitmap = 'Text_s.bmp'
    imgIdx = imgHTMLFileModel
    ext = '.html'

class XMLFileModel(PersistentModel):
    modelIdentifier = 'XML'
    defaultName = 'xml'
    bitmap = 'Text_s.bmp'
    imgIdx = imgXMLFileModel
    ext = '.xml'

class ClassModel(ModuleModel):
    """ Represents access to 1 maintained main class in the module.
        This class is identified by the 3rd header entry  #Boa:Model:Class """
    def __init__(self, data, name, main, editor, saved, app = None):
        self.main = main
        self.mainConstr = None
        ModuleModel.__init__(self, data, name, editor, saved, app)

    def renameMain(self, oldName, newName):
        self.getModule().renameClass(oldName, newName)
        self.main = newName

        idx = 0
        for line in self.getModule().source:
            if line:
                if line[0] != '#': break

                header = string.split(string.strip(line), ':')
                if (len(header) == 3) and (header[0] == boaIdent):
                    self.getModule().source[idx] = string.join((header[0], header[1], newName), ':')
                    break
            else: break
            idx = idx + 1

class BaseFrameModel(ClassModel):
    modelIdentifier = 'Frames'
    companion = Companions.DesignTimeCompanion
    designerBmp = 'Images/Shared/Designer.bmp'
    def __init__(self, data, name, main, editor, saved, app = None):
        ClassModel.__init__(self, data, name, main, editor, saved, app)
        self.designerTool = None

    def addTools(self, toolbar):
        ClassModel.addTools(self, toolbar)
        toolbar.AddSeparator()
        AddToolButtonBmpIS(self.editor, toolbar, self.designerBmp, 'Frame Designer', self.editor.OnDesigner)

    def addMenus(self, menu):
        accls = ClassModel.addMenus(self, menu)
        self.addMenu(menu, EditorHelper.wxID_EDITORDESIGNER, 'Frame Designer', accls, (keyDefs['Designer']))
        return accls

    def renameMain(self, oldName, newName):
        ClassModel.renameMain(self, oldName, newName)
        if self.getModule().functions.has_key('create'):
            self.getModule().replaceFunctionBody('create',
                  ['    return %s(parent)'%newName, ''])

    def renameCtrl(self, oldName, newName):
        # Currently DesignerView maintains ctrls
        pass

    def new(self, params):
        paramLst = []
        for param in params.keys():
            paramLst.append('%s = %s'%(param, params[param]))
        paramStr = 'self, ' + string.join(paramLst, ', ')

        self.data = (defSig + defImport + defCreateClass + defWindowIds + \
          defClass) % (self.modelIdentifier, self.main, self.main,
          Utils.windowIdentifier(self.main, ''), init_ctrls, 1, self.main,
          self.defaultName, self.defaultName, paramStr)

        self.savedAs = false
        self.modified = true
        self.initModule()
#        self.readComponents()
        self.notify()

    def identifyCollectionMethods(self):
        results = []
        module = self.getModule()
        if module.classes.has_key(self.main):
            main = module.classes[self.main]
            for meth in main.methods.keys():
                if len(meth) > len('_init_') and meth[:6] == '_init_':
                    results.append(meth)
        return results

    def allObjects(self):
        views = ['Data', 'Designer']

        order = []
        objs = {}

        for view in views:
            order.extend(self.views[view].objectOrder)
            objs.update(self.views[view].objects)

        return order, objs

    def readDesignerMethod(self, meth, codeBody):
        """ Create a new ObjectCollection by parsing the given method body """
        import methodparse
        # Collection method
        if ObjCollection.isInitCollMeth(meth):
            try:
                res = Utils.split_seq(codeBody, '', string.strip)
                inits, body, fins = res[:3]
            except ValueError:
                raise 'Collection body %s not in init, body, fin form' % meth

            allInitialisers, unmatched = methodparse.parseMixedBody(\
             [methodparse.CollectionItemInitParse, methodparse.EventParse],body)

            creators = allInitialisers.get(methodparse.CollectionItemInitParse, [])
            collectionInits = []
            properties = []
            events = allInitialisers.get(methodparse.EventParse, [])
        # Normal method
        else:
            inits = []
            fins = []

            allInitialisers, unmatched = methodparse.parseMixedBody(\
              [methodparse.ConstructorParse, methodparse.EventParse,
               methodparse.CollectionInitParse, methodparse.PropertyParse],
               codeBody)

            creators = allInitialisers.get(methodparse.ConstructorParse, [])
            collectionInits = allInitialisers.get(methodparse.CollectionInitParse, [])
            properties = allInitialisers.get(methodparse.PropertyParse, [])
            events = allInitialisers.get(methodparse.EventParse, [])

        newObjColl = ObjCollection.ObjectCollection()
        newObjColl.setup(creators, properties, events, collectionInits, inits, fins)
    
        if unmatched:
            wx.wxLogWarning('The following lines were not used by the Designer '\
                         'and will be lost:\n')
            for line in unmatched:
                wx.wxLogWarning(line)
            wx.wxLogWarning('\nThere were unprocessed lines in the source code of '\
                         'method: %s\nIf this was unexpected, it is advised '\
                         'that you cancel this Designer session and correct '\
                         'the problem before continuing.'%meth)

        return newObjColl

    def readComponents(self):
        """ Setup object collection dict by parsing all designer controlled methods """
        self.objectCollections = {}
        module = self.getModule()
        if module.classes.has_key(self.main):
            main = module.classes[self.main]
            for oc in self.identifyCollectionMethods():
                codeSpan = main.methods[oc]
                codeBody = module.source[codeSpan.start : codeSpan.end]

                # XXX Hack: This should not be necessary !!
##                if len(oc) >= 11 and oc[:11] == init_ctrls and \
##                  string.strip(codeBody[1]) == 'self._init_utils()':
##                    del codeBody[1]

                self.objectCollections[oc] = self.readDesignerMethod(oc, codeBody)

                for prop in self.objectCollections[oc].properties[:]:
                    if prop.asText() == 'self._init_utils()':
                        self.objectCollections[oc].properties.remove(prop)

            # Set the model's constructor
            if self.objectCollections.has_key(init_ctrls):
                try:
                    self.mainConstr = self.objectCollections[init_ctrls].creators[0]
                except IndexError:
                    raise 'Inherited __init__ method missing'


    def removeWindowIds(self, colMeth):
        # find windowids in source
        winIdIdx = -1
        reWinIds = re.compile(srchWindowIds % colMeth)
        module = self.getModule()
        for idx in range(len(module.source)):
            match = reWinIds.match(module.source[idx])
            if match:
                del module.source[idx]
                del module.source[idx]
                module.renumber(-2, idx)
                break

    def writeWindowIds(self, colMeth, companions):
        # To integrate efficiently with Designer.SaveCtrls this method
        # modifies module.source but doesn't refresh anything

        # find windowids in source
        winIdIdx = -1
        reWinIds = re.compile(srchWindowIds % colMeth)
        module = self.getModule()
        for idx in range(len(module.source)):
            match = reWinIds.match(module.source[idx])
            if match:
                winIdIdx = idx
                break

        # build window id list
        lst = []
        for comp in companions:
            if winIdIdx == -1:
                comp.updateWindowIds()
            comp.addIds(lst)
        lst.sort()

        if winIdIdx == -1:
            if lst:
                # No window id definitions could be found add one above class def
                insPt = module.classes[self.main].block.start - 1
                module.source[insPt:insPt] = \
                  [string.strip(defWindowIds % (string.join(lst, ', '), colMeth,
                  len(lst))), '']
                module.renumber(2, insPt)
        else:
            # Update window ids
            module.source[idx] = \
              string.strip(defWindowIds % (string.join(lst, ', '), colMeth, len(lst)))

    def update(self):
        ClassModel.update(self)
#        self.readComponents()

    def getSimpleRunnerSrc(self):
        return simpleAppFrameRunSrc

class FrameModel(BaseFrameModel):
    modelIdentifier = 'Frame'
    defaultName = 'wxFrame'
    bitmap = 'wxFrame_s.bmp'
    imgIdx = imgFrameModel
    companion = Companions.FrameDTC

class DialogModel(BaseFrameModel):
    modelIdentifier = 'Dialog'
    defaultName = 'wxDialog'
    bitmap = 'wxDialog_s.bmp'
    imgIdx = imgDialogModel
    companion = Companions.DialogDTC

    def getSimpleRunnerSrc(self):
        return simpleAppDialogRunSrc

class MiniFrameModel(BaseFrameModel):
    modelIdentifier = 'MiniFrame'
    defaultName = 'wxMiniFrame'
    bitmap = 'wxMiniFrame_s.bmp'
    imgIdx = imgMiniFrameModel
    companion = Companions.MiniFrameDTC

class MDIParentModel(BaseFrameModel):
    modelIdentifier = 'MDIParent'
    defaultName = 'wxMDIParentFrame'
    bitmap = 'wxMDIParentFrame_s.bmp'
    imgIdx = imgMDIParentModel
    companion = Companions.MDIParentFrameDTC

class MDIChildModel(BaseFrameModel):
    modelIdentifier = 'MDIChild'
    defaultName = 'wxMDIChildFrame'
    bitmap = 'wxMDIChildFrame_s.bmp'
    imgIdx = imgMDIChildModel
    companion = Companions.MDIChildFrameDTC

# XXX Autocreated frames w/ corresponding imports
# XXX module references to app mut be cleared on closure

class AppModel(ClassModel):
    modelIdentifier = 'App'
    defaultName = 'wxApp'
    bitmap = 'wxApp_s.bmp'
    imgIdx = imgAppModel
    def __init__(self, data, name, main, editor, saved, openModules):
        self.moduleModels = {}
        self.textInfos = {}
        self.unsavedTextInfos = []
        self.modules = {}
        ClassModel.__init__(self, data, name, main, editor, saved, self)
        if data:
            self.update()
            self.notify()

        # Connect all open modules to this app obj if they are defined in
        # the app's modules
        # XXX This does not work yet, the problem is that the menus and toolbar
        # XXX def is built in the constructors so they cannot yet be changed
        # XXX to include the runn app button / action
        abspaths = self.absModulesPaths()
        for modPage in openModules.values():
            if hasattr(modPage.model, 'app') and modPage.model.filename in abspaths:
                modPage.model.app = self

    def absModulesPaths(self):
        modules = self.modules.keys()
        abspaths = []
        for moduleName in modules:
            abspaths.append(self.normaliseModuleRelativeToApp(self.modules[moduleName][2]))
        return abspaths

    def addMenus(self, menu):
        accls = ClassModel.addMenus(self, menu)
        self.addMenu(menu, EditorHelper.wxID_EDITORCMPAPPS, 'Compare apps...', accls, ())
        return accls

    def convertToUnixPath(self, filename):
        # Don't convert absolute windows paths, will stay illegal until saved
        if os.path.splitdrive(filename)[0] != '':
            return filename
        else:
            return string.join(string.split(filename, '\\'), '/')

    def save(self):
        ClassModel.save(self)
        for tin in self.unsavedTextInfos:
            fn = os.path.join(os.path.dirname(self.filename), tin)
            data = self.textInfos[tin]
            if data:
                # XXX Reference by transport, not by file
                open(fn, 'w').write(data)
        self.unsavedTextInfos = []

    def saveAs(self, filename):
        for mod in self.modules.keys():
            self.modules[mod][2] = self.convertToUnixPath(\
              relpath.relpath(os.path.dirname(filename),
              self.normaliseModuleRelativeToApp(self.modules[mod][2])))

        self.writeModules()

        ClassModel.saveAs(self, filename)

        self.notify()

##    def modulePathChange(self, oldFilename, newFilename):
##        # self.modules have already been renamed, use newFilename
##        key = path.splitext(path.basename(newFilename))[0]
##        self.modules[key][2] = relpath.relpath(path.dirname(self.filename), newFilename)
##
##        self.writeModules()

    def renameMain(self, oldName, newName):
        ClassModel.renameMain(self, oldName, newName)
        self.getModule().replaceFunctionBody('main',
          ['    application = %s(0)'%newName, '    application.MainLoop()', ''])

    def new(self, mainModule):
        self.data = (defSig + defEnvPython + defImport + defApp) \
          %(self.modelIdentifier, boaClass, mainModule, mainModule,
            mainModule, mainModule)
        self.saved = false
        self.modified = true
        self.update()
        self.notify()

    def findImports(self):
        impPos = string.find(self.data, defImport)
        impPos = string.find(self.data, 'import', impPos + 1)

        # XXX Add if not found
        if impPos == -1: raise 'Module import list not found in application'
        impEnd = string.find(self.data, '\012', impPos + len('import') +1) + 1
        if impEnd == -1: raise 'Module import list not terminated'
        return impPos + len('import'), impEnd

    def findModules(self):
        modStr = 'modules ='
        modPos = string.find(self.data, modStr)
        if modPos == -1:
            raise 'Module list not found in application'
        modEnd = string.find(self.data, '}\n', modPos + len(modStr) +1) + 1
        if modEnd == -1: raise 'Module list not terminated properly'
        return modPos + len(modStr), modEnd

    def idModel(self, name):
        absPath = self.normaliseModuleRelativeToApp(self.modules[name][2])
        if os.path.exists(absPath):
            self.moduleModels[name], main = identifyFile(absPath)
        else:
            if self.editor.modules.has_key(absPath):
                self.moduleModels[name], main = identifySource(
                    self.editor.modules[absPath].model.getModule().source)
            elif self.editor.modules.has_key(os.path.basename(absPath)):
                self.moduleModels[name], main = identifySource(
                    self.editor.modules[os.path.basename(absPath)\
                                       ].model.getModule().source)
            else:
                print 'could not find unsaved module', absPath, self.editor.modules

    def readModules(self):
        modS, modE = self.findModules()
        try:
            self.modules = eval(self.data[modS:modE])
        except: raise 'Module list not a valid dictionary'

        for mod in self.modules.keys():
            self.idModel(mod)

##    def readImports(self):
##        impS, impE = self.findImports()
##        try:
##            self.imports = string.split(self.data[impS:impE], ', ')
##        except: raise 'Module import list not a comma delimited list'

    def writeModules(self, notify = true):
        modS, modE = self.findModules()
#        self.data = self.data[:modS]+`self.modules`+self.data[modE:]
        self.data = self.data[:modS]+pprint.pformat(self.modules)+self.data[modE:]

        self.modified = true
        self.editor.updateTitle()
        self.editor.updateModulePage(self)

        if notify: self.notify()

##    def writeImports(self, notify = true):
##        impS, impE = self.findImports()
##        self.data = self.data[:impS]+string.join(self.imports, ', ')+ \
##          self.data[impE:]
##        if notify: self.notify()

    def viewAddModule(self):
        fn = self.editor.openFileDlg()
        if fn:
            self.addModule(fn, '')

    def addModule(self, filename, descr):
        name, ext = os.path.splitext(os.path.basename(filename))
        if self.modules.has_key(name): raise 'Module exists in application'
        if self.savedAs:
            relative = relpath.relpath(os.path.dirname(self.filename), filename)
        else:
            relative = filename
        self.modules[name] = [0, descr, self.convertToUnixPath(relative)]

        self.idModel(name)

        self.writeModules()

    def hasModule(self, absfilename):
        modRelPath = self.convertToUnixPath(\
              relpath.relpath(os.path.dirname(self.filename), absfilename) )
        for main, descr, relPath in self.modules.values():
            if modRelPath == relPath:
                return true
        else:
            return false

    def removeModule(self, name):
        if not self.modules.has_key(name): raise 'No such module in application'

        del self.modules[name]
        self.writeModules()

    def editModule(self, oldname, newname, main, descr):
        _1, _2, relpath = self.modules[oldname]
        if oldname != newname:
            del self.modules[oldname]
        self.modules[newname] = [main, descr, relpath]
        self.writeModules()

    def moduleFilename(self, name):
        """ Return absolute filename of the given module """
        if not self.modules.has_key(name): raise 'No such module in application: '+name
        if self.savedAs:
            if os.path.isabs(self.modules[name][2]):
                absPath = self.modules[name][2]
            else:
                absPath = os.path.normpath(os.path.join(os.path.dirname(self.filename),
                  self.modules[name][2]))
        else:
            absPath = name + ModuleModel.ext
        return absPath

    def updateAutoCreateImports(self, oldName, newName):
        """ Rename module in import list.

            Only autocreated modules should be on this list.
            The module is modified and the model is not updated"""
        module = self.getModule()
        if module.imports.has_key(oldName):
            impLine = module.imports[oldName][0]-1
            # read in the import line
            line = module.source[impLine]
            impIndent = string.find(line, 'import')
            imports = string.split(line[7+impIndent:], ', ')
            impIdx = imports.index(oldName)
            imports[impIdx] = newName
            module.imports[newName] = module.imports[oldName]
            del module.imports[oldName]
            module.source[impLine] = 'import '+string.join(imports, ', ')
            return impIdx
        return None

    def updateMainFrameModuleRefs(self, oldName, newName):
        """ Replace references to old main module with new main module """
        module = self.getModule()
        block = module.classes[boaClass].methods['OnInit']
        mainDef = 'self.main = %s.'
        fndOldStr = mainDef % oldName
        repNewStr = mainDef % newName

        for idx in range(block.start, block.end):
            line = module.source[idx]
            newLine = string.replace(line, fndOldStr, repNewStr)
            if newLine != line:
                module.source[idx] = newLine

    def changeMainFrameModule(self, newMainFrameModule):
        """ Select a new main frame module """
        if len(self.viewsModified):
            self.refreshFromViews()

        # determine which module is the main module
        module = self.getModule()
        for mod, props in filter(lambda v: v[1][0], self.modules.items()):
            impLine = module.imports[mod][0]-1
            line = module.source[impLine]
            impIndent = string.find(line, 'import')
            imports = string.split(line[7+impIndent:], ', ')
            if len(imports) and imports[0] == mod:
                try:
                    impIdx = imports.index(newMainFrameModule)
                except ValueError:
                    impIdx = 0
                del imports[impIdx]

                imports.insert(0, newMainFrameModule)
                module.source[impLine] = impIndent*' '+'import '+string.join(imports, ', ')

                self.updateMainFrameModuleRefs(mod, newMainFrameModule)
                self.refreshFromModule()

                # Update autocreation status
                props[0] = 0
                self.modules[newMainFrameModule][0] = 1
                self.writeModules(false)

                self.update()
                break
        else:
            raise 'No main frame module found in application'

    def moduleSaveAsNotify(self, module, oldFilename, newFilename):
        if module != self:
            newName, ext = os.path.splitext(os.path.basename(newFilename))
            oldName = os.path.splitext(os.path.basename(oldFilename))[0]

            if not self.modules.has_key(oldName): raise 'Module does not exists in application'

            if self.savedAs:
                relative = relpath.relpath(os.path.dirname(self.filename), newFilename)
            else:
                relative = newFilename

            if newName != oldName:
                self.modules[newName] = self.modules[oldName]
                del self.modules[oldName]
            self.modules[newName][2] = self.convertToUnixPath(relative)

            # Check if it's autocreated module
            if self.modules[newName][0]:
                if len(self.viewsModified):
                    self.refreshFromViews()

                impIdx = self.updateAutoCreateImports(oldName, newName)

                if impIdx is not None:
                    # check if it's the main module, first in the import list is
                    # always the main module
                    if not impIdx:
                        self.updateMainFrameModuleRefs(oldName, newName)

                    # preserve modified modules
                    mods = self.modules
                    self.refreshFromModule()
                    self.modules = mods

            self.writeModules()
            self.update()

    def crashLog(self):
        err = ErrorStack.crashError(os.path.splitext(self.filename)[0]+'.trace')
        if err:
            frm = self.editor.erroutFrm
            if frm:
                frm.updateCtrls(err)
                if not frm.IsShown():
                    frm.Show(true)
##
##                self.editor.erroutFrm. return self.checkError(serr, 'Ran', dlg.output)
##                            import ErrorStackFrm
##            esf = ErrorStackFrm.ErrorStackMF(self.editor, self.app)
##            esf.updateCtrls(err)
##            esf.Show(true)
                return frm
        else:
            wx.wxLogError('Trace file not found. Run with command line param -T')
            return None

    def openModule(self, name):
        absPath = self.moduleFilename(name)

        module = self.editor.openOrGotoModule(absPath, self)

        return module

    def readPaths(self):
        pass

    def normaliseModuleRelativeToApp(self, relFilename):
        """ Normalise relative paths to absolute paths """
        if not self.savedAs:
            return os.path.normpath(os.path.join(Preferences.pyPath, relFilename))
        else:
            return os.path.normpath(os.path.join(os.path.dirname(self.filename), relFilename))

    def buildImportRelationshipDict(self, modules = None):
        relationships = {}

        if modules is None:
            modules = self.modules.keys()

        tot = len(modules)
        self.editor.statusBar.progress.SetRange(tot)
        prog = 0
        totLOC = 0
        classCnt = 0
        # XXX Rewrite in terms of transport
        for moduleName in modules:
            self.editor.statusBar.progress.SetValue(prog)
            prog = prog + 1
            self.editor.statusBar.setHint('Parsing '+moduleName+'...')
            module = self.modules[moduleName]
            try: f = open(self.normaliseModuleRelativeToApp(module[2]))
            except IOError:
                print "couldn't load", module[2]
                continue
            else:
                data = f.read()
                f.close()
                model = ModuleModel(data, module[2], self.editor, 1)
                relationships[moduleName] = model.getModule() #.imports

            totLOC = totLOC + model.getModule().loc
            classCnt = classCnt + len(model.getModule().classes)

        print 'Project LOC', totLOC
        print 'Class count', classCnt
        print 'in', len(modules), 'modules'

        self.editor.statusBar.progress.SetValue(0)
        self.editor.statusBar.setHint('')
        return relationships

    def showImportsView(self):
        # XXX Should be more generic
        self.editor.showImportsView()

    def compareApp(self, filename):
        tbName = 'App. Compare : '+filename
        if not self.views.has_key(tbName):
            resultView = self.editor.addNewView(tbName, AppCompareView)
        else:
            resultView = self.views[tbName]

        resultView.tabName = tbName
        resultView.compareTo = filename
        resultView.refresh()
        resultView.focus()

    def update(self):
        ClassModel.update(self)
        self.readModules()
        self.readPaths()

    def loadTextInfo(self, viewName):
        fn = os.path.join(os.path.dirname(self.filename), viewName)
        if os.path.exists(fn):
            self.textInfos[viewName] = open(fn).read()
        else:
            self.textInfos[viewName] = ''

class SetupModuleModel(ModuleModel):
    modelIdentifier = 'setup'
    defaultName = 'Setup'
    bitmap = 'Setup_s.bmp'
    imgIdx = imgSetupModel
    def __init__(self, data, name, editor, saved, app = None):
        ModuleModel.__init__(self, data, name, editor, saved, app)
        if data:
            self.update()
            self.notify()

    def addMenus(self, menu):
        accls = ModuleModel.addMenus(self, menu)
        menu.AppendSeparator()
        self.addMenu(menu, EditorHelper.wxID_SETUPBUILD, 'build', accls, ())
        self.addMenu(menu, EditorHelper.wxID_SETUPCLEAN, 'clean', accls, ())
        self.addMenu(menu, EditorHelper.wxID_SETUPINSTALL, 'install', accls, ())
        self.addMenu(menu, EditorHelper.wxID_SETUPSDIST, 'sdist', accls, ())
        self.addMenu(menu, EditorHelper.wxID_SETUPBDIST, 'bdist', accls, ())
        self.addMenu(menu, EditorHelper.wxID_SETUPBDIST_WININST, 'bdist_wininst', accls, ())
        menu.AppendSeparator()
        self.addMenu(menu, EditorHelper.wxID_SETUPPY2EXE, 'py2exe', accls, ())
        return accls

    def new(self):
        self.data = (defSetup_py) % ('default', '0.1', '')
        self.saved = false
        self.modified = true
        self.update()
        self.notify()

    def getPageName(self):
        return 'setup (%s)' % os.path.basename(os.path.dirname(self.filename))

# model registry: add to this dict to register a Model
modelReg.update({AppModel.modelIdentifier: AppModel,
            FrameModel.modelIdentifier: FrameModel,
            DialogModel.modelIdentifier: DialogModel,
            MiniFrameModel.modelIdentifier: MiniFrameModel,
            MDIParentModel.modelIdentifier: MDIParentModel,
            MDIChildModel.modelIdentifier: MDIChildModel,
            ModuleModel.modelIdentifier: ModuleModel,
            TextModel.modelIdentifier: TextModel,
            PackageModel.modelIdentifier: PackageModel,
            ConfigFileModel.modelIdentifier: ConfigFileModel,
            BitmapFileModel.modelIdentifier: BitmapFileModel,
            ZipFileModel.modelIdentifier: ZipFileModel,
            CPPModel.modelIdentifier: CPPModel,
            UnknownFileModel.modelIdentifier: UnknownFileModel,
            HTMLFileModel.modelIdentifier: HTMLFileModel,
            XMLFileModel.modelIdentifier: XMLFileModel,
            SetupModuleModel.modelIdentifier: SetupModuleModel})

# All non python files recogniseable by extension
for mod in modelReg.values():
    extMap[mod.ext] = mod
del extMap['.py']
del extMap['.*']
extMap['.cpp'] = extMap['.c'] = extMap['.h'] = CPPModel
extMap['.jpg'] = extMap['.gif'] = extMap['.png'] = BitmapFileModel
extMap['.dtml'] = extMap['.htm'] = extMap['.html']
extMap['.dtd'] = extMap['.xml']
extMap[''] = extMap['.txt']

internalFilesReg = ['.umllay', '.implay', '.brk', '.trace', '.stack']
inspectableFiles = ['.py']

def identifyHeader(headerStr):
    header = string.split(headerStr, ':')
    if len(header) and (header[0] == boaIdent) and modelReg.has_key(header[1]):
        return modelReg[header[1]], header[2]
    return ModuleModel, ''

def identifyFile(filename, source = None, localfs = true):
    """ Return appropriate model for given source file.
        Assumes header will be part of the first continious comment block """
    dummy, name = os.path.split(filename)
    if name == '__init__.py':
        return PackageModel, ''
    if name == 'setup.py':
        return SetupModuleModel, ''
    base, ext = os.path.splitext(filename)
    if not ext and string.upper(base) == base:
        return TextModel, ''
    lext = string.lower(ext)
    if extMap.has_key(lext):
        return extMap[lext], ''

    if not localfs:
        return ModuleModel, ''
    elif lext in inspectableFiles:
        if source is not None:
            return identifySource(string.split(source, '\n'))
        f = open(filename)
        try:
            while 1:
                line = f.readline()
                if not line: break
                line = string.strip(line)
                if line:
                    if line[0] != '#':
                        return ModuleModel, ''
                    headerInfo = identifyHeader(line)
                    if headerInfo[0] != ModuleModel:
                        return headerInfo
            return ModuleModel, ''
        finally:
            f.close()
    else:
        return ModuleModel, ''


def identifySource(source):
    """ Return appropriate model for given source.
        The logic is a copy paste from above func """
    for line in source:
        if line:
            if line[0] != '#':
                return ModuleModel, ''

            headerInfo = identifyHeader(string.strip(line))

            if headerInfo[0] != ModuleModel:
                return headerInfo
        else:
            return ModuleModel, ''
