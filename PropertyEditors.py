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
    XXX Todo XXX
    
    * write/wrap many more classes
    * choice between PropertyEditors having
    	- Predetermined editor controls (Textbox, combo, ellipsis button) 
    	  determined by a type flag
    	- Custom control derived from InspectorEditor control 
    	  attached per PropertyEditor
    	  This involves a little more work
    	  * needs solid default options/base classes for extension
    	  
Exception exceptions.AttributeError: 'thisown' in <method wxColourPtr.__del__
 wxColour instance at b09100> ignored    	  
"""

# XXX Value getting setting of value between internal and sometime control value
# XXX Is still too fuzzy

from wxPython.wx import *
from types import *
import Inspector, Utils
from Enumerations import reverseDict
from InspectorEditorControls import *

class EditorStyles:pass
class esExpandable(EditorStyles):pass
class esDialog(EditorStyles):pass
class esReadOnly(EditorStyles):pass
class esChoice(EditorStyles):pass

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
#            print propClass.__name__, 'registered'

    def registerTypes(self, propType, propEditors):
        for propEdit in propEditors:
            self.typeRegistry[propType] = propEdit
#            print propType, 'registered'
    
    def factory(self, name, parent, companion, rootCompanion, getsetters, idx, width):
        try:
            value = getsetters[0](companion.control)
        except Exception, message:
            print 'Error on accessing Getter for', name, ':', message
            value = ''
            
        
        if type(value) == InstanceType:
            if self.classRegistry.has_key(value.__class__.__name__):
                return self.classRegistry[value.__class__.__name__](name, parent, companion, rootCompanion, getsetters, idx, width)
            else:
#                raise 'Class '+value.__class__.__name__+' not supported by factory.'
#                pass
                print 'e:class', value, value.__class__.__name__, 'for', name, 'not supported'
        else:
            if type(value) == type(None):
                return None 
            elif self.typeRegistry.has_key(type(value)):
         	return self.typeRegistry[type(value)](name, parent, companion, rootCompanion, getsetters, idx, width)
            else:
#                raise 'Type '+`type(value)`+' not supported by factory.'
#                pass
                print 'e:type', value, type(value), 'for', name, 'not supported'


# XXX Check IEC initialisation not from Display value but from 'valueFromIEC'
class PropertyEditor:
    """ Class associated with a design time identified type, 
        it manages the behaviour of a NameValue in the Inspector """
    def __init__(self, name, parent, companion, rootCompanion, getsetters, idx, width):
        self.name = name
        self.parent = parent
        
        self.idx = idx
        self.width = width
        self.editorCtrl = None
#        print 'gs',getsetters
        self.getter = getsetters[0]
        self.setter = getsetters[1]
        self.companion = companion
        self.obj = companion.control
        self.rootCompanion = rootCompanion
        self.root = rootCompanion.control
        self.initFromComponent()
        self.style = []
    	
    def initFromComponent(self):
        if self.obj: 
            self.value = self.getter(self.obj)
#            print 'ic:', self.value, self.valueToIECValue()
            if self.editorCtrl:
                self.editorCtrl.setValue(self.valueToIECValue())
        else: self.value = ''

    def edit(self):
        pass
    def inspectorEdit(self):
        pass
    def refreshCompCtrl(self):
        if self.root and hasattr(self.root, 'Refresh'):
            self.root.Refresh()
        
    def inspectorPost(self):
        if self.editorCtrl:
            v = self.getValue()
#            print 'posting', v
            cv = self.getCtrlValue()
            if v != cv:
                self.setCtrlValue(cv, v)
                self.persistValue(self.valueAsExpr())
            else:
                print "prop's the same"
            self.editorCtrl.destroyControl()
            self.refreshCompCtrl()
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
        else: print ''
        return self.value

    def setValue(self, value):
        'property editor: set value', value
        self.value = value
        if self.editorCtrl:
            self.editorCtrl.SetValue(self.value)

    def getCtrlValue(self):
        return self.getter(self.obj)

    def setCtrlValue(self, oldValue, value):
        # If overwridden, rem to call check triggers if not calling parent method
        self.companion.checkTriggers(self.name, oldValue, value)
        self.setter(self.obj, value)

    def persistValue(self, value):
#        print 'property editor, persistprop', self.name, value
        self.companion.persistProp(self.name, self.setter, value)

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

class OptionedPropEdit(PropertyEditor):
    """ Property editors initialised with options """
    def __init__(self, name, parent, companion, rootCompanion, getsetters, idx, width, options, names):
        PropertyEditor.__init__(self, name, parent, companion, rootCompanion, getsetters, idx, width)
        self.options = options
        self.names = names
        if names:
            self.revNames = reverseDict(names)
        else:
    	    self.revNames = None	

class ConstrPropEditFacade:
    def setCtrlValue(self, oldValue, value):
        self.companion.checkTriggers(self.name, oldValue, value)
        
        #self.setter(self.name, value)
    def initFromComponent(self):
        self.value = ''
    def getCtrlValue(self):
        return ''#self.getter(self.obj)
    def getValue(self):
        return ''
    def setValue(self, value):
        self.value = value
        
class ConstrPropEdit(ConstrPropEditFacade, PropertyEditor):
    def __init__(self, name, parent, companion, rootCompanion, getsetters, idx, 
      width, options, names):
        PropertyEditor.__init__(self, name, parent, companion, rootCompanion, 
          getsetters, idx, width)
#        self.value = ''        
    def initFromComponent(self):
        self.value = self.getValue()
    def valueToIECValue(self):
        return self.value
    def getDisplayValue(self):
        return  self.getValue()
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

class StyleConstrPropEdit(IntConstrPropEdit):
    pass
#    constrKey = 'style'
    # self.companion.constructors()[self.name]

#        self.getter(self.obj)

class StrConstrPropEdit(ConstrPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx, 
          self.width)
    
    def getValue(self):
        if self.editorCtrl:
            try:
                aStr = eval(self.editorCtrl.getValue())
                if type(aStr) is StringType:
                    self.value = self.editorCtrl.getValue()
                else:
                    self.value = self.getCtrlValue()
            except Exception, message:
                self.value = self.getCtrlValue()
                print 'invalid constr prop value', message
        else:
            self.value = self.getCtrlValue()
        return self.value

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
#    constrKey = 'style'
    # self.companion.constructors()[self.name]
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
        
##    
##(PropertyEditor):
##    def __init__(self, name, parent, companion, rootCompanion, getsetters, idx, width, options, names):
##        PropertyEditor.__init__(self, name, parent, companion, rootCompanion, getsetters, idx, width)
##        self.value = ''        
##    def initFromComponent(self):
##        self.value = ''
    
class EventPropEdit(OptionedPropEdit):
    """ Property editor to handle design time definition of events """
    def initFromComponent(self):
        # unlike other propedit getter setters these are methods not funcs
        self.value = self.getter(self.name)

    def valueToIECValue(self):
    	v = self.value
    	return v

    def inspectorEdit(self):
        self.editorCtrl = ChoiceIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.value)

    def setCtrlValue(self, oldValue, value):
#        self.companion.checkTriggers(self.name, oldValue, value)
        self.setter(self.name, value)

    def getDisplayValue(self):
#        print 'evt getdisplayval', self.valueToIECValue()
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
                
##        if self.obj: 
##            self.value = self.getter(self.obj)
###            print 'ic:', self.value, self.valueToIECValue()
##            if self.editorCtrl:
##                self.editorCtrl.setValue(self.valueToIECValue())
##     	else: self.value = ''

    	    	    
class BITPropEditor(FactoryPropEdit):
    """ Editors for Built-in Python Types """
    def valueToIECValue(self):
        return `self.value`
    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx, self.width)
	     	         	    
class IntPropEdit(BITPropEditor):
    def getValue(self):
        if self.editorCtrl:
            try:
                value = eval(self.editorCtrl.getValue())
            except Exception, mess:
		Utils.ShowErrorMessage(self.parent, 'Invalid value', mess)
                raise                          
            self.value = value
        return self.value
	
class StrPropEdit(BITPropEditor):
    def valueToIECValue(self):
        return self.value

class TuplPropEdit(BITPropEditor): pass

# Property editors for design type types :)
class BoolPropEdit(OptionedPropEdit):
    def valueToIECValue(self):
    	v = self.value
    	if type(v) == IntType:
    	    return self.getValues()[v]
    	else: return `v`
    def inspectorEdit(self):
        self.editorCtrl = ChoiceIEC(self, self.value)
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
    	    return self.revNames[self.value]
    	else: OptionedPropEdit.getDisplayValue(self)
    def inspectorEdit(self):
        self.editorCtrl = ChoiceIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.setValue(self.value)
    def getDisplayValue(self):
	return self.valueToIECValue()
    def getValues(self):
        return self.names.keys()
    def setValue(self, value):
        self.value = value
        if self.editorCtrl:
            self.editorCtrl.setValue(self.revNames[value])
    def getValue(self):
        if self.editorCtrl:
	    strVal = self.editorCtrl.getValue()
            self.value = self.names[strVal]
        return self.value
# SetPropEdit


# Property editors for classes
class ClassPropEdit(FactoryPropEdit):
    def getDisplayValue(self):
        return '('+self.value.__class__.__name__+')'
    def getStyle(self):
        return [esExpandable]

class ClassLinkPropEdit(ClassPropEdit):
    def getStyle(self):
        return []
    
class ColPropEdit(ClassPropEdit):
#    def getDisplayValue(self):
#	return 
    def getStyle(self):
        return [esDialog]
        
    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)
    
    def edit(self, event):
        data = wxColourData()
        data.SetColour(self.value)
        dlg = wxColourDialog(self.parent, data)
#        dlg.GetColourData().SetColour(self.value)
        if dlg.ShowModal() == wxID_OK:
            self.value = dlg.GetColourData().GetColour()
            self.setter(self.obj, self.value)
            self.obj.Refresh()
        dlg.Destroy()

    def getValue(self):
        return self.value

    def valueAsExpr(self):
        return 'wxColour(%d, %d, %d)'%(self.value.Red(), self.value.Green(), self.value.Blue())


##class ColElementPE(OptionedPropEdit):
##    def __init__(self, parent, obj, getsetters, idx, width, options, names):
##        OptionedPropEdit.__init__(self, parent, obj, getsetters, idx, width, options, names)
##        if self.obj: self.value = wxColor(self.value[0],self.value[1],self.value[2])
##        else: print 'Fuck'
##    def inspectorEdit(self):
##        elemVal = self.getElemValue()
##        self.editorCtrl = TextCtrlIEC(self, self.value)
##        self.editorCtrl.createControl(self.parent, elemVal, self.idx, self.width)
##    def inspectorPost(self):
##        if self.editorCtrl:
##            v = self.getValue()
##            self.setter(self.obj, v.Red(), v.Green(), v.Blue())
##            print 'set:', v.Red(), v.Green(), v.Blue()
##            self.editorCtrl.destroyControl()

##class RedColPE(ColElementPE):
##    def getElemValue(self):
##        if self.editorCtrl: 
##            ev = self.editorCtrl.getValue()
##            print 'ec, red:', self.editorCtrl.getValue(), type(ev), ev
##            if type(ev) == InstanceType:
##                return ev.Red()
##            else:
##                return int(ev)
##        else: 
##            print 'ne, red', self.value.Red()
##            return self.value.Red()
##    def setValue(self, value):
##        self.value = value
##        if self.editorCtrl:
##            self.editorCtrl.SetValue(`self.value.Red()`)
##    def getValue(self):
##        return wxColour(self.getElemValue(), self.value.Green(), self.value.Blue())
##    def getDisplayValue(self):
##        return `self.getElemValue()`
##        

##class GreenColPE(ColElementPE):
##    def getElemValue(self):
##        if self.editorCtrl: 
##            ev = self.editorCtrl.getValue()
##            print 'ec, green:', self.editorCtrl.getValue(), type(ev), ev
##            if type(ev) == InstanceType:
##                return ev.Green()
##            else: return int(ev)
##        else: 
##            print 'ne, green', self.value.Green()
##            return self.value.Green()
##    def setValue(self, value):
##        self.value = value
##        if self.editorCtrl:
##            self.editorCtrl.SetValue(`self.value.Green()`)
##    def getValue(self):
##        return wxColour(self.value.Red(), self.getElemValue(), self.value.Blue())
##    def getDisplayValue(self):
##        return `self.getElemValue()`

##class BlueColPE(ColElementPE):
##    def getElemValue(self):
##        if self.editorCtrl: 
##            ev = self.editorCtrl.getValue()
##            print 'ec, blue:', self.editorCtrl.getValue(), type(ev), ev
##            if type(ev) == InstanceType:
##                return ev.Blue()
##            else: return int(ev)
##        else: 
##            print 'ne, blue', self.value.Blue()
##            return self.value.Blue()
##    def setValue(self, value):
##        self.value = value
##        if self.editorCtrl:
##            self.editorCtrl.SetValue(`self.value.Blue()`)
##    def getValue(self):
##        return wxColour(self.value.Red(), self.value.Green(), self.getElemValue())
##    def getDisplayValue(self):
##        return `self.getElemValue()`
    
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
#    def setValue(self, value):
    def valueAsExpr(self):
        return 'wxSize(%d, %d)'%(self.value.x, self.value.y)
                

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

class FontPropEdit(ClassPropEdit):
    def getStyle(self):
        return ClassPropEdit.getStyle(self) + [esDialog, esReadOnly]

    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def getValue(self):
        return self.value
    
    def edit(self, event):
#        print 'FPE:edit'
        dlg = wxFontDialog(self.parent)
        dlg.GetFontData().SetInitialFont(self.value)
        if dlg.ShowModal() == wxID_OK:
            self.value = dlg.GetFontData().GetChosenFont()
            self.setter(self.obj, self.value)
            self.obj.Refresh()
        dlg.Destroy()
    def valueAsExpr(self):
        fnt = self.value
        return 'wxFont(%d, %d, %d, %d, %d, %s)'%(fnt.GetPointSize(), 
          fnt.GetFamily(), fnt.GetStyle(), fnt.GetWeight(), fnt.GetUnderlined(),
          `fnt.GetFaceName()`)
        
class BitmapPropEdit(ClassPropEdit):
    def getStyle(self):
        return ClassPropEdit.getStyle(self) + [esDialog, esReadOnly]

    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def getValue(self):
        return self.value
    
##    def edit(self, event):
###        print 'FPE:edit'
##        dlg = wxFontDialog(self.parent)
##        dlg.GetFontData().SetInitialFont(self.value)
##        if dlg.ShowModal() == wxID_OK:
##            self.value = dlg.GetFontData().GetChosenFont()
##            self.setter(self.obj, self.value)
##            self.obj.Refresh()
##        dlg.Destroy()
        

""" Property editor registration """

propertyRegistry = PropertyRegistry()

propertyRegistry.registerTypes(IntType, [IntPropEdit])
propertyRegistry.registerTypes(StringType, [StrPropEdit])
propertyRegistry.registerTypes(TupleType, [TuplPropEdit])
propertyRegistry.registerClasses(wxSize, [SizePropEdit])
propertyRegistry.registerClasses(wxSizePtr, [SizePropEdit])
propertyRegistry.registerClasses(wxPoint, [PosPropEdit])
propertyRegistry.registerClasses(wxPointPtr, [PosPropEdit])
propertyRegistry.registerClasses(wxFontPtr, [FontPropEdit])
propertyRegistry.registerClasses(wxColourPtr, [ColPropEdit])
propertyRegistry.registerClasses(wxValidator, [ClassLinkPropEdit])
