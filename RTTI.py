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

def getPropList(obj, cmp):
    """
       Function to extract sorted list of properties and getter/setter methods
       from a given object and companion
       
       Returns a structure that looks like this
       
       {'constructor': [ [name, (getter, setter)], ...],
        'properties': [ [name, (getter, setter)], ...]}
        
    
    """
    def getMethodType(method, obj, dict):
        """ classify methods according to prefix
            return category, property name, getter, setter
        """
        
        if (type(dict[method]) == FunctionType):
            prefix = method[:3]
            property = method[3:]
            
            if (method[:2] == '__'):
 	        return 'Built-ins', method, dict[method], dict[method]

            if (prefix == 'Get') and dict.has_key('Set'+property) and property:
                try:
                    #see if getter breaks
                    v = dict[method](obj)
                    return 'Properties', property, dict[method], dict['Set'+property]
                except:
        	    return 'Methods', method, dict[method], dict[method]
            if (prefix == 'Set') and dict.has_key('Get'+property) and property:
                try:
                    #see if getter breaks
                    v = dict['Get'+property](obj)
 	            return 'Properties', property, dict['Get'+property], dict[method]
                except:
        	    return 'Methods', method, dict[method], dict[method]

 	return 'Methods', method, dict[method], dict[method]
    
    def catalogProperty(name, meths, constructors, propLst, constrLst):
        if constructors.has_key(name):
            constrLst.append([name, meths])
        else:
            propLst.append([name, meths])
        
        

    #getPropList(obj, cmp):
    props = {}
    props['Properties']= {}
    props['Methods']= {}
    props['Built-ins']= {}
    
    # traverse inheritance hierarchy
    if type(obj) is InstanceType:
        cls = obj.__class__
        notDone = true
        while notDone:
	    for m in cls.__dict__.keys():
	        cat, method, methGetter, methSetter = getMethodType(m, obj, cls.__dict__)
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
	    propMeths = props['Properties'][propName]
	    try:
	        catalogProperty(propName, propMeths, constrNames, propLst, constrLst)
	    except:
	        catalogProperty(propName, (None, None), constrNames, propLst, constrLst)
        if cmp:
            xtraProps = cmp.properties()
            propNames = xtraProps.keys()
            propNames.sort()
            for propName in propNames:
	        propMeths = xtraProps[propName]
	        try:
 	            catalogProperty(propName, propMeths, constrNames, propLst, constrLst)
		except: pass
		
	propLst.sort()
	constrLst.sort()

        return {'constructor': constrLst, 'properties': propLst}
    else : 
        print 'Empty object', obj
        return {'constructor': [], 'properties': []}

def getFunction(inst, funcName):
    cls = inst.__class__
    found = cls.__dict__.has_key(funcName)
    while not found:
        if not len(cls.__bases__): raise 'method '+funcName+' not found'
        cls = cls.__bases__[0]
        found = cls.__dict__.has_key(funcName)
    
    return cls.__dict__[funcName]
    
    
