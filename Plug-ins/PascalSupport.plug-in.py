#-----------------------------------------------------------------------------
# Name:        PascalSupport.py
# Purpose:     Example plugin module showing how to add new filetypes to the ide
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002 - 2003
# Licence:     GPL
#-----------------------------------------------------------------------------

import os

from wxPython.wx import *
from wxPython.stc import *

import Preferences, Utils, Plugins
import PaletteStore

from Models import Controllers, EditorHelper, EditorModels
from Views import SourceViews, StyledTextCtrls
from Explorers import ExplorerNodes

# Allocate an image index for Pascal files
EditorHelper.imgPascalModel = EditorHelper.imgIdxRange()

# Register plug-in preference
Plugins.registerPreference('PascalSupport', 'psPascalCompilerPath', "''", 
                           ['Path to the compiler'], 'type: filepath')

class PascalModel(EditorModels.SourceModel):
    modelIdentifier = 'Pascal'
    defaultName = 'pascal'  # default name given to newly created files
    bitmap = 'Pascal_s.png' # this image must exist in Images/Modules
    ext = '.pas'
    imgIdx = EditorHelper.imgPascalModel

# get the style definitions file in either the prefs directory or the Boa root
pascal_cfgfile = Preferences.rcPath +'/stc-pascal.rc.cfg'
#Preferences.rcPath +'/stc-pascal.rc.cfg'
#if not os.path.exists(pascal_cfgfile):
#    pascal_cfgfile = Preferences.pyPath +'/Plug-ins/stc-pascal.rc.cfg'

class PascalStyledTextCtrlMix(StyledTextCtrls.LanguageSTCMix):
    def __init__(self, wId):
        StyledTextCtrls.LanguageSTCMix.__init__(self, wId,
              (0, Preferences.STCLineNumMarginWidth), 'pascal', pascal_cfgfile)
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
      PascalStyledTextCtrlMix, pascal_cfgfile) )

# The compile action is just added as an example of how to add an action to
# a controller and is not implemented
wxID_PASCALCOMPILE = wxNewId()
class PascalController(Controllers.SourceController):
    Model = PascalModel
    DefaultViews = [PascalSourceView]

    compileBmp = 'Images/Debug/Compile.png'

    def actions(self, model):
        return Controllers.SourceController.actions(self, model) + [
              ('Compile', self.OnCompile, '-', 'CheckSource')]

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


#-------------------------------------------------------------------------------
# Config file embedded in plug-in

pascalSource = '''unit Unit1;

interface

uses
  Windows, Messages, SysUtils, Classes, Graphics, Controls, Forms, Dialogs,
  StdCtrls;

type
  TForm1 = class(TForm)
    Button1: TButton;
    procedure Button1Click(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

implementation

{$R *.DFM}

procedure TForm1.Button1Click(Sender: TObject);
const
  a = 10;
var
  b : String;
begin
  b := 'String'
end;

end.
'''

pascalStyleEditorConfig = '''
common.defs.msw={'size': 10, 'backcol': '#FFFFFF', 'lnsize2': 7, 'mono': 'Courier New', 'lnsize': 8, 'helv': 'Lucida Console'}
common.defs.gtk={'mono': 'Courier', 'helv': 'Helvetica', 'other': 'new century schoolbook', 'size': 9, 'lnsize': 6, 'backcol': '#FFFFFF'}
common.styleidnames = {wxSTC_STYLE_DEFAULT: 'Style default', wxSTC_STYLE_LINENUMBER: 'Line numbers', wxSTC_STYLE_BRACELIGHT: 'Matched braces', wxSTC_STYLE_BRACEBAD: 'Unmatched brace', wxSTC_STYLE_CONTROLCHAR: 'Control characters', wxSTC_STYLE_INDENTGUIDE: 'Indent guide'}

[style.pascal]
setting.pascal.-3=fore:#8080FF
setting.pascal.-2=
setting.pascal.-1=
style.pascal.000=
style.pascal.001=fore:#008040,back:#EAFFEA
style.pascal.002=fore:#008040,back:#EAFFEA,size:%(size)d
style.pascal.003=
style.pascal.004=fore:#0076AE
style.pascal.005=bold,fore:#004080
style.pascal.006=fore:#800080
style.pascal.007=fore:#800040
style.pascal.008=
style.pascal.009=fore:#808000
style.pascal.010=bold
style.pascal.011=
style.pascal.012=back:#FFD5FF
style.pascal.013=fore:#8000FF
style.pascal.032=face:%(mono)s,size:%(size)d
style.pascal.033=size:%(lnsize)s
style.pascal.034=fore:#0000FF,back:#FFFFB9,bold
style.pascal.035=fore:#FF0000,back:#FFFFB9,bold
style.pascal.036=
style.pascal.037=

[style.pascal.default]

[pascal]
displaysrc='''+`pascalSource`[1:-1]+'''
braces={}
keywords=and array as asm begin case class const constructor destructor dispinterface div do downto else end except exports file finalization finally for function goto if implementation in inherited initialization inline interface is label library mod nil not object of or out packed procedure program property raise record repeat resourcestring set shl shr string then threadvar to try type unit until uses var while with xor private protected public published automated at on
lexer=wxSTC_LEX_PASCAL
styleidnames={wxSTC_C_DEFAULT: 'Default', wxSTC_C_COMMENT: 'Comment',wxSTC_C_COMMENTLINE: 'Comment line',wxSTC_C_COMMENTDOC: 'Comment doc',wxSTC_C_NUMBER: 'Number',wxSTC_C_WORD: 'Keyword',wxSTC_C_STRING: 'String',wxSTC_C_CHARACTER: 'Character',wxSTC_C_PREPROCESSOR: 'Preprocessor',wxSTC_C_OPERATOR: 'Operator', wxSTC_C_IDENTIFIER: 'Identifier', wxSTC_C_STRINGEOL: 'EOL unclosed string'}
'''

Plugins.assureConfigFile(pascal_cfgfile, pascalStyleEditorConfig)