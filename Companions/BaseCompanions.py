#-------------------------------------------------------------------------------
# Name:        BaseCompanions.py
# Purpose:     Classes that 'shadow' controls. They implement design time
#              behaviour and interfaces
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2002 Riaan Booysen
# Licence:     GPL
#-------------------------------------------------------------------------------

""" Classes that 'shadow' controls.

They implement design time behaviour and interfaces. Also used for inspectable
objects """

print 'importing Companions'

import string, copy

from wxPython.wx import *

import Preferences, Utils

from PropEdit.PropertyEditors import *
from Constructors import WindowConstr
import RTTI, EventCollections
import methodparse

bodyIndent = Utils.getIndentBlock()*2

# XXX parent passed in constr not used

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
    * define event and name for popup menu on component
    * overrideable method or new multi inheritance class
      for palette creation in container companions,

"""

class Companion:
    """ Default companion, entity with a name and default documentation """
    def __init__(self, name):
        self.name = name
    def getPropertyHelp(self, propName):
        return propName

class CodeCompanion(Companion):
    pass

class DesignTimeCompanion(Companion):
    """ Base class for all companions participating in the design-time process.
    """
    handledConstrParams = ()
    suppressWindowId = false
    def __init__(self, name, designer):
        Companion.__init__(self, name)
        self.parentCompanion = None
        self.designer = designer
        # Design time window id
        self.dId = wxNewId()
        self.id = None

        # Property editors for properties whose types cannot be deduced
        self.editors = {'Class': ClassConstrPropEdit}
        # Enumerated values for the options of a property editor
        self.options = {}
        # Enumerated display values for the options of a property editor
        # XXX Change to something less generic
        self.names = {}

        # Companion methods that must be called when a property changes
        self.triggers = {'Name': self.SetName}
        # Companions for properties for which a companion can not be deduced
        self.subCompanions = {}
        # Parsers for special properties, given string value should
        # return valid wxPython object
        # The property evaluator should return a tuple of arguments
        # as customPropEvaluators are also used to initialise multi parameter
        # properties
        self.customPropEvaluators = {}
        # Properties that should be initialised thru the companion instead of
        # directly on the control. Usually this applies to 'write-only'
        # properties whose values cannot otherwise be determined
        # It's keyed on the property name and if the setter does not start
        # with Set*, it's keyed on the setter name
        self.initPropsThruCompanion = []
        # Run time dict of created collection companions
        self.collections = {}
        # Can't work, remove
        self.letClickThru = false
        # Mutualy depentent props
        # These props will all be refeshed in the inspector when any one of
        # them is updated
        self.mutualDepProps = []
        # Flag for controls which do not process mouse events correctly
        self.ctrlDisabled = false

#        SetterOverrides = {}

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

    def extraConstrProps(self):
        return {}

#    def defaults(self):
#        return {}

    def getPropList(self):
        propList = RTTI.getPropList(self.control, self)
        pw = RTTI.PropertyWrapper('Class', 'CompnRoute', self.GetClass, self.SetClass)
        propList['constructor'].append(pw)
        return propList

    def GetClass(self, dummy=None):
        return self.textConstr.class_name

    def SetClass(self, value):
        self.textConstr.class_name = value

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
        return ['Class']

    def onlyPersistProps(self):
        """ Properties that should not be applied at design-time and should
            only be applied to the source """
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
            return self.names[prop]
        else:
            return None

    def evtGetter(self, name):
        for evt in self.textEventList:
            if evt.event_name == name: return evt.trigger_meth
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

        self.designer.addCtrlToObjectCollection(self.textConstr)

    def persistCollInit(self, method, ctrlName, propName, params = {}):
        """ Define a new collection init method for source code, called when
            creating a new item in CollectionEditor
        """

        collInitParse = methodparse.CollectionInitParse(None, ctrlName, method,
          [], propName)

        self.parentCompanion.textCollInitList.append(collInitParse)

        self.designer.addCollToObjectCollection(collInitParse)

    def checkTriggers(self, name, oldValue, newValue):
        #trigger specially handled callbacks for property changes with consequences
        if self.triggers.has_key(name):
            self.triggers[name](oldValue, newValue)

    def getCompName(self):
        if id(self.control) == id(self.designer):
            return ''
        else:
            return self.name

    def persistProp(self, name, setterName, value):
        c = self.constructor()
        #constructor
        if c.has_key(name):
            self.textConstr.params[c[name]] = value
        #property
        elif name not in self.dontPersistProps():
            for prop in self.textPropList:
                if prop.prop_setter == setterName:
                    prop.params = [value]
                    return

            self.textPropList.append(methodparse.PropertyParse( \
                None, self.getCompName(), setterName, [value], name))

    def persistedPropVal(self, name, setterName):
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

    def propRevertToDefault(self, name, setterName):
        """ Removes property methods from source and revert constructor
            parameters to default values """
        c = self.constructor()
        #constructor
        if c.has_key(name):
            defVal = self.designTimeSource()[c[name]]
            self.textConstr.params[c[name]] = defVal
        #property
        elif name not in self.dontPersistProps():
            idx = 0
            while idx < len(self.textPropList):
                prop = self.textPropList[idx]
                if prop.prop_setter == setterName:
                    del self.textPropList[idx]
                else:
                    idx = idx + 1

    def propIsDefault(self, name, setterName):
        """ Returns true if no modification has been made to the property
            or constructor parameter """
        c = self.constructor()
        #constructor
        if c.has_key(name):
            dts = self.designTimeSource()
            if dts.has_key(c[name]):
                defVal = self.designTimeSource()[c[name]]
                return self.textConstr.params[c[name]] == defVal
            else:
                return true
        #property
        elif name not in self.dontPersistProps():
            for prop in self.textPropList:
                if prop.prop_setter == setterName:
                    return false
        return true

    def persistEvt(self, name, value, wId = None):
        """ Add a source entry for an event or update the trigger method of
            am existing event. """
        for evt in self.textEventList:
            if evt.event_name == name:
                evt.trigger_meth = value
                return
        if self.control == self.designer or not isinstance(self.control, wxEvtHandlerPtr): # or wId is not None:
            comp_name = ''
        else:
            comp_name = self.name
        self.textEventList.append(methodparse.EventParse(None, comp_name, name,
                                                         value, wId))

    def evtName(self):
        return self.name

    def addIds(self, lst):
        if self.id is not None:
            lst.append(self.id)

    def renameEventListIds(self, wId):
        for evt in self.textEventList:
            if evt.windowid and evt.windowid not in EventCollections.reservedWxIds:
                evt.windowid = wId

    def setProp(self, name, value):
        """ Optional callback companions can override for extra functionality
            after updating a property e.g. refreshing """
        pass

    def SetName(self, oldValue, newValue):
        """ Triggered when the 'Name' property is changed """
        if self.designer.objects.has_key(newValue):
            wxLogError('There is already an object named '+newValue)
        else:
            self.name = newValue
            self.designer.model.renameCtrl(oldValue, newValue)
            self.designer.renameCtrl(oldValue, newValue)

    def renameCtrl(self, oldName, newName):
        self.textConstr.comp_name = newName
        for prop in self.textPropList:
            prop.comp_name = newName
        for collInit in self.textCollInitList:
            collInit.renameCompName2(oldName, newName)
        for evt in self.textEventList:
            if evt.comp_name:
                evt.comp_name = newName

    def renameCtrlRefs(self, oldName, newName):
        """ Notification of a the rename of another control, used to fix up
            references
        """
        if self.textConstr:
            self.textConstr.renameCompName2(oldName, newName)
        for prop in self.textPropList:
            prop.renameCompName2(oldName, newName)

    def getPropNameFromSetter(self, setter):
        props = self.properties()
        for prop in props.keys():
            if props[prop][1] and props[prop][1].__name__ == setter:
                return prop
        if setter[:3] == 'Set': return setter[3:]
        else: return setter

    def eval(self, expr):
        import PaletteMapping
        return PaletteMapping.evalCtrl(expr, self.designer.model.specialAttrs)

    def defaultAction(self):
        """ Invoke the default property editor for this component,
            This can be anything from a custom editor to an event.
        """
        pass

    def notification(self, compn, action):
        """ Called after components are added and before they are removed.
            Used for initialisation or finalisation hooks in other
            components.
        """
        pass

    def writeImports(self):
        """ Return import line that will be added to module
        """
        return None

#---Source writing methods------------------------------------------------------
    def writeConstructor(self, output, collectionMethod, stripFrmId=''):
        """ Writes out constructor and parameters for control
        """
        # Add constructor
        if self.textConstr:
            output.append(bodyIndent + self.textConstr.asText(stripFrmId))
            # XXX HACK attack
            # Add call to init utils after frame constructor
            if self.textConstr.comp_name == '' and \
              collectionMethod == '_init_ctrls':
                output.append(bodyIndent + 'self._init_utils()')

    nullProps = ('None',)
    def writeProperties(self, output, ctrlName, definedCtrls, deps, depLinks, stripFrmId=''):
        """ Write out property setters but postpone dependent properties.
        """
        # Add properties
        for prop in self.textPropList:
            # Skip blanked out props
            if len(prop.params) == 1 and prop.params[0] in self.nullProps:
                continue
            # Postpone dependent props
            if self.designer.checkAndAddDepLink(ctrlName, prop,
                  self.dependentProps(), deps, depLinks, definedCtrls):
                continue
            output.append(bodyIndent + prop.asText(stripFrmId))

    def writeEvents(self, output, module=None, stripFrmId=''):
        """ Write out EVT_* calls for all events. Optionally For every event
            definition not defined in source add an empty method declaration to
            the bottom of the class """
        for evt in self.textEventList:
            if evt.trigger_meth != '(delete)':
                output.append(bodyIndent + evt.asText(stripFrmId))
                model = self.designer.model
                ##module = model.getModule()
                # Either rename the event or add if a new one
                # The first streamed occurrence will do the rename or add
                if evt.prev_trigger_meth and module and module.classes[
                      model.main].methods.has_key(evt.prev_trigger_meth):
                    module.renameMethod(model.main, evt.prev_trigger_meth,
                          evt.trigger_meth)
                elif module and not module.classes[
                      model.main].methods.has_key(evt.trigger_meth):
                    module.addMethod(model.main, evt.trigger_meth,
                          'self, event', [bodyIndent + 'event.Skip()'])

    def writeCollections(self, output, collDeps, stripFrmId=''):
        # Add collection initialisers
        for collInit in self.textCollInitList:
            if collInit.getPropName() in self.dependentProps():
                collDeps.append(bodyIndent + collInit.asText(stripFrmId))
            else:
                output.append(bodyIndent + collInit.asText(stripFrmId))

    def writeDependencies(self, output, ctrlName, depLinks, definedCtrls, stripFrmId=''):
        """ Write out dependent properties if all the ctrls they reference
            have been created.
        """
        if depLinks.has_key(ctrlName):
            for prop, otherRefs in depLinks[ctrlName]:
                for oRf in otherRefs:
                    if oRf not in definedCtrls:
                        # special attrs are not 'reference dependencies'
                        if not hasattr(self.designer.model.specialAttrs['self'], oRf):
                            break
                else:
                    output.append(bodyIndent + prop.asText(stripFrmId))



class NYIDTC(DesignTimeCompanion):
    """ Blank holder for companions which have not been implemented."""
    host = 'Not Implemented'
    def __init__(self, name, designer, parent, ctrlClass):
        raise 'Not Implemented'


class ControlDTC(DesignTimeCompanion):
    """ Visible controls created on a Frame and defined from
        _init_ctrls.
    """
    handledConstrParams = ('id', 'parent')
    windowIdName = 'id'
    windowParentName = 'parent'
    host = 'Designer'
    def __init__(self, name, designer, parent, ctrlClass):
        DesignTimeCompanion.__init__(self, name, designer)
        self.parent = parent
        self.ctrlClass = ctrlClass
        self.generateWindowId()
        self.container = false


    def designTimeControl(self, position, size, args = None):
        """ Create and initialise a design-time control """
        if args:
            self.control = apply(self.ctrlClass, (), args)
        else:
            self.control = apply(self.ctrlClass, (), self.designTimeDefaults(position, size))

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
            dts[param] = self.eval(dts[param])

        dts[self.windowParentName] = self.parent

        if not self.suppressWindowId:
            dts[self.windowIdName] = self.dId

        return dts

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        """ Return a dictionary of parameters for the constructor of a wxPython
            control's source. 'parent' and 'id' handled automatically
        """
        return {}

    def generateWindowId(self):
        if self.designer:
            self.id = Utils.windowIdentifier(self.designer.GetName(), self.name)
        else: self.id = `wxNewId()`

    def SetName(self, oldValue, newValue):
        DesignTimeCompanion.SetName(self, oldValue, newValue)
        self.updateWindowIds()

    def extraConstrProps(self):
        return {'Class': 'class'}

##    def GetClass(self, dummy):
##        return self.control.__class__.__name__
##
##    def SetClass(self, value):
##        raise 'Cannot change'

    def updateWindowIds(self):
        self.generateWindowId()
        if not self.suppressWindowId:
            EventCollections.renameCmdIdInDict(self.textConstr.params, self.windowIdName, self.id)
            self.renameEventListIds(self.id)

    def initDesignTimeEvents(self, ctrl):
        # XXX Uncommenting this causes a crash after the first
        # XXX OnMouseOver event
        # By pushing the eventhandler, even ctrls
        # that hook to the Mouse events will still cause
        # mouse event to fire (theoretically)
        # ctrl.PushEventHandler(self.designer.ctrlEvtHandler)
        self.designer.ctrlEvtHandler.connectEvts(ctrl)

    def initDesignTimeControl(self):
        #try to set the name
        try:
            self.control.SetName(self.name)
            self.control.SetToolTipString(self.name)
            # Disabled controls do not pass thru mouse clicks to their parents on GTK :(
            if wxPlatform != '__WXGTK__' and self.ctrlDisabled:
                self.control.Enable(false)
        except:
            pass

        self.initDesignTimeEvents(self.control)

        self.popx = self.popy = 0

        EVT_RIGHT_DOWN(self.control, self.designer.OnRightDown)
        # for wxMSW
#        EVT_COMMAND_RIGHT_CLICK(self.control, -1, self.designer.OnRightClick)
        # for wxGTK
        EVT_RIGHT_UP(self.control, self.designer.OnRightClick)

    def beforeResize(self):
        pass
        #print 'beforeResize'

    def afterResize(self):
        pass
        #print 'afterResize'

    def updatePosAndSize(self):
        if self.textConstr and self.textConstr.params.has_key('pos') \
              and self.textConstr.params.has_key('size'):
            pos = self.control.GetPosition()
            size = self.control.GetSize()
            self.textConstr.params['pos'] = 'wxPoint(%d, %d)' % (pos.x, pos.y)
            self.textConstr.params['size'] = 'wxSize(%d, %d)' % (size.x, size.y)

    def getDefCtrlSize(self):
        return 'wxSize(%d, %d)'%(Preferences.dsDefaultControlSize.x,
                                 Preferences.dsDefaultControlSize.y)


    def getPositionDependentProps(self):
        return [('constr', 'Position'), ('prop', 'Position')]

    def getSizeDependentProps(self):
        return [('constr', 'Size'), ('prop', 'Size'), ('prop', 'ClientSize')]

class MultipleSelectionDTC(DesignTimeCompanion):
    """ Semi mythical class at the moment that will represent a group of
        selected objects. It's properties should represent the common subset
        of properties of the selection.

        Currently only used so the inspector has something to hold on to during
        multiple selection
    """

# sub properties (Font etc)
class HelperDTC(DesignTimeCompanion):
    """ Helpers are subobjects or enumerations of properties. """
    def __init__(self, name, designer, ownerCompanion, obj, ownerPropWrap):
        DesignTimeCompanion.__init__(self, name, designer)
        self.control = obj
#        self.obj = obj
        self.ownerCompn = ownerCompanion
        self.owner = ownerCompanion.control
        self.ownerPW = ownerPropWrap

        self.updateObjFromOwner()

    def updateObjFromOwner(self):
        """ The object to which a sub object is connected may change
            this method reconnects the property to the current object.
        """
        self.obj = self.ownerPW.getValue(self)
        self.ctrl = self.obj
        self.control = self.obj

    def updateOwnerFromObj(self):
        """ Changes to subobjects do not reflect in their owners
            automatically they have to be reassigned to their
            property
        """
        self.ownerPW.setValue(self.obj)

    def persistProp(self, name, setterName, value):
        """ When a subobject's property is told to persist, it
            should persist it's owner

           This is currently managed by the property editor
        """
        pass

# non-visual classes (Imagelists, etc)
class UtilityDTC(DesignTimeCompanion):
    """ Utility companions are 'invisible' components that
        are not owned by the Frame.

        Utilities are created before the frame and controls
        and defined in the _init_utils method.
    """

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
            dts[param] = self.eval(dts[param])
        return dts

    def updateWindowIds(self):
        pass

    def updatePosAndSize(self):
        pass

# XXX Parents, from constructor or current selected container in designer
class WindowDTC(WindowConstr, ControlDTC):
    """ Defines the wxWindow interface overloading/defining specialised
        property editors. """
    def __init__(self, name, designer, parent, ctrlClass):
        ControlDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors.update({'AutoLayout': BoolPropEdit,
                        'Shown': BoolPropEdit,
                        'Enabled': BoolPropEdit,
                        #'EvtHandlerEnabled': BoolPropEdit,
                        'Style': StyleConstrPropEdit,
                        'Constraints': CollectionPropEdit,
                        'Name': NamePropEdit,
                        'Anchors': AnchorPropEdit,
                        #'Sizer': SizerClassLinkPropEdit,
                        'SizeHints': TuplePropEdit,
                        'Cursor': CursorClassLinkPropEdit,
                        'Centered': EnumPropEdit,
                        })
        self.options['Centered'] = [None, wxHORIZONTAL, wxVERTICAL, wxBOTH]
        self.names['Centered'] = {'None': None, 'wxHORIZONTAL': wxHORIZONTAL,
                                  'wxVERTICAL': wxVERTICAL, 'wxBOTH': wxBOTH}
        self.triggers.update({'Size'     : self.SizeUpdate,
                              'Position' : self.PositionUpdate})
        self.customPropEvaluators.update({'Constraints': self.EvalConstraints,
                                          'SizeHints': self.EvalSizeHints,})

        self.windowStyles = ['wxCAPTION', 'wxMINIMIZE_BOX', 'wxMAXIMIZE_BOX',
                             'wxTHICK_FRAME', 'wxSIMPLE_BORDER', 'wxDOUBLE_BORDER',
                             'wxSUNKEN_BORDER', 'wxRAISED_BORDER',
                             'wxSTATIC_BORDER', 'wxTRANSPARENT_WINDOW', 'wxNO_3D',
                             'wxTAB_TRAVERSAL', 'wxWANTS_CHARS',
                             'wxNO_FULL_REPAINT_ON_RESIZE', 'wxVSCROLL', 'wxHSCROLL',
                             'wxCLIP_CHILDREN']

        self.mutualDepProps = ['Value', 'Title', 'Label']

        import UtilCompanions
        self.subCompanions['Constraints'] = UtilCompanions.IndividualLayoutConstraintOCDTC
        #self.subCompanions['SizeHints'] = UtilCompanions.SizeHintsDTC
        self.anchorSettings = []
        self._applyConstraints = false
        self.initPropsThruCompanion = ['SizeHints', 'Cursor', 'Center']
        self._sizeHints = (-1, -1, -1, -1)
        self._cursor = None
        self._centered = None

    def properties(self):
        return {'Shown': ('CompnRoute', self.GetShown, self.Show),
                'Enabled': ('CompnRoute', self.GetEnabled, self.Enable),
                'ToolTipString': ('CompnRoute', self.GetToolTipString, self.SetToolTipString),
                'Anchors': ('CompnRoute', self.GetAnchors, self.SetConstraints),
                'SizeHints': ('CompnRoute', self.GetSizeHints, self.SetSizeHints),
                'Cursor': ('CompnRoute', self.GetCursor, self.SetCursor),
                'Centered': ('CompnRoute', self.GetCentered, self.Center),
                }

    def designTimeSource(self, position = 'wxDefaultPosition', size = 'wxDefaultSize'):
        return {'pos':  position,
                'size': self.getDefCtrlSize(),
                'name': `self.name`,
                'style': '0'}

    def dependentProps(self):
        return ['Cursor']

    def onlyPersistProps(self):
        return ['Show', 'Enable']

    def hideDesignTime(self):
        return ['NextHandler', 'PreviousHandler', 'EventHandler', 'EvtHandlerEnabled', 
                'Id', 'Caret', 'WindowStyleFlag', 'ToolTip', 'Title', 'Rect',
                'DragTarget', 'DropTarget','Cursor', 'VirtualSize',
                'Sizer', 'ContainingSizer']

    def dontPersistProps(self):
        return ControlDTC.dontPersistProps(self) + ['ClientSize']
    def applyRunTime(self):
        return ['Shown', 'Enabled', 'EvtHandlerEnabled']
    def events(self):
        return ['MiscEvent', 'MouseEvent', 'FocusEvent', 'KeyEvent', 'HelpEvent']

#---ToolTips--------------------------------------------------------------------
    def GetToolTipString(self, blah):
        return self.control.GetToolTip().GetTip()

    def SetToolTipString(self, value):
        self.control.SetToolTipString(value)

#---Anchors---------------------------------------------------------------------
    from wxPython.lib.anchors import LayoutAnchors

    def writeImports(self):
        if self.anchorSettings:
            return 'from wxPython.lib.anchors import LayoutAnchors'
        else:
            return None

    def GetAnchors(self, compn):
        if self.anchorSettings:
            return apply(self.LayoutAnchors, [self.control] + self.anchorSettings)
        else:
            return None

    # Named like the wxWindow method to override it when generating code
    def SetConstraints(self, value):
        curVal = self.control.GetConstraints()
        if curVal != value:
            self.control.SetConstraints(value)
        if self.designer.selection:
            self.designer.selection.updateAnchors()
        elif self.designer.multiSelection:
            for selection in self.designer.multiSelection:
                selection.updateAnchors()
        self.designer.inspector.propertyUpdate('Anchors')

    def EvalConstraints(self, exprs, objects):
        if Utils.startswith(exprs[0], 'LayoutAnchors'):
            ctrl, left, top, right, bottom = \
             methodparse.safesplitfields(exprs[0][len('LayoutAnchors')+1:-1], ',')
            ctrl, left, top, right, bottom = (objects[ctrl], self.eval(left),
                  self.eval(top), self.eval(right), self.eval(bottom))
            self.anchorSettings = [left, top, right, bottom]
            return (self.LayoutAnchors(ctrl, left, top, right, bottom), )
        return (None,)

    def updateAnchors(self, flagset, value):
        if not self.anchorSettings:
            self.defaultAnchors()

        for idx in range(4):
            if flagset[idx]:
                self.anchorSettings[idx] = value

    def removeAnchors(self):
        self.anchorSettings = []
        idx = 0
        while idx < len(self.textPropList):
            prop = self.textPropList[idx]
            if prop.prop_setter == 'SetConstraints' and \
                  Utils.startswith(prop.params[0], 'LayoutAnchors'):
                del self.textPropList[idx]
                break
            else:
                idx = idx + 1

    def defaultAnchors(self):
        self.anchorSettings = [true, true, false, false]

    def applyConstraints(self):
        left, top, right, bottom = self.anchorSettings
        self.control.SetConstraints( \
            self.LayoutAnchors(self.control, left, top, right, bottom))

    def beforeResize(self):
        lc = self.control.GetConstraints()
        self._applyConstraints = lc != None and self.anchorSettings
        if self._applyConstraints:
            self.SetConstraints(None)

    def afterResize(self):
        if self._applyConstraints and self.anchorSettings:
            self.applyConstraints()

#---Designer updaters-----------------------------------------------------------
    def SizeUpdate(self, oldValue, newValue):
        if self.designer.selection:
            self.designer.selection.selectCtrl(self.control, self)
            self.designer.selection.moveCapture(self.control, self, wxPoint(0, 0))

    def PositionUpdate(self, oldValue, newValue):
        if self.designer.selection:
            self.designer.selection.selectCtrl(self.control, self)
            self.designer.selection.moveCapture(self.control, self, wxPoint(0, 0))

#---Size hints------------------------------------------------------------------
    def GetSizeHints(self, dummy):
        return self._sizeHints

    def SetSizeHints(self, value):
        self._sizeHints = value
        self.control.SetSizeHints(value[0], value[1], value[2], value[3])

    def EvalSizeHints(self, exprs, objects):
        res = []
        for expr in exprs:
            res.append(self.eval(expr))
        return tuple(res)

    def persistProp(self, name, setterName, value):
        if setterName == 'SetSizeHints':
            minW, minH, maxW, maxH = self.eval(value)
            newParams = [`minW`, `minH`, `maxW`, `maxH`]
            # edit if exists
            for prop in self.textPropList:
                if prop.prop_setter == setterName:
                    prop.params = newParams
                    return
            # add if not defined
            self.textPropList.append(methodparse.PropertyParse( None,
                self.getCompName(), setterName, newParams, 'SetSizeHints'))
        else:
            ControlDTC.persistProp(self, name, setterName, value)

#---Cursors---------------------------------------------------------------------

    def GetCursor(self, x):
        return self._cursor

    def SetCursor(self, value):
        self._cursor = value
        self.control.SetCursor(value)

    def notification(self, compn, action):
        if action == 'delete':
            if self._cursor and `self._cursor` == `compn.control`:
                self.propRevertToDefault('Cursor', 'SetCursor')
                self.SetCursor(wxNullCursor)

#-------------------------------------------------------------------------------

    def GetCentered(self, dummy):
        return self._centered
    def Center(self, value):
        self._centered = value
        if value:
            self.control.Center(value)

    def GetShown(self, x):
        for prop in self.textPropList:
            if prop.prop_setter == 'Show':
                return prop.params[0] == 'true'
        return true
    def Show(self, value):
        pass
    def GetEnabled(self, x):
        for prop in self.textPropList:
            if prop.prop_setter == 'Enable':
                return prop.params[0] == 'true'
        return true
    def Enable(self, value):
        pass


class ChoicedDTC(WindowDTC):
    def __init__(self, name, designer, parent, ctrlClass):
        WindowDTC.__init__(self, name, designer, parent, ctrlClass)
        self.editors['Choices'] = ChoicesConstrPropEdit

class ContainerDTC(WindowDTC):
    """ Parent for controls that contain/own other controls """
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
        DesignTimeCompanion.renameCtrl(self, oldName, newName)
        self.setCollectionMethod()

    def renameCtrlRefs(self, oldName, newName):
        # textConstr and textPropList not used in collections
        # DesignTimeCompanion.renameCtrlRefs(self, oldName, newName)
        for constr in self.textConstrLst:
            constr.renameCompName2(oldName, newName)

    def getCount(self):
        return len(self.textConstrLst)

    def getDisplayProp(self):
        return self.eval(self.textConstrLst[self.index].params[self.displayProp])

    def initialiser(self):
        """ When overriding, append this after derived initialiser """
        return ['']

    def finaliser(self):
        """ When overriding, append this before derived finaliser """
        return []

    def appendItem(self):
        self.index = self.getCount()
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
            getattr(self.control, self.deletionMethod)(idx)

        del self.textConstrLst[idx]
        # renumber items following deleted one
        if self.indexProp != '(None)':
            for constr in self.textConstrLst[idx:]:
                constr.params[self.indexProp] = `int(constr.params[self.indexProp]) -1`

    def applyDesignTimeDefaults(self, params):
        apply(getattr(self.control, self.insertionMethod), (),
              self.designTimeDefaults(params))

    def SetName(self, oldValue, newValue):
        self.name = newValue
        self.setCollectionMethod()

    def GetClass(self, dummy=None):
        return self.propName

    def SetClass(self, value):
        pass

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
            dtd[param] = self.eval(vals[param])
        return dtd

    def initCollection(self):
        pass

    def writeCollectionInitialiser(self, output, stripFrmId=''):
        output.extend(self.initialiser())

    def writeCollectionItems(self, output, stripFrmId=''):
        for creator in self.textConstrLst:
            output.append(bodyIndent + creator.asText(stripFrmId))

    def writeCollectionFinaliser(self, output, stripFrmId=''):
        output.extend(self.finaliser())

    def getPropList(self):
        """ Returns a dictionary of methods suported by the control

            The dict has 'properties' and 'methods' keys which contain the
            getters/setters and undefined methods.
         """
        # XXX should use sub objects if available, but properties on collection
        # XXX items aren't supported yet
        return RTTI.getPropList(None, self)

    def defaultAction(self):
        """ Called when a component is double clicked in a designer
        """
        pass
##        print 'CDTC', self.textConstrLst[self.index]

    def notification(self, compn, action):
        """ Called when other components are deleted.

            Use it to clear references to components which are being deleted.
        """
        # XXX Should use this mechanism to trap renames as well
        pass
##        print 'CollectionDTC.notification', compn, action

class CollectionIddDTC(CollectionDTC):
    """ Collections which have window ids and events """
    windowIdName = 'id'
    idProp = '(undefined)'
    idPropNameFrom = '(undefined)'

    def __init__(self, name, designer, parentCompanion, ctrl):
        CollectionDTC.__init__(self, name, designer, parentCompanion, ctrl)
        self.editors = {'ItemId': ItemIdConstrPropEdit}

    def properties(self):
        props = CollectionDTC.properties(self)
        props['ItemId'] = ('CompnRoute', self.GetItemId, self.SetItemId)
        return props

    def evtName(self):
        return '%s%s%d' % (self.name, self.propName, self.index)

##    def setIndex(self, idx):
##        CollectionDCT.setIndex(idx)
##        self.setEvents(

    def getEvents(self):
        evts = []
        idxWId = self.getWinId()
        for evt in self.textEventList:
            if evt.windowid == idxWId:
                evts.append(evt)
        return evts

    def getWinId(self):
        return self.textConstrLst[self.index].params[self.idProp]

    def addIds(self, lst):
        for constr in self.textConstrLst:
            lst.append(constr.params[self.idProp])

    def appendItem(self):
        CollectionDTC.appendItem(self)

#1        self.generateWindowId(self.index)
        self.updateWindowIds()

    def deleteItemEvents(self, idx):
        wIdStr = self.textConstrLst[idx].params[self.idProp]
        for evt in self.textEventList[:]:
            if evt.windowid == wIdStr:
                self.textEventList.remove(evt)

    def deleteItem(self, idx):
        self.deleteItemEvents(idx)
        CollectionDTC.deleteItem(self, idx)

        self.updateWindowIds()

    def newUnusedItemNames(self, wId):
        while 1:
            newItemName = '%s%d'%(self.propName, wId)
            winId = self.newWinId(newItemName)
            if self.isIdUsed(winId): wId = wId + 1
            else: break
        return newItemName, winId

    def isIdUsed(self, wId):
        for tc in self.textConstrLst:
            if tc.params[self.idProp] == wId:
                return true
        return false


    def newWinId(self, itemName):
        return Utils.windowIdentifier(self.designer.controllerView.GetName(),
              self.name + itemName)

    def generateWindowId(self, idx):
        if self.designer:
            oldId = self.textConstrLst[idx].params[self.idProp]
            newId = self.newWinId('%s%d' % (self.propName, idx))

            if oldId != newId and oldId not in EventCollections.reservedWxIds:
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
                evt.trigger_meth = value
                return
        if self.control == self.designer or wId is not None:
            comp_name = ''
        else:
            comp_name = self.name
        self.textEventList.append(methodparse.EventParse(None, comp_name, name,
                                                         value, wId))

    def updateWindowIds(self):
        for idx in range(len(self.textConstrLst)):
            self.generateWindowId(idx)

    def designTimeDefaults(self, vals):
        """ Return a dictionary of parameters for the constructor of a wxPython
            control. e.g. {'name': 'button1', etc) """
        values = copy.copy(vals)
        values[self.idProp] = `wxNewId()`
        dts = CollectionDTC.designTimeDefaults(self, values)
        dts[self.idProp] = wxNewId()
        return dts

    def GetItemId(self, x):
        return self.textConstrLst[self.index].params[self.idProp]

    def SetItemId(self, value):
        oldValue = self.textConstrLst[self.index].params[self.idProp]
        self.textConstrLst[self.index].params[self.idProp] = value
        for evt in self.textEventList:
            if evt.windowid == oldValue:
                evt.windowid = value
