#----------------------------------------------------------------------
# Name:        PropertyEditors.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
"""
    Property editors provide a design time interface for the inspector to
    examine and manipulate properties of controls.

    Some properties are live and also update the design time control,
    others only update the source and changes may only be seen when the
    frame is reloaded.
"""

# XXX Value getting setting of value between internal and sometime control value
# XXX Is still too fuzzy

from wxPython.wx import *
from wxPython.utils import *
from types import *
import Utils
from Enumerations import reverseDict
from InspectorEditorControls import *
from Preferences import wxFileDialog
#import PaletteMapping

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
        self.initFromComponent()
        self.style = []
        self.ownerPropEdit = None
        self.expanded = false

    def initFromComponent(self):
        try:
            self.value = self.propWrapper.getValue()
        except Exception, message:
            print 'initFromComponent error', message
            self.value = ''
        if self.editorCtrl:
            self.editorCtrl.setValue(self.valueToIECValue())

    def edit(self):
        pass

    def inspectorEdit(self):
        pass

    def refreshCompCtrl(self):
        if self.obj and hasattr(self.obj, 'Refresh'):
            self.obj.Refresh()

    def validateProp(self, oldVal, newVal):
        pass

    def inspectorPost(self, closeEditor = true):
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

            if closeEditor and self.editorCtrl:
                self.editorCtrl.destroyControl()
                self.editorCtrl = None

    def inspectorCancel(self):
        if self.editorCtrl:
            self.editorCtrl.destroyControl()
            self.editorCtrl = None

    def getStyle(self):
        return self.style

    def getValue(self):
        if self.editorCtrl:
            self.value = self.editorCtrl.getValue()
        return self.value

    def setValue(self, value):
        self.value = value
        if self.editorCtrl:
            self.editorCtrl.SetValue(self.value)

    def getCtrlValue(self):
        return self.propWrapper.getValue()

    def setCtrlValue(self, oldValue, value):
        # If overridden, rem to call check triggers if not calling parent method
        self.companion.checkTriggers(self.name, oldValue, value)
        self.propWrapper.setValue(value)

    def persistValue(self, value):
        funcName = self.propWrapper.getSetterName()
        self.companion.persistProp(self.name, funcName, value)

    def getDisplayValue(self):
        return `self.value`

    def valueAsExpr(self):
        return self.getDisplayValue()

    def getValues(self):
        return self.values

    def setValues(self, values):
        self.values = values

    def valueToIECValue(self):
        return self.value

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


class ConfPropEdit(PropertyEditor):
    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx,
      width, options, names):
        PropertyEditor.__init__(self, name, parent, companion, rootCompanion,
          propWrapper, idx, width)
    def initFromComponent(self):
        self.value = self.getCtrlValue()
    def persistValue(self, value):
        pass

class ContainerConfPropEdit(ConfPropEdit):
    def getStyle(self):
        return [esExpandable]

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
##    def setCtrlValue(self, oldValue, value):
##        self.companion.checkTriggers(self.name, oldValue, value)
    def initFromComponent(self):
        self.value = ''
    def getCtrlValue(self):
        return ''#self.getter(self.obj)
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
        return  self.getValue()
    def setCtrlValue(self, oldValue, value):
        self.companion.checkTriggers(self.name, oldValue, value)
        if hasattr(self.companion, 'index'):
            import PaletteMapping
            self.propWrapper.setValue(PaletteMapping.evalCtrl(value), self.companion.index)
        else:
            self.propWrapper.setValue(value)
    def getCtrlValue(self):
        return self.companion.textConstr.params[ \
          self.companion.constructor()[self.name]]

class IntConstrPropEdit(ConstrPropEdit):
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

class SBFWidthConstrPropEdit(IntConstrPropEdit):
    def getCtrlValue(self):
        return self.companion.GetWidth()

    def setCtrlValue(self, oldValue, value):
        self.companion.SetWidth(value)

    def persistValue(self, value):
        pass

class ClassLinkConstrPropEdit(IntConstrPropEdit): pass

class BitmapConstrPropEdit(IntConstrPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def edit(self, event):
        dlg = wxFileDialog(self.parent, 'Choose an image', '.', '', 'Bitmaps (*.bmp)|*.bmp', wxOPEN)
        try:
            if dlg.ShowModal() == wxID_OK:
                try:
                    self.value = 'wxBitmap(%s, wxBITMAP_TYPE_BMP)'%(`dlg.GetPath()`)
                    v = self.getValue()
                    cv = self.getCtrlValue()
                    self.setCtrlValue(cv, v)
#                self.inspectorPost(false)
                # XXX Inspector post should handle this
                    self.persistValue(self.value)
                    self.propWrapper.setValue(eval(self.value), self.companion.index)
                    self.refreshCompCtrl()
                except Exception, err:
                    print 'Edit except', str(err)
        finally:
            dlg.Destroy()
        return ''

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

class BoolConstrPropEdit(EnumConstrPropEdit):
    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width, options, names):
        EnumConstrPropEdit.__init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width, options, ['true', 'false'])

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


class StyleConstrPropEdit(IntConstrPropEdit):
#class AnchorPropEdit(OptionedPropEdit):
##    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx,
##      width, options, names):
##        ClassPropEdit.__init__(self, name, parent, companion, rootCompanion,
##          propWrapper, idx, width)

    def getStyle(self):
        return [esExpandable]

    def getSubCompanion(self):
        from Companions.Companions import WindowStyleDTC
        return WindowStyleDTC

#    def inspectorEdit(self):
#        self.editorCtrl = ButtonIEC(self, self.value)
#        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

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

##    def getDisplayValue(self):

##    def valueAsExpr(self):

##    def edit(self, event):

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
                    self.value = `self.editorCtrl.getValue()`
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

    def getValues(self):
        vals = []
        if self.companion:
            for evt in self.companion.textEventList:
                if evt.trigger_meth <> '(delete)':
                    try: vals.index(evt.trigger_meth)
                    except: vals.append(evt.trigger_meth)
        vals.append('(delete)')
        return vals

    def getValue(self):
        if self.editorCtrl:
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

class TuplPropEdit(BITPropEditor):
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
    linkClass = None
    def getStyle(self):
        return []
    def valueToIECValue(self):
        if self.value is None: return `None`
        objs = self.companion.designer.getObjectsOfClass(self.linkClass)
        for objName in objs.keys():
            if `objs[objName]` == `self.value`:
                return objName
        # Ok lets try again ;\
##        if hasattr(self.value, 'GetId'):
##            for objName in objs.keys():
##                if objs[objName].GetId() == self.value.GetId():
##                    return objName
        print 'ClassLinkPropEdit: ', self.value, 'not found'
        return `None`
    def inspectorEdit(self):
        self.editorCtrl = ChoiceIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.setValue(self.value)
    def getDisplayValue(self):
        return self.valueToIECValue()
    def getValues(self):
        return ['None'] + self.companion.designer.getObjectsOfClass(self.linkClass).keys()
    def setValue(self, value):
        self.value = value
        if self.editorCtrl:
            self.editorCtrl.setValue(self.valueToIECValue())
    def getValue(self):
        if self.editorCtrl:
            strVal = self.editorCtrl.getValue()
            if strVal == `None`:
                self.value = None
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


class BitmapPropEdit(PropertyEditor):
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

        if constr:
            idx1 = string.find(constr, "'")
            idx2 = string.rfind(constr, "'")
            if idx1 != -1 and idx2 != -1:
                self.bmpPath = eval(constr[idx1:idx2+1])
            else:
                self.bmpPath = ''
        else:
            self.bmpPath = ''

    def edit(self, event):
        dlg = wxFileDialog(self.parent, 'Choose an image', '.', '', 'Bitmaps (*.bmp)|*.bmp', wxOPEN)
        try:
            if dlg.ShowModal() == wxID_OK:
                self.bmpPath = dlg.GetPath()
                self.value = wxBitmap(self.bmpPath, wxBITMAP_TYPE_BMP)
                self.inspectorPost(false)
        finally:
            dlg.Destroy()
        return ''

    def getValue(self):
        return self.value

    def valueAsExpr(self):
        if self.bmpPath:
            return "wxBitmap(%s, wxBITMAP_TYPE_BMP)"%`self.bmpPath`
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
        self.editorCtrl = ChoiceIEC(self, self.value[1])
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
    ('Type', TupleType, [TuplPropEdit]),
    ('Class', wxSize, [SizePropEdit]),
    ('Class', wxSizePtr, [SizePropEdit]),
    ('Class', wxPoint, [PosPropEdit]),
    ('Class', wxPointPtr, [PosPropEdit]),
    ('Class', wxFontPtr, [FontPropEdit]),
    ('Class', wxColourPtr, [ColPropEdit]),
    ('Class', wxBitmapPtr, [BitmapPropEdit]),
    ('Class', wxValidator, [ClassLinkPropEdit]),
]
