#-----------------------------------------------------------------------------
# Name:        HTMLSupport.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002 - 2004
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Models.HTMLSupport'

from wxPython import wx

import Preferences, Utils

true=1;false=0

import EditorHelper
EditorHelper.imgHTMLFileModel = EditorHelper.imgIdxRange()

from Models.EditorModels import PersistentModel

class HTMLFileModel(PersistentModel):
    modelIdentifier = 'HTML'
    defaultName = 'html'
    bitmap = 'WebDocHTML_s.png'
    imgIdx = EditorHelper.imgHTMLFileModel
    ext = '.html'

EditorHelper.modelReg[HTMLFileModel.modelIdentifier] = HTMLFileModel
EditorHelper.extMap['.htm'] = HTMLFileModel

from Views.StyledTextCtrls import LanguageSTCMix, stcConfigPath
class BaseHTMLStyledTextCtrlMix(LanguageSTCMix):
    def __init__(self, wId):
        LanguageSTCMix.__init__(self, wId,
              (0, Preferences.STCLineNumMarginWidth), 'html', stcConfigPath)

class HTMLStyledTextCtrlMix(BaseHTMLStyledTextCtrlMix):
    def __init__(self, wId):
        BaseHTMLStyledTextCtrlMix.__init__(self, wId)
        self.setStyles()

wxID_HTMLSOURCEVIEW = wx.wxNewId()
from Views.SourceViews import EditorStyledTextCtrl
class HTMLSourceView(EditorStyledTextCtrl, HTMLStyledTextCtrlMix):
    viewName = 'HTML'
    def __init__(self, parent, model):
        EditorStyledTextCtrl.__init__(self, parent, wxID_HTMLSOURCEVIEW,
          model, (), -1)
        HTMLStyledTextCtrlMix.__init__(self, wxID_HTMLSOURCEVIEW)
        self.active = true

from Explorers import ExplorerNodes
ExplorerNodes.langStyleInfoReg.append( ('HTML', 'html',
      BaseHTMLStyledTextCtrlMix, 'stc-styles.rc.cfg') )

import Controllers
from Views.EditorViews import HTMLFileView
class HTMLFileController(Controllers.PersistentController):
    Model           = HTMLFileModel
    DefaultViews    = [HTMLSourceView]
    AdditionalViews = [HTMLFileView]

Controllers.modelControllerReg[HTMLFileModel] = HTMLFileController

import PaletteStore
PaletteStore.newControllers['HTML'] = HTMLFileController
PaletteStore.paletteLists['New'].append('HTML')
