#-----------------------------------------------------------------------------
# Name:        PythonEditorModels.py
# Purpose:     
#
# Author:      Riaan Booysen
#
# Created:     2002/02/09
# RCS-ID:      $Id$
# Copyright:   (c) 2002
# Licence:     GPL
#-----------------------------------------------------------------------------

print 'importing PythonEditorModels'

import os, string, sys, pprint, imp, stat
from thread import start_new_thread
from time import time, gmtime, strftime

from wxPython import wx

import Preferences, Utils

import EditorHelper, ErrorStack
from EditorModels import SourceModel, EditorModel

import relpath

from Debugger import Debugger
    
from sourceconst import *

true=1;false=0

(imgPyAppModel, imgModuleModel, imgPackageModel, imgSetupModel, 
 imgPythonBinaryFileModel,
) = EditorHelper.imgIdxRange(5)

class SourcePseudoFile(Utils.PseudoFileOutStore):
    def readlines(self):
        return self.output

class ModuleModel(SourceModel):
    modelIdentifier = 'Module'
    defaultName = 'module'
    bitmap = 'Module_s.png'
    imgIdx = imgModuleModel
    ext = '.py'

    def __init__(self, data, name, editor, saved, app=None):
        SourceModel.__init__(self, data, name, editor, saved)
        self.moduleName = os.path.split(self.filename)[1]
        self.app = app
        #self.debugger = None
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
        #del self.debugger

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
            if os: os.chdir(cwd)

    def run(self, args = ''):
        """ Excecute the current saved image of the application. """
        if self.savedAs:
            filename = self.assertLocalFile()

            self.editor.statusBar.setHint('Running %s...' % filename)
            if Preferences.minimizeOnRun:
                self.editor.getMainFrame().Iconize(true)
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
            if not debugger:
                filename = self.assertLocalFile(self.filename)
                debugger = Debugger.DebuggerFrame(self.editor, filename)
                debugger.setDebugClient()
                debugger.setParams(params)
                self.editor.debugger = debugger
            debugger.Show()
            debugger.initSashes()
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

    def buildImportSearchPath(self):
        try: filename = self.assertLocalFile()
        except AssertionError: srchpath = []
        else: srchpath = [os.path.dirname(filename)]
        if self.app:
            try: appfilename = self.app.assertLocalFile()
            except AssertionError: pass
            else: srchpath.insert(0, os.path.dirname(appfilename))

        return srchpath

    def findModule(self, modName, impName=''):
        """ Tries it's best to locate given module name or raise ImportError """
        # first search std python modules
        stdPyPath = sys.path[1:]
        srchpath = stdPyPath[:]
        for name in string.split(modName, '.'):
            try:
                file, path, (ext, mode, tpe) = imp.find_module(name, srchpath)
            except ImportError:
                if srchpath == stdPyPath:
                    # else search module and app dirs
                    srchpath = self.buildImportSearchPath()
                    file, path, (ext, mode, tpe) = imp.find_module(name, srchpath)
                else:
                    raise

            if srchpath == stdPyPath:
                srchpath = []

            if tpe == imp.PKG_DIRECTORY:
                srchpath.append(path)
                continue
            elif tpe == imp.PY_SOURCE:
                # handle from [package.]module import name
                return path, 'name'
            else:
                raise ImportError('Unhandled import type')
        # handle from package import module
        if srchpath and srchpath != stdPyPath:
            if impName:
                path = os.path.join(srchpath[-1], impName+'.py')
                if os.path.isfile(path):
                    return path, 'module'
            else:
                return srchpath[-1], 'package'

        #print '%s not found in %s'%(modName, `srchpath`)
        raise ImportError('Module not found')

    def importInShell(self):
        modDir, modFile = os.path.split(self.assertLocalFile())
        modName = os.path.splitext(modFile)[0]
        if self.app:
            execDir = os.path.dirname(self.app.assertLocalFile())
            if execDir != modDir:
                p, m = os.path.split(relpath.relpath(execDir, self.assertLocalFile()))
                p = string.replace(p, '/', '.')
                p = string.replace(p, '\\', '.')
                pckName = p
                impExecStr = 'from %s import %s'%(pckName, modName)
            else:
                impExecStr = 'import %s'%modName

        else:
            execDir = modDir
            impExecStr = 'import %s'%modName

        shell = self.editor.shell
        if execDir not in sys.path:
            sys.path.append(execDir)
            shell.pushLine("print '## Appended to sys.path'")
        else:
            info = ''

        #self.editor.shell.pushLine('%s%s;print "## Executed from SourceView:\n%s"'%(info, impExecStr, impExecStr))
        shell.pushLine(impExecStr, impExecStr)
        if shell.lastResult != 'stderr':
            return 'Import of %s successfull'%modName, 'Info'
        else:
            return 'Import of %s failed'%modName, 'Error'

    def reloadInShell(self):
        modDir, modFile = os.path.split(self.assertLocalFile())
        modName = os.path.splitext(modFile)[0]
        impExecStr = 'reload(%s)'%modName

        shell = self.editor.shell
        shell.pushLine(impExecStr, impExecStr)

        if shell.lastResult != 'stderr':
            return 'Reload of %s successfull'%modName, 'Info'
        else:
            return 'Reload of %s failed'%modName, 'Error'

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

class ImportRelationshipMix:
    def buildImportRelationshipDict(self, modules):
        relationships = {}

        tot = len(modules)
        self.editor.statusBar.progress.SetRange(tot)
        prog = 0
        totLOC = 0
        classCnt = 0
        # XXX Rewrite in terms of transport
        for module in modules:
            self.editor.statusBar.progress.SetValue(prog)
            prog = prog + 1
            self.editor.statusBar.setHint('Parsing '+module+'...')
            #module = self.modules[moduleName]
            #filename = self.normaliseModuleRelativeToApp(module[2])
            if module[:7] != 'file://':
                print '%s skipped, only local files supported for Imports View'
            else:
                module = module[7:]
            try: f = open(module)
            except IOError:
                print "couldn't load %s" % module
                continue
            else:
                data = f.read()
                f.close()
                name = os.path.splitext(os.path.basename(module))[0]
                model = ModuleModel(data, name, self.editor, 1)
                relationships[name] = model.getModule() #.imports

            totLOC = totLOC + model.getModule().loc
            classCnt = classCnt + len(model.getModule().classes)

        print 'Project LOC: %d,\n%d classes in %d modules.'%(totLOC, classCnt, len(modules))

        self.editor.statusBar.progress.SetValue(0)
        self.editor.statusBar.setHint('')
        return relationships

class PackageModel(ModuleModel, ImportRelationshipMix):
    """ Must be constructed in a valid path, name being filename, actual
        name will be derived from path """

    modelIdentifier = 'Package'
    defaultName = 'package'
    bitmap = 'Package_s.png'
    imgIdx = imgPackageModel
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
                   item.imgIdx == imgPackageModel):
                filtered.append(item)
        return filtered

    def getPageName(self):
        return self.packageName

    def buildImportRelationshipDict(self):
        mods = []
        for module in self.generateFileList():
            mods.append('file://'+module.resourcepath)

        return ImportRelationshipMix.buildImportRelationshipDict(self, mods)

class PythonBinaryFileModel(EditorModel):
    modelIdentifier = 'PythonBinary'
    defaultName = ''
    bitmap = 'PythonBinary_s.png'
    imgIdx = imgPythonBinaryFileModel
    ext = '.pybin'

class BaseAppModel(ClassModel, ImportRelationshipMix):
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
        if not modEnd:
            modEnd = string.find(self.data, '}\r\n', modPos + len(modStr) +1) + 1
            if not modEnd:
                raise 'Module list not terminated properly'
        return modPos + len(modStr), modEnd

    def idModel(self, name, src=None):
        # XXX This should be cached until rename or delete
        absPath = self.normaliseModuleRelativeToApp(self.modules[name][2])
        import Controllers

        from Explorers.Explorer import splitURI
        prot, cat, res, fn = splitURI(absPath)

        if src is None:
            if self.editor.modules.has_key(name):
                self.moduleModels[name], main = Controllers.identifySource(
                    self.editor.modules[name].model.getDataAsLines())
            if self.editor.modules.has_key(absPath):
                self.moduleModels[name], main = Controllers.identifySource(
                    self.editor.modules[absPath].model.getDataAsLines())
            else:
                try: self.moduleModels[name], main = \
                           Controllers.identifyFile(res, localfs=prot=='file')
                except: pass
        else:
            self.moduleModels[name], main = Controllers.identifySource(src)

    def readModules(self):
        modS, modE = self.findModules()
        try:
            self.modules = eval(string.replace(self.data[modS:modE], '\r\n', '\n'))
        except:
            raise 'The "modules" attribute is not a valid dictionary'

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
        err = ErrorStack.crashError(os.path.splitext(self.assertLocalFile())[0]+'.trace')
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

    def buildImportRelationshipDict(self):
        return ImportRelationshipMix.buildImportRelationshipDict(self,
               self.absModulesPaths())

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

class PyAppModel(BaseAppModel):
    modelIdentifier = 'PyApp'
    defaultName = 'PyApp'
    bitmap = 'PythonApplication_s.png'
    imgIdx = imgPyAppModel

##    def renameMain(self, oldName, newName):
##        BaseAppModel.renameMain(self, oldName, newName)

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
    bitmap = 'Setup_s.png'
    imgIdx = imgSetupModel
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

#-------------------------------------------------------------------------------

EditorHelper.modelReg.update({
            PyAppModel.modelIdentifier: PyAppModel,
            ModuleModel.modelIdentifier: ModuleModel,
            SetupModuleModel.modelIdentifier: SetupModuleModel,
            PackageModel.modelIdentifier: PackageModel,
            PythonBinaryFileModel.modelIdentifier: PythonBinaryFileModel,
            })

EditorHelper.inspectableFilesReg.extend(['.py'])