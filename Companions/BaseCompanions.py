#-------------------------------------------------------------------------------
# Name:        BaseCompanions.py                                                
# Purpose:     Classes that 'shadow' controls. They implement design time       
#              behaviour and interfaces                                         
#                                                                               
# Author:      Riaan Booysen                                                    
#                                                                               
# Created:     1999                                                             
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen                                     
# Licence:     GPL                                                              
#-------------------------------------------------------------------------------

#Multi viewed source code exploration generation tool
#mvscgaet

from wxPython.wx import *
from PropEdit.PropertyEditors import *
import HelpCompanions, RTTI, Preferences
import methodparse
import string, copy

bodyIndent = ' '*8

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

# XXX This bitmap must be added to the scope of any method
# XXX that evaluates parameters or properies
#wxNullBitmap = Preferences.IS.load('Images/Inspector/wxNullBitmap.bmp')

class Companion:
    """ Default companion, entity with a name and default documentation """
    wxDocs = HelpCompanions.wxDefaultDocs
    def __init__(self, name):
        self.name = name

class CodeCompanion(Companion):
    pass

class DesignTimeCompanion(Companion):
    """ Base class for all companions participating in the design-time process.
    """
    def __init__(self, name, designer):
        Companion.__init__(self, name)
        self.parentCompanion = None
        self.designer = designer
        # Design time window id
        self.dId = NewId()
        self.id = None

        # Property editors for properties whose types cannot be deduced
        self.editors = {}
        # Enumerated values for the options of a property editor
        self.options = {}
        # Enumerated display values for the options of a property editor
        # XXX Change to something less generic
        self.names = {}
        
        # Companion methods that must be called when a property changes
        self.triggers = {'Name': self.SetName}
        # Companions for properties for which a companion can not be deduced
        self.subCompanions = {}

        # Parse objects for reading in and writing out source
        self.textConstr = None
        self.textPropList = []
        self.textEventList = []
        self.textCollInitList = []
        
    def destroy(self):
        del self.triggers

    def constructor(self):
        """ This method must be overriden by defining it in in another class
            and multiply inheriting from this new class and a 
            DesignTimeCompanion derivative. This allows groups of components 
            having the same constructor to be created."""

        return {}

#    def defaults(self):
#        return {}

    def getPropList(self):
        return RTTI.getPropList(self.control, self)

    def properties(self):
        """ Properties additional to those gleened thru reflection. 
            Dictionary key=propname : type, val=getter, setter tuple. 
            type = 'CtrlRoute' : Routed to get/setters on the control
                   'CompnRoute': Routed to get/setters on the companion
        """ 
 
        return {}

    def setConstr(self, constr):
        """ Define a new constructor for source code, called when a component is
            parsed from source
            See also: persistConstr """
        self.textConstr = constr

    def setProps(self, propList):
        # XXX Should companion initialise comp props instead of Designer?
        self.textPropList = propList

    def setCollInits(self, collInitList):
##        print 'COMPANION setcollinits'
        self.textCollInitList = collInitList

    def setEvents(self, eventList):
        self.textEventList = eventList

    def getEvents(self):
        return self.textEventList
    
    def getWinId(self):
        return self.id

    def hideDesignTime(self):
        return []

    def dontPersistProps(self):
        """ Properties are live (i.e. read/write) at design time but whose
            changes won't be applied to source. This is for cascading type
            properties like Size vs ClientSize. Updating one will automatically
            update the other so only one of them has to be stored."""
        return []

    def events(self):
        return []

    def editor(self):
        pass

    def vetoedMethods(self):
        return []

##    def links(self):
##        return []

    # Rename to links
    def dependentProps(self):
        """ These are properties that depend on other controls already
            being created. They will be initialised right at the end of 
            the definition block
        """
        return []
        
    def applyRunTime(self):
        """ Properties whose value will be modifyable at design-time
            and whose changes will be applied to the source but will
            not be applied to the controls at design time e.g. Show/Enable.
        """
        pass

    def getPropEditor(self, prop):
        if self.editors.has_key(prop): return self.editors[prop]
        else: return None

    def getPropOptions(self, prop):
        if self.options.has_key(prop): return self.options[prop]
        else: return None

    def getPropNames(self, prop):
        
        if self.names.has_key(prop):
##            print 'gpn:', prop, self.names[prop]
            return self.names[prop]
        else:
##            print 'gpnX:', prop, self.names, self.options, self.__class__
            return None

    def evtGetter(self, name):
        for evt in self.textEventList:
            if evt.event_name == name: return evt.trigger_meth
##        print 'no getter', name
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
##            print param, params[param]
            paramStrs.append('%s = %s'%(param, params[param]))

        self.textConstr = methodparse.ConstructorParse('self.%s = %s(%s)' %(self.name, className, string.join(paramStrs, ', ')))

        self.designer.addCtrlToObjectCollection(self.textConstr)

    def persistCollInit(self, method, ctrlName, propName, params = {}):
        """ Define a new collection init method for source code, called when    
            creating a new item in CollectionEditor                             
        """
        
##        paramStrs = []
##        print 'persist constr'
##        for param in params.keys():
##            print param, params[param]
##            paramStrs.append('%s = %s'%(param, params[param]))

        collInitParse = methodparse.CollectionInitParse(None, ctrlName, method, 
          [], propName)

        self.parentCompanion.textCollInitList.append(collInitParse)
        
        self.designer.addCollToObjectCollection(collInitParse)

    def checkTriggers(self, name, oldValue, newValue):
        #trigger specially handled callbacks for property changes with consequences
        if self.triggers.has_key(name):
            self.triggers[name](oldValue, newValue)

    def persistProp(self, name, setterName, value):
        c = self.constructor()
        #constructor
        if c.has_key(name):
            self.textConstr.params[c[name]] = value
        #property
        elif name not in self.dontPersistProps():
            for prop in self.textPropList:
                try:
                    if prop.prop_setter == setterName: 
                        prop.params = [value]
                        return 
                except:
                    print 'except in persistprop'
                    raise
            
            if self.control == self.designer:
                comp_name = ''
            else:
                comp_name = self.name
            self.textPropList.append(methodparse.PropertyParse( \
                None, comp_name, setterName, [value], name))

    def persistedPropVal(self, name, setterName):
##        print 'companion.persistedpropval', self.name, name
        c = self.constructor()
        #constructor
        if c.has_key(name):
            return self.textConstr.params[c[name]]
        #property
        elif name not in self.dontPersistProps():
            for prop in self.textPropList:
                try:
                    if prop.prop_setter == setterName: 
                        return prop.params
                except:
                    print 'except in persistprop'
                    raise
        return None

    def persistEvt(self, name, value, wId = None):
        """ Add a source entry for an event or update the trigger method of
            am existing event. """
        for evt in self.textEventList:
            if evt.event_name == name: 
                evt.trigger_meth = value
                return
        if self.control == self.designer: # or wId is not None:
            comp_name = ''
        else:
            comp_name = self.name
        self.textEventList.append(methodparse.EventParse(None, comp_name, name, 
                                                         value, wId))
##        print 'PersistEvt', self.textEventList

    def setProp(self, name, value):
        """ Optional callback companions can override for extra functionality
            after updating a property e.g. refreshing """
        pass
    
    def SetName(self, oldValue, newValue):
        """ Triggered when the 'Name' property is changed """
##        print self.__class__.__name__,'companion: setting name from', oldValue, 'to', newValue
        if self.designer.objects.has_key(newValue):
            wxLogError('There is already an object named '+newValue)
        else:
            self.name = newValue
            self.designer.model.renameCtrl(oldValue, newValue)
            self.designer.renameCtrl(oldValue, newValue)
    
    def evtName(self):
        return self.name

    def renameCtrl(self, oldName, newName):
        self.textConstr.comp_name = newName
        for prop in self.textPropList:
            prop.comp_name = newName
        for collInit in self.textCollInitList:
            collInit.renameCompName(newName)
        for evt in self.textEventList:
            evt.comp_name = newName
    
    def addIds(self, lst):
        if self.id is not None:
            lst.append(self.id)        
        
    def getPropNameFromSetter(self, setter):
        props = self.properties()
        for prop in props.keys():
            if props[prop][1] and props[prop][1].__name__ == setter:
                return prop
        if setter[:3] == 'Set': return setter[3:]
        else: return setter

    def writeConstructor(self, output, collectionMethod):
        # Add constructor
        if self.textConstr:
            output.append(bodyIndent + self.textConstr.asText())
            # XXX HACK attack
            # Add call to init utils after frame constructor
            if self.textConstr.comp_name == '' and \
              collectionMethod == '_init_ctrls':
                output.append(bodyIndent + 'self._init_utils()')

##        try:
##            # Add constructor
##            if compn.textConstr:
##                newBody.append(bodyIndent + compn.textConstr.asText())
##                # XXX HACK attack
##                # Add call to init utils after frame constructor
##                if compn.textConstr.comp_name == '' and \
##                  self.collectionMethod == '_init_ctrls':
##                    newBody.append(bodyIndent + 'self._init_utils()')
##        except: 
##            print 'no constr:', ctrlName
        
    def writeProperties(self, output, ctrlName, definedCtrls, deps, depLinks):
        # Add properties
        for prop in self.textPropList:
            # Postpone dependent props
            if self.designer.checkAndAddDepLink(ctrlName, prop, 
                  self.dependentProps(), deps, depLinks, definedCtrls):
                continue
            output.append(bodyIndent + prop.asText())

    def writeEvents(self, output, addModuleMethod = false):
        """ Write out EVT_* calls for all events. Optionally For every event 
            definition not defined in source add an empty method declaration to 
            the bottom of the class """
        for evt in self.textEventList:
            if evt.trigger_meth != '(delete)':
                output.append(bodyIndent + evt.asText())
                model = self.designer.model
                module = model.getModule()
                if addModuleMethod and not module.classes[
                    model.main].methods.has_key(evt.trigger_meth):
                    module.addMethod(model.main, evt.trigger_meth, 
                          'self, event', ['        pass'])

    def writeCollections(self, output, collDeps):
        # Add collection initialisers
        for collInit in self.textCollInitList:
            if collInit.getPropName() in self.dependentProps():
                collDeps.append(bodyIndent + collInit.asText())
            else:
                output.append(bodyIndent + collInit.asText())

    def writeDependencies(self, output, ctrlName, depLinks):
        if depLinks.has_key(ctrlName):
            for prop in depLinks[ctrlName]:
                output.append(bodyIndent + prop.asText())

                          
        
class NYIDTC(DesignTimeCompanion):
    host = 'Not Implemented'
    def __init__(self, name, designer, parent, ctrlClass):
        raise 'Not Implemented'
    
    
class ControlDTC(DesignTimeCompanion):
    """ Create the design-time control """
    windowIdName = 'id'
    windowParentName = 'parent'
    host = 'Designer'
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
##        print 'design time control', self, self.ctrlClass, self.designTimeDefaults(position)
        if args:
            self.control = apply(self.ctrlClass, (), args)
        else:
            self.control = apply(self.ctrlClass, (), self.designTimeDefaults(position, size))
##        print 'design time control created', self

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
                print 'could not eval design time default param', dts[param]
        
        dts.update({self.windowParentName: self.parent, self.windowIdName: self.dId})
        return dts

    def designTimeSource(self, position, size):
        """ Return a dictionary of parameters for the constructor of a wxPython
            control's source. 'parent' and 'id' handled automatically """
	return {}    

    def generateWindowId(self):
        if self.designer: 
            self.id = Utils.windowIdentifier(self.designer.GetName(), self.name)
        else: self.id = `wxNewId()`

    def SetName(self, oldValue, newValue):
        DesignTimeCompanion.SetName(self, oldValue, newValue)
        self.updateWindowIds()
    
    def updateWindowIds(self):
        self.generateWindowId()
        self.textConstr.params[self.windowIdName] = self.id        
        for evt in self.textEventList:
            if evt.windowid:
                evt.windowid = self.id

    def initDesignTimeEvents(self, ctrl):
        EVT_MOTION(ctrl, self.designer.OnMouseOver)
        EVT_LEFT_DOWN(ctrl, self.designer.OnControlSelect)
        EVT_LEFT_UP(ctrl, self.designer.OnControlRelease)
        EVT_LEFT_DCLICK(ctrl, self.designer.OnControlDClick)
        EVT_SIZE(ctrl, self.designer.OnControlResize)

    def initDesignTimeControl(self):
        #try to set the name
        try:
           self.control.SetName(self.name)
           self.control.SetToolTipString(self.name)
        except:
           pass
           
        self.designer.senderMapper.addObject(self.control)

        self.initDesignTimeEvents(self.control)

        self.popx = self.popy = 0

        EVT_RIGHT_DOWN(self.control, self.designer.OnRightDown)
        # for wxMSW
        EVT_COMMAND_RIGHT_CLICK(self.control, -1, self.designer.OnRightClick)
        # for wxGTK
        EVT_RIGHT_UP(self.control, self.designer.OnRightClick)

class MultipleSelectionDTC(DesignTimeCompanion):
    """ Semi mythical class at the moment that will represent a group of
        selected objects. It's properties should represent the common subset
        of properties of the selection.
        
        Currently only used so the inspector has something to hold on to during
        multiple selection        
    """

# sub properties (Font etc)
class HelperDTC(DesignTimeCompanion):
    def __init__(self, name, designer, ctrl, obj):
        DesignTimeCompanion.__init__(self, name, designer)
        self.control = obj
        self.obj = obj

# non-visual classes (Imagelists, etc)
class UtilityDTC(DesignTimeCompanion):
    host = 'Data'
    def __init__(self, name, designer, objClass):
        DesignTimeCompanion.__init__(self, name, designer)
        self.objClass = objClass
        self.editors = {'Name': NameConstrPropEdit}

    def properties(self):
        props = DesignTimeCompanion.properties(self)
        props.update({'Name':  ('NoneRoute', None, None)})
        return props

    def designTimeObject(self, args = None):
        if args:
            self.control = apply(self.objClass, (), args)
        else:
            self.control = apply(self.objClass, (), self.designTimeDefaults())

        return self.control

    def designTimeDefaults(self):
        """ Return a dictionary of parameters for the constructor of a wxPython
            control. e.g. {'name': 'Frame1', etc) """

        dts = self.designTimeSource()

        for param in dts.keys():
            try:
                dts[param] = eval(dts[param])
            except:
                print 'could not eval 2', dts[param]

        return dts

    def updateWindowIds(self):
        pass

# Testing
class TestDTC(ControlDTC):        
    def __init__(self, name, designer, parent, ctrlClass):
        ControlDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors = {'boolean': BoolPropEdit, 
        		'Shown': BoolPropEdit, }
        
    def properties(self):
        return {'Shown': ['CtrlRoute', wxWindow.IsShown, wxWindow.Show]}
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
                        'Style': StyleConstrPropEdit,
                        'Constraints': CollectionPropEdit,
                        'Name': NamePropEdit,
                        'Sizer': SizerClassLinkPropEdit}
        import UtilCompanions
        self.subCompanions['Constraints'] = UtilCompanions.IndividualLayoutConstraintOCDTC
        
    def properties(self):
        return {'Shown': ('CtrlRoute', wxWindow.IsShown.im_func, wxWindow.Show.im_func),
        	'Enabled': ('CtrlRoute', wxWindowPtr.IsEnabled.im_func, wxWindowPtr.Enable.im_func),
        	'ToolTipString': ('CompnRoute', self.GetToolTipString, self.SetToolTipString)
#        	    (wxWindowPtr.GetName.im_func, wxWindowPtr.SetToolTipString.im_func)
        }

    def hideDesignTime(self):
        return ['NextHandler', 'PreviousHandler', 'EventHandler', 'Id', 'Caret',
                'WindowStyleFlag', 'ToolTip']

    def dontPersistProps(self):
        return ['ClientSize']
    def applyRunTime(self):
	return ['Shown', 'Enabled', 'EvtHandlerEnabled']
    def events(self):
        return ['MiscEvent', 'MouseEvent', 'FocusEvent', 'KeyEvent']
    
    def GetToolTipString(self, blah):
        return self.control.GetToolTip().GetTip()

    def SetToolTipString(self, value):
        self.control.SetToolTipString(value)
    
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
        
class CollectionDTC(DesignTimeCompanion):
    """ Companions encapsulating list maintaining behaviour into a single 
        property
        Maintains an index which points to the currently active item in the 
        collection
    """
    
    propName = 'undefined'
    insertionMethod = 'undefined'
    deletionMethod = 'undefined'
    displayProp = 'undefined'
    indexProp = 'undefined'
    sourceObjName = 'parent'
    
    def __init__(self, name, designer, parentCompanion, ctrl):
        DesignTimeCompanion.__init__(self, name, designer)
##        print 'CollectionDesigner', designer
        from Views.CollectionEdit import CollectionEditor
        self.CollEditorFrame = CollectionEditor
        self.control = ctrl
        self.setCollectionMethod()
        self.index = 0
        self.parentCompanion = parentCompanion
    
    def setCollectionMethod(self):
        self.collectionMethod = '_init_coll_%s_%s' %(self.name, self.propName)
    
    def setIndex(self, index):
        self.index = index
        self.setConstr(self.textConstrLst[index])

    def setConstrs(self, constrLst, inits, fins):
        self.initialisers = inits
        self.finalisers = fins
        
        self.textConstrLst = constrLst
    
    def renameCtrl(self, oldName, newName):
##        print 'Collection rename ctrl'
        DesignTimeCompanion.renameCtrl(self, oldName, newName)
        self.setCollectionMethod()
    
    def getCount(self):
        return len(self.textConstrLst)
    
    def getDisplayProp(self):
        return eval(self.textConstrLst[self.index].params[self.displayProp])    
    
    def initialiser(self):
        """ When overriding, append this after derived initialiser """
        return ['']

    def finaliser(self):
        """ When overriding, append this before derived finaliser """
        # Removed cause it looks icky
        return []
        
    def appendItem(self):
        self.index = self.getCount()
##        print 'append item'
        collItemInit = methodparse.CollectionItemInitParse(None, 
          self.sourceObjName, self.insertionMethod, 
          self.designTimeSource(self.index))
          
        self.textConstrLst.append(collItemInit)
        self.setConstr(collItemInit)
        
        self.applyDesignTimeDefaults(collItemInit.params)
        
        return collItemInit

    def deleteItem(self, idx):
        # remove from ctrl
        if self.deletionMethod != '(None)':
            f = RTTI.getFunction(self.control, self.deletionMethod)
##            print 'applying', f, self.control
            apply(f, [self.control, idx])
        
        del self.textConstrLst[idx]
        # renumber items following deleted one
        if self.indexProp != '(None)':
            for constr in self.textConstrLst[idx:]:
                constr.params[self.indexProp] = `int(constr.params[self.indexProp]) -1`

    def applyDesignTimeDefaults(self, params):
        f = RTTI.getFunction(self.control, self.insertionMethod)
        params = self.designTimeDefaults(params)
        apply(f, [self.control], params)

    def SetName(self, oldValue, newValue):
        self.name = newValue
        self.setCollectionMethod()

    def updateWindowIds(self):
        pass

##    def addIds(self, lst):
##        """ Iterate over items and extend lst for collections with ids """
##        pass

    def designTimeDefaults(self, vals):
        """ Return a dictionary of parameters for the constructor of a wxPython
            control. e.g. {'name': 'button1', etc) """
        dtd = {}
        for param in vals.keys():
            try:
                dtd[param] = eval(vals[param])
            except Exception, message:
                print 'could not eval 3', param, vals[param], message
        
        return dtd
    
    def initCollection(self):
        pass
    
    def writeCollectionInitialiser(self, output):
        output.extend(self.initialiser())

    def writeCollectionItems(self, output):        
        for creator in self.textConstrLst:
            output.append(bodyIndent + creator.asText())

    def writeCollectionFinaliser(self, output):
        output.extend(self.finaliser())

    def getPropList(self):
        # XXX should use sub objects if available, but properties on collection
        # XXX items aren't supported yet
        return RTTI.getPropList(None, self)

class CollectionIddDTC(CollectionDTC):
    windowIdName = 'id'
    idProp = '(undefined)'    
    idPropNameFrom = '(undefined)'

    def evtName(self):
        return '%s%s%d' % (self.name, self.propName, self.index)
    
##    def setIndex(self, idx):
##        CollectionDCT.setIndex(idx)
##        self.setEvents(

    def getEvents(self):
        evts = []
        idxWId = self.getWinId()
        for evt in self.textEventList:
##            print 'GE', evt.windowid, idxWId
            if evt.windowid == idxWId:
                evts.append(evt)
        return evts

    def getWinId(self):
        return self.textConstrLst[self.index].params[self.idProp]
        
    def addIds(self, lst):
        for constr in self.textConstrLst:
            lst.append(constr.params[self.windowIdName])
        
    def appendItem(self):
        CollectionDTC.appendItem(self)

        self.generateWindowId(self.index)

    def newWinId(self, itemName):
        return Utils.windowIdentifier(self.designer.controllerView.GetName(), 
              self.name + itemName)
              
    def generateWindowId(self, idx):
##        print 'generateWindowId', idx, self.textConstrLst[idx].params[self.idProp]
        if self.designer: 
            oldId = self.textConstrLst[idx].params[self.idProp]
            newId = self.newWinId('%s%d' % (self.propName, idx))
            
            if oldId != newId:
                self.textConstrLst[idx].params[self.idProp] = newId
                for evt in self.textEventList:
                    if evt.windowid == oldId:
                        evt.windowid = newId

    def SetName(self, oldValue, newValue):
        CollectionDTC.SetName(self, oldValue, newValue)
        self.updateWindowIds()

    def evtGetter(self, name):
        wId = self.getWinId()
        for evt in self.textEventList:
            if evt.event_name == name and evt.windowid == wId:
                return evt.trigger_meth
        return None
        
    def evtSetter(self, name, value):
        wId = self.getWinId()
        for evt in self.textEventList:
            if evt.event_name == name and evt.windowid == wId:
                evt.trigger_meth = value
                return

    def persistEvt(self, name, value, wId = None):
        """ Add a source entry for an event or update the trigger method of
            am existing event. """
        for evt in self.textEventList:
            if evt.event_name == name and evt.windowid == wId: 
##                print 'Already defined'
                evt.trigger_meth = value
                return
        if self.control == self.designer or wId is not None:
            comp_name = ''
        else:
            comp_name = self.name
        self.textEventList.append(methodparse.EventParse(None, comp_name, name, 
                                                         value, wId))
#        print 'PersistEvt', self.textEventList
    
    def updateWindowIds(self):
        for idx in range(len(self.textConstrLst)):
            self.generateWindowId(idx)
# XXX ???
##            for evt in self.textEventList:
##                if evt.windowid:
##                    self.textConstrLst[idx].params[self.idProp]:
##                    evt.windowid = self.id

    def designTimeDefaults(self, vals):
        """ Return a dictionary of parameters for the constructor of a wxPython
            control. e.g. {'name': 'button1', etc) """
        values = copy.copy(vals)
        values[self.idProp] = `wxNewId()`
        dts = CollectionDTC.designTimeDefaults(self, values)
        dts[self.idProp] = wxNewId()
        return dts
    
