#----------------------------------------------------------------------
# Name:        EditorModels.py
# Purpose:     Model classes usually representing different types of
#              source code
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2001 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

# Behind the screen
# beyond interpretation
# essence

""" The model classes represent different types of source code files,
    Different views can be connected to a model  """

# XXX form inheritance

print 'importing Models'

import string, os, sys, re, pprint, stat
from time import time, gmtime, strftime
from thread import start_new_thread

from wxPython import wx

# XXX 
#import PaletteMapping
import Preferences, Utils, EditorHelper, ErrorStack
from Companions import Companions
from Preferences import keyDefs, Debugger
from Utils import AddToolButtonBmpIS

import relpath
from sourceconst import *

true = 1;false = 0

_vc_hook = None

class EditorModel:
    defaultName = 'abstract'
    bitmap = 'None'
    imgIdx = -1
    closeBmp = 'Images/Editor/Close.bmp'
    objCnt = 0
    def __init__(self, name, data, editor, saved):
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

    def reorderFollowingViewIdxs(self, idx):
        for view in self.views.values():
            if view.pageIdx > idx:
                view.pageIdx = view.pageIdx - 1

    def getDataAsLines(self):
        return string.split(self.data, '\012')

    def setDataFromLines(self, lines):
        data = self.data
        self.data = string.join(lines, '\012')
        self.modified = self.modified or self.data != data


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
    imgIdx = EditorHelper.imgFolder

    def __init__(self, data, name, editor, filepath):
        EditorModel.__init__(self, name, data, editor, true)
        self.filepath = filepath

class SysPathFolderModel(FolderModel):
    modelIdentifier = 'SysPathFolder'
    defaultName = 'syspathfolder'
    bitmap = 'Folder_green.bmp'
    imgIdx = EditorHelper.imgPathFolder

class CVSFolderModel(FolderModel):
    modelIdentifier = 'CVS Folder'
    defaultName = 'cvsfolder'
    bitmap = 'Folder_cyan_s.bmp'
    imgIdx = EditorHelper.imgCVSFolder

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
    imgIdx = EditorHelper.imgBitmapFileModel
    ext = '.bmp'

class UnknownFileModel(EditorModel):
    modelIdentifier = 'Unknown'
    defaultName = '*'
    bitmap = 'Unknown_s.bmp'
    imgIdx = EditorHelper.imgUnknownFileModel
    ext = '.*'


class ZipFileModel(EditorModel):
    modelIdentifier = 'ZipFile'
    defaultName = 'zip'
    bitmap = 'ZipFile_s.bmp'
    imgIdx = EditorHelper.imgZipFileModel
    ext = '.zip'

class BasePersistentModel(EditorModel):
    saveBmp = 'Images/Editor/Save.bmp'
    saveAsBmp = 'Images/Editor/SaveAs.bmp'

    def load(self, notify = true):
        """ Loads contents of data from file specified by self.filename.
            Note: Load's not really used much currently cause objects are 
                  constructed with their data as parameter """
        if not self.transport:
            raise 'No transport for loading'

        self.data = self.transport.load(mode='r')
        self.modified = false
        self.saved = false
        self.update()
        if notify: self.notify()

    def save(self):
        """ Saves contents of data to file specified by self.filename. """
        if not self.transport:
            raise 'No transport for saving'

        if self.filename:
            filename = self.transport.assertFilename(self.filename)
            self.transport.save(filename, self.data, mode='w')
            self.modified = false
            self.saved = true
            
            for view in self.views.values():
                view.saveNotification()
            
            if _vc_hook:
                _vc_hook.save(filename, self.data, mode='w')
        else:
            raise 'No filename'

    def saveAs(self, filename):
        """ Saves contents of data to file specified by filename.
            Override this to catch name changes. """
        # Catch transport changes
        from Explorers.Explorer import splitURI, getTransport
        protO, catO, resO, uriO = splitURI(self.filename)
        protN, catN, resN, uriN = splitURI(filename)

        if protO != protN:
            self.transport = getTransport(protN, catN, resN, 
                  self.editor.explorer.tree.transports)
        
        # Rename and save
        self.filename = filename
        self.save()
        self.savedAs = true

    def assertLocalFile(self, filename=None):
        if filename is None:
            filename = self.filename
        from Explorers.Explorer import splitURI
        prot, cat, filename, uri = splitURI(filename)
        assert prot=='file', 'Operation only supported on the filesystem.'
        return filename

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

    def load(self, notify=true):
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
        self.setDataFromLines(lines)

        self.update()
        self.notify()
        
        self.editor.updateModulePage(self)
        self.editor.updateTitle()

    def acceptConflictChange(self, conflict):
        self.applyChangeBlock(conflict, 1)

    def rejectConflictChange(self, conflict):
        self.applyChangeBlock(conflict, 0)

class ModuleModel(SourceModel):

    modelIdentifier = 'Module'
    defaultName = 'module'
    bitmap = 'Module_s.bmp'
    imgIdx = EditorHelper.imgModuleModel
    ext = '.py'

    def __init__(self, data, name, editor, saved, app=None):
        SourceModel.__init__(self, name, data, editor, saved)
        self.moduleName = os.path.split(self.filename)[1]
        self.app = app
        self.debugger = None
        self.lastRunParams = ''
        self.lastDebugParams = ''
        
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
                import moduleparse
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
        self.setDataFromLines(self.getModule().source)
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
            if os:
                os.chdir(cwd)

    def run(self, args = ''):
        """ Excecute the current saved image of the application. """
        if self.savedAs:
            filename = self.assertLocalFile()

            self.editor.statusBar.setHint('Running %s...' % filename)
            if Preferences.minimizeOnRun:
                self.editor.palette.Iconize(true)
            start_new_thread(self.runInThread, (filename, args,
                  self.app, Preferences.pythonInterpreterPath))

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
        filename = self.assertLocalFile()
        execfile(filename)

    def compile(self):
        import ModRunner
        oldErr = sys.stderr
        sys.stderr = ErrorStack.RecFile()
        try:
            cmr = ModRunner.CompileModuleRunner(self.editor.erroutFrm, self.app)
            cmr.run(self.filename, self.data+'\n\n', self.modified)

            serr = ErrorStack.errorList(sys.stderr)

            cmr.checkError(serr, 'Compiled')
        finally:
            sys.stderr = oldErr
        
        return len(serr)

    def cyclops(self):
        """ Run the saved application thru Cyclops """
        if self.savedAs:
            cwd = os.path.abspath(os.getcwd())
            filename = self.assertLocalFile()
            os.chdir(os.path.dirname(filename))
            page = ''
            try:
                name = os.path.basename(filename)

                # excecute Cyclops in Python with module as parameter
                command = '"%s" "%s" "%s"'%(Preferences.pythonInterpreterPath,
                      Preferences.toPyPath('RunCyclops.py'), name)
                wx.wxExecute(command, true)

                # read report that Cyclops generated
                page = open(name[:-3]+'.cycles', 'r').read()
            finally:
                os.chdir(cwd)
                return page
        else:
            wx.wxLogWarning('Save before running Cyclops')
            raise 'Not saved yet!'

    def debug(self, params=None, cont_if_running=0, cont_always=0,
              temp_breakpoint=None):
        if self.savedAs:
            debugger = self.editor.debugger
            if Preferences.useDebugger == 'old':
                if debugger:
                    debugger.Show(true)
                else:
                    self.editor.debugger = Debugger.DebuggerFrame(self)
                    debugger = self.editor.debugger
                    debugger.Show(true)
                    if params is None: params = []
                    debugger.debug_file(debugger.filename, params)
            elif Preferences.useDebugger == 'new':
                if not debugger:
                    if self.defaultName != 'App' and self.app:
                        filename = self.app.filename
                    else:
                        filename = self.filename
                    filename = self.assertLocalFile(filename)
                    debugger = Debugger.DebuggerFrame(self.editor, filename)
                    debugger.setDebugClient()
                    self.editor.debugger = debugger
                    debugger.setParams(params)
                debugger.Show(true)
                debugger.ensureRunning(cont_if_running, cont_always,
                                       temp_breakpoint)
    
    def profile(self):
        filename = self.assertLocalFile()
        statFile = os.path.splitext(filename)[0]+'.prof'
        if os.path.exists(statFile):
            modtime = os.stat(statFile)[stat.ST_MTIME]
        else:
            modtime = None
        profDir = os.path.dirname(filename)
        
        cwd = os.path.abspath(os.getcwd())
        os.chdir(profDir)
        try:
            profCmd = string.strip(""""%s" -c "import profile;profile.run('execfile('+chr(34)+%s+chr(34)+')', '%s')" """)

            cmd = profCmd % (`Preferences.pythonInterpreterPath`[1:-1],
                  `os.path.basename(filename)`, `statFile`[1:-1])

            if hasattr(self, 'app'): app = self.app
            else: app = None

            from ModRunner import ExecuteModuleRunner
            runner = ExecuteModuleRunner(None, app, profDir)
            self.editor.statusBar.setHint('Profiling %s...'%filename)
            runner.run(cmd)
            self.editor.statusBar.setHint('Finished profiling.')
            
        finally:
            os.chdir(cwd)
        
        return statFile, modtime, profDir


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
        SourceModel.saveAs(self, filename)
        if self.app:
            self.app.moduleSaveAsNotify(self, oldFilename, filename)
        self.moduleName = os.path.basename(filename)
        self.notify()

    def reindent(self, updateModulePage=true):
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

    def disassembleSource(self):
        import dis
        try:
            code = compile(self.data, self.filename, 'exec')
        except:
            oldOut = sys.stdout
            sys.stdout = Utils.PseudoFileOutStore()
            try:
                print "''' Code does not compile\n\n    Disassembly of Traceback:\n'''"
                try:
                    dis.distb(sys.exc_info()[2])
                except:
                    print "''' Could not disassemble traceback '''\n"
                return sys.stdout.read()
            finally:
                sys.stdout = oldOut

        oldOut = sys.stdout
        sys.stdout = Utils.PseudoFileOutStore()
        try:
            try:
                dis.disco(code)
            except:
                raise
            return sys.stdout.read()
        finally:
            sys.stdout = oldOut

        return 'Invisible code'

    def runLint(self):
        filename = self.assertLocalFile()
        from ExternalLib import pylint
        import StringIO
        pylint.pylint(StringIO.StringIO(self.data), filename)
        if pylint.warnings:
            return ErrorStack.buildLintWarningList(pylint.warnings[:])
            

class PackageModel(ModuleModel):
    """ Must be constructed in a valid path, name being filename, actual
        name will be derived from path """

    modelIdentifier = 'Package'
    defaultName = 'package'
    bitmap = 'Package_s.bmp'
    imgIdx = EditorHelper.imgPackageModel
    pckgIdnt = '__init__.py'
    ext = '.py'
    
    def __init__(self, data, name, editor, saved, app=None):
        ModuleModel.__init__(self, data, name, editor, saved, app)
        self.packagePath = os.path.split(self.filename)[0]
        self.packageName = os.path.split(self.packagePath)[1]
        self.savedAs = true
        self.modified = false

    def openPackage(self, name):
        self.editor.openOrGotoModule(os.path.join(self.packagePath, name, self.pckgIdnt))

    def openFile(self, name):
        self.editor.openOrGotoModule(os.path.join(self.packagePath, name + self.ext))

    def generateFileList(self):
        """ Generate a list of modules and packages in the package path """
        
        from Explorers.Explorer import openEx
        transp = openEx(self.packagePath)
        
        filtered = []
        for item in transp.openList():
            if item.treename != '__init__.py' and \
                  (os.path.splitext(item.treename)[1] == self.ext or \
                   item.imgIdx == EditorHelper.imgPackageModel):
                filtered.append(item)
        return filtered
            
    def getPageName(self):
        return self.packageName


class SourcePseudoFile(Utils.PseudoFileOutStore):
    def readlines(self):
        return self.output


class TextModel(PersistentModel):

    modelIdentifier = 'Text'
    defaultName = 'text'
    bitmap = 'Text_s.bmp'
    imgIdx = EditorHelper.imgTextModel
    ext = '.txt'


class CPPModel(SourceModel):

    modelIdentifier = 'CPP'
    defaultName = 'cpp'
    bitmap = 'Cpp_s.bmp'
    imgIdx = EditorHelper.imgCPPModel
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

class ConfigFileModel(PersistentModel):
    modelIdentifier = 'Config'
    defaultName = 'config'
    bitmap = 'Config_s.bmp'
    imgIdx = EditorHelper.imgConfigFileModel
    ext = '.cfg'

class HTMLFileModel(PersistentModel):
    modelIdentifier = 'HTML'
    defaultName = 'html'
    bitmap = 'WebDocHTML_s.bmp'
    imgIdx = EditorHelper.imgHTMLFileModel
    ext = '.html'

class XMLFileModel(PersistentModel):
    modelIdentifier = 'XML'
    defaultName = 'xml'
    bitmap = 'WebDocXML_s.bmp'
    imgIdx = EditorHelper.imgXMLFileModel
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

class _your_frame_: pass
#    def __repr__(self):return `self.__dict__`

class BaseFrameModel(ClassModel):
    """ Base class for all frame type models that can be opened in the Designer
    
    This class is responsible for parsing the _init_* methods generated by the
    Designer and maintaining other special values like window id declarations
    """
    modelIdentifier = 'Frames'
    companion = Companions.DesignTimeCompanion
    def __init__(self, data, name, main, editor, saved, app = None):
        ClassModel.__init__(self, data, name, main, editor, saved, app)
        self.designerTool = None
        self.specialAttrs = []

    def renameMain(self, oldName, newName):
        """ Rename the main class of the module """
        ClassModel.renameMain(self, oldName, newName)
        if self.getModule().functions.has_key('create'):
            self.getModule().replaceFunctionBody('create',
                  ['    return %s(parent)'%newName, ''])

    def renameCtrl(self, oldName, newName):
        # Currently DesignerView maintains ctrls
        pass

    def new(self, params):
        """ Create a new frame module """
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
        """ Return a list of all _init_* methods in the class """
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
        from Views import ObjCollection
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

    def readSpecialAttrs(self, mod, cls):
        """ Read special attributes from __init__ method.
        
        All instance attributes defined between the top of the __init__ method
        and the _init_ctrls() method call will be available to the Designer
        as valid names bound to properties.

        For an attribute to qualify, it has to have a simple deduceable type;
        Python builtin or wxPython objects.
        If for example the attribute is bound to a variable passed in as a
        parameter, you have to first initialise it to a literal of the same
        type. This value will be used at design time.
        
        e.g.    def __init__(self, parent, myFrameCaption):
                    self.frameCaption = 'Design time frame caption'
                    self.frameCaption = myFrameCaption
                    self._init_ctrls(parent)

        No by hand you may add this attribute as a parameter or property value
        in the source.

        In the Inspector property values recognised as special attributes
        will display as bold values and cannot be edited (yet).
        """
        initMeth = cls.methods['__init__']
        startline = initMeth.start
        for idx in range(startline, initMeth.end):
            if Utils.startswith(string.strip(mod.source[idx]), 'self._init_ctrls('):
                endline = idx
                break
        else:
            raise 'self._init_ctrls not found in __init__'

        attrs = []
        for attr, blocks in cls.attributes.items():
            for block in blocks:
                if startline <= block.start <= endline and attr not in attrs:
                    line = mod.source[block.start-1]
                    val = line[string.find(line, '=')+1:]
                    attrs.append( (attr, val) )
        
        import PaletteMapping
        # build a dictionary that can be passed to eval
        evalNS = _your_frame_()
        for attr, code in attrs:
            if hasattr(evalNS, attr):
                continue
            try:
                val = PaletteMapping.evalCtrl(code)
            except Exception, err:
                print str(err)
                continue
            else:
                setattr(evalNS, attr, val)
        return {'self': evalNS}
    
    def readCustomClasses(self, mod, cls):
        """ Read definition for Custom Classes
        
        Custom Classes can be defined as a class attribute named _custom_classes
        containing a dictionary defining wxPython classes and their custom
        equivalents, e.g.
        _custom_classes = {'wxTreeCtrl': ['MyTreeCtrl', 'AdvancedTreeCtrl']}
        
        These custom classes will then be available to the Designer
        and will act as equivalent to the corresponding wxPython class,
        but will generate source for the custom definition.
        
        One implication is that you loose the constructor. Because Boa
        will generate the creation code for the object, the constructor
        signature has to be the same as the wxPython class.
        """
        res = {}
        if cls.class_attributes.has_key('_custom_classes'):
            try:
                import PaletteMapping
                cls_attr = cls.class_attributes['_custom_classes'][0]
                attr_val = cls_attr.signature
                srcline = cls_attr.start
                
                # multiline parser ;)
                while 1:
                    try:
                        custClasses = eval(attr_val)
                        assert type(custClasses) == type({})
                        break
                    except SyntaxError, err: 
                        if err[0] == 'unexpected EOF while parsing':
                            attr_val = attr_val + mod.source[srcline]
                            srcline = srcline + 1
                        else:
                            raise
            except Exception, err:
                raise '_custom_classes is not valid: '+str(err)
            
            for wxClassName, customs in custClasses.items():
                wxClass = PaletteMapping.evalCtrl(wxClassName)
                res[wxClassName] = wxClass
                for custom in customs:
                    res[custom] = wxClass
        return res
        

    def readComponents(self):
        """ Setup object collection dict by parsing all designer controlled methods """
        module = self.getModule()
        # Parse all _init_* methods
        self.objectCollections = {}
        if module.classes.has_key(self.main):
            main = module.classes[self.main]
            
            self.specialAttrs = self.readSpecialAttrs(module, main)
            self.customClasses = self.readCustomClasses(module, main)

            for oc in self.identifyCollectionMethods():
                codeSpan = main.methods[oc]
                codeBody = module.source[codeSpan.start : codeSpan.end]

                self.objectCollections[oc] = self.readDesignerMethod(oc, codeBody)

                # XXX Hack: This should not be necessary !!
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
        """ Remove a method's corresponding window ids from the source code """
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
        """ Write a method's corresponding window ids to the source code """
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
        """ Return template of source code that will run this module type as
        a stand-alone file """
        return simpleAppFrameRunSrc

class FrameModel(BaseFrameModel):
    modelIdentifier = 'Frame'
    defaultName = 'wxFrame'
    bitmap = 'wxFrame_s.bmp'
    imgIdx = EditorHelper.imgFrameModel
    companion = Companions.FrameDTC

class DialogModel(BaseFrameModel):
    modelIdentifier = 'Dialog'
    defaultName = 'wxDialog'
    bitmap = 'wxDialog_s.bmp'
    imgIdx = EditorHelper.imgDialogModel
    companion = Companions.DialogDTC

    def getSimpleRunnerSrc(self):
        return simpleAppDialogRunSrc

class MiniFrameModel(BaseFrameModel):
    modelIdentifier = 'MiniFrame'
    defaultName = 'wxMiniFrame'
    bitmap = 'wxMiniFrame_s.bmp'
    imgIdx = EditorHelper.imgMiniFrameModel
    companion = Companions.MiniFrameDTC

class MDIParentModel(BaseFrameModel):
    modelIdentifier = 'MDIParent'
    defaultName = 'wxMDIParentFrame'
    bitmap = 'wxMDIParentFrame_s.bmp'
    imgIdx = EditorHelper.imgMDIParentModel
    companion = Companions.MDIParentFrameDTC

class MDIChildModel(BaseFrameModel):
    modelIdentifier = 'MDIChild'
    defaultName = 'wxMDIChildFrame'
    bitmap = 'wxMDIChildFrame_s.bmp'
    imgIdx = EditorHelper.imgMDIChildModel
    companion = Companions.MDIChildFrameDTC

# XXX Autocreated frames w/ corresponding imports
# XXX module references to app mut be cleared on closure

class BaseAppModel(ClassModel):
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

    def convertToUnixPath(self, filename):
        # Don't convert absolute windows paths, will stay illegal until saved
        if os.path.splitdrive(filename)[0] != '':
            return filename
        else:
            return string.replace(filename, '\\', '/')

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

#    def renameMain(self, oldName, newName):
#        ClassModel.renameMain(self, oldName, newName)
#        self.getModule().replaceFunctionBody('main',
#          ['    application = %s(0)'%newName, '    application.MainLoop()', ''])

#    def new(self, mainModule):
#        self.data = (defEnvPython + defSig + defImport + defApp) \
#          %(self.modelIdentifier, boaClass, mainModule, mainModule,
#            mainModule, mainModule)
#        self.saved = false
#        self.modified = true
#        self.update()
#        self.notify()

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

    def idModel(self, name, src=None):
        # XXX This should be cached until rename or delete
        absPath = self.normaliseModuleRelativeToApp(self.modules[name][2])
        
        from Explorers.Explorer import splitURI
        prot, cat, res, fn = splitURI(absPath)
        
        if src is None:
            if self.editor.modules.has_key(name):
                self.moduleModels[name], main = identifySource(
                    self.editor.modules[name].model.getDataAsLines())
            if self.editor.modules.has_key(absPath):
                self.moduleModels[name], main = identifySource(
                    self.editor.modules[absPath].model.getDataAsLines())
            else:
                try: self.moduleModels[name], main = \
                           identifyFile(res, localfs=prot=='file')
                except: pass
        else:
            self.moduleModels[name], main = identifySource(src)

    def readModules(self):
        modS, modE = self.findModules()
        try:
            self.modules = eval(self.data[modS:modE])
        except: 
            raise 'Module list not a valid dictionary'

        for mod in self.modules.keys():
            self.idModel(mod)

    def writeModules(self, notify=true):
        modS, modE = self.findModules()
        self.data = self.data[:modS]+pprint.pformat(self.modules)+self.data[modE:]

        self.modified = true
        self.editor.updateTitle()
        self.editor.updateModulePage(self)

        if notify: self.notify()

    def viewAddModule(self):
        fn = self.editor.openFileDlg()
        if fn:
            self.addModule(fn, '')

    def addModule(self, filename, descr, source=None):
        name, ext = os.path.splitext(os.path.basename(filename))
        if self.modules.has_key(name): 
            raise Exception('Module name exists in application')
        if self.savedAs:
            relative = relpath.relpath(os.path.dirname(self.filename), filename)
        else:
            relative = filename
        self.modules[name] = [0, descr, self.convertToUnixPath(relative)]

        self.idModel(name, source)

        self.writeModules()

##    def hasModule(self, absfilename):
##        modRelPath = self.convertToUnixPath(\
##              relpath.relpath(os.path.dirname(self.filename), absfilename) )
##        for main, descr, relPath in self.modules.values():
##            #print os.path.normcase(modRelPath), os.path.normcase(relPath)
##            if os.path.normcase(modRelPath) == os.path.normcase(relPath):
##                return true
##        else:
##            return false

    def removeModule(self, name):
        if not self.modules.has_key(name): raise 'No such module in application'

        del self.modules[name]
        self.writeModules()

    def editModule(self, oldname, newname, main, descr):
        relpath = self.modules[oldname][2]
        if oldname != newname:
            del self.modules[oldname]
        self.modules[newname] = [main, descr, relpath]
        self.writeModules()
    
    def splitProtFile(self, uri):
        protsplit = string.split(uri, '://')
        if len(protsplit) == 1:
            return 'file', uri
        elif len(protsplit) == 2:
            return protsplit
        else:
            raise 'Unhandled protocol %s'%uri

    def moduleFilename(self, name):
        """ Return absolute filename of the given module """
        if not self.modules.has_key(name): 
            raise 'No such module in application: '+name
        
        prot, modFilename = self.splitProtFile(self.modules[name][2])
        if self.savedAs:
            if os.path.isabs(modFilename) or prot != 'file':
                absPath = self.modules[name][2]
            else:
                appProt, appFilename = self.splitProtFile(self.filename)
                absPath = appProt+'://'+self.convertToUnixPath(os.path.normpath(os.path.join(\
                      os.path.dirname(appFilename), modFilename)))
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

            if not self.modules.has_key(oldName): 
                raise 'Module does not exists in application'

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
                frm.display(err)
                return frm
        else:
            wx.wxLogError('Trace file not found. Run with command line param -T')
            return None

    def openModule(self, name):
        return self.editor.openOrGotoModule(self.moduleFilename(name), self)

    def normaliseModuleRelativeToApp(self, relFilename):
        """ Normalise relative paths to absolute paths """
        if not self.savedAs:
            return relFilename#os.path.normpath(os.path.join(Preferences.pyPath, relFilename))
        else:
            protsplit = string.split(self.filename, '://')
            if len(protsplit) == 1:
                prot, appFilename = 'file', self.filename
            elif len(protsplit) == 2:
                prot, appFilename = protsplit
            else:
                raise 'Unhandled protocol'

            normedpath = os.path.normpath(os.path.join(os.path.dirname(appFilename), 
                  relFilename))
            if prot == 'file':
                return '%s://%s' %(prot, normedpath)
            else:
                return '%s://%s' %(prot, string.replace(normedpath, '\\', '/'))
                

    def buildImportRelationshipDict(self, modules=None):
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
            filename = self.normaliseModuleRelativeToApp(module[2])
            if filename[:7] != 'file://':
                print '%s skipped, only local files supported for Imports View'
            else:
                filename = filename[7:]
            try: f = open(filename)
            except IOError:
                print "couldn't load %s" % filename
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

    def update(self):
        ClassModel.update(self)
        self.readModules()

    def loadTextInfo(self, viewName):
        # XXX rewrite for transport
        fn = os.path.join(os.path.dirname(self.filename), viewName)
        if os.path.exists(fn):
            self.textInfos[viewName] = open(fn).read()
        else:
            self.textInfos[viewName] = ''

class AppModel(BaseAppModel):
    modelIdentifier = 'App'
    defaultName = 'wxApp'
    bitmap = 'wxApp_s.bmp'
    imgIdx = EditorHelper.imgAppModel

    def renameMain(self, oldName, newName):
        BaseAppModel.renameMain(self, oldName, newName)
        self.getModule().replaceFunctionBody('main',
          ['    application = %s(0)'%newName, '    application.MainLoop()', ''])

    def new(self, mainModule):
        self.data = (defEnvPython + defSig + defImport + defApp) \
          %(self.modelIdentifier, boaClass, mainModule, mainModule,
            mainModule, mainModule)
        self.saved = false
        self.modified = true
        self.update()
        self.notify()

class PyAppModel(BaseAppModel):
    modelIdentifier = 'PyApp'
    defaultName = 'PyApp'
    bitmap = 'PythonApplication_s.bmp'
    imgIdx = EditorHelper.imgPyAppModel

    def renameMain(self, oldName, newName):
        BaseAppModel.renameMain(self, oldName, newName)
##        self.getModule().replaceFunctionBody('main',
##          ['    application = %s(0)'%newName, '    application.MainLoop()', ''])

    def new(self):
        self.data = (defEnvPython + defSig + defPyApp) \
          %(self.modelIdentifier, 'main')
        self.saved = false
        self.modified = true
        self.update()
        self.notify()

class SetupModuleModel(ModuleModel):
    modelIdentifier = 'setup'
    defaultName = 'Setup'
    bitmap = 'Setup_s.bmp'
    imgIdx = EditorHelper.imgSetupModel
    def __init__(self, data, name, editor, saved, app=None):
        ModuleModel.__init__(self, data, name, editor, saved, app)
        if data:
            self.update()
            self.notify()

    def new(self):
        self.data = (defSetup_py) % ('default', '0.1', '')
        self.saved = false
        self.modified = true
        self.update()
        self.notify()

    def getPageName(self):
        return 'setup (%s)' % os.path.basename(os.path.dirname(self.filename))

modelReg = EditorHelper.modelReg
extMap = EditorHelper.extMap

# model registry: add to this dict to register a Model
modelReg.update({AppModel.modelIdentifier: AppModel,
            FrameModel.modelIdentifier: FrameModel,
            DialogModel.modelIdentifier: DialogModel,
            MiniFrameModel.modelIdentifier: MiniFrameModel,
            MDIParentModel.modelIdentifier: MDIParentModel,
            MDIChildModel.modelIdentifier: MDIChildModel,
            PyAppModel.modelIdentifier: PyAppModel,
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

def identifyFilename(filename):
    dummy, name = os.path.split(filename)
    base, ext = os.path.splitext(filename)
    lext = string.lower(ext)

    if name == '__init__.py':
        return PackageModel, '', lext
    if name == 'setup.py':
        return SetupModuleModel, '', lext
    if not ext and string.upper(base) == base:
        return TextModel, '', lext
    if extMap.has_key(lext):
        return extMap[lext], '', lext
    return None, '', lext

def identifyFile(filename, source=None, localfs=true):
    """ Return appropriate model for given source file.
        Assumes header will be part of the first continious comment block """
    Model, main, lext = identifyFilename(filename)
    if Model is not None:
        return Model, main
    
##    dummy, name = os.path.split(filename)
##    if name == '__init__.py':
##        return PackageModel, ''
##    if name == 'setup.py':
##        return SetupModuleModel, ''
##    base, ext = os.path.splitext(filename)
##    if not ext and string.upper(base) == base:
##        return TextModel, ''
##    lext = string.lower(ext)
##    if extMap.has_key(lext):
##        return extMap[lext], ''

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
