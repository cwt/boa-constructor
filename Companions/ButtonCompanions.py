#-----------------------------------------------------------------------------
# Name:        ButtonCompanions.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002 - 2006
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Companions.ButtonCompanions'

import wx

import wx.lib.buttons

from Utils import _

from BaseCompanions import WindowDTC

import Constructors
from EventCollections import *

from PropEdit.PropertyEditors import *
from PropEdit.Enumerations import *

import methodparse

EventCategories['ButtonEvent'] = ('wx.EVT_BUTTON',)
commandCategories.append('ButtonEvent')

class ButtonDTC(Constructors.LabeledInputConstr, WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Default'] = BoolPropEdit
        self.windowStyles = ['wx.BU_LEFT', 'wx.BU_TOP', 'wx.BU_RIGHT',
                             'wx.BU_BOTTOM', 'wx.BU_EXACTFIT'] + self.windowStyles
        self.customPropEvaluators['Default'] = self.EvalDefault

    def properties(self):
        props = WindowDTC.properties(self)
        props['Default'] = ('CompnRoute', self.GetDefault, self.SetDefault)
        return props

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
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
        insp.events.doAddEvent('ButtonEvent', 'wx.EVT_BUTTON')

    def GetDefault(self, x):
        prnt = self.control.GetParent()
        if hasattr(prnt, '_default'):
            return prnt._default == self
        else:
            return False

    def SetDefault(self, value):
        prnt = self.control.GetParent()
        if value:
            if hasattr(prnt, '_default') and prnt._default != self:
                prnt._default.persistProp('Default', 'SetDefault', 'False')
            prnt._default = self
            self.control.SetDefault()
        elif hasattr(prnt, '_default'):
            del prnt._default

    def EvalDefault(self, exprs, objects):
        self.SetDefault(True)
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


EventCategories['ToggleButtonEvent'] = ('wx.EVT_TOGGLEBUTTON',)
commandCategories.append('ToggleButtonEvent')

class ToggleButtonDTC(ButtonDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        ButtonDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Value'] = BoolPropEdit

    def events(self):
        return ButtonDTC.events(self) + ['ToggleButtonEvent']


class BitmapButtonDTC(WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'Bitmap':          BitmapPropEdit,
                             'BitmapSelected' : BitmapPropEdit,
                             'BitmapFocused'  : BitmapPropEdit,
                             'BitmapDisabled' : BitmapPropEdit})
        self.windowStyles = ['wx.BU_AUTODRAW', 'wx.BU_LEFT', 'wx.BU_TOP',
                             'wx.BU_RIGHT', 'wx.BU_BOTTOM'] + self.windowStyles

    def constructor(self):
        return {'Bitmap': 'bitmap', 'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Name': 'name'}

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'bitmap': 'wx.NullBitmap',
                'pos': position,
                'size': size,
                'style': 'wx.BU_AUTODRAW',
                'name': `self.name`}

    def properties(self):
        props = WindowDTC.properties(self)
        props.update({'Bitmap': ('CtrlRoute', wx.BitmapButton.GetBitmapLabel,
                                              wx.BitmapButton.SetBitmapLabel)})
        return props

    def events(self):
        return WindowDTC.events(self) + ['ButtonEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        # Show events property page
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('ButtonEvent', 'wx.EVT_BUTTON')

class SpinButtonDTC(Constructors.WindowConstr, WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wx.SP_HORIZONTAL', 'wx.SP_VERTICAL',
                             'wx.SP_ARROW_KEYS', 'wx.SP_WRAP'] + self.windowStyles
        self.customPropEvaluators['Range'] = self.EvalRange

    def properties(self):
        props = WindowDTC.properties(self)
        props['Range'] = ('CompnRoute', self.GetRange, self.SetRange)
        return props

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'pos': position,
                'size': size,
                'style': 'wx.SP_HORIZONTAL',
                'name': `self.name`}
    def events(self):
        return WindowDTC.events(self) + ['SpinEvent', 'CmdScrollEvent']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('SpinEvent', 'wx.EVT_SPIN')

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

EventCategories['SpinCtrlEvent'] = ('wx.EVT_SPINCTRL',)
commandCategories.append('SpinCtrlEvent')
class SpinCtrlDTC(SpinButtonDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        SpinButtonDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Min'] = IntConstrPropEdit
        self.editors['Max'] = IntConstrPropEdit
        self.editors['Initial'] = IntConstrPropEdit
        self.compositeCtrl = True

    def constructor(self):
        return {'Min': 'min', 'Max': 'max',
                'Position': 'pos', 'Size': 'size', 'Style': 'style',
                'Initial': 'initial', 'Name': 'name'}

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {#'value': `'0'`,
                'pos': position,
                'size': size,
                'style': 'wx.SP_ARROW_KEYS',
                'min': '0',
                'max': '100',
                'initial': '0',
                'name': `self.name`}

    def events(self):
        return SpinButtonDTC.events(self) + ['SpinCtrlEvent', 'TextCtrlEvent']

    def hideDesignTime(self):
        return SpinButtonDTC.hideDesignTime(self) + ['Label']

    def defaultAction(self):
        insp = self.designer.inspector
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('SpinCtrlEvent', 'wx.EVT_SPINCTRL')


class GenButtonDTC(WindowDTC):
    if wx.VERSION[:2] >= (2, 7):
        handledConstrParams = ('parent', 'id')
        windowIdName = 'id'
    else:
        handledConstrParams = ('parent', 'ID')
        windowIdName = 'ID'
        
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['UseFocusIndicator'] = BoolPropEdit
        self.ctrlDisabled = True

    def constructor(self):
        return {'Label': 'label', 'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Name': 'name'}


    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'label': `self.name`,
                'pos': position,
                'size': size,
                'name': `self.name`,
                'style': '0'}

    def events(self):
        return WindowDTC.events(self) + ['ButtonEvent']

    def writeImports(self):
        return '\n'.join( (WindowDTC.writeImports(self),
                           'import wx.lib.buttons') )


class GenBitmapButtonDTC(GenButtonDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        GenButtonDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'Bitmap'         : BitmapConstrPropEdit,
                             'BitmapLabel'    : BitmapPropEdit,
                             'BitmapSelected' : BitmapPropEdit,
                             'BitmapFocus'    : BitmapPropEdit,
                             'BitmapDisabled' : BitmapPropEdit})

    def constructor(self):
        return {'BitmapLabel': 'bitmap', 'Position': 'pos', 'Size': 'size',
                'Style': 'style', 'Name': 'name'}

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'bitmap': 'wx.NullBitmap',
                'pos': position,
                'size': size,
                'name': `self.name`,
                'style': '0'}

    def defaultAction(self):
        insp = self.designer.inspector
        # Show events property page
        insp.pages.SetSelection(2)
        insp.events.doAddEvent('ButtonEvent', 'wx.EVT_BUTTON')

class GenBitmapTextButtonDTC(GenBitmapButtonDTC):
    def constructor(self):
        return {'BitmapLabel': 'bitmap', 'Position': 'pos', 'Size': 'size',
                'Label': 'label', 'Style': 'style',
                'Name': 'name'}

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'bitmap': 'wx.NullBitmap',
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
    suppressWindowId = True
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.windowStyles = ['wx.BU_AUTODRAW', 'wx.BU_LEFT', 'wx.BU_TOP',
                             'wx.BU_RIGHT', 'wx.BU_BOTTOM'] + self.windowStyles

    def constructor(self):
        return {'Position': 'pos', 'Size': 'size', 'Style': 'style'}

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        return {'pos':   position,
                'size':  size,
                'style': 'wx.BU_AUTODRAW',}


#-------------------------------------------------------------------------------
import Plugins

Plugins.registerPalettePage('Buttons', 'Buttons')
Plugins.registerComponents('Buttons',
      (wx.Button, 'wx.Button', ButtonDTC),
      (wx.BitmapButton, 'wx.BitmapButton', BitmapButtonDTC),
      (wx.SpinButton, 'wx.SpinButton', SpinButtonDTC),
      (wx.SpinCtrl, 'wx.SpinCtrl', SpinCtrlDTC),
      (wx.lib.buttons.GenButton, 'wx.lib.buttons.GenButton', GenButtonDTC),
      (wx.lib.buttons.GenBitmapButton, 'wx.lib.buttons.GenBitmapButton', GenBitmapButtonDTC),
      (wx.lib.buttons.GenToggleButton, 'wx.lib.buttons.GenToggleButton', GenToggleButtonDTC),
      (wx.lib.buttons.GenBitmapToggleButton, 'wx.lib.buttons.GenBitmapToggleButton', GenBitmapToggleButtonDTC),
      (wx.lib.buttons.GenBitmapTextButton, 'wx.lib.buttons.GenBitmapTextButton', GenBitmapTextButtonDTC),
      (wx.lib.buttons.GenBitmapTextToggleButton, 'wx.lib.buttons.GenBitmapTextToggleButton', GenBitmapTextToggleButtonDTC),
      (wx.ContextHelpButton, 'wx.ContextHelpButton', ContextHelpButtonDTC),
    )

try:
    Plugins.registerComponent('Buttons', wx.ToggleButton, 'wx.ToggleButton', ToggleButtonDTC)
except AttributeError:
    # MacOS X
    pass
