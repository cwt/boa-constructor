#-----------------------------------------------------------------------------
# Name:        Controllers.py
# Purpose:     Controller classes for the MVC pattern
#
# Author:      Riaan Booysen
#
# Created:     2001/13/08
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2002 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Models.Controllers'

import os#, sys, time

from wxPython.wx import *

import Preferences, Utils
from Preferences import keyDefs

import EditorHelper, PaletteStore, EditorModels

import PythonEditorModels
if Preferences.suWxPythonSupport:
    import wxPythonEditorModels

from Views import EditorViews, SourceViews, OGLViews

from Explorers import ExplorerNodes

addTool = Utils.AddToolButtonBmpIS

true=1;false=0

from sourceconst import *

# XXX Controller should handle transport attachment

class BaseEditorController:
    """ Between user and model operations

    Provides interface to add new and open existing models
    Manages toolbar and menu actions
    Custom classes should define Model operations as events
    """
    docked = true

    Model           = None
    DefaultViews    = []
    AdditionalViews = []
    def __init__(self, editor):
        self.editor = editor
        self.evts = []

    def getModel(self):
        return self.editor.getActiveModulePage().model

    def createModel(self, source, filename, name, editor, saved, modelParent=None):
        pass

    def createNewModel(self, modelParent=None):
        pass

    def afterAddModulePage(self, model):
        pass

    def newFileTransport(self, name, filename):
        from Explorers.FileExplorer import PyFileNode
        return PyFileNode(name, filename, None, -1, None, None, properties = {})

    def addEvt(self, wId, meth):
        EVT_MENU(self.editor, wId, meth)
        self.evts.append(wId)

    def disconnectEvts(self):
        for wId in self.evts:
            self.editor.Disconnect(wId)
        self.evts = []

    def addMenu(self, menu, wId, label, accls, code = ()):
        menu.Append(wId, label + (code and '\t'+code[2] or ''))
        if code:
            accls.append((code[0], code[1], wId),)

#-------------------------------------------------------------------------------
    def addEvts(self):
        """ Override and connect events with addEvt """

    def addMenus(self, menu, model):
        """ Override and define File->Menus with addMenu """
        return []

    def addTools(self, toolbar, model):
        """ Override and define ToolBar buttons with function addTool """
        pass


class EditorController(BaseEditorController):
    closeBmp = 'Images/Editor/Close.png'

    def addEvts(self):
        self.addEvt(EditorHelper.wxID_EDITORCLOSEPAGE, self.OnClose)

    def addTools(self, toolbar, model):
        addTool(self.editor, toolbar, self.closeBmp, 'Close', self.OnClose)

    def addMenus(self, menu, model):
        accls = []
        self.addMenu(menu, EditorHelper.wxID_EDITORCLOSEPAGE, 'Close', accls, (keyDefs['Close']))
        return accls

    def OnClose(self, event):
        self.editor.closeModulePage(self.editor.getActiveModulePage())

class PersistentController(EditorController):
    saveBmp = 'Images/Editor/Save.png'
    saveAsBmp = 'Images/Editor/SaveAs.png'

    def addEvts(self):
        EditorController.addEvts(self)
        self.addEvt(EditorHelper.wxID_EDITORSAVE, self.OnSave)
        self.addEvt(EditorHelper.wxID_EDITORSAVEAS, self.OnSaveAs)
        self.addEvt(EditorHelper.wxID_EDITORRELOAD, self.OnReload)
        self.addEvt(EditorHelper.wxID_EDITORTOGGLERO, self.OnToggleReadOnly)

    def addTools(self, toolbar, model):
        EditorController.addTools(self, toolbar, model)
        addTool(self.editor, toolbar, self.saveBmp, 'Save', self.OnSave)
        addTool(self.editor, toolbar, self.saveAsBmp, 'Save as...', self.OnSaveAs)

    def addMenus(self, menu, model):
        accls = EditorController.addMenus(self, menu, model)
        self.addMenu(menu, EditorHelper.wxID_EDITORRELOAD, 'Reload', accls, ())
        self.addMenu(menu, EditorHelper.wxID_EDITORSAVE, 'Save', accls, (keyDefs['Save']))
        self.addMenu(menu, EditorHelper.wxID_EDITORSAVEAS, 'Save as...', accls, (keyDefs['SaveAs']))
        menu.Append(-1, '-')
        self.addMenu(menu, EditorHelper.wxID_EDITORTOGGLERO, 'Toggle read-only', accls, ())
        return accls

    def createModel(self, source, filename, main, saved, modelParent=None):
        return self.Model(source, filename, self.editor, saved)

    def createNewModel(self, modelParent=None):
        name = self.editor.getValidName(self.Model)
        model = self.createModel('', name, '', false)
        model.transport = self.newFileTransport('', name)
        model.new()

        return model, name

    def checkUnsaved(self, model, checkModified=false):
        if not model.savedAs or checkModified and (model.modified or \
              len(model.viewsModified)):
            wxLogError('Cannot perform this action on an unsaved%s module'%(
                  checkModified and '/modified' or '') )
            return true
        else:
            return false

    def OnSave(self, event):
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
            if model.hasUnsavedChanges() and \
                  wxMessageBox('There are unsaved changes.\n'\
                  'Are you sure you want to reload?',
                  'Confirm reload', wxYES_NO | wxICON_WARNING) != wxYES:
                return
            try:
                model.load()

                self.editor.updateModuleState(model)
            except ExplorerNodes.TransportLoadError, error:
                wxLogError(str(error))

    def OnToggleReadOnly(self, event):
        model = self.getModel()
        if model and model.transport and model.transport.stdAttrs.has_key('read-only'):
            model.transport.updateStdAttrs()
            ro = model.transport.stdAttrs['read-only']
            model.transport.setStdAttr('read-only', not ro)

            model.views['Source'].updateFromAttrs()

            self.editor.updateModuleState(model)
        else:
            wxLogError('Read-only not supported on this transport')

class SourceController(PersistentController):
    AdditionalViews = [EditorViews.CVSConflictsView]
    def addEvts(self):
        PersistentController.addEvts(self)
        self.addEvt(EditorHelper.wxID_EDITORDIFF, self.OnDiffFile)
        self.addEvt(EditorHelper.wxID_EDITORPATCH, self.OnPatchFile)

    def addMenus(self, menu, model):
        accls = PersistentController.addMenus(self, menu, model)
        #self.addMenu(menu, EditorHelper.wxID_EDITORDIFF, 'Create file diff', accls, ())
        #self.addMenu(menu, EditorHelper.wxID_EDITORPATCH, 'Patch file', accls, ())
        return accls

    def OnDiffFile(self, event, diffWithFilename=''):
        model = self.getModel()
        if model:
            if self.checkUnsaved(model): return
            if not diffWithFilename:
                diffWithFilename = self.editor.openFileDlg()
            filename = model.assertLocalFile(filename)

    def OnPatchFile(self, event, patchFilename=''):
        model = self.getModel()
        if model:
            if self.checkUnsaved(model): return
            if not patchFilename:
                patchFilename = self.editor.openFileDlg()
            filename = model.assertLocalFile(filename)

class TextController(PersistentController):
    Model           = EditorModels.TextModel
    DefaultViews    = [SourceViews.TextView]
    AdditionalViews = []

class UndockedController(BaseEditorController):
    docked          = false
    def createModel(self, source, filename, main, saved, modelParent=None):
        return self.Model(source, filename, self.editor, saved)

    def display(self, model):
        """ Override to display undocked interface """

class BitmapFileController(UndockedController):
    Model           = EditorModels.BitmapFileModel
    DefaultViews    = []
    AdditionalViews = []
    
    def display(self, model):
        from ZopeLib import ImageViewer
        ImageViewer.create(self.editor).showImage(model.filename, model.transport)

class MakePyController(BaseEditorController):
    docked          = false
    Model           = None
    DefaultViews    = []
    AdditionalViews = []

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

#-------------------------------------------------------------------------------

def identifyHeader(headerStr):
    header = string.split(headerStr, ':')
    if len(header) and (header[0] == boaIdent) and EditorHelper.modelReg.has_key(header[1]):
        return EditorHelper.modelReg[header[1]], header[2]
    return PythonEditorModels.ModuleModel, ''

def identifyFilename(filename):
    dummy, name = os.path.split(filename)
    base, ext = os.path.splitext(filename)
    lext = string.lower(ext)

    if name == '__init__.py':
        return PythonEditorModels.PackageModel, '', lext
    if name == 'setup.py':
        return PythonEditorModels.SetupModuleModel, '', lext
    if not ext and string.upper(base) == base:
        return EditorModels.TextModel, '', lext
    if EditorHelper.extMap.has_key(lext):
        return EditorHelper.extMap[lext], '', lext
    if lext in EditorHelper.internalFilesReg:
        return EditorModels.InternalFileModel, '', lext
    if lext in EditorHelper.pythonBinaryFilesReg:
        return PythonEditorModels.PythonBinaryFileModel, '', lext
    return None, '', lext

def identifyFile(filename, source=None, localfs=true):
    """ Return appropriate model for given source file.
        Assumes header will be part of the first continious comment block """
    Model, main, lext = identifyFilename(filename)
    if Model is not None:
        return Model, main

    if lext == '.py':
        BaseModel = PythonEditorModels.ModuleModel
    else:
        BaseModel = EditorModels.UnknownFileModel

    if source is None and not localfs:
        return BaseModel, ''
    elif lext in EditorHelper.inspectableFilesReg:
        if source is not None:
            return identifySource(string.split(source, '\n'))
        elif not Preferences.exInspectInspectableFiles:
            return BaseModel, ''
        f = open(filename)
        try:
            while 1:
                line = f.readline()
                if not line: break
                line = string.strip(line)
                if line:
                    if line[0] != '#':
                        return BaseModel, ''
                    headerInfo = identifyHeader(line)
                    if headerInfo[0] != PythonEditorModels.ModuleModel:
                        return headerInfo
            return BaseModel, ''
        finally:
            f.close()
    else:
        return BaseModel, ''


def identifySource(source):
    """ Return appropriate model for given Python source.
        The logic is a copy paste from above func """
    for line in source:
        if line:
            if line[0] != '#':
                return PythonEditorModels.ModuleModel, ''

            headerInfo = identifyHeader(string.strip(line))

            if headerInfo[0] != PythonEditorModels.ModuleModel:
                return headerInfo
        else:
            return PythonEditorModels.ModuleModel, ''

#-Registration of this modules classes---------------------------------------
modelControllerReg = {EditorModels.TextModel: TextController,
                      EditorModels.BitmapFileModel: BitmapFileController}

