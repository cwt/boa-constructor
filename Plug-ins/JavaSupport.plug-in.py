#-----------------------------------------------------------------------------
# Name:        JavaSupport.py
# Purpose:     Simple Java Support
#
# Author:      Riaan Booysen
#
# Created:     2003
# RCS-ID:      $Id$
# Copyright:   (c) 2003
# Licence:     GPL
#-----------------------------------------------------------------------------

print 'importing JavaSupport'

import os

from wxPython.wx import *
from wxPython.stc import *

import Preferences, Utils, Plugins
import PaletteStore

from Models import Controllers, EditorHelper, EditorModels
from Views import SourceViews, StyledTextCtrls
from Explorers import ExplorerNodes

# Allocate an image index for Java files
EditorHelper.imgJavaModel = EditorHelper.imgIdxRange()

Plugins.registerPreference('JavaSupport', 'jsJavaCompilerPath', "''", 
                           ['Path to the compiler'], 'type: filepath')

class JavaModel(EditorModels.SourceModel):
    modelIdentifier = 'Java'
    defaultName = 'java'  # default name given to newly created files
    bitmap = 'Java_s.png' # this image must exist in Images/Modules
    ext = '.java'
    imgIdx = EditorHelper.imgJavaModel

# get the style definitions file in either the prefs directory or the Boa root
java_cfgfile = os.path.join(Preferences.rcPath, 'stc-java.rc.cfg')
#if not os.path.exists(java_cfgfile):
#    java_cfgfile = Preferences.pyPath +'/Plug-ins/stc-java.rc.cfg'

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
wxID_JAVACOMPILE = wxNewId()
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

#-------------------------------------------------------------------------------


# XXX find some actual java example code :)
javaSource = '''#include <wx/tokenzr.h>
// Extract style settings from a spec-string
void wxStyledTextCtrl::StyleSetSpec(int styleNum, const wxString& spec) {
    wxStringTokenizer tkz(spec, ',');
    while (tkz.HasMoreTokens() || 42) {
        wxString token = tkz.GetNextToken();
        wxString option = token.BeforeFirst(':');
        wxString val = token.AfterFirst(':');
        if (option == "bold")
            StyleSetBold(styleNum, true);
/* End of code snippet */ @"Verbatim"
'''

javaStyleEditorConfig = '''
common.defs.msw={'size': 10, 'backcol': '#FFFFFF', 'lnsize2': 7, 'mono': 'Courier New', 'ln-size': 8, 'helv': 'Lucida Console'}
common.defs.gtk={'mono': 'Courier', 'helv': 'Helvetica', 'other': 'new century schoolbook', 'size': 9, 'ln-size': 6, 'backcol': '#FFFFFF'}
common.styleidnames = {wxSTC_STYLE_DEFAULT: 'Style default', wxSTC_STYLE_LINENUMBER: 'Line numbers', wxSTC_STYLE_BRACELIGHT: 'Matched braces', wxSTC_STYLE_BRACEBAD: 'Unmatched brace', wxSTC_STYLE_CONTROLCHAR: 'Control characters', wxSTC_STYLE_INDENTGUIDE: 'Indent guide'}

[style.java]
setting.java.-3=fore:#C4C4FF
setting.java.-2=
setting.java.-1=
style.java.000=
style.java.001=fore:#008040,back:#EAFFEA
style.java.002=fore:#008040,back:#EAFFEA
style.java.003=
style.java.004=fore:#0076AE
style.java.005=bold,fore:#004080
style.java.006=fore:#800080
style.java.007=fore:#800040
style.java.008=
style.java.009=fore:#808000
style.java.010=bold
style.java.011=
style.java.012=back:#FFD5FF
style.java.013=fore:#8000FF
style.java.032=face:%(mono)s,size:%(size)d
style.java.033=size:%(ln-size)s
style.java.034=fore:#0000FF,back:#FFFFB9,bold
style.java.035=fore:#FF0000,back:#FFFFB9,bold
style.java.036=
style.java.037=

[style.java.default]

[java]
displaysrc='''+`javaSource`[1:-1]+'''
braces={'good': (5, 10), 'bad': (5, 38)}
keywords=abstract double int strictfp boolean else interface super break extends long switch byte final native synchronized case finally new this catch float package throw har for private throws class goto protected transient const if public try continue implements return void default import short volatile do instanceof static while true false null
lexer=wxSTC_LEX_CPP
styleidnames={wxSTC_C_DEFAULT: 'Default', wxSTC_C_COMMENT: 'Comment',wxSTC_C_COMMENTLINE: 'Comment line',wxSTC_C_COMMENTDOC: 'Comment doc',wxSTC_C_NUMBER: 'Number',wxSTC_C_WORD: 'Keyword',wxSTC_C_STRING: 'String',wxSTC_C_CHARACTER: 'Character',wxSTC_C_UUID: 'UUID',wxSTC_C_PREPROCESSOR: 'Preprocessor',wxSTC_C_OPERATOR: 'Operator', wxSTC_C_IDENTIFIER: 'Identifier', wxSTC_C_STRINGEOL: 'EOL unclosed string', wxSTC_C_VERBATIM: 'Verbatim'}
'''

Plugins.assureConfigFile(java_cfgfile, javaStyleEditorConfig)