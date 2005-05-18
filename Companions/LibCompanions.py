#-----------------------------------------------------------------------------
# Name:        LibCompanions.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2003
# RCS-ID:      $Id$
# Copyright:   (c) 2003 - 2005
# Licence:     GPL
#-----------------------------------------------------------------------------
print 'importing Companions.LibCompanions'

import wx

from BaseCompanions import WindowDTC
from BasicCompanions import StaticTextDTC, TextCtrlDTC, ComboBoxDTC

from PropEdit import PropertyEditors, InspectorEditorControls
import EventCollections


import MaskedEditFmtCodeDlg


class GenStaticTextDTC(StaticTextDTC):
    handledConstrParams = ('parent', 'ID')
    windowIdName = 'ID'

    def writeImports(self):
        return 'import wx.lib.stattext'

#-------------------------------------------------------------------------------

##class MaskConstrPropEdit(PropertyEditors.StrConstrPropEdit):
##    def inspectorEdit(self):
##        self.editorCtrl = InspectorEditorControls.TextCtrlButtonIEC(self, self.value)
##        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)
##
##    def edit(self, event):
##        pass

class FormatCodePropEdit(PropertyEditors.StrPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = InspectorEditorControls.TextCtrlButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def edit(self, event):
        dlg = MaskedEditFmtCodeDlg.MaskedEditFormatCodesDlg(self.parent, self.value)
        try:
            if dlg.ShowModal() != wx.ID_OK:
                return

            self.value = dlg.getFormatCode()
            self.editorCtrl.setValue(self.value)
            self.inspectorPost(False)
        finally:
            dlg.Destroy()

class AutoFormatPropMixin:
    dependents = ['mask', 'datestyle', 'formatcodes',
                  'description', 'excludeChars', 'validRegex']

    def __init__(self):
        self.editors['Autoformat'] = PropertyEditors.StringEnumPropEdit

        from wx.lib.masked import maskededit
        autofmt = maskededit.masktags.keys()
        autofmt.sort()
        self.options['Autoformat'] = [s for s in ['']+autofmt]
        self.names['Autoformat'] = {}
        for opt in self.options['Autoformat']:
            self.names['Autoformat'][opt] = opt

        self.mutualDepProps += ['Autoformat'] + [s[0].upper()+s[1:]
                                                 for s in self.dependents]

    def properties(self):
        props = {'Autoformat': ('CompnRoute', self.GetAutoformat,
                                              self.SetAutoformat)}
        return props

    def GetAutoformat(self, x):
        return self.control.GetAutoformat()

    def SetAutoformat(self, val):
        currVals = {}
        for dp in self.dependents:
            currVals[dp] = self.control.GetCtrlParameter(dp)

        self.control.SetAutoformat(val)

        # call delayed so that Inspector may update first
        wx.CallAfter(self.revertAutoFormatDeps, currVals)

    def revertAutoFormatDeps(self, currVals):
        # revert source for properties that were changed to default values
        for dp in self.dependents:
            newVal = self.control.GetCtrlParameter(dp)
            if newVal != currVals[dp]:
                prop = dp[0].upper()+dp[1:]
                self.propRevertToDefault(prop, 'Set'+prop)


class MaskedDTCMixin:
    def __init__(self):
        BoolPE = PropertyEditors.BoolPropEdit
        StrEnumPE = PropertyEditors.StringEnumPropEdit
        BITPropEdit = PropertyEditors.BITPropEditor
        self.editors.update({'AutoCompleteKeycodes': BITPropEdit,
                             'UseFixedWidthFont': BoolPE,
                             'RetainFieldValidation': BoolPE,
                             'Datestyle': StrEnumPE,
                             'Choices': BITPropEdit,
                             'ChoiceRequired': BoolPE,
                             'CompareNoCase': BoolPE,
                             'EmptyInvalid': BoolPE,
                             'ValidRequired': BoolPE,
                             'Formatcodes': FormatCodePropEdit,
                            })

        self.options['Datestyle'] = ['YMD','MDY','YDM','DYM','DMY','MYD']
        self.names['Datestyle'] = {}
        for opt in self.options['Datestyle']:
            self.names['Datestyle'][opt] = opt

    def hideDesignTime(self):
        return ['Demo', 'Fields', 'Autoformat', 'ValidFunc']

class BaseMaskedTextCtrlDTC(TextCtrlDTC, MaskedDTCMixin):
    def __init__(self, name, designer, parent, ctrlClass):
        TextCtrlDTC.__init__(self, name, designer, parent, ctrlClass)
        MaskedDTCMixin.__init__(self)

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        dts = TextCtrlDTC.designTimeSource(self, position, size)
        dts['value'] = "''"
        return dts

    def hideDesignTime(self):
        return TextCtrlDTC.hideDesignTime(self) + MaskedDTCMixin.hideDesignTime(self)


class MaskedTextCtrlDTC(BaseMaskedTextCtrlDTC, AutoFormatPropMixin):
    def __init__(self, name, designer, parent, ctrlClass):
        BaseMaskedTextCtrlDTC.__init__(self, name, designer, parent, ctrlClass)
        AutoFormatPropMixin.__init__(self)

    def properties(self):
        props = BaseMaskedTextCtrlDTC.properties(self)
        props.update(AutoFormatPropMixin.properties(self))
        return props

    def writeImports(self):
        return 'import wx.lib.masked.textctrl'

class IpAddrCtrlDTC(BaseMaskedTextCtrlDTC):
    def writeImports(self):
        return 'import wx.lib.masked.ipaddrctrl'


class MaskedComboBoxDTC(ComboBoxDTC, MaskedDTCMixin, AutoFormatPropMixin):
    def __init__(self, name, designer, parent, ctrlClass):
        ComboBoxDTC.__init__(self, name, designer, parent, ctrlClass)
        MaskedDTCMixin.__init__(self)
        AutoFormatPropMixin.__init__(self)

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        dts = ComboBoxDTC.designTimeSource(self, position, size)
        dts['value'] = "''"
        return dts

    def properties(self):
        props = ComboBoxDTC.properties(self)
        props.update(AutoFormatPropMixin.properties(self))
        return props

    def hideDesignTime(self):
        return ComboBoxDTC.hideDesignTime(self) + \
               MaskedDTCMixin.hideDesignTime(self)
##               ['Mark', 'EmptyInvalid']

    def writeImports(self):
        return 'import wx.lib.masked.combobox'

class MaskedNumCtrlDTC(TextCtrlDTC, MaskedDTCMixin):
    def __init__(self, name, designer, parent, ctrlClass):
        TextCtrlDTC.__init__(self, name, designer, parent, ctrlClass)
        MaskedDTCMixin.__init__(self)

        self.editors.update({'Min': PropertyEditors.BITPropEditor,
                             'Max': PropertyEditors.BITPropEditor,
                             'Bounds': PropertyEditors.BITPropEditor})

        self.mutualDepProps += ['Bounds', 'Min', 'Max']

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        dts = TextCtrlDTC.designTimeSource(self, position, size)
        dts['value'] = '0'
        return dts

    def events(self):
        return TextCtrlDTC.events(self) + ['MaskedNumCtrlEvent']

    def writeImports(self):
        return 'import wx.lib.masked.numctrl'

    def hideDesignTime(self):
        return TextCtrlDTC.hideDesignTime(self) + \
               MaskedDTCMixin.hideDesignTime(self)
##               ['Datestyle', 'AutoCompleteKeycodes', 'ExcludeChars',
##               'IncludeChars', 'Choices', 'ChoiceRequired', 'CompareNoCase',
##               'ValidRange']


#-------------------------------------------------------------------------------

class SpinButtonEnumConstrPropEdit(PropertyEditors.ObjEnumConstrPropEdit):
    def getObjects(self):
        designer = self.companion.designer#.controllerView
        windows = designer.getObjectsOfClass(wx.SpinButton)
        windowNames = windows.keys()
        windowNames.sort()
        res = ['None'] + windowNames
        if self.value != 'None':
            res.insert(1, self.value)
        return res

    def getDisplayValue(self):
        return `self.valueToIECValue()`

    def getCtrlValue(self):
        return self.companion.GetSpinButton()
    def setCtrlValue(self, oldValue, value):
        self.companion.SetSpinButton(value)

class SpinButtonClassLinkPropEdit(PropertyEditors.ClassLinkPropEdit):
    linkClass = wx.SpinButton

#EventCollections.EventCategories['TimeCtrlEvent'] = (EVT_TIMEUPDATE,)
#EventCollections.commandCategories.append('TimeCtrlEvent')

# XXX min, max & limited params not supported yet
# XXX should be implemented as a wxDateTime property editor using
# XXX this very time ctrl, a problem is how to handle None values.

class TimeCtrlDTC(MaskedTextCtrlDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        MaskedTextCtrlDTC.__init__(self, name, designer, parent, ctrlClass)
        BoolPE = PropertyEditors.BoolConstrPropEdit
        ColourPE = PropertyEditors.ColourConstrPropEdit
        self.editors.update({'Format24Hours': BoolPE,
                             'SpinButton': SpinButtonClassLinkPropEdit,
                             'OutOfBoundsColour': ColourPE,
                             'DisplaySeconds': BoolPE,
                             'UseFixedWidthFont': BoolPE,
                             'Format': PropertyEditors.StringEnumPropEdit})

        format = ['MILHHMMSS', 'MILHHMM', 'HHMMSS', 'HHMM']
        self.options['Format'] = format
        self.names['Format'] = {}
        for name in format: self.names['Format'][name] = name


        self._spinbutton = None
        self.initPropsThruCompanion.extend(['SpinButton', 'BindSpinButton'])

    def constructor(self):
        constr = MaskedTextCtrlDTC.constructor(self)
        constr.update({'Format24Hours':     'fmt24hr',
                       'DisplaySeconds':    'display_seconds',
                       'OutOfBoundsColour': 'oob_color',
                       'UseFixedWidthFont': 'useFixedWidthFont',
                      })
        return constr

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        dts = MaskedTextCtrlDTC.designTimeSource(self, position, size)
        dts.update({'value': "'12:00:00 AM'",
                    'fmt24hr': 'False',
                    'display_seconds': 'True',
                    'oob_color': "wx.NamedColour('Yellow')",
                    'useFixedWidthFont': 'True',
                   })
        return dts

    def properties(self):
        props = MaskedTextCtrlDTC.properties(self)
        if props.has_key('Autoformat'):
            del props['Autoformat']
        props['SpinButton'] = ('CompnRoute', self.GetSpinButton,
                                             self.BindSpinButton)
##        props['Format24Hours'] = ('CompnRoute', self.GetFormat24Hours,
##                                                self.SetFormat24Hours)
##        props['DisplaySeconds'] = ('CompnRoute', self.GetDisplaySeconds,
##                                                 self.SetDisplaySeconds)

        return props

    def dependentProps(self):
        return MaskedTextCtrlDTC.dependentProps(self) + ['SpinButton', 'BindSpinButton']

    def events(self):
        return MaskedTextCtrlDTC.events(self) + ['TimeCtrlEvent']

    def writeImports(self):
        return 'import wx.lib.masked.timectrl'

##    def hideDesignTime(self):
##        return MaskedTextCtrlDTC.hideDesignTime(self) + ['Mask',
##               'Datestyle', 'AutoCompleteKeycodes', 'EmptyBackgroundColour',
##               'SignedForegroundColour', 'GroupChar', 'DecimalChar',
##               'ShiftDecimalChar', 'UseParensForNegatives', 'ExcludeChars',
##               'IncludeChars', 'Choices', 'ChoiceRequired', 'CompareNoCase',
##               'AutoSelect', 'ValidRegex', 'ValidRange']

    def GetSpinButton(self, x):
        return self._spinbutton

    def BindSpinButton(self, value):
        self._spinbutton = value
        if value is not None:
            spins = self.designer.getObjectsOfClass(wx.SpinButton)
            if value in spins:
                self.control.BindSpinButton(spins[value])

##    def GetDisplaySeconds(self, x):
##        return self.eval(self.textConstr.params['display_seconds'])
##
##    def SetDisplaySeconds(self, value):
##        self.textConstr.params['display_seconds'] = self.eval(value)

#-------------------------------------------------------------------------------

#EventCollections.EventCategories['IntCtrlEvent'] = (EVT_INT,)
#EventCollections.commandCategories.append('IntCtrlEvent')


class IntCtrlDTC(TextCtrlDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        TextCtrlDTC.__init__(self, name, designer, parent, ctrlClass)
        BoolPE = PropertyEditors.BoolConstrPropEdit
        ColourPE = PropertyEditors.ColourConstrPropEdit
        self.editors.update({'Min': PropertyEditors.BITPropEditor,
                             'Max': PropertyEditors.BITPropEditor,
                             'Limited': BoolPE,
                             'AllowNone': BoolPE,
                             'AllowLong': BoolPE,
                             'DefaultColour': ColourPE,
                             'OutOfBoundsColour': ColourPE})

    def constructor(self):
        constr = TextCtrlDTC.constructor(self)
        constr.update({'Min': 'min', 'Max': 'max', 'Limited': 'limited',
            'AllowNone': 'allow_none', 'AllowLong': 'allow_long',
            'DefaultColour': 'default_color', 'OutOfBoundsColour': 'oob_color'})
        return constr

    def designTimeSource(self, position = 'wx.DefaultPosition', size = 'wx.DefaultSize'):
        dts = TextCtrlDTC.designTimeSource(self, position, size)
        dts.update({'value': '0',
                    'min': 'None',
                    'max': 'None',
                    'limited': 'False',
                    'allow_none': 'False',
                    'allow_long': 'False',
                    'default_color': 'wx.BLACK',
                    'oob_color': 'wx.RED'})
        return dts

##    def hideDesignTime(self):
##        return TextCtrlDTC.hideDesignTime(self) + ['Bounds', 'InsertionPoint']

    def events(self):
        return TextCtrlDTC.events(self) + ['IntCtrlEvent']

    def writeImports(self):
        return 'import wx.lib.intctrl'


#-------------------------------------------------------------------------------

import wx.lib.stattext
import wx.lib.masked.textctrl
import wx.lib.masked.ipaddrctrl
import wx.lib.masked.combobox
import wx.lib.masked.numctrl
import wx.lib.masked.timectrl
import wx.lib.intctrl

import Plugins

Plugins.registerPalettePage('wxPython.lib', 'wxPython.lib')

Plugins.registerComponents('wxPython.lib',
      (wx.lib.stattext.GenStaticText, 'wx.lib.stattext.GenStaticText', GenStaticTextDTC),
      (wx.lib.masked.textctrl.TextCtrl, 'wx.lib.masked.textctrl.TextCtrl', MaskedTextCtrlDTC),
      (wx.lib.masked.ipaddrctrl.IpAddrCtrl, 'wx.lib.masked.ipaddrctrl.IpAddrCtrl', IpAddrCtrlDTC),
      (wx.lib.masked.combobox.ComboBox, 'wx.lib.masked.combobox.ComboBox', MaskedComboBoxDTC),
      (wx.lib.masked.numctrl.NumCtrl, 'wx.lib.masked.numctrl.NumCtrl', MaskedNumCtrlDTC),
      (wx.lib.masked.timectrl.TimeCtrl, 'wx.lib.masked.timectrl.TimeCtrl', TimeCtrlDTC),
      (wx.lib.intctrl.IntCtrl, 'wx.lib.intctrl.IntCtrl', IntCtrlDTC),
    )

EventCollections.EventCategories['MaskedNumCtrlEvent'] = ('wx.lib.masked.numctrl.EVT_MASKEDNUM',)
EventCollections.commandCategories.append('MaskedNumCtrlEvent')
EventCollections.EventCategories['TimeCtrlEvent'] = ('wx.lib.masked.timectrl.EVT_TIMEUPDATE',)
EventCollections.commandCategories.append('TimeCtrlEvent')
EventCollections.EventCategories['IntCtrlEvent'] = ('wx.lib.intctrl.EVT_INT',)
EventCollections.commandCategories.append('IntCtrlEvent')
