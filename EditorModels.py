#----------------------------------------------------------------------
# Name:        EditorModels.py
# Purpose:     
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

""" The model classes represent different types of source code files """

# XXX form inheritance
# XXX Dynamically adding buttons to taskbar depending on the model and view

import moduleparse, string, os, sys, re
from os import path
import relpath
import Companions, Editor, Debugger
import Preferences, Utils
from wxPython.wx import wxBitmap, wxBITMAP_TYPE_BMP
from Utils import AddToolButtonBmpObject
from time import time, gmtime, strftime

true = 1
false = 0

nl = chr(13)+chr(10)
init_ctrls = '_init_ctrls'
init_utils = '_init_utils'
init_props = '_init_props'
init_events = '_init_events'
defEnvPython = '#!/bin/env python\n'
defImport = 'from wxPython.wx import *\n\n'
defSig= '#Boa:%s:%s\n\n'

defCreateClass = '''def create(parent):
    return %s(parent)
\n'''
wid = '[A-Za-z0-9_, ]*'
srchWindowIds = '\[(?P<winids>[A-Za-z0-9_, ]*)\] = '+\
'map\(lambda %s: NewId\(\), range\((?P<count>\d)\)\)'
defWindowIds = '''[%s] = map(lambda %s: NewId(), range(%d))\n'''
defClass = '''
class %s(%s):
    def '''+init_utils+'''(self): 
        pass

    def '''+init_ctrls+'''(self, prnt): 
        %s.__init__(%s)
        
    def __init__(self, parent): 
        self.'''+init_utils+'''()
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

defApp = """import %s

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
    main()"""

defInfoBlock = """#----------------------------------------------------------------------
# Name:        %s
# Purpose:     %s
#
# Author:      %s
#
# Created:     %s
# RCS-ID:      %s
# Copyright:   %s
# Licence:     %s
#----------------------------------------------------------------------
"""        


class EditorModel:
    defaultName = 'abstract'
    bitmap = 'None'
    imgIdx = -1
    closeBmp = wxBitmap('Images/Editor/Close.bmp', wxBITMAP_TYPE_BMP)
    def __init__(self, name, data, editor, saved):
        self.data = data
        self.savedAs = saved
        self.filename = name
        self.editor = editor
        
        self.views = {}
        self.modified = not saved
        self.viewsModified = []

    def addTools(self, toolbar):
        AddToolButtonBmpObject(self.editor, toolbar, self.closeBmp, 'Close', self.editor.OnClose)

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
            f = open(self.filename, 'w')
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

class FolderModel(EditorModel):
    modelIdentifier = 'Folder'
    defaultName = 'folder'
    bitmap = 'Folder_s.bmp'
    imgIdx = 9

class PackageModel(EditorModel):
    """ Must be constructed in a valid path, name being filename, actual
        name will be derived from path """
    modelIdentifier = 'Package'
    defaultName = 'package'
    bitmap = 'Package_s.bmp'
    imgIdx = 7
    pckgIdnt = '__init__.py'
    ext = '.py'

    saveBmp = wxBitmap('Images/Editor/Save.bmp', wxBITMAP_TYPE_BMP)
    saveAsBmp = wxBitmap('Images/Editor/SaveAs.bmp', wxBITMAP_TYPE_BMP)

    def __init__(self, data, name, editor, saved):
        EditorModel.__init__(self, name, data, editor, saved)
        self.packagePath, dummy = path.split(self.filename)
        dummy, self.packageName = path.split(self.packagePath)
        self.savedAs = true
        self.modified = false
    
    def addTools(self, toolbar):
        EditorModel.addTools(self, toolbar)
        AddToolButtonBmpObject(self.editor, toolbar, self.saveBmp, 'Save', self.editor.OnSave)
        AddToolButtonBmpObject(self.editor, toolbar, self.saveAsBmp, 'Save as...', self.editor.OnSaveAs)

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
                
class ModuleModel(EditorModel):

    modelIdentifier = 'Module'
    defaultName = 'module'
    bitmap = 'Module_s.bmp'
    imgIdx = 6
    ext = '.py'

    saveBmp = wxBitmap('Images/Editor/Save.bmp', wxBITMAP_TYPE_BMP)
    saveAsBmp = wxBitmap('Images/Editor/SaveAs.bmp', wxBITMAP_TYPE_BMP)

    def __init__(self, data, name, editor, saved):
        EditorModel.__init__(self, name, data, editor, saved)
        self.moduleName = path.split(self.filename)[1]
        self.app = None
        self.debugger = None
        if data: self.update()

    def addTools(self, toolbar):
        EditorModel.addTools(self, toolbar)
        AddToolButtonBmpObject(self.editor, toolbar, self.saveBmp, 'Save', self.editor.OnSave)
        AddToolButtonBmpObject(self.editor, toolbar, self.saveAsBmp, 'Save as...', self.editor.OnSaveAs)
        
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
        
    def initModule(self):
        self.module = moduleparse.Module(self.moduleName, string.split(self.data, '\012'))
        
    def refreshFromModule(self):
        """ Must call this method to apply changes were made to module object. """
        self.data = string.join(self.module.source, '\012')#os.linesep)
        self.notify()
    
    def renameClass(self, oldname, newname):
        pass
    
    def update(self):
        EditorModel.update(self)
        self.initModule()
    
    def run(self):
        """ Excecute the current saved image of the application. """
        if self.savedAs:
            cwd = path.abspath(os.getcwd())
            os.chdir(path.dirname(self.filename))
            try:
                cmd = '"%s" %s'%(sys.executable, path.basename(self.filename))
                print 'executing', cmd
                os.system(cmd)
            finally:
                os.chdir(cwd)

    def runAsScript(self):
        execfile(self.filename)

    def debug(self):
        if self.savedAs:
            if self.editor.debugger:
                self.editor.debugger.Show(true)
            else:
                self.editor.debugger = Debugger.DebuggerFrame(self)
                self.editor.debugger.Show(true)  
                self.editor.debugger.debug_file(self.editor.debugger.filename)

    def addModuleInfo(self, prefs):
        # XXX Check that module doesn't already have an info block

        prefs['Name'] = self.moduleName
        prefs['Created'] = strftime('%Y/%d/%m', gmtime(time()))
        prefs['RCS-ID'] = '$Id$' % self.moduleName 

        self.data = defInfoBlock % (prefs['Name'], prefs['Purpose'], prefs['Author'],
          prefs['Created'], prefs['RCS-ID'], prefs['Copyright'], prefs['Licence']) + self.data
        self.modified = true
        self.update()
        self.notify()

    def saveAs(self, filename):
        EditorModel.saveAs(self, filename)
        self.moduleName = path.basename(filename)
        self.notify()

class TextModel(EditorModel):

    modelIdentifier = 'Text'
    defaultName = 'text'
    bitmap = 'Text_s.bmp'
    imgIdx = 8
    ext = '.txt'

    saveBmp = wxBitmap('Images/Editor/Save.bmp', wxBITMAP_TYPE_BMP)
    saveAsBmp = wxBitmap('Images/Editor/SaveAs.bmp', wxBITMAP_TYPE_BMP)

    def __init__(self, data, name, editor, saved):
        EditorModel.__init__(self, name, data, editor, saved)
        if data: self.update()
        
    def addTools(self, toolbar):
        EditorModel.addTools(self, toolbar)
        AddToolButtonBmpObject(self.editor, toolbar, self.saveBmp, 'Save', self.editor.OnSave)
        AddToolButtonBmpObject(self.editor, toolbar, self.saveAsBmp, 'Save as...', self.editor.OnSaveAs)

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
                

class ClassModel(ModuleModel):
    """ Represents access to 1 maintained main class in the module.
        This class is identified by the 3rd header entry  """
    def __init__(self, data, name, main, editor, saved):
        self.main = main
        self.mainConstr = None
        ModuleModel.__init__(self, data, name, editor, saved)
    
    def renameMain(self, oldName, newName):
        self.module.renameClass(oldName, newName)
        self.main = newName

        header = string.split(string.strip(self.module.source[0]), ':')
        if (len(header) == 3) and (header[0] == '#Boa'):
            self.module.source[0] = string.join((header[0], header[1], newName), ':')

class ObjectCollection:
    def __init__(self, creators = [], properties = [], events = []):
        self.creators = creators
        self.properties = properties
        self.events = events

class BaseFrameModel(ClassModel):
    companion = Companions.DesignTimeCompanion
    designerBmp = wxBitmap('Images/Shared/Designer.bmp', wxBITMAP_TYPE_BMP)
    objectCollectionMethods = [init_ctrls, init_utils]
    def __init__(self, data, name, main, editor, saved):
        ClassModel.__init__(self, data, name, main, editor, saved)
        self.designerTool = None
        if data:
            self.update()

    def addTools(self, toolbar):
        ClassModel.addTools(self, toolbar)
        toolbar.AddSeparator()
        AddToolButtonBmpObject(self.editor, toolbar, self.designerBmp, 'Frame Designer', self.editor.OnDesigner)

    def renameMain(self, oldName, newName):
        ClassModel.renameMain(self, oldName, newName)
        self.module.replaceFunctionBody('create', ['    return %s(parent)'%newName, ''])

    def renameCtrl(self, oldName, newName):
        # Currently DesignerView maintains ctrls
        pass
        
    def saveAs(self, filename):
        oldFilename = self.filename  
        ClassModel.saveAs(self, filename)
        if self.app:
            self.app.modulePathChange(oldFilename, filename)       
    
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
        self.readComponents()
        self.notify()

    def readComponents(self):
        from methodparse import *
        self.objectCollections = {}
        if self.module.classes.has_key(self.main):
            main = self.module.classes[self.main]
            for oc in self.objectCollectionMethods: 
                codeSpan = main.methods[oc]
                codeBody = self.module.source[codeSpan.start : codeSpan.end]
            
                allInitialisers = parseMixedBody([ConstructorParse, EventParse, PropertyParse], codeBody)
                if allInitialisers.has_key(ConstructorParse):
                    creators = allInitialisers[ConstructorParse]
                    if len(creators) and oc == init_ctrls:
                        self.mainConstr = creators[0]
                else:
                    creators = []
                if allInitialisers.has_key(PropertyParse):
                    properties = allInitialisers[PropertyParse]
                else:
                    properties = []
                if allInitialisers.has_key(EventParse):
                    events = allInitialisers[EventParse]
                else:
                    events = []

                self.objectCollections[oc] = ObjectCollection(creators, properties, events)

    def writeWindowIds(self, colMeth, ctrls, order):
        # To integrate efficiently with Designer.SaveCtrls this method
        # modifies module.source but doesn't refresh anything
        
        # find windowids in source
        winIdIdx = -1
        reWinIds = re.compile(srchWindowIds % colMeth)
        for idx in range(len(self.module.source)):
            match = reWinIds.match(self.module.source[idx])
            if match:
                winIdIdx = idx
                break
        # build window id list
        lst = []
        for ctrlName in order:
            comp = ctrls[ctrlName][0]
            if winIdIdx == -1:
                comp.updateWindowIds()
            lst.append(comp.id)
	
	if winIdIdx == -1:
           # No window id definitions could be found add one above class def
	    insPt = self.module.classes[self.main].block.start - 1
	    self.module.source[insPt : insPt] = \
	      [string.strip(defWindowIds % (string.join(lst, ', '), colMeth, len(lst))), '']
	    self.module.renumber(2, insPt)
	else:
	    # Update window ids
	    self.module.source[idx] = \
	      string.strip(defWindowIds % (string.join(lst, ', '), colMeth, len(lst)))
	    
    def update(self):
        ClassModel.update(self)
        self.readComponents()
            
class FrameModel(BaseFrameModel):
    modelIdentifier = 'Frame'
    defaultName = 'wxFrame'
    bitmap = 'wxFrame_s.bmp'
    imgIdx = 1
    companion = Companions.FrameDTC

class DialogModel(BaseFrameModel):
    modelIdentifier = 'Dialog'
    defaultName = 'wxDialog'
    bitmap = 'wxDialog_s.bmp'
    imgIdx = 2
    companion = Companions.DialogDTC

class MiniFrameModel(BaseFrameModel):
    modelIdentifier = 'MiniFrame'
    defaultName = 'wxMiniFrame'
    bitmap = 'wxMiniFrame_s.bmp'
    imgIdx = 3
    companion = Companions.MiniFrameDTC

class MDIParentModel(BaseFrameModel):
    modelIdentifier = 'MDIParent'
    defaultName = 'wxMDIParentFrame'
    bitmap = 'wxMDIParentFrame_s.bmp'
    imgIdx = 4
    companion = Companions.MDIParentFrameDTC

class MDIChildModel(BaseFrameModel):
    modelIdentifier = 'MDIChild'
    defaultName = 'wxMDIChildFrame'
    bitmap = 'wxMDIChildFrame_s.bmp'
    imgIdx = 5
    companion = Companions.MDIChildFrameDTC
    
# XXX Autocreated frames w/ corresponding imports
# XXX Paths
# XXX module references to app mut be cleared on closure

class AppModel(ClassModel):
    modelIdentifier = 'App'
    defaultName = 'wxApp'
    bitmap = 'wxApp_s.bmp'
    imgIdx = 0
    def __init__(self, data, name, main, editor, saved):
        self.moduleModels = {}
        ClassModel.__init__(self, data, name, main, editor, saved)
        if data:
            self.update()
            self.notify()

    def saveAs(self, filename):
        for mod in self.modules.keys():
            if not self.savedAs:
                self.modules[mod][2] = path.normpath(path.join(Preferences.pyPath, 
                  self.modules[mod][2]))
            else:
                self.modules[mod][2] = path.normpath(path.join(path.dirname(self.filename), 
                  self.modules[mod][2]))

        for mod in self.modules.keys():
            self.modules[mod][2] = relpath.relpath(path.dirname(filename), self.modules[mod][2])

        self.writeModules()    
        
        ClassModel.saveAs(self, filename)
        
        self.notify()
    
    def modulePathChange(self, oldFilename, newFilename):
        key = path.splitext(path.basename(oldFilename))[0]
        self.modules[key][2] = relpath.relpath(path.dirname(self.filename), newFilename)

        self.writeModules()    

    def renameMain(self, oldName, newName):
        ClassModel.renameMain(self, oldName, newName)
        self.module.replaceFunctionBody('main', 
          ['    application = %s(0)'%newName, '    application.MainLoop()', ''])

    def new(self, mainModule):
        self.data = (defSig + defEnvPython + defImport + defApp) \
          %(self.modelIdentifier, 'BoaApp', mainModule, mainModule,
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
        try:
            absPath = path.join(path.dirname(self.filename), self.modules[name][2])
        except:
            print 'invalid path', self.modules[name]
        else:
            try:
                self.moduleModels[name], main = identifyFile(absPath)
            except IOError:
                if self.editor.modules.has_key(absPath):
                    self.moduleModels[name], main = identifySource( \
                      self.editor.modules[absPath].model.module.source)
                elif self.editor.modules.has_key(absPath[:-3]):
                    self.moduleModels[name], main = identifySource( \
                      self.editor.modules[absPath[:-3]].model.module.source)
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
        self.modules[name] = [0, descr, relative]

        self.idModel(name)

##        try: 
##          self.moduleModels[name] = identifyFile(filename)[0]
##        except IOError:
##            self.idModel(name)

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

    def openModule(self, name):
        if not self.modules.has_key(name): raise 'No such module in application: '+name
        if self.savedAs:
            if path.isabs(self.modules[name][2]):
                absPath = self.modules[name][2]
            else:
                absPath = path.join(path.dirname(self.filename), self.modules[name][2])
        else:
            absPath = name + ModuleModel.ext
        
        newMod = self.editor.openOrGotoModule(absPath)
        newMod.app = self
        
        return newMod
        
    def readPaths(self):
        pass
        
    def buildImportRelationshipDict(self):
        relationships = {}
        
        modules = self.modules.keys()
        tot = len(modules)
        self.editor.statusBar.progress.SetRange(tot)
        prog = 0
        for moduleName in modules:
            self.editor.statusBar.progress.SetValue(prog)
            prog = prog + 1
            self.editor.statusBar.hint.SetLabel('Parsing '+moduleName+'...')
            module = self.modules[moduleName]
            try: f = open(module[2])
            except: continue
            else:
                data = f.read()
                f.close()
                model = ModuleModel(data, module[2], self.editor, 1)
                relationships[moduleName] = model.module#.imports
        self.editor.statusBar.progress.SetValue(0)
        self.editor.statusBar.hint.SetLabel('')
        return relationships
    
    def showImportsView(self):
        self.editor.showImportsView()
                    
    def update(self):
        ClassModel.update(self)
        self.readModules()
        self.readPaths()
                
        

# model registry: add to this dict to register a Model
modelReg = {AppModel.modelIdentifier: AppModel, 
            FrameModel.modelIdentifier: FrameModel,
            DialogModel.modelIdentifier: DialogModel,
            MiniFrameModel.modelIdentifier: MiniFrameModel,
            MDIParentModel.modelIdentifier: MDIParentModel,
            MDIChildModel.modelIdentifier: MDIChildModel,
            ModuleModel.modelIdentifier: ModuleModel,
            TextModel.modelIdentifier: TextModel,
            PackageModel.modelIdentifier: PackageModel}

def identifyHeader(headerStr):
    header = string.split(headerStr, ':')
    if len(header) and (header[0] == '#Boa') and modelReg.has_key(header[1]):
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
        dummy, ext = path.splitext(filename)
        if ext == '.txt':
            return TextModel, ''
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
        The logic is a copy paste from above func I have not generalised yet """
    for line in source:
        if line:
            if line[0] != '#':
                return ModuleModel, ''
            
            headerInfo = identifyHeader(string.strip(line))
            
            if headerInfo[0] != ModuleModel:
                return headerInfo
        else:
            return ModuleModel, ''
