#----------------------------------------------------------------------
# Name:        RTTI.py
# Purpose:     
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
from types import *
from wxPython.wx import *

def sort_proxy(self, other):
    return self < other and -1 or self > other and 1 or 0
    
class PropertyWrapper:
    # XXX This would be better implemented with subclassing
    def __init__(self, name, rType, getter, setter):
        """ Types: 'CtrlRoute', 'CompnRoute', 'EventRoute', 'NoneRoute', 
                   'IndexRoute', 'NameRoute'
        """
    
        self.name = name
        self.routeType = rType
        self.getter = getter
        self.setter = setter 
        self.ctrl = None
        self.compn = None
        
        # Not used yet
        self.setterName = ''
    
    def __cmp__(self, other):
        """ This is for sorting lists of PropertyWrappers """
#        sort_proxy(self.name, other.name)
        if self.name < other.name:
            return -1
        if self.name > other.name:
            return 1
        return 0
    
    def __repr__(self):
        return '<instance PropertyWrapper: %s, %s (%s, %s)'%(self.name, 
          self.routeType, self.getter, self.setter)
    
    def connect(self, ctrl, compn):
        self.ctrl = ctrl
        self.compn = compn
    
    def getValue(self, *params):
##        print 'PropWrapper.GetValue', self.routeType, self.ctrl, self.getter
        if self.routeType == 'CtrlRoute' and self.ctrl:
##            print 'PropWrapper.GetValue.CtrlRoute', self.ctrl, self.getter, self.getter(self.ctrl)
            return self.getter(self.ctrl)
        elif self.routeType == 'CompnRoute' and self.compn:
            return self.getter(self.compn)
        elif self.routeType == 'EventRoute' and self.compn and len(params):
            return self.getter(params[0])
        elif self.routeType == 'IndexRoute' and self.ctrl and len(params):
            return self.getter(self.ctrl, params[0])
        elif self.routeType == 'NameRoute':
            return self.getter(self.name)
        else:
            return None

    def setValue(self, value, *params):
##        print 'PropWrap setValue', self.name, value, self.routeType
        if self.routeType == 'CtrlRoute' and self.ctrl:
            self.setter(self.ctrl, value)
        elif self.routeType == 'CompnRoute' and self.compn:
            self.setter(value)
        elif self.routeType == 'EventRoute' and self.compn and len(params):
            self.setter(params[0], value)
        elif self.routeType == 'IndexRoute' and self.ctrl and len(params):
##            print 'PropWrap setValue index route', self.ctrl, params[0], value
            self.setter(self.ctrl, params[0], value)
        elif self.routeType == 'ReApplyRoute' and self.compn and len(params):
            apply(self.setter, [self.ctrl], params)
        elif self.routeType == 'NameRoute':
            return self.setter(self.name, value)
    
    def getSetterName(self):
        from types import FunctionType, MethodType
        if self.setter:
            if self.setterName:
                return self.setterName
            if type(self.setter) == FunctionType:
                return self.setter.func_name
            if type(self.setter) == MethodType:
                return self.setter.im_func.func_name
            else:
                return ''
        else:
            return ''

_methodTypeCache = {}
def getPropList(obj, cmp):
    """
       Function to extract sorted list of properties and getter/setter methods
       from a given object and companion.
       Property names that also occur in the Constructor list are stored under
       the 'constructor' key
       Vetoes are dangerous methods that should not be inspected
       
       Returns:
       {'constructor': [ PropertyWrapper, ... ],
        'properties': [ PropertyWrapper, ... ] }
            
    """

    def getMethodType(method, obj, dict):
        """ classify methods according to prefix
            return category, property name, getter, setter
        """
    
        if _methodTypeCache.has_key( (method, obj) ):
            return _methodTypeCache[(method, obj)]
        else:
            if (type(dict[method]) == FunctionType):
                prefix = method[:3]
                property = method[3:]
                
                if (method[:2] == '__'):
                     result = ('Built-ins', method, dict[method], dict[method])
                elif (prefix == 'Get') and dict.has_key('Set'+property) and property:
                    try:
                        #see if getter breaks
                        v = dict[method](obj)
                        result = ('Properties', property, dict[method], dict['Set'+property])
                    except:
                        result = ('Methods', method, dict[method], dict[method])
                elif (prefix == 'Set') and dict.has_key('Get'+property) and property:
                    try:
                        #see if getter breaks
                        v = dict['Get'+property](obj)
                        result = ('Properties', property, dict['Get'+property], dict[method])
                    except:
                        result = ('Methods', method, dict[method], dict[method])
                else:
                    result = ('Methods', method, dict[method], dict[method])
            else:
                result = ('Methods', method, dict[method], dict[method])
            
            return result
    
#            return 'Methods', method, dict[method], dict[method]
    
    def catalogProperty(name, methType, meths, constructors, propLst, constrLst):
        if constructors.has_key(name):
            constrLst.append(PropertyWrapper(name, methType, meths[0], meths[1]))
        else:
            propLst.append(PropertyWrapper(name, methType, meths[0], meths[1]))

    #getPropList(obj, cmp):
    props = {}
    props['Properties']= {}
    props['Methods']= {}
    props['Built-ins']= {}
    
    # traverse inheritance hierarchy
##    print 'traverse inheritance hierarchy'
    # populate property list
    propLst = []
    constrLst = []
    vetoes = cmp.vetoedMethods()
    if obj and type(obj) is InstanceType:
        cls = obj.__class__
        notDone = true
        while notDone:
            for m in cls.__dict__.keys():
                if m not in vetoes:
                    cat, method, methGetter, methSetter = \
                      getMethodType(m, obj, cls.__dict__)
                    props[cat][method] = (methGetter, methSetter)
            notDone = len(cls.__bases__)
            if notDone:
                cls = cls.__bases__[0]

        # populate property list
        propLst = []
        constrLst = []
        if cmp:
            constrNames = cmp.constructor()
        else:
            constrNames = {}
        propNames = props['Properties'].keys()
        propNames.sort()
        for propName in propNames:
            if cmp and propName in cmp.hideDesignTime(): 
                continue
            propMeths = props['Properties'][propName]
            try:
                catalogProperty(propName, 'CtrlRoute', propMeths, 
                  constrNames, propLst, constrLst)
            except:
                catalogProperty(propName, 'NoneRoute', (None, None), 
                  constrNames, propLst, constrLst)
        if cmp:
            xtraProps = cmp.properties()
            propNames = xtraProps.keys()
            propNames.sort()
            for propName in propNames:
##                if propName in cmp.hideDesignTime():
##                    continue
                propMeths = xtraProps[propName]
                try:
                    catalogProperty(propName, propMeths[0], propMeths[1:], 
                      constrNames, propLst, constrLst)
                except: pass

        propLst.sort()
        constrLst.sort()
    else : 
        if cmp:
            xtraProps = cmp.properties()
            propNames = xtraProps.keys()
            propNames.sort()
            for propName in propNames:
                propMeths = xtraProps[propName]
                try:
                    catalogProperty(propName, propMeths[0], propMeths[1:], 
                      constrNames, propLst, constrLst)
                except: pass
        else:
            print 'Empty object', obj, cmp
        
    return {'constructor': constrLst, 'properties': propLst}

def getFunction(inst, funcName):
    cls = inst.__class__
    found = cls.__dict__.has_key(funcName)
    while not found:
        if not len(cls.__bases__): raise 'method '+funcName+' not found'
        cls = cls.__bases__[0]
        found = cls.__dict__.has_key(funcName)
    
    return cls.__dict__[funcName]
    
