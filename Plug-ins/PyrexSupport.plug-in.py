#-----------------------------------------------------------------------------
# Name:        PyrexSupport.py
# Purpose:     Support for editing pyrex files and compiling to C 
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002 - 2003
# Licence:     GPL
#-----------------------------------------------------------------------------

import os, imp

from wxPython.wx import *
from wxPython.stc import *

import Preferences, Utils, Plugins

try:
    imp.find_module('Pyrex')
except ImportError:
    raise Plugins.SkipPlugin, 'Pyrex is not installed'

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

pyrex_cfgfile = os.path.join(Preferences.rcPath, 'stc-pyrex.rc.cfg')
#if not os.path.exists(pyrex_cfgfile):
#    pyrex_cfgfile = Preferences.pyPath +'/Plug-ins/stc-pyrex.rc.cfg'

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

#-------------------------------------------------------------------------------

pyrexSource = '''## Comment Blocks!
cdef extern from "Numeric/arrayobject.h":

  struct PyArray_Descr:
    int type_num, elsize
    char type
  ctypedef class PyArrayObject [type PyArray_Type]:
    cdef char *data
    cdef int nd
    cdef int *dimensions, *strides
    cdef object base
    cdef PyArray_Descr *descr
    cdef int flags
'''

pyrexStyleEditorConfig = '''
common.defs.msw={'size': 10, 'backcol': '#FFFFFF', 'lnsize2': 7, 'mono': 'Courier New', 'lnsize': 8, 'helv': 'Lucida Console', 'ln-font': 'Lucida Console', 'ln-size': 8}
common.defs.gtk={'mono': 'Courier', 'helv': 'Helvetica', 'other': 'new century schoolbook', 'size': 9, 'lnsize': 6, 'backcol': '#FFFFFF', 'ln-font': 'Lucida Console', 'ln-size': 8}
common.styleidnames = {wxSTC_STYLE_DEFAULT: 'Style default', wxSTC_STYLE_LINENUMBER: 'Line numbers', wxSTC_STYLE_BRACELIGHT: 'Matched braces', wxSTC_STYLE_BRACEBAD: 'Unmatched brace', wxSTC_STYLE_CONTROLCHAR: 'Control characters', wxSTC_STYLE_INDENTGUIDE: 'Indent guide'}

[style.pyrex]
setting.pyrex.-3=
setting.pyrex.-2=fore:#000000
setting.pyrex.-1=fore:#000000,back:#88C4FF
style.pyrex.000=fore:#808080
style.pyrex.001=fore:#007F00,back:#E8FFE8
style.pyrex.002=fore:#007F7F
style.pyrex.003=fore:#7F007F
style.pyrex.004=fore:#7F007F
style.pyrex.005=fore:#00007F,bold
style.pyrex.006=fore:#7F0000
style.pyrex.007=fore:#000033,back:#FFFFE8
style.pyrex.008=fore:#0000FF,bold
style.pyrex.009=fore:#007F7F,bold
style.pyrex.010=bold
style.pyrex.011=
style.pyrex.012=fore:#7F7F7F
style.pyrex.013=fore:#000000,back:#ECD7EC,eolfilled
style.pyrex.032=back:%(backcol)s,face:%(mono)s,size:%(size)d
style.pyrex.033=size:%(ln-size)d,face:%(ln-font)s,back:#A0A0A0
style.pyrex.034=fore:#0000FF,back:#FFFF88,bold
style.pyrex.035=fore:#FF0000,back:#FFFF88,bold
style.pyrex.036=
style.pyrex.037=

[style.pyrex.default]

[pyrex]
displaysrc='''+`pyrexSource`[1:-1]+'''
braces={}
styleidnames={wxSTC_P_DEFAULT: 'Default', wxSTC_P_COMMENTLINE: 'Comment', wxSTC_P_NUMBER : 'Number', wxSTC_P_STRING : 'String', wxSTC_P_CHARACTER: 'Single quoted string', wxSTC_P_WORD: 'Keyword', wxSTC_P_TRIPLE:'Triple quotes', wxSTC_P_TRIPLEDOUBLE: 'Triple double quotes', wxSTC_P_CLASSNAME: 'Class definition', wxSTC_P_DEFNAME: 'Function or method', wxSTC_P_OPERATOR: 'Operators', wxSTC_P_IDENTIFIER: 'Identifiers', wxSTC_P_COMMENTBLOCK: 'Comment blocks', wxSTC_P_STRINGEOL: 'EOL unclosed string'}
lexer=wxSTC_LEX_PYTHON
keywords=and assert break class continue def del elif else except exec finally for from global if import in is lambda not or pass print raise return try while struct union enum ctypedef cdef void extern NULL
'''

Plugins.assureConfigFile(pyrex_cfgfile, pyrexStyleEditorConfig)
