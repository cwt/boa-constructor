print 'executing wxPythonDemo plug-in'

import string, os, sys

from wxPython import wx
from wxPython.lib.anchors import LayoutAnchors

import Preferences, Utils, Plugins

from Explorers import ExplorerNodes, FileExplorer
from Models import EditorModels, EditorHelper, Controllers
from Views import EditorViews

# Register plug-in preference
Plugins.registerPreference('wxPythonDemo', 'wpWxPythonDemoFolder', "''", 
                           ['Path to the wxPython demo folder.', 
                            'If empty, wxPython/demo is used.'], 'type: dirpath')
Plugins.registerPreference('wxPythonDemo', 'wpShowWxPythonDemoTemplate', 'False', 
                           ['Should a template for an empty wxPython demo file', 
                            'be available on the Palette.'])


demoDir = os.path.join(os.path.dirname(wx.__file__), 'demo')
if not os.path.exists(demoDir):
    raise Plugins.SkipPlugin('wxPython demo directory not found.\n'
          'Please define the a path under Preferences->Plug-ins')

true = 1
false = 0

def importFromWxPyDemo(name):
    cwd = os.getcwd()
    sys.path.insert(0, demoDir)
    try:
        os.chdir(demoDir)
        try:
            return __import__(name, globals())
        finally:
            os.chdir(cwd)
            del sys.path[0]
    except Exception, err:
        print str(err)
        return None
        

def getWxPyDemoTree():
    Main = importFromWxPyDemo('Main')
    return Main._treeList


EditorHelper.imgWxPythonDemo = EditorHelper.addPluginImgs('Images\wxPythonDemo.png')


class SkipViewSignal(Exception):
    """ Raised when the demo is not docked """

class wxPythonDemoView(wxPanel, EditorViews.EditorView, EditorViews.CloseableViewMix):
    viewName = tabName = 'Demo'
    def __init__(self, parent, model):
        wxPanel.__init__(self, parent, -1)
        EditorViews.CloseableViewMix.__init__(self)
        EditorViews.EditorView.__init__(self, model, actions=self.closingActionItems)
        
        self.demoCtrl = None
        self.updateDemoCtrl()
        
        if self.demoCtrl is None:
            raise SkipViewSignal
        
    def updateDemoCtrl(self):
        demoModule = self.model.demoModule
        if demoModule:
            if self.demoCtrl:
                self.demoCtrl.Destroy()
    
            cwd = os.getcwd()
            os.chdir(demoDir)
            try:
                self.demoCtrl = demoModule.runTest(self.model.editor, self, self)
            finally:
                os.chdir(cwd)
                
            if self.demoCtrl:
                self.demoCtrl.SetSize(self.GetClientSize())
                self.SetAutoLayout(True)
                self.demoCtrl.SetConstraints(LayoutAnchors(self.demoCtrl, 
                                             True, True, True, True))
    
    def refreshCtrl(self):
        pass
    
    def WriteText(self, text):
        """ When View used as demo log """
        ef = self.model.editor.erroutFrm
        ef.appendToOutput(text)
        ef.display()

    def write(self, text):
        """ When View used as demo log """
        self.WriteText(text)

class wxPythonDemoOverView(EditorViews.HTMLView, EditorViews.CloseableViewMix):
    viewName = tabName = 'Overview'
    def __init__(self, parent, model):
        EditorViews.CloseableViewMix.__init__(self)
        EditorViews.HTMLView.__init__(self, parent, model, actions=self.closingActionItems)
        
        self.refreshCtrl()
    
    def generatePage(self):
        if self.model.demoModule:
            return self.model.demoModule.overview
        else:
            return 'No module imported'


class wxPythonDemoNode(FileExplorer.FileSysNode):
    def open(self, editor):
        model, cntrl = editor.openOrGotoModule(self.resourcepath)
 
        if not hasattr(model, 'demoModule'):
            name = os.path.splitext(os.path.basename(model.filename))[0]
            model.demoModule = importFromWxPyDemo(name)
       
        if model.demoModule and (model, cntrl) != (None, None): 
            for View, focus in ((wxPythonDemoOverView, False), 
                                (wxPythonDemoView, True)):
                if model.views.has_key(View.viewName):
                    view = model.views[View.viewName]
                    view.updateDemoCtrl()
                else:
                    modPge = editor.getActiveModulePage()
                    try:
                        view = modPge.addView(View)
                    except SkipViewSignal:
                        view = None
                        
                if focus and view:
                    view.focus()

        return model, cntrl
    
class wxPythonDemoSectionNode(ExplorerNodes.ExplorerNode):
    protocol = 'wxpydemo.section'
    def __init__(self, name, items, clipboard, bookmarks):
        ExplorerNodes.ExplorerNode.__init__(self, name, '', clipboard, 
              EditorHelper.imgFolder)
        self.bookmarks = bookmarks
        self.vetoSort = true
        self.items = items

    def isFolderish(self):
        return true

    def createChildNode(self, name):
        mod = importFromWxPyDemo(name)
        if mod is None:
            return None
        else:
            demoFile = os.path.splitext(mod.__file__)[0]+'.py'
            imgIdx = Controllers.identifyFile(demoFile)[0].imgIdx
            return wxPythonDemoNode(name, demoFile, self.clipboard, imgIdx, 
                                    self, self.bookmarks)

    def openList(self):
        return [n for n in [self.createChildNode(name) for name in self.items] if n]
    

class wxPythonDemoDirNode(ExplorerNodes.ExplorerNode):
    protocol = 'wxpydemo'
    def __init__(self, clipboard, parent, bookmarks):
        ExplorerNodes.ExplorerNode.__init__(self, 'wxPython demo', '', 
              clipboard, EditorHelper.imgWxPythonDemo)
        self.bookmarks = bookmarks
        self.bold = true
        self.vetoSort = true
        self.treeList = getWxPyDemoTree()

    def isFolderish(self):
        return true

    def createChildNode(self, section, items):
        return wxPythonDemoSectionNode(section, items, self.clipboard,
              self.bookmarks)

    def openList(self):
        return [self.createChildNode(name, items) 
                for name, items in self.treeList]


#-------------------------------------------------------------------------------
ExplorerNodes.register(wxPythonDemoDirNode, root=True)

#-------------------------------------------------------------------------------

import PaletteStore
from Models import PythonEditorModels, PythonControllers

class wxPythonDemoModuleModel(PythonEditorModels.ModuleModel):
    modelIdentifier = 'wxPythonDemoModule'
    defaultName = 'wxpythondemomodule'
    
    def getDefaultData(self):
        return '''from wxPython.wx import *
    
#-------------------------------------------------------------------------------

# Define your demo class here and save this module in the wxPython demo folder

#-------------------------------------------------------------------------------

def runTest(frame, nb, log):
    win = wxPanel(nb, -1) # Replace with your demo class 
    return win

#-------------------------------------------------------------------------------

overview = """<html><body>
<h2>Demo Name</h2>
<p>
</body></html>
"""
  
if __name__ == '__main__':
    import sys,os
    import run
    run.main(['', os.path.basename(sys.argv[0])])
'''

class wxPythonDemoModuleController(PythonControllers.ModuleController):
    Model = wxPythonDemoModuleModel

if Preferences.wpShowWxPythonDemoTemplate:
    Controllers.modelControllerReg[wxPythonDemoModuleModel] = wxPythonDemoModuleController
    PaletteStore.newControllers['wxPythonDemoModule'] = wxPythonDemoModuleController
    PaletteStore.paletteLists['New'].append('wxPythonDemoModule')
