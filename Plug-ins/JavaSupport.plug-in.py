#-----------------------------------------------------------------------------
# Name:        JavaSupport.py
# Purpose:     Simple Java Support
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002
# Licence:     GPL
#-----------------------------------------------------------------------------

print 'importing JavaSupport'

import os

from wxPython.wx import *
from wxPython.stc import *

import Preferences, Utils
import PaletteStore

from Models import Controllers, EditorHelper, EditorModels
from Views import SourceViews, StyledTextCtrls
from Explorers import ExplorerNodes

# Allocate an image index for Java files
EditorHelper.imgJavaModel = EditorHelper.imgIdxRange()

class JavaModel(EditorModels.SourceModel):
    modelIdentifier = 'Java'
    defaultName = 'java'  # default name given to newly created files
    bitmap = 'Java_s.png' # this image must exist in Images/Modules
    ext = '.java'
    imgIdx = EditorHelper.imgJavaModel

# get the style definitions file in either the prefs directory or the Boa root
java_cfgfile = Preferences.rcPath +'/Plug-ins/stc-java.rc.cfg'
if not os.path.exists(java_cfgfile):
    java_cfgfile = Preferences.pyPath +'/Plug-ins/stc-java.rc.cfg'

class JavaStyledTextCtrlMix(StyledTextCtrls.LanguageSTCMix):
    def __init__(self, wId):
        StyledTextCtrls.LanguageSTCMix.__init__(self, wId,
              (0, Preferences.STCLineNumMarginWidth), 'java', java_cfgfile)
        self.setStyles()

wxID_JAVASOURCEVIEW = wxNewId()
class JavaSourceView(SourceViews.EditorStyledTextCtrl, JavaStyledTextCtrlMix):
    viewName = 'Source'
    def __init__(self, parent, model):
        SourceViews.EditorStyledTextCtrl.__init__(self, parent, wxID_JAVASOURCEVIEW,
          model, (), -1)
        JavaStyledTextCtrlMix.__init__(self, wxID_JAVASOURCEVIEW)
        self.active = true

# Register a Java STC style editor under Preferences
ExplorerNodes.langStyleInfoReg.append( ('Java', 'java',
      JavaStyledTextCtrlMix, java_cfgfile) )

# The compile action is just added as an example of how to add an action to
# a controller and is not implemented
wxID_PASCALCOMPILE = wxNewId()
class JavaController(Controllers.SourceController):
    Model = JavaModel
    DefaultViews = [JavaSourceView]

    compileBmp = 'Images/Debug/Compile.png'

    def actions(self, model):
        return Controllers.SourceController.actions(self, model) + [
              ('Compile', self.OnCompile, '-', 'CheckSource')]

    def OnCompile(self, event):
        wxLogWarning('Not implemented')

# Register Model for opening in the Editor
EditorHelper.modelReg[JavaModel.modelIdentifier] = JavaModel
# Register file extensions
EditorHelper.extMap[JavaModel.ext] = JavaModel
# Register Controller for opening in the Editor
Controllers.modelControllerReg[JavaModel] = JavaController
# Add item to the New palette
# There needs to be a 24x24 png image:
#   Images/Palette/[Model.modelIdentifier].png
PaletteStore.paletteLists['New'].append(JavaModel.modelIdentifier)
# Link up controller for creation from the New palette
PaletteStore.newControllers[JavaModel.modelIdentifier] = JavaController
