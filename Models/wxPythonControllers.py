#-----------------------------------------------------------------------------
# Name:        wxPythonControllers.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2002/02/09
# RCS-ID:      $Id$
# Copyright:   (c) 2002
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Models.wxPythonControllers'

import os, string

from wxPython.wx import *

import Preferences, Utils
from Preferences import keyDefs
import PaletteStore

import Controllers
from Controllers import addTool
from PythonControllers import BaseAppController, ModuleController
import EditorHelper, wxPythonEditorModels
from Views import EditorViews, AppViews, DataView, Designer

true,false=1,0

class AppController(BaseAppController):
    Model = wxPythonEditorModels.AppModel

    def afterAddModulePage(self, model):
        frmMod = self.editor.addNewPage('Frame', FrameController, model)

        frmNme = os.path.splitext(os.path.basename(frmMod.filename))[0]
        model.new(frmNme)


class BaseFrameController(ModuleController):
    designerBmp = 'Images/Shared/Designer.png'

    DefaultViews = ModuleController.DefaultViews + [EditorViews.ExploreEventsView]

    def addEvts(self):
        ModuleController.addEvts(self)
        self.addEvt(EditorHelper.wxID_EDITORDESIGNER, self.OnDesigner)

    def addTools(self, toolbar, model):
        ModuleController.addTools(self, toolbar, model)
        toolbar.AddSeparator()
        addTool(self.editor, toolbar, self.designerBmp, 'Frame Designer',
                self.OnDesigner)

    def addMenus(self, menu, model):
        accls = ModuleController.addMenus(self, menu, model)
        self.addMenu(menu, EditorHelper.wxID_EDITORDESIGNER, 'Frame Designer',
              accls, (keyDefs['Designer']))
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
        # Special case for PopupWindow, has no id or title
        if params.has_key('title'):
            params['id'] = Utils.windowIdentifier(model.main, '')
            params['title'] = `model.main`

        model.new(params)

        if self.activeApp and self.activeApp.data and Preferences.autoAddToApplication:
            self.activeApp.addModule(model.filename, '')

    def OnDesigner(self, event):
        import time
        t = time.time()
        self.showDesigner()

    def showDesigner(self):
        # Just show if already opened
        modulePage = self.editor.getActiveModulePage()
        model = modulePage.model
        if model.views.has_key('Designer'):
            model.views['Data'].focus()
            model.views['Designer'].restore()
            return

        dataView = None
        try:
            cwd = os.getcwd()
            mwd = Utils.getModelBaseDir(model)
            if mwd and Utils.startswith(mwd, 'file://'): os.chdir(mwd[7:])

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
                              self.editor.inspector, model,
                              self.editor.compPalette, model.companion, dataView)
                        model.views['Designer'] = designer
                        designer.refreshCtrl()
                    model.views['Designer'].Show()
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

                self.editor.setStatus('Designer session started.')

            finally:
                os.chdir(cwd)

        except Exception, error:
            self.editor.setStatus(\
                'An error occured while opening the Designer: %s'%str(error),
                'Error')
            self.editor.statusBar.progress.SetValue(0)
            raise

class FrameController(BaseFrameController):
    Model = wxPythonEditorModels.FrameModel

class DialogController(BaseFrameController):
    Model = wxPythonEditorModels.DialogModel

class MiniFrameController(BaseFrameController):
    Model = wxPythonEditorModels.MiniFrameModel

class MDIParentController(BaseFrameController):
    Model = wxPythonEditorModels.MDIParentModel

class MDIChildController(BaseFrameController):
    Model = wxPythonEditorModels.MDIChildModel

class PopupWindowController(BaseFrameController):
    Model = wxPythonEditorModels.PopupWindowModel

class PopupTransientWindowController(BaseFrameController):
    Model = wxPythonEditorModels.PopupTransientWindowModel

#-------------------------------------------------------------------------------

Preferences.paletteTitle = Preferences.paletteTitle +' - wxPython GUI Builder'

Controllers.modelControllerReg.update({
      wxPythonEditorModels.AppModel: AppController,
      wxPythonEditorModels.FrameModel: FrameController,
      wxPythonEditorModels.DialogModel: DialogController,
      wxPythonEditorModels.MiniFrameModel: MiniFrameController,
      wxPythonEditorModels.MDIParentModel: MDIParentController,
      wxPythonEditorModels.MDIChildModel: MDIChildController,
      wxPythonEditorModels.PopupWindowModel: PopupWindowController,
      wxPythonEditorModels.PopupTransientWindowModel: PopupTransientWindowController,
     })

PaletteStore.newControllers.update({
      'wxApp': AppController,
      'wxFrame': FrameController,
      'wxDialog': DialogController,
      'wxMiniFrame': MiniFrameController,
      'wxMDIParentFrame': MDIParentController,
      'wxMDIChildFrame': MDIChildController,
      'wxPopupWindow': PopupWindowController,
      'wxPopupTransientWindow': PopupTransientWindowController,
     })


# Register controllers on the New palette
PaletteStore.paletteLists['New'].extend(['wxApp', 'wxFrame', 'wxDialog',
  'wxMiniFrame', 'wxMDIParentFrame', 'wxMDIChildFrame',
  'wxPopupWindow', 'wxPopupTransientWindow'])
