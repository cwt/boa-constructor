#-----------------------------------------------------------------------------
# Name:        PyrexSupport.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002
# Licence:     GPL
#-----------------------------------------------------------------------------

import os, imp

from wxPython.wx import *
from wxPython.stc import *

import Preferences, Utils

try:
    imp.find_module('Pyrex')
except ImportError:
    raise Utils.SkipPlugin, 'Pyrex is not installed'

import PaletteStore

from Models import Controllers, EditorHelper, EditorModels, PythonEditorModels, PythonControllers
from Views import SourceViews, StyledTextCtrls
from Explorers import ExplorerNodes

EditorHelper.imgPyrexModel = EditorHelper.imgIdxRange()

class PyrexModel(EditorModels.SourceModel):
    modelIdentifier = 'Pyrex'
    defaultName = 'pyrex'
    bitmap = 'Pyrex_s.png'
    ext = '.pyx'
    imgIdx = EditorHelper.imgPyrexModel

pyrex_cfgfile = Preferences.rcPath +'/Plug-ins/stc-pyrex.rc.cfg'
if not os.path.exists(pyrex_cfgfile):
    pyrex_cfgfile = Preferences.pyPath +'/Plug-ins/stc-pyrex.rc.cfg'

class PyrexStyledTextCtrlMix(StyledTextCtrls.LanguageSTCMix):
    def __init__(self, wId):
        StyledTextCtrls.LanguageSTCMix.__init__(self, wId,
              (0, Preferences.STCLineNumMarginWidth), 'pyrex', pyrex_cfgfile)
        self.setStyles()

wxID_PYREXSOURCEVIEW = wxNewId()
class PyrexSourceView(SourceViews.EditorStyledTextCtrl, PyrexStyledTextCtrlMix):
    viewName = 'Source'
    def __init__(self, parent, model):
        SourceViews.EditorStyledTextCtrl.__init__(self, parent,
              wxID_PYREXSOURCEVIEW, model, (), -1)
        PyrexStyledTextCtrlMix.__init__(self, wxID_PYREXSOURCEVIEW)
        self.active = true

ExplorerNodes.langStyleInfoReg.append(
      ('Pyrex', 'pyrex', PyrexStyledTextCtrlMix, pyrex_cfgfile) )

#wxID_PYREXCOMPILE = wxNewId()
class PyrexController(Controllers.SourceController):
    Model = PyrexModel
    DefaultViews = [PyrexSourceView]

    compileBmp = 'Images/Debug/Compile.png'

    def actions(self, model):
        return Controllers.SourceController.actions(self, model) + [
              ('Compile', self.OnCompile, '-', 'CheckSource')]

    def OnCompile(self, event):
        from Pyrex.Compiler import Main, Errors

        model = self.getModel()
        try:
            result = Main.compile(model.localFilename(), c_only=1)
        except Errors.PyrexError, err:
            wxLogError(str(err))
            msg = 'Error'
        else:
            msg = 'Info'

        if msg == 'Error' or result.num_errors > 0:
            model.editor.setStatus('Pyrex compilation failed', 'Error')
        else:
            model.editor.setStatus('Pyrex compilation succeeded')


modId = PyrexModel.modelIdentifier
EditorHelper.modelReg[modId] = EditorHelper.extMap[PyrexModel.ext] = PyrexModel
Controllers.modelControllerReg[PyrexModel] = PyrexController

PaletteStore.paletteLists['New'].append(modId)
PaletteStore.newControllers[modId] = PyrexController
