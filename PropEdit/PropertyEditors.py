#----------------------------------------------------------------------
# Name:        PropertyEditors.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2002 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
"""
    Property editors provide a design time interface for the inspector to
    examine and manipulate properties of controls.

    Some properties are live and also update the design time control,
    others only update the source and changes may only be seen when the
    frame is reloaded or the control is recreated.
"""

print 'importing PropertyEditors'

# XXX Value getting setting of value between internal and sometime control value
# XXX Is still too fuzzy

from types import *
import os

from wxPython.wx import *
#from wxPython.utils import *

from InspectorEditorControls import *

import Utils
from Enumerations import reverseDict

class EditorStyles:pass
class esExpandable(EditorStyles):pass
class esDialog(EditorStyles):pass
class esReadOnly(EditorStyles):pass
class esRecreateProp(EditorStyles):pass

class PropertyRegistry:
    """ Factory to return propery editors from recognisable types
        It does not return property editors for certain design-time types like
        sets, enumerations, booleans, etc.
    """

    def __init__(self):
        self.classRegistry = {}
        self.typeRegistry = {}#{type(None): None}

    def registerClasses(self, propClass, propEditors):
        for propEdit in propEditors:
            self.classRegistry[propClass.__name__] = propEdit

    def registerTypes(self, propType, propEditors):
        for propEdit in propEditors:
            self.typeRegistry[propType] = propEdit

    def factory(self, name, parent, companion, rootCompanion, propWrapper, idx, width):
        try:
            propWrapper.connect(companion.control, companion)
            value = propWrapper.getValue()
        except Exception, message:
            print 'Error on accessing Getter for', name, ':', message
            value = None

        if type(value) == InstanceType:
            if self.classRegistry.has_key(value.__class__.__name__):
                return self.classRegistry[value.__class__.__name__](name,
                  parent, companion, rootCompanion, propWrapper, idx, width)
            else:
                pass
##                print 'e:class', value, value.__class__.__name__, 'for', name, 'not supported'
        else:
            if type(value) == type(None):
                return None
            elif self.typeRegistry.has_key(type(value)):
                return self.typeRegistry[type(value)](name, parent, companion,
                  rootCompanion, propWrapper, idx, width)
            else:
                pass
##                print 'e:type', value, type(value), 'for', name, 'not supported'


# XXX Check IEC initialisation not from Display value but from 'valueFromIEC'
class PropertyEditor:
    """ Class associated with a design time identified type,
        it manages the behaviour of a NameValue in the Inspector
    """

    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width, _1=None , _2=None):
        self.name = name
        self.parent = parent

        self.idx = idx
        self.width = width
        self.editorCtrl = None
        self.companion = companion
        self.obj = companion.control
        self.propWrapper = propWrapper
        self.propWrapper.connect(self.obj, self.companion)
        self.rootCompanion = rootCompanion
        self.root = rootCompanion.control
        self.style = []
        self.ownerPropEdit = None
        self.expanded = false
        self.initFromComponent()

    def initFromComponent(self):
        self.value = self.propWrapper.getValue()
        if self.editorCtrl:
            self.editorCtrl.setValue(self.valueToIECValue())

    def edit(self):
        pass

    def inspectorEdit(self):
        """ Start a property editing operation and opens the inplace editor """
        pass

    def refreshCompCtrl(self):
        if self.obj and hasattr(self.obj, 'Refresh'):
            self.obj.Refresh()

    def validateProp(self, oldVal, newVal):
        pass

    def inspectorPost(self, closeEditor = true):
        """ Post inspector editor control, update ctrl and persist value """
        if self.editorCtrl:
            v = self.getValue()
            cv = self.getCtrlValue()
            # Only post changes
            if `v` != `cv`:
                self.validateProp(v, cv)
                self.setCtrlValue(cv, v)
                self.refreshCompCtrl()
                self.persistValue(self.valueAsExpr())
                # When sub properties post, update their main properies
                if self.ownerPropEdit:
                    self.companion.updateOwnerFromObj()
                    self.ownerPropEdit.initFromComponent()

                    # XXX Font's want new objects assigned to them before
                    # XXX they update
                    if esRecreateProp in self.ownerPropEdit.getStyle():
                        v = eval(self.ownerPropEdit.valueAsExpr())
                        self.ownerPropEdit.setCtrlValue(v, v)

                    self.ownerPropEdit.persistValue(self.ownerPropEdit.valueAsExpr())
                    self.ownerPropEdit.refreshCompCtrl()

                if self.name in self.companion.mutualDepProps:
                    for prop in self.companion.mutualDepProps:
                        if prop != self.name:
                            insp = self.companion.designer.inspector
                            insp.constructorUpdate(prop)
                            insp.propertyUpdate(prop)

            if closeEditor and self.editorCtrl:
                self.editorCtrl.destroyControl()
                self.editorCtrl = None


    def inspectorCancel(self):
        """ Cancel a property editor operation """
        if self.editorCtrl:
            self.editorCtrl.destroyControl()
            self.editorCtrl = None

    def getStyle(self):
        return self.style

    def getValue(self):
        """ Returns and initialises value for prop editor.

        If in edit mode, value should be read from the editor control

        Override if needed.
        """
        if self.editorCtrl:
            self.value = self.editorCtrl.getValue()
        return self.value

    def setValue(self, value):
        """ Initialise the prop editor and if needed the editor control """
        self.value = value
        if self.editorCtrl:
            self.editorCtrl.setValue(self.valueToIECValue())

    def getCtrlValue(self):
        """ Read current prop value from designed object """
        return self.propWrapper.getValue()

    def setCtrlValue(self, oldValue, value):
        """ Update designed object with current prop """
        # If overridden, rem to call check triggers if not calling parent method
        self.companion.checkTriggers(self.name, oldValue, value)
        self.propWrapper.setValue(value)

    def persistValue(self, value):
        funcName = self.propWrapper.getSetterName()
        self.companion.persistProp(self.name, funcName, value)

    def getDisplayValue(self):
        """ Value that should display when the prop editor is not in edit mode """
        return `self.value`

    def valueAsExpr(self):
        """ Return value as evaluatable source """
        return self.getDisplayValue()

    def getValues(self):
        """ Return list of options """
        return self.values

    def setValues(self, values):
        """ Sets list of options """
        self.values = values

    def valueToIECValue(self):
        """ Return prop value in the form that the form that the editor control expects """
        return self.value

    def setValueFromIECValue(self, value):
        """ Set value from the format that the editor control produces """
        self.value = value

    def setWidth(self, width):
        self.width = width
        if self.editorCtrl:
            self.editorCtrl.setWidth(width)

    def setIdx(self, idx):
        self.idx = idx
        if self.editorCtrl:
            self.editorCtrl.setIdx(idx)

class FactoryPropEdit(PropertyEditor):
    pass

class LockedPropEdit(PropertyEditor):
    def getDisplayValue(self):
        return str(self.value)

#-------------------------------------------------------------------------------

class ConfPropEdit(PropertyEditor):
    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx,
          width, options, names):
        PropertyEditor.__init__(self, name, parent, companion, rootCompanion,
          propWrapper, idx, width)
        self.setValues(names)

    def getDisplayValue(self):
        return str(self.value)

    def initFromComponent(self):
        self.value = self.getCtrlValue()

    def persistValue(self, value):
        pass

class ContainerConfPropEdit(ConfPropEdit):
    def getStyle(self):
        return [esExpandable]
    def inspectorEdit(self):
        self.editorCtrl = BevelIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width)

class StrConfPropEdit(ConfPropEdit):
    def valueToIECValue(self):
        return self.value
#        return eval(self.value)

    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx,
          self.width)

    def getValue(self):
        if self.editorCtrl:
            try:
                self.value = self.editorCtrl.getValue()
            except Exception, message:
                self.value = self.getCtrlValue()
                print 'invalid constr prop value', message
        else:
            self.value = self.getCtrlValue()
        return self.value

class PasswdStrConfPropEdit(StrConfPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx,
          self.width, style = wxTE_PASSWORD)
    def getDisplayValue(self):
        return '*'*len(self.value)

class EvalConfPropEdit(ConfPropEdit):
    def valueToIECValue(self):
        return `self.value`

    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, `self.value`)
        self.editorCtrl.createControl(self.parent, self.value, self.idx,
          self.width)

    def getValue(self):
        if self.editorCtrl:
            try:
                self.value = eval(self.editorCtrl.getValue())
            except Exception, message:
                self.value = self.getCtrlValue()
                print 'invalid constr prop value', message
        else:
            self.value = self.getCtrlValue()
        return self.value

class EnumConfPropEdit(ConfPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = ChoiceIEC(self, self.getValue())
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.value)
##
##    def getValues(self):
##        return self.names

class ColourConfPropEdit(ConfPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def edit(self, event):
        data = wxColourData()
        data.SetColour(self.companion.eval(self.value))
        data.SetChooseFull(true)
        dlg = wxColourDialog(self.parent, data)
        try:
            if dlg.ShowModal() == wxID_OK:
                col = dlg.GetColourData().GetColour()
                self.editorCtrl.value = \
                      'wxColour(%d, %d, %d)'%(col.Red(),col.Green(),col.Blue())
                self.inspectorPost(false)
        finally:
            dlg.Destroy()

class FilepathConfPropEdit(ConfPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def edit(self, event):
        from FileDlg import wxFileDialog
        dlg = wxFileDialog(self.parent, 'Choose the file', '.', '', 'AllFiles', wxSAVE)
        try:
            if dlg.ShowModal() == wxID_OK:
                self.editorCtrl.value = `dlg.GetFilePath()`
                self.inspectorPost(false)
            else:
                if wxMessageBox('Clear the current property value?',
                      'Clear filepath?', style=wxICON_QUESTION | wxYES_NO) == wxYES:
                    self.editorCtrl.value = "''"
                    self.inspectorPost(false)
        finally:
            dlg.Destroy()

class DirpathConfPropEdit(ConfPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def edit(self, event):
        dlg = wxDirDialog(self.parent, defaultPath=self.editorCtrl.value)
        try:
            if dlg.ShowModal() == wxID_OK:
                self.editorCtrl.value = `dlg.GetPath()`
                self.inspectorPost(false)
            else:
                if wxMessageBox('Clear the current property value?',
                      'Clear dirpath?', style=wxICON_QUESTION | wxYES_NO) == wxYES:
                    self.editorCtrl.value = "''"
                    self.inspectorPost(false)
        finally:
            dlg.Destroy()

class BoolConfPropEdit(ConfPropEdit):
    truths = ['on', 'true', '1']
    def getDisplayValue(self):
        return self.valueToIECValue()

    def valueToIECValue(self):
        return self.value in self.truths and 'true' or 'false'

    def inspectorEdit(self):
        self.editorCtrl = CheckBoxIEC(self, self.value in self.truths)
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.value)

#-------------------------------------------------------------------------------

class OptionedPropEdit(PropertyEditor):
    """ Property editors initialised with options """
    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width, options, names):
        PropertyEditor.__init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width)
        self.options = options
        self.names = names
        if names:
            self.revNames = reverseDict(names)
        else:
            self.revNames = None

class ConstrPropEditFacade:
    def initFromComponent(self):
        self.value = ''
    def getCtrlValue(self):
        return ''
    def getValue(self):
        return ''
    def setValue(self, value):
        self.value = value

class ConstrPropEdit(ConstrPropEditFacade, PropertyEditor):
    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx,
      width, options, names):
        PropertyEditor.__init__(self, name, parent, companion, rootCompanion,
          propWrapper, idx, width)
    def initFromComponent(self):
        self.value = self.getValue()
    def valueToIECValue(self):
        return self.value
    def getDisplayValue(self):
        return self.getValue()
    def getCtrlValue(self):
        return self.companion.textConstr.params[ \
          self.companion.constructor()[self.name]]
    def setCtrlValue(self, oldValue, value):
        self.companion.checkTriggers(self.name, oldValue, value)
        if hasattr(self.companion, 'index'):
            self.propWrapper.setValue(self.companion.eval(value), self.companion.index)
        else:
            self.propWrapper.setValue(value)

# Collection id name
class ItemIdConstrPropEdit(ConstrPropEdit):
    def inspectorEdit(self):
        val = self.valueToIECValue()
        self.editorCtrl = TextCtrlIEC(self, val)
        self.editorCtrl.createControl(self.parent, val, self.idx, self.width)

    def valueToIECValue(self):
        return self.getDisplayValue()

    def getDisplayValue(self):
        base = self.companion.newWinId('')
        return self.getValue()[len(base):]

    def fixupName(self, name):
        newname = []
        for c in name:
            if c == ' ': c = '_'
            if c in string.digits + string.letters + '_':
                newname.append(c)

        return string.upper(string.join(newname, ''))

    def getValue(self):
        if self.editorCtrl and self.editorCtrl.getValue():
            base = self.companion.newWinId('')
            self.value = base + self.fixupName(self.editorCtrl.getValue())
        else:
            self.value = self.getCtrlValue()
        return self.value

    def valueAsExpr(self):
        return self.getValue()

    def setCtrlValue(self, oldValue, value):
        self.companion.checkTriggers(self.name, oldValue, value)
        self.propWrapper.setValue(value, self.companion.index)

class IntConstrPropEdit(ConstrPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx,
          self.width)

    def getValue(self):
        if self.editorCtrl and self.editorCtrl.getValue():
            try:
                anInt = eval(self.editorCtrl.getValue())
                if type(anInt) is IntType:
                    self.value = self.editorCtrl.getValue()
                else:
                    self.value = self.getCtrlValue()
            except Exception, message:
                self.value = self.getCtrlValue()
                #print 'invalid constr prop value', message, self.editorCtrl.getValue()
        else:
            self.value = self.getCtrlValue()
        return self.value

class SBFWidthConstrPropEdit(IntConstrPropEdit):
    def getCtrlValue(self):
        return self.companion.GetWidth()

    def setCtrlValue(self, oldValue, value):
        self.companion.SetWidth(value)

    def persistValue(self, value):
        pass

class ClassLinkConstrPropEdit(IntConstrPropEdit): pass

class BitmapPropEditMix:
    extTypeMap = {'.bmp': 'wxBITMAP_TYPE_BMP',
                  '.gif': 'wxBITMAP_TYPE_GIF',
                  '.jpg': 'wxBITMAP_TYPE_JPEG',
                  '.png': 'wxBITMAP_TYPE_PNG'}
    def showImgDlg(self, dir, name):
        if not os.path.isdir(dir):
            wxMessageBox('The given directory is invalid, using current directory.\n(%s)'%dir,
                  'Warning', wxOK | wxICON_EXCLAMATION)
            dir = '.'

        from FileDlg import wxFileDialog
        dlg = wxFileDialog(self.parent, 'Choose an image', dir, name,
              'ImageFiles', wxOPEN)
        try:
            if dlg.ShowModal() == wxID_OK:
                pth = abspth = string.replace(dlg.GetFilePath(), '\\', '/')
                if not Preferences.cgAbsoluteImagePaths:
                    pth = Utils.pathRelativeToModel(pth, self.companion.designer.model)
                return abspth, pth, self.extTypeMap[string.lower(os.path.splitext(pth)[-1])]
            else:
                return '', '', ''
        finally:
            dlg.Destroy()

    def extractPathFromSrc(self, src):
        if src and Utils.startswith(src, 'wxBitmap('):
            filename = src[len('wxBitmap(')+1:]
            pth = filename[:string.rfind(filename, ',')-1]
            if not os.path.isabs(pth):
                mbd = Utils.getModelBaseDir(self.companion.designer.model)
                if mbd: mbd = mbd[7:]
                pth = string.replace(os.path.normpath(os.path.join(mbd, pth)), '\\', '/')
            dir, name = os.path.split(pth)
            if not dir: dir = '.'
            return pth, dir, name
        return '', '.', ''


class BitmapConstrPropEdit(IntConstrPropEdit, BitmapPropEditMix):
    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def edit(self, event):
        dummy, dir, name = self.extractPathFromSrc(self.value)
        abspth, pth, tpe = self.showImgDlg(dir, name)
        if abspth:
            self.value = 'wxBitmap(%s, %s)'%(`pth`, tpe)
            #v = self.getValue()
            #cv = self.getCtrlValue()
            #self.setCtrlValue(cv, v)
            self.persistValue(self.value)
            # manually update ctrl
            self.propWrapper.setValue(wxBitmap(abspth, getattr(wx, tpe)),
                  self.companion.index)
            self.refreshCompCtrl()

    def getValue(self):
        if self.editorCtrl:
            return self.value
        else:
            return self.getCtrlValue()


class EnumConstrPropEdit(IntConstrPropEdit):
    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width, options, names):
        IntConstrPropEdit.__init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width, options, names)
        self.names = names
    def valueToIECValue(self):
        return self.getValue()
    def inspectorEdit(self):
        self.editorCtrl = ChoiceIEC(self, self.getValue())
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.getValue())
    def getDisplayValue(self):
        return self.valueToIECValue()
    def getValues(self):
        return self.names

class ClassConstrPropEdit(ConstrPropEdit):
    def inspectorEdit(self):
        val = self.getValue()
        if self.companion.designer.model.customClasses.has_key(self.value):
            self.editorCtrl = ChoiceIEC(self, val)
            self.editorCtrl.createControl(self.parent, self.idx, self.width)
            self.editorCtrl.setValue(val)
        else:
            self.editorCtrl = BeveledLabelIEC(self, val)
            self.editorCtrl.createControl(self.parent, self.idx, self.width)

    def setCtrlValue(self, oldValue, value):
        #self.companion.checkTriggers(self.name, oldValue, value)
        self.propWrapper.setValue(value)
    def getCtrlValue(self):
        return self.propWrapper.getValue()

    def getValue(self):
        if self.editorCtrl:
            self.value = self.editorCtrl.getValue()
        else:
            self.value = self.getCtrlValue()
        return self.value

    def getValues(self):
        custClss = self.companion.designer.model.customClasses
        MyCls = custClss[self.value]
        vals = []
        for name, Cls in custClss.items():
            if MyCls == Cls:
                vals.append(name)
        vals.remove(MyCls.__name__)
        vals.insert(0, MyCls.__name__)
        return vals




##    def getDisplayValue(self):
##        dv = EnumConstrPropEdit.getDisplayValue(self)
##        print dv
##        return dv

class BoolConstrPropEdit(EnumConstrPropEdit):
    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width, options, names):
        EnumConstrPropEdit.__init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width, options, ['true', 'false'])

    def inspectorEdit(self):
        self.editorCtrl = CheckBoxIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.value)

class LCCEdgeConstrPropEdit(EnumConstrPropEdit):
    def getCtrlValue(self):
        return self.companion.GetEdge()

    def getValue(self):
        if self.editorCtrl:
            try:
                # Sad to admit, a hack; don't use combo value if it's None
                if self.editorCtrl.getValue():
                    self.value = self.editorCtrl.getValue()
                else:
                    self.value = self.getCtrlValue()
            except Exception, message:
                self.value = self.getCtrlValue()
        else:
            self.value = self.getCtrlValue()
        return self.value

    def setCtrlValue(self, oldValue, value):
        self.companion.SetEdge(value)

    def persistValue(self, value):
        pass

    def getValues(self):
        objName = self.companion.__class__.sourceObjName
        return [self.getCtrlValue()] + \
          map(lambda a, objName=objName: '%s.%s'%(objName, a),
          self.companion.availableItems())

class ObjEnumConstrPropEdit(EnumConstrPropEdit):
    def getValue(self):
        if self.editorCtrl:
            try:
                # Sad to say, a hack; don't use combo value if it's None
                if self.editorCtrl.getValue():
                    self.value = self.editorCtrl.getValue()
                else:
                    self.value = self.getCtrlValue()
            except Exception, message:
                self.value = self.getCtrlValue()
        else:
            self.value = self.getCtrlValue()
        return self.value

    def persistValue(self, value):
        pass

    def getObjects(self):
        return self.companion.designer.getAllObjects().keys()

    def getValues(self):
        vals = self.getObjects()
        try:
            val = self.getValue()
            if val == 'self': vals.remove('self')
            else: vals.remove('self.'+val)
        except: pass
        return vals

class WinEnumConstrPropEdit(ObjEnumConstrPropEdit):
    def setCtrlValue(self, oldValue, value):
        self.companion.SetOtherWin(value)
    def getCtrlValue(self):
        return self.companion.GetOtherWin()
    def getValues(self):
        return ['None'] + ObjEnumConstrPropEdit.getValues(self)

class MenuEnumConstrPropEdit(ObjEnumConstrPropEdit):
    def getValues(self):
        return ['wxMenu()'] + ObjEnumConstrPropEdit.getValues(self)
    def getObjects(self):
        return self.companion.designer.getObjectsOfClass(wxMenu).keys()
    def setCtrlValue(self, oldValue, value):
        self.companion.SetMenu(value)
    def getCtrlValue(self):
        return self.companion.GetMenu()

class SizerEnumConstrPropEdit(ObjEnumConstrPropEdit):
##    def getValues(self):
##        return ['wxMenu()'] + ObjEnumConstrPropEdit.getValues(self)
    def getObjects(self):
        return self.companion.designer.getObjectsOfClass(wxBoxSizer).keys()
##    def setCtrlValue(self, oldValue, value):
##        self.companion.SetMenu(value)
##    def getCtrlValue(self):
##        return self.companion.GetMenu()


class BaseFlagsConstrPropEdit(IntConstrPropEdit):
    def getStyle(self):
        return [esExpandable]

    def getValue(self):
        """ For efficiency override the entire getValue"""
        if self.editorCtrl:
            try:
                anInt = eval(self.editorCtrl.getValue())
                if type(anInt) is IntType:
                    self.value = string.join(map(string.strip,
                        string.split(self.editorCtrl.getValue(), '|')), ' | ')
                else:
                    self.value = self.getCtrlValue()
            except Exception, message:
                self.value = self.getCtrlValue()
                print 'invalid constr prop value', message
        else:
            self.value = self.getCtrlValue()
        return self.value

class StyleConstrPropEdit(BaseFlagsConstrPropEdit):
    def getSubCompanion(self):
        from Companions.Companions import WindowStyleDTC
        return WindowStyleDTC

class FlagsConstrPropEdit(BaseFlagsConstrPropEdit):
    def getSubCompanion(self):
        from Companions.Companions import FlagsDTC
        return FlagsDTC

class StrConstrPropEdit(ConstrPropEdit):
    def valueToIECValue(self):
        return eval(self.value)

    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx,
          self.width)

    def getValue(self):
        if self.editorCtrl:
            try:
                aStr = self.editorCtrl.getValue()
                if type(aStr) is StringType:
                    self.value = `aStr`
                else:
                    self.value = self.getCtrlValue()
            except Exception, message:
                self.value = self.getCtrlValue()
                print 'invalid constr prop value', message
        else:
            self.value = self.getCtrlValue()
        return self.value

# XXX Check for name conflicts
class NameConstrPropEdit(StrConstrPropEdit):
    def getValue(self):
        if self.editorCtrl:
            value = self.editorCtrl.getValue()
            if type(value) is StringType:
                value = `self.editorCtrl.getValue()`
            else:
                value = self.getCtrlValue()

            if value != self.value:
                if not value[1:-1]:
                    message = 'Invalid name for Python object'
                    wxLogError(message)
                    return self.value

                for c in value[1:-1]:
                    if c not in string.letters+string.digits+'_':#"\'':
                        message = 'Invalid name for Python object'
                        wxLogError(message)
                        return self.value
                        #raise message

                if self.companion.designer.objects.has_key(value):
                    wxLogError('Name already used by another control.')
                    return self.value
                    #raise 'Name already used by another control.'
            self.value = value
        else:
            self.value = self.getCtrlValue()
        return self.value


    def getCtrlValue(self):
        return `self.companion.name`

    def setCtrlValue(self, oldValue, newValue):
        self.companion.checkTriggers(self.name, eval(oldValue), eval(newValue))
#        self.companion.name = eval(newValue)

    def persistValue(self, value):
        pass

class ChoicesConstrPropEdit(ConstrPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx,
          self.width)

    def getValue(self):
        if self.editorCtrl:
            try:
                aList = eval(self.editorCtrl.getValue())
                if type(aList) is ListType:
                    self.value = self.editorCtrl.getValue()
                else:
                    self.value = self.getCtrlValue()
            except Exception, message:
                self.value = self.getCtrlValue()
                print 'invalid constr prop value', message
        else:
            self.value = self.getCtrlValue()
        return self.value

class MajorDimensionConstrPropEdit(ConstrPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx,
          self.width)

    def getValue(self):
        if self.editorCtrl:
            try:
                anInt = eval(self.editorCtrl.getValue())
                if type(anInt) is IntType:
                    self.value = self.editorCtrl.getValue()
                else:
                    self.value = self.getCtrlValue()
            except Exception, message:
                self.value = self.getCtrlValue()
                print 'invalid constr prop value', message
        else:
            self.value = self.getCtrlValue()
        return self.value

class EventPropEdit(OptionedPropEdit):
    """ Property editor to handle design time definition of events """
    def initFromComponent(self):
        # unlike other propedit getter setters these are methods not funcs
        self.value = self.propWrapper.getValue(self.name)
    def valueToIECValue(self):
        v = self.value
        return v

    def inspectorEdit(self):
        self.editorCtrl = ChoiceIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.value)

    def setCtrlValue(self, oldValue, value):
##        self.companion.checkTriggers(self.name, oldValue, value)

        self.propWrapper.setValue(value, self.name)

    def getDisplayValue(self):
        return self.valueToIECValue()

    extraOpts = ['(delete)', '(rename)']
    scopeOpts = {'(show all)': 'all',
                 '(show own)': 'own'}
    def getValues(self):
        """ Build event list based on currently selected scope for the event """
        # XXX Should ideally do this one day:
        # XXX   Show event's of similar types, e.g. mouse events, cmd events.
        # XXX   Also show events from the code not bound to the frame
        vals = []
        showScope = 'own'
        if self.companion:
            for evt in self.companion.textEventList:
                if evt.event_name == self.name:
                    showScope = evt.show_scope

                if evt.trigger_meth not in self.extraOpts:
                    try: vals.index(evt.trigger_meth)
                    except ValueError: vals.append(evt.trigger_meth)

            if showScope != 'own':
                # Add evts from other scopes
                # XXX Collection items' events aren't handled correctly
                # XXX designer != CollEditorView
                for comp, ctrl, prnt in self.companion.designer.objects.values():
                    if comp != self.companion and showScope == 'all':
                        #or  showScope == 'same' and comp.__class__ == self.companion.__class__):
                        for evt in comp.textEventList:
                            if evt.trigger_meth not in self.extraOpts:
                                try: vals.index(evt.trigger_meth)
                                except ValueError: vals.append(evt.trigger_meth)

        scopeChoices = self.scopeOpts.keys()
        del scopeChoices[self.scopeOpts.values().index(showScope)]

        vals.extend(self.extraOpts + scopeChoices)
        return vals

    def _repopulateChoice(self, value):
        self.editorCtrl.repopulate()
        self.editorCtrl.setValue(value)

    def getValue(self):
        """ Return current value, or if a special (*) value is selected,
            process it, and return previous 'current value' """
        if self.editorCtrl:
            oldVal = defVal = self.value
            value = self.editorCtrl.getValue()
            # Event rename
            if value == '(rename)':
                if oldVal == '(delete)':
                    for evt in self.companion.textEventList:
                        if evt.trigger_meth == oldVal:
                            defVal = evt.prev_trigger_meth
                            break

                ted = wxTextEntryDialog(self.parent, 'Enter a new method name:',
                      'Rename event method', defVal)
                try:
                    if ted.ShowModal() == wxID_OK:
                        self.value = ted.GetValue()

                        # XXX All references should be renamed !!!!
                        # XXX Add as method on designer
                        for evt in self.companion.textEventList:
                            if evt.trigger_meth == oldVal:
                                if not evt.prev_trigger_meth:
                                    evt.prev_trigger_meth = oldVal
                                evt.trigger_meth = self.value
                                break
                        self._repopulateChoice(self.value)
                finally:
                    ted.Destroy()
            # Event deletion
            elif value == '(delete)':
                for evt in self.companion.textEventList:
                    if evt.trigger_meth == oldVal:
                        if not evt.prev_trigger_meth:
                            evt.prev_trigger_meth = oldVal
                        break
                self.value = self.editorCtrl.getValue()
            # Event scope change
            elif value in self.scopeOpts.keys():
                self.value = oldVal
                for evt in self.companion.textEventList:
                    if evt.event_name == self.name:
                        evt.show_scope = self.scopeOpts[value]
                        self._repopulateChoice(oldVal)
                        break
            # Normal event selection
            else:
                self.value = self.editorCtrl.getValue()

        return self.value

    def persistValue(self, value):
        self.companion.persistEvt(self.name, value)

class BITPropEditor(FactoryPropEdit):
    """ Editors for Built-in Python Types """
    def valueToIECValue(self):
        return `self.value`
    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx, self.width)
    def getValue(self):
        if self.editorCtrl:
            try:
                value = eval(self.editorCtrl.getValue())
            except Exception, mess:
                wxLogError('Invalid value: %s' % str(mess))
                raise
            self.value = value
        return self.value

class IntPropEdit(BITPropEditor):
    pass

class StrPropEdit(BITPropEditor):
    def valueToIECValue(self):
        return self.value
    def getValue(self):
        return FactoryPropEdit.getValue(self)

# The following is a work in progress for having a string editor dlg that
# also handles gettext formatted strings
#
# The current problem is that for normal string properties, the property
# refers to a string object, not to the source reference, iow _() is not a string
##    def inspectorEdit(self):
##        self.editorCtrl = TextCtrlButtonIEC(self, self.value)
##        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)
##    def edit(self, event):
##        import StringPropEditorDlg
##        dlg = StringPropEditorDlg.create(self.parent, repr(self.value))
##        try:
##            if dlg.ShowModal() == wxID_OK:
##                self.inspectorPost(false)
##                pass
##        finally:
##            dlg.Destroy()


class NamePropEdit(StrPropEdit):
    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width, options, names):
        StrPropEdit.__init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width)

    identifier = string.letters+string.digits+'_'

    def getValue(self):
        # XXX Currently returning the old value in case of error because
        # XXX an exception here cannot be gracefully handled yet.
        # XXX Specifically closing the frame with the focus on the
        if self.editorCtrl:
            value = self.editorCtrl.getValue()
            if value != self.value:
                if self.companion.designer.objects.has_key(value):
                    wxLogError('Name already used by another control.')
                    return self.value

                if not value:
                    message = 'Invalid name for Python object'
                    wxLogError(message)
                    return self.value

                for c in value:
                    if c not in self.identifier:
                        message = 'Invalid name for Python object'
                        wxLogError(message)
                        return self.value
            self.value = value
        return self.value

class TuplePropEdit(BITPropEditor):
    pass

class BoolPropEdit(OptionedPropEdit):
    def valueToIECValue(self):
        v = self.value
        if type(v) == IntType:
            return self.getValues()[v]
        else: return `v`
    def inspectorEdit(self):
        self.editorCtrl = CheckBoxIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.getValues()[self.value])
    def getDisplayValue(self):
        return self.valueToIECValue()
    def getValues(self):
        return ['false', 'true']
    def getValue(self):
        if self.editorCtrl:
            # trick to convert boolean string to integer
            v = self.editorCtrl.getValue()
            self.value = self.getValues().index(self.editorCtrl.getValue())
        return self.value

class EnumPropEdit(OptionedPropEdit):
    def valueToIECValue(self):
        if self.revNames:
            try:
                return self.revNames[self.value]
            except KeyError:
                return `self.value`

        else: OptionedPropEdit.getDisplayValue(self)
    def inspectorEdit(self):
        self.editorCtrl = ChoiceIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.setValue(self.value)
    def getDisplayValue(self):
        return self.valueToIECValue()
    def getValues(self):
        vals = self.names.keys()
        try:
            name = self.revNames[self.value]
        except KeyError:
            name = `self.value`
        if name not in vals:
            vals.append(name)
        return vals
    def setValue(self, value):
        self.value = value
        if self.editorCtrl:
            try:
                self.editorCtrl.setValue(self.revNames[value])
            except KeyError:
                self.editorCtrl.setValue(`value`)
    def getValue(self):
        if self.editorCtrl:
            strVal = self.editorCtrl.getValue()
            try:
                self.value = self.names[strVal]
            except KeyError:
                self.value = eval(strVal)

        return self.value
# SetPropEdit

# Property editors for classes
class ClassPropEdit(FactoryPropEdit):
    def getDisplayValue(self):
        return '('+self.value.__class__.__name__+')'
    def getStyle(self):
        return [esExpandable]

class ClassLinkPropEdit(OptionedPropEdit):
    defaults = {'None': None}
    linkClass = None
    def getStyle(self):
        return []
    def valueToIECValue(self):
        for k, v in self.defaults.items():
            if self.value == v:
                return k

        objs = self.companion.designer.getObjectsOfClass(self.linkClass)
        for objName in objs.keys():
            if `objs[objName]` == `self.value`:
                return objName
        # Ok lets try again ;\
##        if hasattr(self.value, 'GetId'):
##            for objName in objs.keys():
##                if objs[objName].GetId() == self.value.GetId():
##                    return objName
        #print 'ClassLinkPropEdit: ', self.value, 'not found'
        return `None`
    def inspectorEdit(self):
        self.editorCtrl = ChoiceIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.setValue(self.value)
    def getDisplayValue(self):
        return self.valueToIECValue()
    def getValues(self):
        defs = self.defaults.keys()
        defs.sort()
        return defs + self.companion.designer.getObjectsOfClass(self.linkClass).keys()
    def setValue(self, value):
        self.value = value
        if self.editorCtrl:
            self.editorCtrl.setValue(self.valueToIECValue())
    def getValue(self):
        if self.editorCtrl:
            strVal = self.editorCtrl.getValue()
            if self.defaults.has_key(strVal):
                self.value = self.defaults[strVal]
            else:
                objs = self.companion.designer.getObjectsOfClass(self.linkClass)
                self.value = objs[strVal]

        return self.value

class WindowClassLinkPropEdit(ClassLinkPropEdit):
    linkClass = wxWindowPtr

class WindowClassLinkWithParentPropEdit(WindowClassLinkPropEdit):
    linkClass = wxWindowPtr
    def getValues(self):
        return ['None'] + self.companion.designer.getObjectsOfClassWithParent(self.linkClass, self.companion.name).keys()

class StatusBarClassLinkPropEdit(ClassLinkPropEdit):
    linkClass = wxStatusBar

class ToolBarClassLinkPropEdit(ClassLinkPropEdit):
    linkClass = wxToolBar

class MenuBarClassLinkPropEdit(ClassLinkPropEdit):
    linkClass = wxMenuBar

class ImageListClassLinkPropEdit(ClassLinkPropEdit):
    linkClass = wxImageList

class SizerClassLinkPropEdit(ClassLinkPropEdit):
    linkClass = wxBoxSizer

class ButtonClassLinkPropEdit(ClassLinkPropEdit):
    linkClass = wxButton

class CursorClassLinkPropEdit(ClassLinkPropEdit):
    defaults = {'None': wxNullCursor, 'wxSTANDARD_CURSOR': wxSTANDARD_CURSOR,
                'wxHOURGLASS_CURSOR': wxHOURGLASS_CURSOR,
                'wxCROSS_CURSOR': wxCROSS_CURSOR}
    linkClass = wxCursorPtr
##    def getValues(self):
##        vals = ClassLinkPropEdit.getValues(self)
##        return vals + ['wxSTANDARD_CURSOR', 'wxHOURGLASS_CURSOR', 'wxCROSS_CURSOR']

class ListCtrlImageListClassLinkPropEdit(ImageListClassLinkPropEdit):
    listTypeMap = {wxIMAGE_LIST_SMALL : 'wxIMAGE_LIST_SMALL',
                   wxIMAGE_LIST_NORMAL: 'wxIMAGE_LIST_NORMAL'}
    def valueToIECValue(self):
        if self.value[0] is None: return `None`
        objs = self.companion.designer.getObjectsOfClass(self.linkClass)
        for objName in objs.keys():
            if `objs[objName]` == `self.value[0]`:
                return objName
        print 'ClassLinkPropEdit: ', self.value[0], 'not found'
        return `None`

    def inspectorEdit(self):
        self.editorCtrl = ChoiceIEC(self, self.valueToIECValue())
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.valueToIECValue())
#        self.setValue(self.value[0])

    def getValue(self):
        if self.editorCtrl:
            strVal = self.editorCtrl.getValue()
            if strVal == `None`:
                self.value = (None, self.value[1])
            else:
                objs = self.companion.designer.getObjectsOfClass(self.linkClass)
                self.value = (objs[strVal], self.value[1])
        return self.value

    def valueAsExpr(self):
        return '%s, %s'%(self.valueToIECValue(), self.listTypeMap[self.value[1]])

class ColPropEdit(ClassPropEdit):
    def getStyle(self):
        return [esExpandable]

    def getSubCompanion(self):
        from Companions.Companions import ColourDTC
        return ColourDTC

    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def edit(self, event):
        data = wxColourData()
        data.SetColour(self.value)
        data.SetChooseFull(true)
        dlg = wxColourDialog(self.parent, data)
        try:
            if dlg.ShowModal() == wxID_OK:
                self.value = dlg.GetColourData().GetColour()
                self.inspectorPost(false)
                #self.propWrapper.setValue(self.value)
                #self.obj.Refresh()
        finally:
            dlg.Destroy()

    def getValue(self):
        return self.value#wxColour(self.value.Red(), self.value.Green(), self.value.Blue())

    def valueAsExpr(self):
        return 'wxColour(%d, %d, %d)'%(self.value.Red(), self.value.Green(), self.value.Blue())

class SizePropEdit(ClassPropEdit):
    def getDisplayValue(self):
        return self.valueToIECValue()
    def valueToIECValue(self):
        return `self.value`
    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.valueToIECValue())
        self.editorCtrl.createControl(self.parent, self.valueToIECValue(), self.idx, self.width)
    def getValue(self):
        if self.editorCtrl:
            try:
                tuplePos = eval(self.editorCtrl.getValue())
            except Exception, mess:
                Utils.ShowErrorMessage(self.parent, 'Invalid value', mess)
                raise
            self.value = wxSize(tuplePos[0], tuplePos[1])
        return self.value
    def valueAsExpr(self):
        return 'wxSize(%d, %d)'%(self.value.x, self.value.y)
    def getSubCompanion(self):
        from Companions.Companions import SizeDTC
        return SizeDTC

class PosPropEdit(ClassPropEdit):
    def getDisplayValue(self):
        return self.valueToIECValue()
    def valueToIECValue(self):
        return `self.value`
    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx, self.width)
    def getValue(self):
        if self.editorCtrl:
            try:
                tuplePos = eval(self.editorCtrl.getValue())
            except Exception, mess:
                Utils.ShowErrorMessage(self.parent, 'Invalid value', mess)
                raise
            self.value = wxPoint(tuplePos[0], tuplePos[1])
        return self.value
    def valueAsExpr(self):
        return 'wxPoint(%d, %d)'%(self.value.x, self.value.y)
    def getSubCompanion(self):
        from Companions.Companions import PosDTC
        return PosDTC

class FontPropEdit(ClassPropEdit):
    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width, _1=None , _2=None):
        ClassPropEdit.__init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width)
        import Enumerations
        self.fontFamily = reverseDict(Enumerations.fontFamilyNames)
        self.fontStyle = reverseDict(Enumerations.fontStyleNames)
        self.fontWeight = reverseDict(Enumerations.fontWeightNames)

    def getStyle(self):
        return ClassPropEdit.getStyle(self) + [esDialog, esReadOnly, esRecreateProp]

    def getSubCompanion(self):
        from Companions.Companions import FontDTC
        return FontDTC

    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def getValue(self):
        return self.value

    def edit(self, event):
        data = wxFontData()
        dlg = wxFontDialog(self.parent, data)
        dlg.GetFontData().SetInitialFont(self.value)
        try:
            if dlg.ShowModal() == wxID_OK:
                self.value = dlg.GetFontData().GetChosenFont()
                self.inspectorPost(false)
        finally:
            dlg.Destroy()
    def valueAsExpr(self):
        # XXX Duplication with sub property editors
        fnt = self.value
        return 'wxFont(%d, %s, %s, %s, %s, %s)'%(\
            fnt.GetPointSize(),
            self.fontFamily[fnt.GetFamily()],
            self.fontStyle[fnt.GetStyle()],
            self.fontWeight[fnt.GetWeight()],
            fnt.GetUnderlined() and 'true' or 'false',
            `fnt.GetFaceName()`)

class AnchorPropEdit(OptionedPropEdit):
    def getStyle(self):
        return [esExpandable]

    def getSubCompanion(self):
        from Companions.Companions import AnchorsDTC
        return AnchorsDTC

    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def edit(self, event):
        if self.expanded:
            wxMessageBox('Anchors can not be reset while the property is expanded',
                  'Anchors')
        else:
            if self.companion.anchorSettings:
                message = 'Remove anchors?'
            else:
                message = 'Define default Anchors?'

            dlg = wxMessageDialog(self.parent, message,
                              'Anchors', wxYES_NO | wxICON_QUESTION)
            try:
                if dlg.ShowModal() == wxID_YES:
                    if self.companion.anchorSettings:
                        self.companion.removeAnchors()
                        self.propWrapper.setValue(self.getValue())
                    else:
                        self.companion.defaultAnchors()
                        self.inspectorPost(false)
            finally:
                dlg.Destroy()

    def getValue(self):
        return self.companion.GetAnchors(self.companion)

    def getDisplayValue(self):
        if self.companion.anchorSettings:
            l, t, r, b = self.companion.anchorSettings
            set = []
            if l: set.append('left')
            if t: set.append('top')
            if r: set.append('right')
            if b: set.append('bottom')
            return '('+string.join(set, ', ')+')'
        else:
            return 'None'

    def valueAsExpr(self):
        if self.companion.anchorSettings:
            l, t, r, b = self.companion.anchorSettings
            return 'LayoutAnchors(self.%s, %s, %s, %s, %s)'%(self.companion.name,
                l and 'true' or 'false', t and 'true' or 'false',
                r and 'true' or 'false', b and 'true' or 'false')


class BitmapPropEdit(PropertyEditor, BitmapPropEditMix):
    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width, options = None, names = None):
        PropertyEditor.__init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width)

##    def getStyle(self):
##        return ClassPropEdit.getStyle(self) + [esDialog, esReadOnly]

    def getDisplayValue(self):
        return '(wxBitmapPtr)'

    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)
        constrs = self.companion.constructor()
        if constrs.has_key(self.name):
            constr = self.companion.textConstr.params[constrs[self.name]]
        else:
            constr = self.companion.persistedPropVal(self.name, self.propWrapper.getSetterName())

        self.bmpPath, dir, name = self.extractPathFromSrc(constr)

    def edit(self, event):
        if self.bmpPath:
            dir, name = os.path.split(self.bmpPath)
        else:
            dir, name = '.', ''

        abspth, pth, tpe = self.showImgDlg(dir, name)
        if abspth:
            self.value = wxBitmap(abspth, getattr(wx, tpe))
            self.bmpPath = pth
            self.inspectorPost(false)

    def getValue(self):
        return self.value

    def valueAsExpr(self):
        if self.bmpPath:
            return 'wxBitmap(%s, %s)'%(`self.bmpPath`,
                    self.extTypeMap[string.lower(os.path.splitext(self.bmpPath)[-1])])
        else:
            return 'wxNullBitmap'

class SashVisiblePropEdit(BoolPropEdit):
    sashEdgeMap = {wxSASH_LEFT: 'wxSASH_LEFT', wxSASH_TOP: 'wxSASH_TOP',
                   wxSASH_RIGHT: 'wxSASH_RIGHT', wxSASH_BOTTOM: 'wxSASH_BOTTOM'}
    def valueToIECValue(self):
        v = self.value[1]
        if type(v) == IntType:
            return self.getValues()[v]
        else: return `v`
    def inspectorEdit(self):
        self.editorCtrl = CheckBoxIEC(self, self.value[1])
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.getValues()[self.value[1]])
##    def getDisplayValue(self):
##        return self.valueToIECValue()
##    def getValues(self):
##        return ['false', 'true']
    def getValue(self):
        if self.editorCtrl:
            # trick to convert boolean string to integer
            v = self.editorCtrl.getValue()
            self.value = (self.value[0], self.getValues().index(self.editorCtrl.getValue()))
        return self.value
    def valueAsExpr(self):
        return '%s, %s'%(self.sashEdgeMap[self.value[0]],
                         self.value[1] and 'true' or 'false')

class CollectionPropEdit(PropertyEditor):
    """ Class associated with a design time identified type,
        it manages the behaviour of a NameValue in the Inspector
    """

    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width, names, options):
        PropertyEditor.__init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width)

    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def inspectorPost(self, closeEditor = true):
        """ Code persistance taken over by companion because collection
            transactions live longer than properties
        """
        if self.editorCtrl and closeEditor:
            self.editorCtrl.destroyControl()
            self.editorCtrl = None
            self.refreshCompCtrl()

    def getDisplayValue(self):
        return '(%s)'%self.name

    def valueAsExpr(self):
        return self.getDisplayValue()

    def edit(self, event):
        self.companion.designer.showCollectionEditor(\
          self.companion.name, self.name)

class ListColumnsColPropEdit(CollectionPropEdit): pass
class AcceleratorEntriesColPropEdit(CollectionPropEdit): pass
class MenuBarColPropEdit(CollectionPropEdit): pass
class MenuColPropEdit(CollectionPropEdit): pass
class ImagesColPropEdit(CollectionPropEdit): pass
class NotebookPagesColPropEdit(CollectionPropEdit): pass

# Property editor registration

def registerEditors(reg):
    for theType, theClass, editors in registeredTypes:
        if theType == 'Type':
            reg.registerTypes(theClass, editors)
        elif theType == 'Class':
            reg.registerClasses(theClass, editors)

registeredTypes = [\
    ('Type', IntType, [IntPropEdit]),
    ('Type', StringType, [StrPropEdit]),
    ('Type', TupleType, [TuplePropEdit]),
    ('Class', wxSize, [SizePropEdit]),
    ('Class', wxSizePtr, [SizePropEdit]),
    ('Class', wxPoint, [PosPropEdit]),
    ('Class', wxPointPtr, [PosPropEdit]),
    ('Class', wxFontPtr, [FontPropEdit]),
    ('Class', wxColourPtr, [ColPropEdit]),
    ('Class', wxBitmapPtr, [BitmapPropEdit]),
    ('Class', wxValidator, [ClassLinkPropEdit]),
]

try:
    registeredTypes.append( ('Type', UnicodeType, [StrPropEdit]) )
except:
    # 1.5.2
    pass
