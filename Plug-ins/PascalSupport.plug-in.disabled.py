#-----------------------------------------------------------------------------
# Name:        PascalSupport.py
# Purpose:     Example plugin module showing how to add new filetypes to the ide
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002
# Licence:     GPL
#-----------------------------------------------------------------------------

import os

from wxPython.wx import *
from wxPython.stc import *

import Preferences, Utils
import PaletteStore

from Models import Controllers, EditorHelper, EditorModels
from Views import SourceViews, StyledTextCtrls
from Explorers import ExplorerNodes

# Allocate an image index for Pascal files
EditorHelper.imgPascalModel = EditorHelper.imgCounter
EditorHelper.imgCounter = EditorHelper.imgPascalModel + 1

class PascalModel(EditorModels.SourceModel):
    modelIdentifier = 'Pascal'
    defaultName = 'pascal'  # default name given to newly created files
    bitmap = 'Pascal_s.png' # this image must exist in Images/Modules
    ext = '.pas'
    imgIdx = EditorHelper.imgPascalModel

# get the slyle definitions file in either the prefs directory or the Boa root
cfgfile = Preferences.rcPath +'/Plug-ins/stc-pascal.rc.cfg'
if not os.path.exists(cfgfile):
    cfgfile = Preferences.pyPath +'/Plug-ins/stc-pascal.rc.cfg'

class PascalStyledTextCtrlMix(StyledTextCtrls.LanguageSTCMix):
    def __init__(self, wId):
        StyledTextCtrls.LanguageSTCMix.__init__(self, wId,
              (0, Preferences.STCLineNumMarginWidth), 'pascal', cfgfile)
        self.setStyles()

wxID_PASSOURCEVIEW = wxNewId()
class PascalSourceView(SourceViews.EditorStyledTextCtrl, PascalStyledTextCtrlMix):
    viewName = 'Source'
    def __init__(self, parent, model):
        SourceViews.EditorStyledTextCtrl.__init__(self, parent, wxID_PASSOURCEVIEW,
          model, (), -1)
        PascalStyledTextCtrlMix.__init__(self, wxID_PASSOURCEVIEW)
        self.active = true

# Register a Pascal STC style editor under Preferences
ExplorerNodes.langStyleInfoReg.append( ('Pascal', 'pascal',
      PascalStyledTextCtrlMix, cfgfile) )

# The compile action is just added as an example of how to add an action to
# a controller and is not implemented
wxID_PASCALCOMPILE = wxNewId()
class PascalController(Controllers.SourceController):
    compileBmp = 'Images/Debug/Compile.png'

    Model = PascalModel
    DefaultViews = [PascalSourceView]

    def addEvts(self):
        Controllers.SourceController.addEvts(self)
        self.addEvt(wxID_PASCALCOMPILE, self.OnCompile)

    def addTools(self, toolbar, model):
        Controllers.SourceController.addTools(self, toolbar, model)
        toolbar.AddSeparator()
        Controllers.addTool(self.editor, toolbar, self.compileBmp,
              'Compile', self.OnCompile)

    def addMenus(self, menu, model):
        accls = Controllers.SourceController.addMenus(self, menu, model)
        self.addMenu(menu, wxID_PASCALCOMPILE, 'Compile', accls,
            (Preferences.keyDefs['CheckSource']))
        return accls

    def OnCompile(self, event):
        wxLogWarning('Not implemented')

# Register Model for opening in the Editor
EditorHelper.modelReg[PascalModel.modelIdentifier] = PascalModel
# Register file extensions
EditorHelper.extMap[PascalModel.ext] = EditorHelper.extMap['.dpr'] = PascalModel
# Register Controller for opening in the Editor
Controllers.modelControllerReg[PascalModel] = PascalController
# Add item to the New palette
# There needs to be a 24x24 png image:
#   Images/Palette/[Model.modelIdentifier].png
PaletteStore.paletteLists['New'].append(PascalModel.modelIdentifier)
# Link up controller for creation from the New palette
PaletteStore.newControllers[PascalModel.modelIdentifier] = PascalController
