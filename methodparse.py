#----------------------------------------------------------------------
# Name:        methodparse.py
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

Creation

self.<componentname> = <wxClassname>(<constr params>) 

constructor
     compname
     classname
     params

Initialisation

self.<componentname>.?Set?<propertyname>(<value>)

property
    compname
    propname
    value
    

Event connection
(2 identified formats)
EVT_<event>(<connect to>, [<windowid>], <eventmethod>)

event
    eventname
    compname
    windowid
    triggermeth

---------------------------

Boilerplate

class frame1(wxFrame):
    def _init_create(self):
        pass
    
    def _init_props(self):
        pass
        
    def _init_event(self):
        pass
    
    def _init(self):
        self._init_create()
        self._init_props()
        self._init_event()

    def __init__(self):
        self._init()
        
"""

from string import strip, split, join, find, rfind
import re

delimeters = [('(', ')'), ('{', '}'), ('[', ']')]
delimBegin = map(lambda d: d[0], delimeters)    
delimEnd = map(lambda d: d[1], delimeters)    

def incLevel(level, pos):
    return level + 1, pos + 1

def decLevel(level, pos):
    return max(level - 1, 0), pos + 1

def safesplitfields(params, delim):
    """ Returns a list of parameters split on delim but not if commas are 
        within (), {}, [], '', ""  
        Also skip '', "" content  """
    
    locparams =  params
    list = []
    i = 0
    nestlevel = 0
    singlequotelevel = 0
    doublequotelevel = 0
    
    while i < len(locparams):
        curchar = locparams[i]
        # only check for delimiter if not inside some block
        if (not nestlevel) and (not singlequotelevel) and (not doublequotelevel) and \
          (curchar == delim):
            param = locparams[:i]
            list.append(param)
            locparams = strip(locparams[i +1:])
            i = 0
            continue
        
        if (not singlequotelevel) and (not doublequotelevel) and nestlevel and \
          (curchar in delimEnd):
            nestlevel, i = decLevel(nestlevel, i)
            continue

        if (not singlequotelevel) and (not doublequotelevel) and \
          (curchar in delimBegin):
            nestlevel, i = incLevel(nestlevel, i)
            continue
 
        # don't check anything except end quotes inside quote blocks
        if singlequotelevel and curchar == "'":
            singlequotelevel, i = decLevel(singlequotelevel, i)
            continue
        if doublequotelevel and curchar == '"':
            doublequotelevel, i = decLevel(doublequotelevel, i)
            continue
        
        if curchar == '"':
            doublequotelevel = doublequotelevel + 1
        elif curchar == "'":
            singlequotelevel = singlequotelevel + 1
        
        i = i + 1
    
    # add last entry not delimited by comma
    list.append(strip(locparams))
    return list


def parseMixedBody(parseClasses, lines):
    """ Return a dictionary with keys representing classes that
        'understood' the line and values a list of found instances
        of the found class """
    cat = {}
    for parseClass in parseClasses:
        cat[parseClass] = []

    for line in lines:
        ln = strip(line)
        if (ln == 'pass') or (ln == ''): continue
        for parseClass in parseClasses:
            try: res = parseClass(ln).value()
            except: pass
            else:
                if res:
                    cat[parseClass].append(res)
#                    print 'found:', parseClass
                    break
    return cat


def parseBody(parseClass, lines):
    list = []
    for line in lines:
        ln = strip(line)
        if ln == 'pass': return []
        if ln == '':
            continue
        list.append(parseClass(ln))
    return list
    
class PerLineParser:
    def value(self):
        if self.m: return self
        else: return None
    def asText(self):
        return ''

id = '[A-Za-z_][A-Za-z0-9_]*'
is_constr = re.compile('^[ \t]*self[.](?P<name>'+id+')[ \t]*=[ \t]*(?P<class>'+\
  id+')\((?P<params>.*)\)$')
is_constr_frm = re.compile('^[ \t]*(?P<class>'+id+\
  ')[.]__init__\(self,[ \t]*(?P<params>.*)\)$')

class ConstructorParse(PerLineParser):
    def __init__(self, line = None, comp_name = '', class_name = '', params = {}):
        self.comp_name = comp_name
        self.class_name = class_name
        self.params = params
        if line:
            self.m = is_constr.search(line)
            if self.m:
                self.comp_name = self.m.group('name')
                self.class_name = self.m.group('class')
                params = safesplitfields(self.m.group('params'), ',')
                self.params = {}
                cnt = 0
                for param in params:
                    kv = split(param, '=')
                    if len(kv) == 2:
                        self.params[strip(kv[0])] = strip(kv[1])
                    else:
                        self.params[`cnt`] = strip(kv[0])
                    cnt = cnt + 1
                        
            else:
                self.m = is_constr_frm.search(line)
                if self.m:
                    self.comp_name = ''
                    self.class_name = self.m.group('class')
                    params = safesplitfields(self.m.group('params'), ',')
                    self.params = {}
                    for param in params:
                        kv = split(param, '=')
                        self.params[strip(kv[0])] = strip(kv[1])
            
    def asText(self):
#        print 'constructor: asText()'
        params = []
        for key in self.params.keys():
            params.append(key+' = '+self.params[key])
        if self.comp_name:
            return 'self.%s = %s(%s)' %(self.comp_name, self.class_name, 
              join(params, ', '))
        else:
            return '%s.__init__(self, %s)' %(self.class_name, join(params, ', '))

def parseConstructors(body):
    return parseBody(ConstructorParse, body)

idp = '[A-Za-z_][A-Za-z0-9_.]*'
is_prop = re.compile('^[ \t]*(?P<name>'+idp+')[ \t]*\([ \t]*(?P<params>.*)[ \t]*\)$')
class PropertyParse(PerLineParser):
    def __init__(self, line = None, comp_name = '', prop_setter = '', params = []):
        self.comp_name = comp_name
        self.prop_setter = prop_setter
        self.params = params
        if line:
            self.m = is_prop.search(line)
            if self.m:
                self.params = safesplitfields(self.m.group('params'), ',')
                compsetter = split(self.m.group('name'), '.')
                    
                if len(compsetter) < 2: raise 'atleast 2 required '+`compsetter`
                if compsetter[0] != 'self': raise 'access outside component invaild', line
                if len(compsetter) == 2:
                    self.comp_name = ''
                    self.prop_setter = compsetter[1]
                elif len(compsetter) == 3:
                    self.comp_name = compsetter[1]
                    self.prop_setter = compsetter[2]
                else: raise 'Too many sections'
    def asText(self):
#        print 'properties: asText()', self.params
        if self.comp_name:
            return 'self.%s.%s(%s)' %(self.comp_name, self.prop_setter, 
              join(self.params, ', '))
        else:
            return 'self.%s(%s)' %(self.prop_setter, join(self.params, ', '))
         

def parseProperties(body):
    return parseBody(PropertyParse, body)

is_event2p = re.compile('^[ \t]*EVT_(?P<evtname>'+id+')[ \t]*\([ \t]*(?P<name>'+\
  idp+')[ \t]*\,[ \t]*self[.](?P<func>'+idp+')\)$')
is_event3p = re.compile('^[ \t]*EVT_(?P<evtname>'+id+')[ \t]*\([ \t]*(?P<name>'+\
  idp+')[ \t]*\,(?P<wid>.*)[ \t]*\,[ \t]*self[.](?P<func>'+idp+')\)$')
class EventParse(PerLineParser):
    def __init__(self, line = None, comp_name = '', event_name = '', 
      trigger_meth = '', windowid = None):
        self.comp_name = comp_name
        self.event_name = event_name
        self.trigger_meth = trigger_meth
        self.windowid = windowid
        if line:
            self.m = is_event2p.search(line)
            if self.m:
                self.trigger_meth = self.m.group('func')
            else:
                self.m = is_event3p.search(line)
                if self.m:
                    self.windowid = self.m.group('wid')
                    self.trigger_meth = self.m.group('func')
                else: return
            
            if self.m.group('name') != 'self':
                self.comp_name = self.m.group('name')[5:]

            self.event_name = self.m.group('evtname')

    def asText(self):
#        print 'event: asText'
        if self.comp_name:
            evt_comp = 'self.'+self.comp_name
        else:
            evt_comp = 'self'

        if self.windowid:
            return 'EVT_%s(%s, %s, self.%s)' %(self.event_name, evt_comp, 
              self.windowid, self.trigger_meth)
        else:
            return 'EVT_%s(%s, self.%s)' %(self.event_name, evt_comp, 
              self.trigger_meth)
            
            

def parseEvents(body):
    return parseBody(EventParse, body)

