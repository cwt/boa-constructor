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

import moduleparse, string, os, sys, re, py_compile
from os import path
import relpath, pprint
from Companions import Companions
import Editor, ErrorStack
from Views.DiffView import PythonSourceDiffView
from Views.AppViews import AppCompareView
import Preferences, Utils
from wxPython import wx 
from Utils import AddToolButtonBmpIS
from time import time, gmtime, strftime
from stat import *
from PrefsKeys import keyDefs
from Debugger import Debugger

#from wxPython.lib.dialogs import wxScrolledMessageDialog
import wxPython
from PhonyApp import wxProfilerPhonyApp
import profile

true = 1
false = 0

boaIdent = '#Boa'
boaClass = 'BoaApp'
#nl = chr(13)+chr(10)
init_ctrls = '_init_ctrls'
init_coll = '_init_coll_'
init_utils = '_init_utils'
init_props = '_init_props'
init_events = '_init_events'
defEnvPython = '#!/bin/env python\n'
defImport = 'from wxPython.wx import *\n\n'
defSig = boaIdent+':%s:%s\n\n'

defCreateClass = '''def create(parent):
    return %s(parent)
\n'''
wid = '[A-Za-z0-9_, ]*'
srchWindowIds = '\[(?P<winids>[A-Za-z0-9_, ]*)\] = '+\
'map\(lambda %s: [wx]*NewId\(\), range\((?P<count>\d+)\)\)'
defWindowIds = '''[%s] = map(lambda %s: wxNewId(), range(%d))\n'''

defClass = '''
class %s(%s):
    def '''+init_utils+'''(self): 
        pass

    def '''+init_ctrls+'''(self, prnt): 
        %s.__init__(%s)
        self.'''+init_utils+'''()
        
    def __init__(self, parent): 
        self.'''+init_ctrls+'''(parent)
'''

# This the closest I get to destroying partially created 
# frames without mucking up my indentation. 
# This doesn't not handle the case where the constructor itself fails
# Replace defClass with this in line 412 if you feel the need

defSafeClass = '''
class %s(%s):
    def '''+init_utils+'''(self): 
        pass

    def '''+init_ctrls+'''(self, prnt): 
        %s.__init__(%s)
        
    def __init__(self, parent): 
        self.'''+init_utils+'''()
        try: 
            self.'''+init_ctrls+'''(parent)

            # Your code
        except: 
            self.Destroy()
            import traceback
            traceback.print_exc()
            raise
'''

defApp = '''import %s

modules = {'%s' : [1, 'Main frame of Application', '%s.py']}

class BoaApp(wxApp):
    def OnInit(self):
        self.main = %s.create(None)
        self.main.Show(true)
        self.SetTopWindow(self.main)
        return true

def main():
    application = BoaApp(0)
    application.MainLoop()

if __name__ == '__main__':
    main()'''

defInfoBlock = '''#-----------------------------------------------------------------------------
# Name:        %s
# Purpose:     %s
#                
# Author:      %s
#                
# Created:     %s
# RCS-ID:      %s
# Copyright:   %s
# Licence:     %s
#-----------------------------------------------------------------------------
''' 

defSetup_py = '''
from distutils.core import setup

setup(name = '%s',
      version = '%s',
      scripts = [%s],
)
'''


# Indexes for the imagelist
imgCounter=33
[imgAppModel, imgFrameModel, imgDialogModel, imgMiniFrameModel, 
 imgMDIParentModel, imgMDIChildModel, imgModuleModel, imgPackageModel,
 imgTextModel, imgConfigFileModel, imgZopeExportFileModel, imgBitmapFileModel,
 imgZipFileModel, imgCPPModel, imgUnknownFileModel, imgHTMLFileModel, 
 imgSetupModel,
 
 imgFolder, imgPathFolder, imgCVSFolder, imgZopeFolder, imgZopeControlPanel,
 imgZopeProductFolder, imgZopeInstalledProduct, imgZopeUserFolder, imgZopeDTMLDoc, 
 imgZopeImage, imgZopeSystemObj, imgZopeConnection, imgBoaLogo, imgFolderUp, 
 imgFSDrive, imgFolderBookmark] = range(imgCounter)

# Indexes for the ZOA relevant imagelist
ZOAIcons={}
ZOAIcons["root"] =imgCounter
ZOAIcons["Folder"] =imgCounter+1
ZOAIcons["directory"]=ZOAIcons["Local Directory"]=ZOAIcons["Folder"]
ZOAIcons["Z Class"] =imgCounter+2
ZOAIcons["Product Help"] =imgCounter+3
ZOAIcons["Product Management"] =imgCounter+4
ZOAIcons["Python Method"] =ZOAIcons["Script (Python)"] =imgCounter+5
ZOAIcons["Z ODBC Database Connection"] =imgCounter+6
ZOAIcons["User Folder"] =imgCounter+7
ZOAIcons["Local File System"] =imgCounter+8
ZOAIcons["Control Panel"] =imgCounter+9
ZOAIcons["External Method"] =imgCounter+10
ZOAIcons["Product"] =imgCounter+11
ZOAIcons["DTML Method"] =imgCounter+12
ZOAIcons["Broken Because Product is Gone"] =imgCounter+13
ZOAIcons["DTML Document"] =imgCounter+14
ZOAIcons["unknown"] =imgCounter+15
ZOAIcons["Zope Factory"] =imgCounter+16
ZOAIcons["Zope Permission"] =imgCounter+17
ZOAIcons["Z SQL Method"] =imgCounter+18
ZOAIcons["Debug Information"]=imgCounter+19
ZOAIcons["Version Management"] =imgCounter+20
ZOAIcons["Database Management"] =imgCounter+21
ZOAIcons["Version"] =imgCounter+22
ZOAIcons["common"] =imgCounter+23
ZOAIcons["Base Class"] =imgCounter+24
ZOAIcons["Aggregation"] =imgCounter+25

        

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
        self.addMenu(menu, Editor.wxID_EDITORCLOSEPAGE, 'Close', (keyDefs['Close']))
        return []

    def reorderFollowingViewIdxs(self, idx):
##        print 'reorder', self.views.values 
        for view in self.views.values():
##            print view.viewName
            if view.pageIdx > idx:
                view.pageIdx = view.pageIdx - 1

    def load(self, notify = true):
        """ Loads contents of data from file specified by self.filename. 
            Note: Load not really used currently objects are constructed
                  with their data as parameter """
        f = open(self.filename, 'r')
        self.data = f.read()
        f.close()
        self.modified = false
        self.saved = false
        self.update()
        if notify: self.notify()
    
    def save(self):
        """ Saves contents of data to file specified by self.filename. """
        if self.filename:
            try:
                f = open(self.filename, 'w')
            except IOError, message:
                dlg = wx.wxMessageDialog(self.editor, 'Could not save\n'+message.strerror,
                                      'Error', wx.wxOK | wx.wxICON_ERROR)
                try: dlg.ShowModal()
                finally: dlg.Destroy()
            else:
                # Strip off final spaces for every line
#                f.writelines(map(lambda s: string.rstrip(s) + '\n', string.split(self.data, '\n')))

                f.write(self.data)
                f.close()
                self.modified = false
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
        return path.splitext(path.basename(self.filename))[0]

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
        self.root = self.readFile(path.join(self.filepath, 'Root'))
        self.repository = self.readFile(path.join(self.filepath, 'Repository'))
        self.entries = []

        f = open(path.join(self.filepath, 'Entries'), 'r')
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

class ZopeExportFileModel(EditorModel):
    modelIdentifier = 'ZopeExport'
    defaultName = 'zexp'
    bitmap = 'ZopeExport_s.bmp'
    imgIdx = imgZopeExportFileModel
    ext = '.zexp'
                        
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
        self.packagePath, dummy = path.split(self.filename)
        dummy, self.packageName = path.split(self.packagePath)
        self.savedAs = true
        self.modified = false
    
    def addTools(self, toolbar):
        EditorModel.addTools(self, toolbar)
        AddToolButtonBmpIS(self.editor, toolbar, self.saveBmp, 'Save', self.editor.OnSave)
        AddToolButtonBmpIS(self.editor, toolbar, self.saveAsBmp, 'Save as...', self.editor.OnSaveAs)

    def addMenus(self, menu):
        accls = EditorModel.addMenus(self, menu)
        self.addMenu(menu, Editor.wxID_EDITORSAVE, 'Save', accls, (keyDefs['Save']))
        self.addMenu(menu, Editor.wxID_EDITORSAVEAS, 'Save as...', accls, (keyDefs['SaveAs']))
        return accls

    def openPackage(self, name):
        self.editor.openModule(path.join(self.packagePath, name, self.pckgIdnt))
    
    def openFile(self, name):
        self.editor.openModule(path.join(self.packagePath, name + self.ext))
    
    def generateFileList(self):
        """ Generate a list of modules and packages in the package path """
        files = os.listdir(self.packagePath)
        packages = []
        modules = []
        for file in files:
            filename = path.join(self.packagePath, file)
            mod, ext = path.splitext(file)
            if file == self.pckgIdnt: continue
            elif (ext == self.ext) and path.isfile(filename):
                modules.append((mod, identifyFile(filename)[0]))
            elif path.isdir(filename) and \
              path.exists(path.join(filename, self.pckgIdnt)):
                packages.append((file, PackageModel))
        
        return packages + modules

    def getPageName(self):
        return self.packageName

class SourceModel(EditorModel):
    modelIdentifier = 'Source'
    def getCVSConflicts(self):
        lines = string.split(self.data, '\012')
        # needless obscurity
        # numedLines = apply(map, (None,) + (lines, range(len(lines))) )

        # use model.module.source
        conflictStart = -1
        confCnt = 0
        lineNo = 0
        conflicts =[]
        for line in lines:
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
        lines = string.split(self.data, '\012')
        
        blocks = Utils.split_seq(lines[start+1 : start+size], '=======')
        lines[start:start+size+1] = blocks[blockIdx]
        self.data = string.join(lines, '\012')

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

    saveBmp = 'Images/Editor/Save.bmp'
    saveAsBmp = 'Images/Editor/SaveAs.bmp'

    def __init__(self, data, name, editor, saved, app = None):
        SourceModel.__init__(self, name, data, editor, saved)
        self.moduleName = path.split(self.filename)[1]
        self.app = app
        self.debugger = None
        if data: self.update()

    def destroy(self):
        SourceModel.destroy(self)
        del self.app
        del self.debugger
        
    def addTools(self, toolbar):
        SourceModel.addTools(self, toolbar)
        AddToolButtonBmpIS(self.editor, toolbar, self.saveBmp, 'Save', self.editor.OnSave)
        AddToolButtonBmpIS(self.editor, toolbar, self.saveAsBmp, 'Save as...', self.editor.OnSaveAs)
        
    def addMenus(self, menu):
        accls = SourceModel.addMenus(self, menu)
        self.addMenu(menu, Editor.wxID_EDITORSAVE, 'Save', accls, (keyDefs['Save']))
        self.addMenu(menu, Editor.wxID_EDITORSAVEAS, 'Save as...', accls, (keyDefs['SaveAs']))
        menu.Append(-1, '-')
        self.addMenu(menu, Editor.wxID_EDITORSWITCHAPP, 'Switch to app', accls, (keyDefs['SwitchToApp']))
        self.addMenu(menu, Editor.wxID_EDITORDIFF, 'Diff modules...', accls, ())
        return accls

    def new(self):
        self.data = ''
        self.savedAs = false
        self.modified = true
        self.update()
        self.notify()

    def load(self, notify = true):
        SourceModel.load(self, false)
        self.update()
        if notify: self.notify()

    def getModule(self):
        if self._module is None:
#            t1 = time()
            wx.wxBeginBusyCursor()
            try:
                self._module = moduleparse.Module(
                    self.moduleName, string.split(self.data, '\012'))
            finally:
                wx.wxEndBusyCursor()
#            t2 = time()
#            print 'parse module', t2 - t1
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

    def run(self, args = ''):
        """ Excecute the current saved image of the application. """
        if self.savedAs:
            cwd = path.abspath(os.getcwd())
            os.chdir(path.dirname(self.filename))
            oldErr = sys.stderr
            oldSysPath = sys.path[:]
            try:
                sys.path.append(Preferences.pyPath)
                cmd = '"%s" %s %s'%(sys.executable, path.basename(self.filename), args)
                print 'executing', cmd, args
                
                from ModRunner import PreferredRunner
                if Preferences.minimizeOnRun:
                    self.editor.palette.Iconize(true)
                try:
                    if self.editor.erroutFrm:
                        self.editor.erroutFrm.Destroy()
                    self.editor.erroutFrm = PreferredRunner(self.editor, self.app).run(cmd)
                finally:
                    if Preferences.minimizeOnRun:
                        self.editor.palette.Iconize(false)
                        if self.editor.erroutFrm:
                            self.editor.erroutFrm.Raise()
##                        self.editor.palette.Raise()
##                        self.editor.inspector.Raise()
##                        self.editor.Raise()
        
                    
            finally:
                sys.path = oldSysPath
                sys.stderr = oldErr
                os.chdir(cwd)

    def runAsScript(self):
        execfile(self.filename)
    
    def compile(self):
        if self.savedAs:
            import ModRunner
            oldErr = sys.stderr
            sys.stderr = ErrorStack.RecFile()
            try:
                try:
                    cmr = ModRunner.CompileModuleRunner(self.editor, self.app)
                    cmr.run(self.filename)
                except:
                    print 'Compile Exception!'
                    raise
                else:
                    print 'Compiled Successfully'
                serr = ErrorStack.errorList(sys.stderr)
                cmr.checkError(serr, 'Compiled')
            finally:
                sys.stderr = oldErr

    def cyclops(self):
        """ Excecute the current saved image of the application. """
        if self.savedAs:
            cwd = path.abspath(os.getcwd())
            os.chdir(path.dirname(self.filename))
            page = ''
            try:
                name = path.basename(self.filename)

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
            wxLogWarning('Save before running Cyclops')
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
            cwd = path.abspath(os.getcwd())
            os.chdir(path.dirname(self.filename))

            tmpApp = wxPython.wx.wxApp
            wxProfilerPhonyApp.realApp = self.editor.app
            wxPython.wx.wxApp = wxProfilerPhonyApp
            try:
                prof = profile.Profile()
                try:
                    prof = prof.run('execfile("%s")'% path.basename(self.filename))
                except SystemExit:
                    pass
                prof.create_stats()
                return prof.stats     

            finally:
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
        self.moduleName = path.basename(filename)
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

class ZopeEditorModel(EditorModel):
    def __init__(self, name, data, editor, saved, zopeObject): 
        EditorModel.__init__(self, name, data, editor, saved)
        self.zopeObj = zopeObject  #this is the instance of our node now
    
class ZopeDocumentModel(ZopeEditorModel):
    modelIdentifier = 'ZopeDocument'
    defaultName = 'zopedoc'
    bitmap = 'Package_s.bmp'
    imgIdx = imgZopeDTMLDoc

    saveBmp = 'Images/Editor/Save.bmp'

    def __init__(self, name, data, editor, saved, zopeObject): 
        #self, name, data, editor, saved, zopeConnection, zopeObject
        
#        imgIdx = zopeObject.image #set correct bitmap
        ZopeEditorModel.__init__(self, name, data, editor, saved, zopeObject)
        #self.zopeConn = zopeConnection
        self.savedAs = true
        
        
    def addTools(self, toolbar):
        ZopeEditorModel.addTools(self, toolbar)
        AddToolButtonBmpIS(self.editor, toolbar, self.saveBmp, 'Save', self.editor.OnSave)
        
    def addMenus(self, menu):
        accls = ZopeEditorModel.addMenus(self, menu)
        self.addMenu(menu, Editor.wxID_EDITORSAVE, 'Save', accls, (keyDefs['Save']))
        return accls

    def load(self, notify = true):
        #self.data = self.zopeObj.zopeConn.load(self.zopeObj)
        self.data = self.zopeObj.getDocument()
        self.modified = false
        self.saved = false
        self.update()
        if notify: self.notify()
    
    def save(self):
        """ Saves contents of data to file specified by self.filename. """
        if self.filename:
            
            #self.zopeObj.zopeConn.save(self.zopeObj,self.data)

            # XXX don't want to import this :(
            from ExternalLib import xmlrpclib

            try:
                self.zopeObj.saveDocument(self.data)
            except xmlrpclib.Error, error:
#                wxLogError('Error while attempting to save: %s' % str(error))
                import HTMLResponse
                frm = HTMLResponse.create(None, error.faultString)
                frm.Show(true)
                raise
            else:                
                self.modified = false
        else:
            raise 'No filename'
    
    def saveAs(self, filename):
        """ Saves contents of data to file specified by filename.
            Override this to catch name changes. """

        raise 'Save as not supported'

    def getPageName(self):
        if self.zopeObj.name == 'index_html':
            return '%s (%s)' % (self.zopeObj.name, string.split(self.zopeObj.path, '/')[-1])
        else:
            return self.zopeObj.name

class ZopePythonSourceModel(ZopeDocumentModel):
    modelIdentifier = 'ZopePythonSource'

    def __init__(self, name, data, editor, saved,  zopeObject):
        ZopeDocumentModel.__init__(self, name, data, editor, saved,  zopeObject)
        self._module = None

    def getModule(self):
        if self._module is None:
            wx.wxBeginBusyCursor()
            try:
                self._module = moduleparse.Module(
                    self.zopeObj.whole_name, string.split(self.data, '\012'))
            finally:
                wx.wxEndBusyCursor()
        return self._module

class ZopePythonScriptModel(ZopePythonSourceModel):
    modelIdentifier = 'ZopePythonScript'
    defaultName = 'zopepythonscript'
    bitmap = 'Package_s.bmp'
    imgIdx = ZOAIcons["Script (Python)"]

class ZopePythonMethodModel(ZopePythonSourceModel):
    modelIdentifier = 'ZopePythonMethod'
    defaultName = 'zopepythonmethod'
    bitmap = 'Package_s.bmp'
    imgIdx = ZOAIcons["Python Method"]

class BasicFileModel(EditorModel):
    
    saveBmp = 'Images/Editor/Save.bmp'
    saveAsBmp = 'Images/Editor/SaveAs.bmp'

    def __init__(self, data, name, editor, saved):
        EditorModel.__init__(self, name, data, editor, saved)
        if data: self.update()
        
    def addTools(self, toolbar):
        EditorModel.addTools(self, toolbar)
        AddToolButtonBmpIS(self.editor, toolbar, self.saveBmp, 'Save', self.editor.OnSave)
        AddToolButtonBmpIS(self.editor, toolbar, self.saveAsBmp, 'Save as...', self.editor.OnSaveAs)

    def addMenus(self, menu):
        accls = EditorModel.addMenus(self, menu)
        self.addMenu(menu, Editor.wxID_EDITORSAVE, 'Save', accls, (keyDefs['Save']))
        self.addMenu(menu, Editor.wxID_EDITORSAVEAS, 'Save as...', accls, (keyDefs['SaveAs']))
        return accls

    def new(self):
        self.data = ''
        self.savedAs = false
        self.modified = true
        self.update()
        self.notify()

    def load(self, notify = true):
        EditorModel.load(self, false)
        self.update()
        if notify: self.notify()

class TextModel(BasicFileModel):

    modelIdentifier = 'Text'
    defaultName = 'text'
    bitmap = 'Text_s.bmp'
    imgIdx = imgTextModel
    ext = '.txt'


class CPPModel(BasicFileModel):

    modelIdentifier = 'CPP'
    defaultName = 'cpp'
    bitmap = 'Cpp_s.bmp'
    imgIdx = imgCPPModel
    ext = '.cxx'

    def __init__(self, data, name, editor, saved):
        BasicFileModel.__init__(self, data, name, editor, saved)
        self.loadHeader()
        
    def loadHeader(self):
        header = os.path.splitext(self.filename)[0]+'.h'
        if os.path.exists(header):
            self.headerData = open(header).read()
        else:
            self.headerData = ''

    def load(self, notify = true):
        BasicFileModel.load(self, false)
        self.loadHeader()
        self.update()
        if notify: self.notify()

##class HPPModel(CPPModel):
##    modelIdentifier = 'HPP'
##    defaultName = 'hpp'
##    bitmap = 'Cpp_s.bmp'
##    imgIdx = 13
##    ext = '.h'
                
class ConfigFileModel(BasicFileModel):
    modelIdentifier = 'Config'
    defaultName = 'config'
    bitmap = 'Config_s.bmp'
    imgIdx = imgConfigFileModel
    ext = '.cfg'

class HTMLFileModel(BasicFileModel):
    modelIdentifier = 'HTML'
    defaultName = 'html'
    bitmap = 'Text_s.bmp'
    imgIdx = imgHTMLFileModel
    ext = '.html'
    
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

##        header = string.split(string.strip(self.getModule().source[0]), ':')
##        if (len(header) == 3) and (header[0] == '#Boa'):
##            self.getModule().source[0] = string.join((header[0], header[1], newName), ':')

class ObjectCollection:
    def __init__(self):#, creators = [], properties = [], events = [], collections = []):
        self.creators = []
        self.properties = []
        self.events = []
        self.collections = []
        self.initialisers = []
        self.finalisers = []
        
        self.creatorByName = {}
        self.propertiesByName = {}
        self.eventsByName = {}
        self.collectionsByName = {}

    def __repr__(self):
        return '<ObjectCollection instance: %s,\n %s,\n %s,\n %s,\nBy name:\n %s,\n %s,\n %s,\n %s,>'% (`self.creators`, `self.properties`, 
           `self.collections`, `self.events`, 
           `self.creatorByName`, `self.propertiesByName`, 
           `self.collectionsByName`, `self.eventsByName`)

    def setup(self, creators, properties, events, collections, initialisers, finalisers):
        self.creators = creators
        self.properties = properties
        self.events = events
        self.collections = collections
        self.initialisers = initialisers
        self.finalisers = finalisers
    
    def merge(self, objColl):
        """ Merge another object collection with this one """

        def mergeList(myLst, newLst):
            for item in newLst:
                myLst.append(item)
        
        mergeList(self.creators, objColl.creators)
        mergeList(self.properties, objColl.properties)
        mergeList(self.events, objColl.events)
        mergeList(self.collections, objColl.collections)
        mergeList(self.initialisers, objColl.initialisers)
        mergeList(self.finalisers, objColl.finalisers)
        
        self.indexOnCtrlName()
    
    def getCtrlNames(self):
        """ Return a list of (name, class) tuples """
        return map(lambda x, d=self.creatorByName: (d[x][0].comp_name, 
              d[x][0].class_name), self.creatorByName.keys())

    def removeReference(self, name, method):
        i = 0
        while i < len(self.collections):
            if self.collections[i].method == method:
                del self.collections[i]
            else:
                i = i + 1

        if self.collectionsByName.has_key(name):
            namedColls = self.collectionsByName[name]
            
            i = 0
            while i < len(namedColls):
                if namedColls[i].method == method:
                    del namedColls[i]
                else:
                    i = i + 1

        i = 0
        while i < len(self.properties):
            prop = self.properties[i]
            if len(prop.params) and prop.params[0][5:len(method) +5] == method:
                del self.properties[i]
            else:
                i = i + 1

        i = 0
        if self.propertiesByName.has_key(name):
            props = self.propertiesByName[name]
            while i < len(props):
                prop = props[i]
                if len(prop.params) and prop.params[0][5:len(method) +5] == method:
                    del props[i]
                else:
                    i = i + 1

    def renameList(self, lst, dict, name, new_name):
        for item in lst:
            item.renameCompName2(name, new_name)
        
        # keep named colls in sync
        if dict.has_key(name):
            dict[new_name] = dict[name]
            del dict[name]

    def renameCtrl(self, name, new_name):
        self.renameList(self.creators, self.creatorByName, name, new_name)
        self.renameList(self.properties, self.propertiesByName, name, new_name)
        self.renameList(self.events, self.eventsByName, name, new_name)
        self.renameList(self.collections, self.collectionsByName, name, new_name)
            
    def deleteCtrl(self, name):
        for list in (self.creators, self.properties, self.events):
            i = 0
            while i < len(list):
                if list[i].comp_name == name:
                    del list[i]
                else:
                    i = i + 1
    
##    def findRootParent(self):
##        for crt in self.creators:
##            if crt.params.has_key('parent'):
                
    def reparent(self, oldParent, newParent):
        for crt in self.creators:
            if crt.params.has_key('parent') and crt.params['parent'] == oldParent:
                crt.params['parent'] = newParent

    def setupList(self, list):
        dict = {}
        for item in list:
            if not dict.has_key(item.comp_name):
                dict[item.comp_name] = []
            dict[item.comp_name].append(item)
        return dict
        
    def indexOnCtrlName(self):
        self.creatorByName = self.setupList(self.creators)
        self.propertiesByName = self.setupList(self.properties)
        self.eventsByName = self.setupList(self.events)
        self.collectionsByName = self.setupList(self.collections)

def isInitCollMeth(meth):
    return len(meth) > len(init_coll) and meth[:11] == init_coll

def getCollName(collInitMethod, name):
    return collInitMethod[len('_init_coll_'+name)+1:]
    
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
        self.addMenu(menu, Editor.wxID_EDITORDESIGNER, 'Frame Designer', accls, (keyDefs['Designer']))
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
        if isInitCollMeth(meth):
            try:
                res = Utils.split_seq(codeBody, '', string.strip)
                inits, body, fins = res[:3]
            except ValueError:
                raise 'Collection body %s not in init, body, fin form' % meth
            
            allInitialisers = methodparse.parseMixedBody(\
              [methodparse.CollectionItemInitParse, methodparse.EventParse], 
               body)

            creators = allInitialisers.get(methodparse.CollectionItemInitParse, [])
            collectionInits = []
            properties = []
            events = allInitialisers.get(methodparse.EventParse, [])
        # Normal method
        else:
            inits = []
            fins = []
                
            allInitialisers = methodparse.parseMixedBody(\
              [methodparse.ConstructorParse, methodparse.EventParse, 
               methodparse.CollectionInitParse, methodparse.PropertyParse], 
               codeBody)
            
            creators = allInitialisers.get(methodparse.ConstructorParse, [])
            collectionInits = allInitialisers.get(methodparse.CollectionInitParse, [])
            properties = allInitialisers.get(methodparse.PropertyParse, [])
            events = allInitialisers.get(methodparse.EventParse, [])

        newObjColl = ObjectCollection()
        newObjColl.setup(creators, properties, events, collectionInits, inits, fins)
        
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

                # XXX This should not be necessary
                if len(oc) >= 11 and oc[:11] == init_ctrls and \
                  string.strip(codeBody[1]) == 'self._init_utils()':
                    del codeBody[1]

                self.objectCollections[oc] = self.readDesignerMethod(oc, codeBody)

            # Set the model's constructor
            if self.objectCollections.has_key(init_ctrls):
                self.mainConstr = self.objectCollections[init_ctrls].creators[0]


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
        self.addMenu(menu, Editor.wxID_EDITORCMPAPPS, 'Compare apps...', accls, ())
        return accls
        
    def convertToUnixPath(self, filename):
        # Don't convert absolute windows paths, will stay illegal until saved
        if path.splitdrive(filename)[0] != '':
            return filename
        else:
            return string.join(string.split(filename, '\\'), '/')

    def save(self):
        ClassModel.save(self)
        for tin in self.unsavedTextInfos:
            fn = os.path.join(os.path.dirname(self.filename), tin)
            data = self.textInfos[tin]
            if data:
                open(fn, 'w').write(data)
        self.unsavedTextInfos = []

    def saveAs(self, filename):
        for mod in self.modules.keys():
            self.modules[mod][2] = self.convertToUnixPath(\
              relpath.relpath(path.dirname(filename), 
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
        modEnd = string.find(self.data, '}', modPos + len(modStr) +1) + 1
        if modEnd == -1: raise 'Module list not terminated properly'
        return modPos + len(modStr), modEnd
            
    def idModel(self, name):
        absPath = self.normaliseModuleRelativeToApp(self.modules[name][2])
        if path.exists(absPath):
            self.moduleModels[name], main = identifyFile(absPath)
        else:
            if self.editor.modules.has_key(absPath):
                self.moduleModels[name], main = identifySource(
                    self.editor.modules[absPath].model.getModule().source)
            elif self.editor.modules.has_key(path.basename(absPath)):
                self.moduleModels[name], main = identifySource(
                    self.editor.modules[path.basename(absPath)
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
        
    def readImports(self):
        impS, impE = self.findImports()
        try:
            self.imports = string.split(self.data[impS:impE], ', ')
        except: raise 'Module import list not a comma delimited list'

    def writeModules(self, notify = true):
        modS, modE = self.findModules()
        self.data = self.data[:modS]+`self.modules`+self.data[modE:]

        self.modified = true
        self.editor.updateTitle()
        self.editor.updateModulePage(self)
        
        if notify: self.notify()

    def writeImports(self, notify = true):
        impS, impE = self.findImports()
        self.data = self.data[:impS]+string.join(self.imports, ', ')+ \
          self.data[impE:]
        if notify: self.notify()

    def viewAddModule(self):
        # XXX Don't really want to access editor
        fn = self.editor.openFileDlg()
        if fn:
            self.addModule(fn, '')
        
    def addModule(self, filename, descr):
        name, ext = path.splitext(path.basename(filename))
        if self.modules.has_key(name): raise 'Module exists in application'
        if self.savedAs:
            relative = relpath.relpath(path.dirname(self.filename), filename)
        else:
            relative = filename
        self.modules[name] = [0, descr, self.convertToUnixPath(relative)]

        self.idModel(name)

        self.writeModules()

    def removeModule(self, name):
        if not self.modules.has_key(name): raise 'No such module in application'
        
        del self.modules[name]
        self.writeModules()
    
    def editModule(self, oldname, newname, main, descr):
        if oldname != newname:
            del self.modules[oldname]
        self.modules[newname] = (main, descr)
        self.writeModules()

    def moduleFilename(self, name):
        if not self.modules.has_key(name): raise 'No such module in application: '+name
        if self.savedAs:
            if path.isabs(self.modules[name][2]):
                absPath = self.modules[name][2]
            else:
                absPath = path.normpath(path.join(path.dirname(self.filename), 
                  self.modules[name][2]))
        else:
            absPath = name + ModuleModel.ext
        return absPath

    def moduleSaveAsNotify(self, module, oldFilename, newFilename):
        if module != self:
            newName, ext = path.splitext(path.basename(newFilename))
            oldName = path.splitext(path.basename(oldFilename))[0]
 
            if not self.modules.has_key(oldName): raise 'Module does not exists in application'

            if self.savedAs:
                relative = relpath.relpath(path.dirname(self.filename), newFilename)
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
                module = self.getModule()
                if module.imports.has_key(oldName):
                    impLine = module.imports[oldName][0]-1
                    # read in the import line
                    line = module.source[impLine]
                    imports = string.split(line[7:], ', ')
                    impIdx = imports.index(oldName)
                    imports[impIdx] = newName
                    module.imports[newName] = module.imports[oldName]
                    del module.imports[oldName]
                    module.source[impLine] = 'import '+string.join(imports, ', ')
                    
                    # check if it's the main module, first in the import list is 
                    # always the main module
                    if not impIdx:
                        block = module.classes[boaClass].methods['OnInit']
                        mainDef = 'self.main = %s.'
                        fndOldStr = mainDef % oldName
                        repNewStr = mainDef % newName
                        
                        for idx in range(block.start, block.end):
                            line = module.source[idx]
                            newLine = string.replace(line, fndOldStr, repNewStr)
                            if newLine != line:
                                module.source[idx] = newLine

                    self.refreshFromModule()

            self.writeModules()
    
    def crashLog(self):
        err = ErrorStack.crashError(os.path.splitext(self.filename)[0]+'.trace')
        if err:
            import ErrorStackFrm
            esf = ErrorStackFrm.ErrorStackMF(self.editor, self.app, self.editor)
            esf.updateCtrls(err)
            esf.Show(true)
            return esf
        else:
            wx.wxLogError('Trace file not found. Run with command line param -T')
            return NOne
                
            

    def openModule(self, name):
        absPath = self.moduleFilename(name)
        
        module = self.editor.openOrGotoModule(absPath, self)
        
        return module
        
    def readPaths(self):
        pass

    def normaliseModuleRelativeToApp(self, relFilename):
        if not self.savedAs:
            return path.normpath(path.join(Preferences.pyPath, relFilename))
        else:
            return path.normpath(path.join(path.dirname(self.filename), relFilename))
        
    def buildImportRelationshipDict(self, modules = None):
        relationships = {}
        
        if modules is None:
            modules = self.modules.keys()
            
        tot = len(modules)
        self.editor.statusBar.progress.SetRange(tot)
        prog = 0
        totLOC = 0
        classCnt = 0
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
        self.addMenu(menu, Editor.wxID_SETUPBUILD, 'build', accls, ())
        self.addMenu(menu, Editor.wxID_SETUPCLEAN, 'clean', accls, ())
        self.addMenu(menu, Editor.wxID_SETUPINSTALL, 'install', accls, ())
        self.addMenu(menu, Editor.wxID_SETUPSDIST, 'sdist', accls, ())
        self.addMenu(menu, Editor.wxID_SETUPBDIST, 'bdist', accls, ())
        self.addMenu(menu, Editor.wxID_SETUPBDIST_WININST, 'bdist_wininst', accls, ())
        menu.AppendSeparator()
        self.addMenu(menu, Editor.wxID_SETUPPY2EXE, 'py2exe', accls, ())
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
modelReg = {AppModel.modelIdentifier: AppModel, 
            FrameModel.modelIdentifier: FrameModel,
            DialogModel.modelIdentifier: DialogModel,
            MiniFrameModel.modelIdentifier: MiniFrameModel,
            MDIParentModel.modelIdentifier: MDIParentModel,
            MDIChildModel.modelIdentifier: MDIChildModel,
            ModuleModel.modelIdentifier: ModuleModel,
            TextModel.modelIdentifier: TextModel,
            PackageModel.modelIdentifier: PackageModel,
            ConfigFileModel.modelIdentifier: ConfigFileModel,
            ZopeExportFileModel.modelIdentifier: ZopeExportFileModel,
            BitmapFileModel.modelIdentifier: BitmapFileModel,
            ZipFileModel.modelIdentifier: ZipFileModel,
            CPPModel.modelIdentifier: CPPModel,
            UnknownFileModel.modelIdentifier: UnknownFileModel,
            HTMLFileModel.modelIdentifier: HTMLFileModel,
            SetupModuleModel.modelIdentifier: SetupModuleModel}

# All non python files recogniseable by extension
extMap = {}
for mod in modelReg.values():
    extMap[mod.ext] = mod
del extMap['.py']
del extMap['.*']
extMap['.cpp'] = extMap['.c'] = extMap['.h'] = CPPModel
extMap['.jpg'] = extMap['.gif'] = extMap['.png'] = BitmapFileModel
extMap['.htm'] = extMap['.html']

internalFilesReg = ['.umllay', '.implay', '.brk', '.trace', '.stack']

def identifyHeader(headerStr):
    header = string.split(headerStr, ':')
    if len(header) and (header[0] == boaIdent) and modelReg.has_key(header[1]):
        return modelReg[header[1]], header[2]
    return ModuleModel, ''
    
def identifyFile(filename):
    """ Return appropriate model for given source file.
        Assumes header will be part of the first continious comment block """
    f = open(filename)
    try:
        dummy, name = path.split(filename)
        if name == '__init__.py':
            return PackageModel, ''
        if name == 'setup.py':
            return SetupModuleModel, ''
        dummy, ext = path.splitext(filename)
        if extMap.has_key(ext):
            return extMap[ext], ''
##        if ext == '.txt':
##            return TextModel, ''
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


