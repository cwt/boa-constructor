#-----------------------------------------------------------------------------
# Name:        BasicCompanions.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002 - 2003
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Companions.BasicCompanions'

from wxPython.wx import *

from wxPython.html import wxHtmlWindow
from wxPython.stc import *

from BaseCompanions import WindowDTC, ChoicedDTC

import Constructors
from EventCollections import *

from PropEdit.PropertyEditors import *
from PropEdit.Enumerations import *

class ScrollBarDTC(Constructors.MultiItemCtrlsConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxScrollBarDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wxSB_HORIZONTAL', 'wxSB_VERTICAL'] + self.windowStyles

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos': position,
                'size': size,
                'style': 'wxSB_HORIZONTAL',
                'name': `self.name`}

    def events(self):
        return WindowDTC.events(self) + ['ScrollEvent', 'CmdScrollEvent']

EventCategories['ComboEvent'] = (EVT_COMBOBOX, EVT_TEXT)
commandCategories.append('ComboEvent')
class ComboBoxDTC(ChoicedDTC):
    #wxDocs = HelpCompanions.wxComboBoxDocs
    def __init__(self, name, designer, parent, ctrlClass):
        ChoicedDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wxCB_SIMPLE', 'wxCB_DROPDOWN', 'wxCB_READONLY',
                             'wxCB_SORT'] + self.windowStyles

    def constructor(self):
        return {'Value': 'value', 'Position': 'pos', 'Size': 'size',
                'Choices': 'choices', 'Style': 'style',
                'Validator': 'validator', 'Name': 'name'}

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'value': `self.name`,
                'pos': position,
                'size': size,
                'choices': '[]',
                'style': '0',
                'validator': 'wxDefaultValidator',
                'name': `self.name`}

##    def vetoedMethods(self):
##        return ['GetColumns', 'SetColumns', 'GetSelection', 'SetSelection',
##                'GetStringSelection', 'SetStringSelection']
##
##    def hideDesignTime(self):
##        return ['Label']

    def events(self):
        return ChoicedDTC.events(self) + ['ComboEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('ComboEvent', 'EVT_COMBOBOX')

EventCategories['ChoiceEvent'] = (EVT_CHOICE,)
commandCategories.append('ChoiceEvent')
class ChoiceDTC(Constructors.ListConstr, ChoicedDTC):
    #wxDocs = HelpCompanions.wxChoiceDocs = 'wx41.htm'
    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos': position,
                'size': size,
                'choices': `[]`,
                'style': '0',
                'validator': 'wxDefaultValidator',
                'name': `self.name`}

    def events(self):
        return ChoicedDTC.events(self) + ['ChoiceEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('ChoiceEvent', 'EVT_CHOICE')

class StaticTextDTC(Constructors.LabeledNonInputConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxStaticTextDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wxALIGN_LEFT', 'wxALIGN_RIGHT', 'wxALIGN_CENTRE',
                             'wxST_NO_AUTORESIZE'] + self.windowStyles
    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'label': `self.name`,
                'pos': position,
                'size': size,
                'style': '0',
                'name': `self.name`}

EventCategories['TextCtrlEvent'] = (EVT_TEXT, EVT_TEXT_ENTER, EVT_TEXT_URL, EVT_TEXT_MAXLEN)
commandCategories.append('TextCtrlEvent')
class TextCtrlDTC(WindowDTC):
    #wxDocs = HelpCompanions.wxTextCtrlDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wxTE_PROCESS_ENTER', 'wxTE_PROCESS_TAB',
                             'wxTE_MULTILINE', 'wxTE_PASSWORD',
                             'wxTE_READONLY', 'wxTE_RICH', 'wxTE_AUTO_URL',
                             'wxTE_NOHIDESEL',
                             ] + self.windowStyles

    def constructor(self):
        return {'Value': 'value', 'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Validator': 'validator', 'Name': 'name'}

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'value': `self.name`,
                'pos': position,
                'size': size,
                'style': '0',
                'name': `self.name`}

    def hideDesignTime(self):
        return WindowDTC.hideDesignTime(self) + \
              ['Selection', 'Title', 'Label', 'DefaultStyle']

    def events(self):
        return WindowDTC.events(self) + ['TextCtrlEvent']

EventCategories['RadioButtonEvent'] = (EVT_RADIOBUTTON,)
commandCategories.append('RadioButtonEvent')
class RadioButtonDTC(Constructors.LabeledInputConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxRadioButtonDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Value'] = BoolPropEdit
        self.windowStyles = ['wxRB_GROUP'] + self.windowStyles

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'label': `self.name`,
                'pos': position,
                'size': size,
                'style': '0',
                'name': `self.name`}

    def events(self):
        return WindowDTC.events(self) + ['RadioButtonEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('RadioButtonEvent', 'EVT_RADIOBUTTON')


EventCategories['CheckBoxEvent'] = (EVT_CHECKBOX,)
commandCategories.append('CheckBoxEvent')
class CheckBoxDTC(Constructors.LabeledInputConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxCheckBoxDocs = 'wx39.htm'
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Value'] = BoolPropEdit
    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'label': `self.name`,
                'pos': position,
                'size': size,
                'style': '0',
                'name': `self.name`}
    def events(self):
        return WindowDTC.events(self) + ['CheckBoxEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('CheckBoxEvent', 'EVT_CHECKBOX')


class SliderDTC(WindowDTC):
    #wxDocs = HelpCompanions.wxSliderDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['MinValue'] = IntConstrPropEdit
        self.editors['MaxValue'] = IntConstrPropEdit
        self.windowStyles = ['wxSL_HORIZONTAL', 'wxSL_VERTICAL',
                             'wxSL_AUTOTICKS', 'wxSL_LABELS', 'wxSL_LEFT',
                             'wxSL_RIGHT', 'wxSL_TOP',
                             'wxSL_SELRANGE'] + self.windowStyles

    def constructor(self):
        return {'Value': 'value', 'MinValue': 'minValue', 'MaxValue': 'maxValue',
                'Position': 'point', 'Size': 'size', 'Style': 'style',
                'Validator': 'validator', 'Name': 'name'}

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'value': '0',
                'minValue': '0',
                'maxValue': '100',
                'point': position,
                'size': size,
                'style': 'wxSL_HORIZONTAL',
                'validator': 'wxDefaultValidator',
                'name': `self.name`}

    def hideDesignTime(self):
        return WindowDTC.hideDesignTime(self) + ['TickFreq']

    def events(self):
        return WindowDTC.events(self) + ['ScrollEvent', 'CmdScrollEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('ScrollEvent', 'EVT_SCROLL')

class GaugeDTC(WindowDTC):
    #wxDocs = HelpCompanions.wxGaugeDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wxGA_HORIZONTAL', 'wxGA_VERTICAL',
                        'wxGA_PROGRESSBAR', 'wxGA_SMOOTH'] + self.windowStyles

    def constructor(self):
        return {'Range': 'range', 'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Validator': 'validator', 'Name': 'name'}

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'range': '100',
                'pos': position,
                'size': size,
                'style': 'wxGA_HORIZONTAL',
                'validator': 'wxDefaultValidator',
                'name': `self.name`}

class StaticBoxDTC(Constructors.LabeledNonInputConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxStaticBoxDocs
    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'label': `self.name`,
                'pos': position,
                'size': self.getDefCtrlSize(),
                'style': '0',
                'name': `self.name`}

class StaticLineDTC(Constructors.WindowConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxStaticLineDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wxLI_HORIZONTAL', 'wxLI_VERTICAL'] + self.windowStyles

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos': position,
                'size': size,
                'style': '0',
                'name': `self.name`}

class StaticBitmapDTC(WindowDTC):
    #wxDocs = HelpCompanions.wxStaticBitmapDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Bitmap'] = BitmapPropEdit

    def constructor(self):
        return {'Bitmap': 'bitmap', 'Label': 'label', 'Position': 'pos',
                'Size': 'size', 'Style': 'style', 'Name': 'name'}

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'bitmap': 'wxNullBitmap',
                'pos': position,
                'size': size,
                'style': '0',
                'name': `self.name`}

class HtmlWindowDTC(WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Style']

    def constructor(self):
        return {'Position': 'pos', 'Size': 'size', 'Name': 'name', 'Style': 'style'}

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos': position,
                'size': self.getDefCtrlSize(),
                'style': 'wxHW_SCROLLBAR_AUTO',
                'name': `self.name`}

    def events(self):
        return WindowDTC.events(self) + ['ScrollEvent']

    def writeImports(self):
        return '\n'.join( (WindowDTC.writeImports(self), 
                           'from wxPython.html import *') )

stcEOLMode = [wxSTC_EOL_CRLF, wxSTC_EOL_CR, wxSTC_EOL_LF]
stcEOLModeNames = {'wxSTC_EOL_CRLF': wxSTC_EOL_CRLF,
                   'wxSTC_EOL_CR': wxSTC_EOL_CR,
                   'wxSTC_EOL_LF': wxSTC_EOL_LF}

stcEdgeMode = [wxSTC_EDGE_NONE, wxSTC_EDGE_LINE, wxSTC_EDGE_BACKGROUND]
stcEdgeModeNames = {'wxSTC_EDGE_NONE': wxSTC_EDGE_NONE,
                    'wxSTC_EDGE_LINE': wxSTC_EDGE_LINE,
                    'wxSTC_EDGE_BACKGROUND': wxSTC_EDGE_BACKGROUND}

stcLexer = [wxSTC_LEX_NULL, wxSTC_LEX_PYTHON, wxSTC_LEX_CONTAINER,
            wxSTC_LEX_CPP , wxSTC_LEX_HTML , wxSTC_LEX_XML, wxSTC_LEX_PERL,
            wxSTC_LEX_SQL, wxSTC_LEX_VB, wxSTC_LEX_PROPERTIES,
            wxSTC_LEX_ERRORLIST, wxSTC_LEX_MAKEFILE, wxSTC_LEX_BATCH,
            wxSTC_LEX_XCODE, wxSTC_LEX_LATEX, wxSTC_LEX_LUA, wxSTC_LEX_DIFF,
            wxSTC_LEX_CONF, wxSTC_LEX_PASCAL, wxSTC_LEX_AVE, wxSTC_LEX_ADA,
            wxSTC_LEX_LISP, wxSTC_LEX_RUBY, wxSTC_LEX_EIFFEL, wxSTC_LEX_EIFFELKW,
            wxSTC_LEX_TCL, wxSTC_LEX_NNCRONTAB, wxSTC_LEX_BULLANT,
            wxSTC_LEX_VBSCRIPT, wxSTC_LEX_ASP, wxSTC_LEX_PHP, wxSTC_LEX_BAAN,
            wxSTC_LEX_MATLAB, wxSTC_LEX_SCRIPTOL, wxSTC_LEX_AUTOMATIC]
stcLexerNames = {'wxSTC_LEX_NULL': wxSTC_LEX_NULL,
      'wxSTC_LEX_PYTHON': wxSTC_LEX_PYTHON,
      'wxSTC_LEX_CONTAINER': wxSTC_LEX_CONTAINER,
      'wxSTC_LEX_CPP': wxSTC_LEX_CPP, 'wxSTC_LEX_HTML': wxSTC_LEX_HTML,
      'wxSTC_LEX_XML': wxSTC_LEX_XML, 'wxSTC_LEX_PERL': wxSTC_LEX_PERL,
      'wxSTC_LEX_SQL': wxSTC_LEX_SQL, 'wxSTC_LEX_VB': wxSTC_LEX_VB,
      'wxSTC_LEX_PROPERTIES': wxSTC_LEX_PROPERTIES,
      'wxSTC_LEX_ERRORLIST': wxSTC_LEX_ERRORLIST,
      'wxSTC_LEX_MAKEFILE': wxSTC_LEX_MAKEFILE,
      'wxSTC_LEX_BATCH': wxSTC_LEX_BATCH,
      'wxSTC_LEX_XCODE': wxSTC_LEX_XCODE, 'wxSTC_LEX_LATEX': wxSTC_LEX_LATEX,
      'wxSTC_LEX_LUA': wxSTC_LEX_LUA, 'wxSTC_LEX_DIFF': wxSTC_LEX_DIFF,
      'wxSTC_LEX_CONF': wxSTC_LEX_CONF, 'wxSTC_LEX_PASCAL': wxSTC_LEX_PASCAL,
      'wxSTC_LEX_AVE': wxSTC_LEX_AVE, 'wxSTC_LEX_ADA': wxSTC_LEX_ADA,
      'wxSTC_LEX_LISP': wxSTC_LEX_LISP, 'wxSTC_LEX_RUBY': wxSTC_LEX_RUBY,
      'wxSTC_LEX_EIFFEL': wxSTC_LEX_EIFFEL,
      'wxSTC_LEX_EIFFELKW': wxSTC_LEX_EIFFELKW,
      'wxSTC_LEX_TCL': wxSTC_LEX_TCL, 'wxSTC_LEX_NNCRONTAB': wxSTC_LEX_NNCRONTAB,
      'wxSTC_LEX_BULLANT': wxSTC_LEX_BULLANT,
      'wxSTC_LEX_VBSCRIPT': wxSTC_LEX_VBSCRIPT, 'wxSTC_LEX_ASP': wxSTC_LEX_ASP,
      'wxSTC_LEX_PHP': wxSTC_LEX_PHP, 'wxSTC_LEX_BAAN': wxSTC_LEX_BAAN,
      'wxSTC_LEX_MATLAB': wxSTC_LEX_MATLAB,
      'wxSTC_LEX_SCRIPTOL': wxSTC_LEX_SCRIPTOL,
      'wxSTC_LEX_AUTOMATIC': wxSTC_LEX_AUTOMATIC}

stcPrintColourMode = [wxSTC_PRINT_NORMAL, wxSTC_PRINT_INVERTLIGHT,
      wxSTC_PRINT_BLACKONWHITE, wxSTC_PRINT_COLOURONWHITE,
      wxSTC_PRINT_COLOURONWHITEDEFAULTBG]
stcPrintColourModeNames = {'wxSTC_PRINT_NORMAL': wxSTC_PRINT_NORMAL,
      'wxSTC_PRINT_INVERTLIGHT': wxSTC_PRINT_INVERTLIGHT,
      'wxSTC_PRINT_BLACKONWHITE': wxSTC_PRINT_BLACKONWHITE,
      'wxSTC_PRINT_COLOURONWHITE': wxSTC_PRINT_COLOURONWHITE,
      'wxSTC_PRINT_COLOURONWHITEDEFAULTBG': wxSTC_PRINT_COLOURONWHITEDEFAULTBG}

stcWrapMode = [wxSTC_WRAP_NONE, wxSTC_WRAP_WORD]
stcWrapModeNames = {'wxSTC_WRAP_NONE': wxSTC_WRAP_NONE,
                    'wxSTC_WRAP_WORD': wxSTC_WRAP_WORD}

class StyledTextCtrlDTC(Constructors.WindowConstr, WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update(
            {'BackSpaceUnIndents': BoolPropEdit,
             'BufferedDraw': BoolPropEdit,
             'CaretLineVisible': BoolPropEdit,
             'EndAtLastLine': BoolPropEdit,
             'IndentationGuides': BoolPropEdit,
             'MouseDownCaptures': BoolPropEdit,
             'Overtype': BoolPropEdit,
             'ReadOnly': BoolPropEdit,
             'UndoCollection': BoolPropEdit,
             'UseHorizontalScrollBar': BoolPropEdit,
             'UseTabs': BoolPropEdit,
             'ViewEOL': BoolPropEdit,
             'ViewWhiteSpace': BoolPropEdit,
             'EOLMode': EnumPropEdit,
             'EdgeMode': EnumPropEdit,
             'Lexer': EnumPropEdit,
             'PrintColourMode': EnumPropEdit,
             'WrapMode': EnumPropEdit,
            })

        self.options.update({'EOLMode'   : stcEOLMode,
                             'EdgeMode' : stcEdgeMode,
                             'Lexer': stcLexer,
                             'PrintColourMode': stcPrintColourMode,
                             'WrapMode': stcWrapMode,
                            })
        self.names.update({'EOLMode'   : stcEOLModeNames,
                           'EdgeMode' : stcEdgeModeNames,
                           'Lexer': stcLexerNames,
                           'PrintColourMode': stcPrintColourModeNames,
                           'WrapMode': stcWrapModeNames,
                          })

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos': position,
                'size': size,
                'style': '0',
                'name': `self.name`}

    def hideDesignTime(self):
        return WindowDTC.hideDesignTime(self) + ['Anchor', 'CodePage',
               'DocPointer', 'LastKeydownProcessed', 'ModEventMask',
               'Status', 'STCFocus']

    def writeImports(self):
        return '\n'.join( (WindowDTC.writeImports(self), 
                           'from wxPython.stc import *') )

#-------------------------------------------------------------------------------
import PaletteStore

PaletteStore.paletteLists['BasicControls'] = []
PaletteStore.palette.append(['Basic Controls', 'Editor/Tabs/Basic',
                             PaletteStore.paletteLists['BasicControls']])
PaletteStore.paletteLists['BasicControls'].extend([wxStaticText, wxTextCtrl,
  wxComboBox, wxChoice, wxCheckBox, wxRadioButton, wxSlider, wxGauge,
  wxScrollBar, wxStaticBitmap, wxStaticLine, wxStaticBox, wxHtmlWindow,
  wxStyledTextCtrl])


PaletteStore.compInfo.update({
    wxStaticText: ['wxStaticText', StaticTextDTC],
    wxTextCtrl: ['wxTextCtrl', TextCtrlDTC],
    wxChoice: ['wxChoice', ChoiceDTC],
    wxComboBox: ['wxComboBox', ComboBoxDTC],
    wxCheckBox: ['wxCheckBox', CheckBoxDTC],
    wxRadioButton: ['wxRadioButton', RadioButtonDTC],
    wxSlider: ['wxSlider', SliderDTC],
    wxGauge: ['wxGauge', GaugeDTC],
    wxStaticBitmap: ['wxStaticBitmap', StaticBitmapDTC],
    wxScrollBar: ['wxScrollBar', ScrollBarDTC],
    wxStaticBox: ['wxStaticBox', StaticBoxDTC],
    wxStaticLine: ['wxStaticLine', StaticLineDTC],
    wxHtmlWindow: ['wxHtmlWindow', HtmlWindowDTC],
    wxStyledTextCtrl: ['wxStyledTextCtrl', StyledTextCtrlDTC],
})
