#-----------------------------------------------------------------------------
# Name:        ButtonCompanions.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002 - 2003
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Companions.ButtonCompanions'

from wxPython.wx import *

from wxPython.lib.buttons import wxGenButton, wxGenBitmapButton, wxGenBitmapTextButton
from wxPython.lib.buttons import wxGenToggleButton, wxGenBitmapToggleButton, wxGenBitmapTextToggleButton
from wxPython.help import *

from BaseCompanions import WindowDTC

import Constructors
from EventCollections import *

from PropEdit.PropertyEditors import *
from PropEdit.Enumerations import *

import methodparse

EventCategories['ButtonEvent'] = (EVT_BUTTON,)
commandCategories.append('ButtonEvent')

class ButtonDTC(Constructors.LabeledInputConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxButtonDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Default'] = BoolPropEdit
        self.windowStyles = ['wxBU_LEFT', 'wxBU_TOP', 'wxBU_RIGHT',
                             'wxBU_BOTTOM', 'wxBU_EXACTFIT'] + self.windowStyles
        self.customPropEvaluators['Default'] = self.EvalDefault
        
    def properties(self):
        props = WindowDTC.properties(self)
        props['Default'] = ('CompnRoute', self.GetDefault, self.SetDefault)
        return props

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'label': `self.name`,
                'pos': position,
                'size': size,
                'name': `self.name`,
                'style': '0',}

    def events(self):
        return WindowDTC.events(self) + ['ButtonEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('ButtonEvent', 'EVT_BUTTON')

    def GetDefault(self, x):
        prnt = self.control.GetParent()
        if hasattr(prnt, '_default'):
            return prnt._default == self
        else:
            return false

    def SetDefault(self, value):
        prnt = self.control.GetParent()
        if value:
            if hasattr(prnt, '_default') and prnt._default != self:
                prnt._default.persistProp('Default', 'SetDefault', 'False')
            prnt._default = self
            self.control.SetDefault()
        else:
            del prnt._default

    def EvalDefault(self, exprs, objects):
        self.SetDefault(true)
        return ()

    def persistProp(self, name, setterName, value):
        if name == 'Default':
            for prop in self.textPropList:
                if prop.prop_setter == setterName:
                    if value.lower() == 'true':
                        prop.params = []
                    else:
                        del self.textPropList[self.textPropList.index(prop)]
                    return
            if value.lower() == 'true':
                self.textPropList.append(methodparse.PropertyParse(
                      None, self.getCompName(), setterName, [], name))
        else:
            WindowDTC.persistProp(self, name, setterName, value)


EventCategories['ToggleButtonEvent'] = (EVT_TOGGLEBUTTON,)
commandCategories.append('ToggleButtonEvent')

class ToggleButtonDTC(ButtonDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        ButtonDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Value'] = BoolPropEdit

    def events(self):
        return ButtonDTC.events(self) + ['ToggleButtonEvent']


class BitmapButtonDTC(WindowDTC):
    #wxDocs = HelpCompanions.wxBitmapButtonDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'Bitmap':          BitmapPropEdit,
                             'BitmapSelected' : BitmapPropEdit,
                             'BitmapFocused'  : BitmapPropEdit,
                             'BitmapDisabled' : BitmapPropEdit})
        self.windowStyles = ['wxBU_AUTODRAW', 'wxBU_LEFT', 'wxBU_TOP',
                             'wxBU_RIGHT', 'wxBU_BOTTOM'] + self.windowStyles

    def constructor(self):
        return {'Bitmap': 'bitmap', 'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Validator': 'validator', 'Name': 'name'}

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'bitmap': 'wxNullBitmap',
                'pos': position,
                'size': size,
                'style': 'wxBU_AUTODRAW',
                'validator': 'wxDefaultValidator',
                'name': `self.name`}

    def properties(self):
        props = WindowDTC.properties(self)
        props.update({'Bitmap': ('CtrlRoute', wxBitmapButton.GetBitmapLabel,
          wxBitmapButton.SetBitmapLabel)})
        return props

    def events(self):
        return WindowDTC.events(self) + ['ButtonEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        # Show events property page
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('ButtonEvent', 'EVT_BUTTON')

class SpinButtonDTC(Constructors.WindowConstr, WindowDTC):
    #wxDocs = HelpCompanions.wxSpinButtonDocs
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wxSP_HORIZONTAL', 'wxSP_VERTICAL',
                             'wxSP_ARROW_KEYS', 'wxSP_WRAP'] + self.windowStyles
        self.customPropEvaluators['Range'] = self.EvalRange

    def properties(self):
        props = WindowDTC.properties(self)
        props['Range'] = ('CompnRoute', self.GetRange, self.SetRange)
        return props

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos': position,
                'size': size,
                'style': 'wxSP_HORIZONTAL',
## cfd           'validator': 'wxDefaultValidator',
                'name': `self.name`}
    def events(self):
        return WindowDTC.events(self) + ['SpinEvent', 'CmdScrollEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('SpinEvent', 'EVT_SPIN')

    def GetRange(self, dummy):
        return (self.control.GetMin(), self.control.GetMax())

    def SetRange(self, value):
        self.control.SetRange(value[0], value[1])

    def EvalRange(self, exprs, objects):
        res = []
        for expr in exprs:
            res.append(self.eval(expr))
        return tuple(res)

    def persistProp(self, name, setterName, value):
        if setterName == 'SetRange':
            rMin, rMax = self.eval(value)
            newParams = [`rMin`, `rMax`]
            # edit if exists
            for prop in self.textPropList:
                if prop.prop_setter == setterName:
                    prop.params = newParams
                    return
            # add if not defined
            self.textPropList.append(methodparse.PropertyParse( None, self.name,
                setterName, newParams, 'SetRange'))
        else:
            WindowDTC.persistProp(self, name, setterName, value)

EventCategories['SpinCtrlEvent'] = (EVT_SPINCTRL,)
commandCategories.append('SpinCtrlEvent')
class SpinCtrlDTC(SpinButtonDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        SpinButtonDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Min'] = IntConstrPropEdit
        self.editors['Max'] = IntConstrPropEdit
        self.editors['Initial'] = IntConstrPropEdit
        self.compositeCtrl = true

    def constructor(self):
        return {'Min': 'min', 'Max': 'max',
                'Position': 'pos', 'Size': 'size', 'Style': 'style',
                'Initial': 'initial', 'Name': 'name'}

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {#'value': `'0'`,
                'pos': position,
                'size': size,
                'style': 'wxSP_ARROW_KEYS',
                'min': '0',
                'max': '100',
                'initial': '0',
                'name': `self.name`}

    def events(self):
        return SpinButtonDTC.events(self) + ['SpinCtrlEvent']

    def hideDesignTime(self):
        return SpinButtonDTC.hideDesignTime(self) + ['Label']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('SpinCtrlEvent', 'EVT_SPINCTRL')


class GenButtonDTC(WindowDTC):
    #wxDocs = HelpCompanions.wxDefaultDocs
    handledConstrParams = ('parent', 'ID')
    windowIdName = 'ID'
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['UseFocusIndicator'] = BoolPropEdit
        self.ctrlDisabled = true

    def constructor(self):
        return {'Label': 'label', 'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Validator': 'validator', 'Name': 'name'}

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'label': `self.name`,
                'pos': position,
                'size': size,
                'name': `self.name`,
                'style': '0'}

    def events(self):
        return WindowDTC.events(self) + ['ButtonEvent']

    def writeImports(self):
        return '\n'.join( (WindowDTC.writeImports(self), 
                           'from wxPython.lib.buttons import *') )


class GenBitmapButtonDTC(GenButtonDTC):
    #wxDocs = HelpCompanions.wxDefaultDocs
    windowIdName = 'ID'
    def __init__(self, name, designer, parent, ctrlClass):
        GenButtonDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'Bitmap'         : BitmapConstrPropEdit,
                             'BitmapLabel'    : BitmapPropEdit,
                             'BitmapSelected' : BitmapPropEdit,
                             'BitmapFocus'    : BitmapPropEdit,
                             'BitmapDisabled' : BitmapPropEdit})

    def constructor(self):
        return {'BitmapLabel': 'bitmap', 'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Validator': 'validator', 'Name': 'name'}

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'bitmap': 'wxNullBitmap',
                'pos': position,
                'size': size,
                'name': `self.name`,
                'style': '0'}

    def defaultAction(self):
        insp = self.designer.inspector
        # Show events property page
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('ButtonEvent', 'EVT_BUTTON')

class GenBitmapTextButtonDTC(GenBitmapButtonDTC):
    def constructor(self):
        return {'BitmapLabel': 'bitmap', 'Position': 'pos', 'Size': 'size',
                'Label': 'label', 'Style': 'style', 'Validator': 'validator',
                'Name': 'name'}

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'bitmap': 'wxNullBitmap',
                'label': `self.name`,
                'pos': position,
                'size': size,
                'name': `self.name`,
                'style': '0'}

class GenToggleButtonMix:
    def __init__(self):
        self.editors['Toggle'] = BoolPropEdit

class GenToggleButtonDTC(GenButtonDTC, GenToggleButtonMix):
    def __init__(self, name, designer, parent, ctrlClass):
        GenButtonDTC.__init__(self, name, designer, parent, ctrlClass)
        GenToggleButtonMix.__init__(self)
class GenBitmapToggleButtonDTC(GenBitmapButtonDTC, GenToggleButtonMix):
    def __init__(self, name, designer, parent, ctrlClass):
        GenBitmapButtonDTC.__init__(self, name, designer, parent, ctrlClass)
        GenToggleButtonMix.__init__(self)
class GenBitmapTextToggleButtonDTC(GenBitmapTextButtonDTC, GenToggleButtonMix):
    def __init__(self, name, designer, parent, ctrlClass):
        GenBitmapTextButtonDTC.__init__(self, name, designer, parent, ctrlClass)
        GenToggleButtonMix.__init__(self)


class ContextHelpButtonDTC(WindowDTC):
    suppressWindowId = true
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wxBU_AUTODRAW', 'wxBU_LEFT', 'wxBU_TOP',
                             'wxBU_RIGHT', 'wxBU_BOTTOM'] + self.windowStyles

    def constructor(self):
        return {'Position': 'pos', 'Size': 'size', 'Style': 'style'}

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos':   position,
                'size':  size,
                'style': 'wxBU_AUTODRAW',}

    def writeImports(self):
        return '\n'.join( (WindowDTC.writeImports(self), 
                           'from wxPython.help import *') )


#-------------------------------------------------------------------------------
import PaletteStore

PaletteStore.paletteLists['Buttons'] = []
PaletteStore.palette.append(['Buttons', 'Editor/Tabs/Basic',
                             PaletteStore.paletteLists['Buttons']])
PaletteStore.paletteLists['Buttons'].extend([wxButton, wxBitmapButton,
      wxSpinButton, wxSpinCtrl,
      wxGenButton, wxGenBitmapButton, wxGenBitmapTextButton,
      wxGenToggleButton, wxGenBitmapToggleButton, wxGenBitmapTextToggleButton,
      wxContextHelpButton])

try:
    PaletteStore.paletteLists['Buttons'].append(wxToggleButton)
except NameError:
    # MacOS X
    pass

PaletteStore.compInfo.update({
    wxButton: ['wxButton', ButtonDTC],
    wxBitmapButton: ['wxBitmapButton', BitmapButtonDTC],
    wxSpinButton: ['wxSpinButton', SpinButtonDTC],
    wxSpinCtrl: ['wxSpinCtrl', SpinCtrlDTC],
    wxGenButton: ['wxGenButton', GenButtonDTC],
    wxGenBitmapButton: ['wxGenBitmapButton', GenBitmapButtonDTC],
    wxGenToggleButton: ['wxGenToggleButton', GenToggleButtonDTC],
    wxGenBitmapToggleButton: ['wxGenBitmapToggleButton', GenBitmapToggleButtonDTC],
    wxGenBitmapTextButton: ['wxGenBitmapTextButton', GenBitmapTextButtonDTC],
    wxGenBitmapTextToggleButton: ['wxGenBitmapTextToggleButton', GenBitmapTextToggleButtonDTC],
    wxContextHelpButton: ['wxContextHelpButton', ContextHelpButtonDTC],
})

try:
    PaletteStore.compInfo[wxToggleButton] = ['wxToggleButton', ToggleButtonDTC]
except NameError:
    # MacOS X
    pass
