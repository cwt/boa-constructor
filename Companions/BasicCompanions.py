#-----------------------------------------------------------------------------
# Name:        BasicCompanions.py
# Purpose:     
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Companions.BasicCompanions'

from wxPython.wx import *

from wxPython.html import wxHtmlWindow

from BaseCompanions import WindowDTC, ChoicedDTC

from Constructors import *
from EventCollections import *

from PropEdit.PropertyEditors import *
from PropEdit.Enumerations import *

class ScrollBarDTC(MultiItemCtrlsConstr, WindowDTC):
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
        return WindowDTC.events(self) + ['ScrollEvent']

class ComboConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Value': 'value', 'Position': 'pos', 'Size': 'size',
                'Choices': 'choices', 'Style': 'style',
                'Validator': 'validator', 'Name': 'name'}

EventCategories['ComboEvent'] = (EVT_COMBOBOX, EVT_TEXT)
commandCategories.append('ComboEvent')
class ComboBoxDTC(ComboConstr, ChoicedDTC):
    #wxDocs = HelpCompanions.wxComboBoxDocs
    def __init__(self, name, designer, parent, ctrlClass):
        ChoicedDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wxCB_SIMPLE', 'wxCB_DROPDOWN', 'wxCB_READONLY',
                             'wxCB_SORT'] + self.windowStyles
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
class ChoiceDTC(ListConstr, ChoicedDTC):
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

class StaticTextDTC(LabeledNonInputConstr, WindowDTC):
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
class TextCtrlDTC(TextCtrlConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxTextCtrlDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wxTE_PROCESS_ENTER', 'wxTE_PROCESS_TAB',
                             'wxTE_MULTILINE', 'wxTE_PASSWORD',
                             'wxTE_READONLY', 'wxTE_RICH', 'wxTE_AUTO_URL',
                             'wxTE_NOHIDESEL',
                             ] + self.windowStyles

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
class RadioButtonDTC(LabeledInputConstr, WindowDTC):
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
class CheckBoxDTC(LabeledInputConstr, WindowDTC):
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

class SliderConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Value': 'value', 'MinValue': 'minValue', 'MaxValue': 'maxValue',
                'Position': 'point', 'Size': 'size', 'Style': 'style',
                'Validator': 'validator', 'Name': 'name'}


class SliderDTC(SliderConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxSliderDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['MinValue'] = IntConstrPropEdit
        self.editors['MaxValue'] = IntConstrPropEdit
        self.windowStyles = ['wxSL_HORIZONTAL', 'wxSL_VERTICAL',
                             'wxSL_AUTOTICKS', 'wxSL_LABELS', 'wxSL_LEFT',
                             'wxSL_RIGHT', 'wxSL_TOP',
                             'wxSL_SELRANGE'] + self.windowStyles

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
        return WindowDTC.events(self) + ['ScrollEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('ScrollEvent', 'EVT_SCROLL')

class GaugeConstr(PropertyKeywordConstructor):
    def constructor(self):
        return {'Range': 'range', 'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Validator': 'validator', 'Name': 'name'}

class GaugeDTC(GaugeConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxGaugeDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wxGA_HORIZONTAL', 'wxGA_VERTICAL',
                        'wxGA_PROGRESSBAR', 'wxGA_SMOOTH'] + self.windowStyles

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'range': '100',
                'pos': position,
                'size': size,
                'style': 'wxGA_HORIZONTAL',
                'validator': 'wxDefaultValidator',
                'name': `self.name`}

class StaticBoxDTC(LabeledNonInputConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxStaticBoxDocs
    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'label': `self.name`,
                'pos': position,
                'size': 'wxSize(150, 150)',
                'style': '0',
                'name': `self.name`}

class StaticLineDTC(WindowConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxStaticLineDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wxLI_HORIZONTAL', 'wxLI_VERTICAL'] + self.windowStyles

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos': position,
                'size': size,
                'style': '0',
                'name': `self.name`}

class StaticBitmapDTC(StaticBitmapConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxStaticBitmapDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Bitmap'] = BitmapPropEdit

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'bitmap': 'wxNullBitmap',
                'pos': position,
                'size': size,
                'style': '0',
                'name': `self.name`}

class HtmlWindowDTC(HtmlWindowConstr, WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        del self.editors['Style']

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos': position,
                'size': size,
##                'style': 'wxHW_SCROLLBAR_AUTO',
                'name': `self.name`}

    def events(self):
        return WindowDTC.events(self) + ['ScrollEvent']

    def writeImports(self):
        return 'from wxPython.html import *'


#-------------------------------------------------------------------------------
import PaletteStore

PaletteStore.paletteLists['BasicControls'] = []
PaletteStore.palette.append(['Basic Controls', 'Editor/Tabs/Basic', 
                             PaletteStore.paletteLists['BasicControls']])
PaletteStore.paletteLists['BasicControls'].extend([wxStaticText, wxTextCtrl,
  wxComboBox, wxChoice, wxCheckBox, wxRadioButton, wxSlider, wxGauge, 
  wxScrollBar, wxStaticBitmap, wxStaticLine, wxStaticBox, wxHtmlWindow])


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
})
