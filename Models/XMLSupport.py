#-----------------------------------------------------------------------------
# Name:        XMLSupport.py
# Purpose:     
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Models.XMLSupport'

from wxPython import wx

true=1;false=0

import Preferences, Utils

import EditorHelper
EditorHelper.imgXMLFileModel = EditorHelper.imgCounter
EditorHelper.imgCounter = EditorHelper.imgCounter + 1

from Models.EditorModels import PersistentModel
class XMLFileModel(PersistentModel):
    modelIdentifier = 'XML'
    defaultName = 'xml'
    bitmap = 'WebDocXML_s.png'
    imgIdx = EditorHelper.imgXMLFileModel
    ext = '.xml'

EditorHelper.modelReg[XMLFileModel.modelIdentifier] = XMLFileModel
EditorHelper.extMap['.dtd'] = XMLFileModel

from Views.StyledTextCtrls import LanguageSTCMix, stcConfigPath
class XMLStyledTextCtrlMix(LanguageSTCMix):
    def __init__(self, wId):
        LanguageSTCMix.__init__(self, wId,
              (0, Preferences.STCLineNumMarginWidth), 'xml', stcConfigPath)
        self.setStyles()

wxID_XMLSOURCEVIEW = wx.wxNewId()
from Views.SourceViews import EditorStyledTextCtrl
class XMLSourceView(EditorStyledTextCtrl, XMLStyledTextCtrlMix):
    viewName = 'XML'
    def __init__(self, parent, model):
        EditorStyledTextCtrl.__init__(self, parent, wxID_XMLSOURCEVIEW,
          model, (), -1)
        XMLStyledTextCtrlMix.__init__(self, wxID_XMLSOURCEVIEW)
        self.active = true

from Explorers import ExplorerNodes
ExplorerNodes.langStyleInfoReg.append( ('XML', 'xml', XMLStyledTextCtrlMix, 
     'stc-styles.rc.cfg') )

#from Models 
import Controllers
class XMLFileController(Controllers.PersistentController):
    Model           = XMLFileModel
    DefaultViews    = [XMLSourceView]
    try:              
        #from Views.XMLView import XMLTreeView
        #AdditionalViews = [XMLTreeView]
        AdditionalViews = []
    except ImportError: 
        AdditionalViews = []

Controllers.modelControllerReg[XMLFileModel] = XMLFileController

import PaletteStore
PaletteStore.newControllers['XML'] = XMLFileController
PaletteStore.paletteLists['New'].append('XML')
