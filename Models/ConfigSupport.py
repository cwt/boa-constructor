#-----------------------------------------------------------------------------
# Name:        ConfigSupport.py
# Purpose:     
#
# Author:      Riaan Booysen
#
# Created:     2002/12/03
# RCS-ID:      $Id$
# Copyright:   (c) 2002
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Models.ConfigSupport'

from wxPython import wx

import Preferences, Utils

true=1;false=0

import EditorHelper
EditorHelper.imgConfigFileModel = EditorHelper.imgCounter
EditorHelper.imgCounter = EditorHelper.imgCounter + 1

from Models.EditorModels import PersistentModel

class ConfigFileModel(PersistentModel):
    modelIdentifier = 'Config'
    defaultName = 'config'
    bitmap = 'Config_s.png'
    imgIdx = EditorHelper.imgConfigFileModel
    ext = '.cfg'

EditorHelper.modelReg[ConfigFileModel.modelIdentifier] = ConfigFileModel
EditorHelper.extMap['.ini'] = ConfigFileModel

from Views.StyledTextCtrls import LanguageSTCMix, stcConfigPath
class ConfigSTCMix(LanguageSTCMix):
    def __init__(self, wId):
        LanguageSTCMix.__init__(self, wId, (), 'prop', stcConfigPath)
        self.setStyles()

wxID_CONFIGVIEW = wx.wxNewId()
from Views.SourceViews import EditorStyledTextCtrl
class ConfigView(EditorStyledTextCtrl, ConfigSTCMix):
    viewName = 'Config'
    def __init__(self, parent, model):
        EditorStyledTextCtrl.__init__(self, parent, wxID_CONFIGVIEW, model, (), -1)
        ConfigSTCMix.__init__(self, wxID_CONFIGVIEW)
        self.active = true

from Explorers import ExplorerNodes
ExplorerNodes.langStyleInfoReg.append( ('Config', 'prop', ConfigSTCMix, 
      'stc-styles.rc.cfg') )

import Controllers
class ConfigFileController(Controllers.PersistentController):
    Model           = ConfigFileModel
    DefaultViews    = [ConfigView]
    AdditionalViews = []

Controllers.modelControllerReg[ConfigFileModel] = ConfigFileController

import PaletteStore
PaletteStore.newControllers['Config'] = ConfigFileController
PaletteStore.paletteLists['New'].append('Config')