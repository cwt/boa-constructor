#----------------------------------------------------------------------
# Name:        BaseCompanions.py
# Purpose:     
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

#Multi viewed source code exploration generation tool
#mvscgaet

# (c) 1999 Riaan Booysen
from wxPython.wx import *
from PropertyEditors import *
import HelpCompanions
import methodparse
import string

# XXX parent passed in constr not used

# XXX New design option: Having the design time ctrls multiply inherit
# XXX from Control and from Companion
# XXX + Companion can implement GetSetters wrapping those of Control that
# XXX   need binding like Enable/IsEnabled with GetEnabled/SetEnabled

""" Design time classes
	These are companion classes to wxPython classes that capture
	design-time behaviour like
	  * Constructor parameters
	  * Events
	  * Property editors

    XXX Todo XXX
    
    * write/wrap many more classes
    * streaming of properties
        * xml option
        * handling of default values
    * collection companion
    * define event and name for popup menu on component
    * overrideable method or new multi inheritance class
      for palette creation in container companions,
    
"""
class Companion:
    wxDocs = HelpCompanions.wxDefaultDocs
    def __init__(self, name):
        self.name = name

class CodeCompanion(Companion):
    pass

class DesignTimeCompanion(Companion):
    def __init__(self, name, designer):
        Companion.__init__(self, name)
        self.designer = designer
        self.dId = NewId()
        self.editors = {}
        self.options = {}
        self.names = {}
        self.triggers = {'Name': self.SetName}
        self.textConstr = None
        self.textPropList = []
        self.textEventList = []

    def setConstr(self, constr):
        """ Define a new constructor for source code, called when a component is
            parsed from source
            See also: persistConstr """
        self.textConstr = constr
    def constructor(self):
        """ This method must be overriden by defining it in in another class
            and multiply inheriting from this new class and a DesignTimeCompanion
            derivative. This allows groups of components having the same constructor
            to be created."""
        return {}
    def defaults(self):
        return {}

    def properties(self):
        """ Properties additional to those gleened thru reflection. 
            Dictionary key=propname : val=get/setter tuple. """ 
        return {}

    def setProps(self, propList):
        # XXX Should companion initialise comp props instead of Designer?
        self.textPropList = propList
    def hideDesignTime(self):
        pass
    def dontPersistProps(self):
        """ Properties are live (i.e. read/write) at design time but whose
            changes won't be applied to source. This is for cascading type
            properties like Size vs ClientSize. Updating one will automatically
            update the other so only one of them has to be stored."""
        return []
    def events(self):
        return []
    def setEvents(self, eventList):
        self.textEventList = eventList
    def editor(self):
        pass
    def applyRunTime(self):
        """ Properties whose value will be modifyable at design-time
            and whose changes will be applied to the source but will
            not be applied to the controls at design time e.g. Show/Enable."""
        pass
    def getPropEditor(self, prop):
        if self.editors.has_key(prop): return self.editors[prop]
        else: return None
    def getPropOptions(self, prop):
        if self.options.has_key(prop): return self.options[prop]
        else: return None
    def getPropNames(self, prop):
        if self.names.has_key(prop):
#            print 'gpn:', prop, self.names[prop]
            return self.names[prop]
        else:
#            print 'gpnX:', prop, self.names, self.options, self.__class__
            return None

    def evtGetter(self, name):
        for evt in self.textEventList:
            if evt.event_name == name: return evt.trigger_meth
        print 'no getter', name
        return None
        
    def evtSetter(self, name, value):
        for evt in self.textEventList:
            if evt.event_name == name: 
                evt.trigger_meth = value
                return 
    def persistConstr(self, className, params):
        """ Define a new constructor for source code, called when creating a
            new component from the palette
            See also: setConstr """
        paramStrs = []
        for param in params.keys():
            paramStrs.append('%s = %s'%(param, params[param]))
        self.textConstr = methodparse.ConstructorParse('self.%s = %s(%s)' %(self.name, className, string.join(paramStrs, ', ')))
        # XXX Is it necessary to update objectCollections ???
        self.designer.model.objectCollections[self.designer.collectionMethod].creators.append(self.textConstr)

    def checkTriggers(self, name, oldValue, newValue):
        #trigger specially handled callbacks for property changes with consequences
        if self.triggers.has_key(name):
            self.triggers[name](oldValue, newValue)

    def persistProp(self, name, setter, value):
#        print 'companion.persistprop', self.name, value
        c = self.constructor()
        #constructor
        if c.has_key(name):
            self.textConstr.params[c[name]] = value
#            print 'pp, constr:', self.textConstr.asText()
        #property
        else:
            for prop in self.textPropList:
                try:
                    if prop.prop_setter == setter.func_name: 
                        prop.params = [value]
#                        print 'pp, prop:', prop.asText()
                        return 
                except:
                    print 'except in persistprop'
#                    print dir(prop)
                    raise
            
            # XXX Ugly, must change
            if self.control == self.designer:
                self.textPropList.append(methodparse.PropertyParse( \
                  'self.%s(%s)' %(setter.func_name, value)))
            else:
                self.textPropList.append(methodparse.PropertyParse( \
                  'self.%s.%s(%s)' %(self.name, setter.func_name, value)))
#            print 'pp, new prop:', self.textPropList[-1].asText()

    def persistEvt(self, name, value, id = None):
        """ Add a source entry for an event or update the trigger method of
            am existing event. """
        for evt in self.textEventList:
            if evt.event_name == name: 
                evt.trigger_meth = value
                return
##        self.textEventList.append(methodparse.EventParse( \
##          'EVT_%s(self.%s, self.%s)' %(name, self.name, value)))
        self.textEventList.append(methodparse.EventParse(None, self.name, name, 
                                                         value, id))

    def setProp(self, name, value):
        """ Optional callback companions can override for extra functionality
            after updating a property e.g. refreshing """
        pass
    
    def SetName(self, oldValue, newValue):
        print 'companion: setting name from', oldValue, 'to', newValue
        self.name = newValue
        self.designer.model.renameCtrl(oldValue, newValue)
        self.designer.renameCtrl(oldValue, newValue)

tPopupIDUp = 200
tPopupIDCut = 201
tPopupIDCopy = 202
tPopupIDPaste = 203
tPopupIDDelete = 204
        
class ControlDTC(DesignTimeCompanion):
    """ Create the design-time control """
    def __init__(self, name, designer, parent, ctrlClass):
        DesignTimeCompanion.__init__(self, name, designer)
        self.parent = parent
        self.ctrlClass = ctrlClass
        self.generateWindowId()
        self.container = false
    
##    def designTimeDefaults(self, position, size):
##	return {}    
##    def designTimeSource(self, position, size):
##	return {}    

    def designTimeControl(self, position, size, args = None):
#        print 'design time control', self, self.ctrlClass, self.designTimeDefaults(position)
        if args:
            self.control = apply(self.ctrlClass, (), args)
        else:
            self.control = apply(self.ctrlClass, (), self.designTimeDefaults(position, size))
#        print 'design time control created', self

        self.initDesignTimeControl()
        return self.control

    def designTimeDefaults(self, position = wxDefaultPosition, 
                                 size = wxDefaultSize):
        """ Return a dictionary of parameters for the constructor of a wxPython
            control. e.g. {'name': 'Frame1', etc) """
        if not position: position = wxDefaultPosition
        if not size: size = wxDefaultSize
        
        dts = self.designTimeSource('wxPoint(%s, %s)'%(position.x, position.y),
          'wxSize(%s, %s)'%(size.x, size.y))

        for param in dts.keys():
            try:
                dts[param] = eval(dts[param])
            except:
                print 'could not eval', dts[param]
        
        dts.update({'parent': self.parent, 'id': self.dId})
        return dts

    def designTimeSource(self, position, size):
        """ Return a dictionary of parameters for the constructor of a wxPython
            control's source. 'parent' and 'id' handled automatically """
	return {}    

    def generateWindowId(self):
        if self.designer: 
            self.id = Utils.windowIdentifier(self.designer.GetName(), self.name)
        else: self.id = `NewId()`

    def SetName(self, oldValue, newValue):
        DesignTimeCompanion.SetName(self, oldValue, newValue)
        self.updateWindowIds()
    
    def updateWindowIds(self):
        # this belongs in ControlDTC
        self.generateWindowId()
        self.textConstr.params['id'] = self.id        
        for evt in self.textEventList:
            if evt.windowid:
                evt.windowid = self.id

    def initDesignTimeControl(self):
        #try to set the name
        try:
           self.control.SetName(self.name)
           self.control.SetToolTipString(self.name)
        except:
           pass
           
        self.designer.senderMapper.addObject(self.control)

        EVT_MOTION(self.control, self.designer.OnMouseOver)
        EVT_LEFT_DOWN(self.control, self.designer.OnControlSelect)
        EVT_LEFT_UP(self.control, self.designer.OnControlRelease)
        EVT_LEFT_DCLICK(self.control, self.designer.OnControlDClick)
        EVT_SIZE(self.control, self.designer.OnControlResize)

        self.popx = self.popy = 0

        EVT_RIGHT_DOWN(self.control, self.designer.OnRightDown)
        # for wxMSW
        EVT_COMMAND_RIGHT_CLICK(self.control, -1, self.designer.OnRightClick)
        # for wxGTK
        EVT_RIGHT_UP(self.control, self.designer.OnRightClick)
##        self.popup = wxMenu()
##        self.popup.Append(tPopupIDUp, "Up")
##        self.popup.Append(-1, "-")
##        self.popup.Append(tPopupIDCut, "Cut")
##        self.popup.Append(tPopupIDCopy, "Copy")
##        self.popup.Append(tPopupIDPaste, "Paste")
##        self.popup.Append(tPopupIDDelete, "Delete")

# sub properties (Font etc)
class HelperDTC(DesignTimeCompanion):
    def __init__(self, name, designer, ctrl, obj):
        DesignTimeCompanion.__init__(self, name, designer)
        self.control = obj
        self.obj = obj

# non-visual classes (Imagelists, etc)
class UtilityDTC(DesignTimeCompanion):
    def __init__(self, name, designer, objClass):
        DesignTimeCompanion.__init__(self, name, designer)
        self.objClass = objClass

    def designTimeObject(self, args = None):
        if args:
            self.control = apply(self.objClass, (), args)
        else:
            self.control = apply(self.objClass, (), self.designTimeDefaults())
        print 'design time object created', self

        return self.control

    def designTimeDefaults(self):
        """ Return a dictionary of parameters for the constructor of a wxPython
            control. e.g. {'name': 'Frame1', etc) """

        dts = self.designTimeSource()

        for param in dts.keys():
            try:
                dts[param] = eval(dts[param])
            except:
                print 'could not eval', dts[param]

        return dts

# Testing
class TestDTC(ControlDTC):        
    def __init__(self, name, designer, parent, ctrlClass):
        ControlDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors = {'boolean': BoolPropEdit, 
        		'Shown': BoolPropEdit, }
        
    def properties(self):
        return {'Shown': [wxWindow.IsShown, wxWindow.Show]}
    def applyRunTime(self):
	return ['Shown']
    def events(self):
        return []


# XXX Parents, from constructor or current selected container in designer
class WindowDTC(ControlDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        ControlDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors = {'AutoLayout': BoolPropEdit,
                        'Shown': BoolPropEdit, 
                        'Enabled': BoolPropEdit,
                        'EvtHandlerEnabled': BoolPropEdit,
                        'Style': StyleConstrPropEdit}
        self.ToolTip = ''
    def properties(self):
        return {'Shown': (wxWindow.IsShown.im_func, wxWindow.Show.im_func),
        	'Enabled': (wxWindowPtr.IsEnabled.im_func, wxWindowPtr.Enable.im_func)
#        	'ToolTip': (wxWindowPtr.GetName.im_func, wxWindowPtr.SetToolTipString.im_func)
        }
    def dontPersistProps(self):
        return ['ClientSize']
    def applyRunTime(self):
	return ['Shown', 'Enabled', 'EvtHandlerEnabled']
    def events(self):
        return ['MiscEvent', 'MouseEvent']
    
##    def getToolTip(self):
##        return self.ToolTip

class ChoicedDTC(WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Choices'] = ChoicesConstrPropEdit
    
class ContainerDTC(WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.container = true
