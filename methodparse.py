#----------------------------------------------------------------------
# Name:        methodparse.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999 - 2001 Riaan Booysen
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
    def _init_utils(self):
        pass

    def _init_ctrls(self):
        self._init_utils()

    def __init__(self):
        self._init_ctrls()
"""

#from string import strip, split, join, find, rfind, upper, replace
import re, string

import Preferences, Utils
from Companions import EventCollections

import sourceconst

true,false=1,0

containers = [('(', ')'), ('{', '}'), ('[', ']')]
containBegin = map(lambda d: d[0], containers)
containEnd = map(lambda d: d[1], containers)

def incLevel(level, pos):
    return level + 1, pos + 1

def decLevel(level, pos):
    return max(level - 1, 0), pos + 1

def safesplitfields(params, delim, returnBlanks = 0,
      containBegin=containBegin, containEnd=containEnd):
    """ Returns a list of parameters split on delim but not if delim are
        within containers (), {}, [], '', ""
        Also skip '', "" content
        Note that results are stripped

        Added returnBlanks flag for compatibility with python's split
        split('', ',') returns ['']
        Usually I want the result of such a split to be []
    """

    locparams =  params
    list = []
    i = 0
    nestlevel = 0
    singlequotelevel = 0
    doublequotelevel = 0

    if returnBlanks and not string.strip(params):
        return [params]

    while i < len(locparams):
        curchar = locparams[i]
        # only check for delimiter if not inside some block
        if (not nestlevel) and (not singlequotelevel) and (not doublequotelevel)\
          and (curchar == delim):
            param = locparams[:i]
            list.append(param)
            locparams = string.strip(locparams[i +1:])
            i = 0
            continue

        if (not singlequotelevel) and (not doublequotelevel) and nestlevel and \
          (curchar in containEnd):
            nestlevel, i = decLevel(nestlevel, i)
            continue

        if (not singlequotelevel) and (not doublequotelevel) and \
          (curchar in containBegin):
            nestlevel, i = incLevel(nestlevel, i)
            continue

        # don't check anything except end quotes inside quote blocks
        if singlequotelevel and curchar == "'":
            singlequotelevel, i = decLevel(singlequotelevel, i)
            continue
        if doublequotelevel and curchar == '"':
            doublequotelevel, i = decLevel(doublequotelevel, i)
            continue

        if (not singlequotelevel) and curchar == '"':
            doublequotelevel, i = incLevel(doublequotelevel, i)
        elif (not doublequotelevel) and curchar == "'":
            singlequotelevel, i = incLevel(singlequotelevel, i)
        else:
            i = i + 1

    # add last entry not delimited by comma
    lastentry = string.strip(locparams)
    if lastentry:
        list.append(lastentry)
    return list

# XXX does not handle ",' yet
def matchbracket(text, findBracket, dir=None):
    if findBracket in containBegin or (dir is not None and dir == -1):
        dir = -1
        start = len(text)-1
        end = -1
        brktIdx = containBegin.index(findBracket)
    elif findBracket in containEnd or (dir is not None and dir == 1):
        dir = 1
        start = 0
        end = len(text)
        brktIdx = containEnd.index(findBracket)
    else:
        raise 'Unhandled bracket'

    # () {} []
    levels = [0, 0, 0]

    for cIdx in range(start, end, dir):
        c = text[cIdx]
        if c in containBegin:
            idx = containBegin.index(c)
            levels[idx] = levels[idx] + dir
        elif c in containEnd:
            idx = containEnd.index(c)
            levels[idx] = levels[idx] - dir

        if levels[brktIdx] < 0:
            return cIdx
    return -1

def parseMixedBody(parseClasses, lines):
    """ Return a dictionary with keys representing classes that
        'understood' the line and values a list of found instances
        of the found class
    """
    cat = {}
    unmatched = []
    for parseClass in parseClasses:
        cat[parseClass] = []

    for line in lines:
        ln = string.strip(line)
        if (ln == 'pass') or (ln == ''): continue
        for parseClass in parseClasses:
            try: res = parseClass(ln).value()
            except Exception, message:
                print str(message)
            else:
                if res:
                    cat[parseClass].append(res)
                    break
        else:
            if string.strip(line) != '# %s'%sourceconst.code_gen_warning:
                unmatched.append(line)
    return cat, unmatched


def parseBody(parseClass, lines):
    list = []
    for line in lines:
        ln = string.strip(line)
        if ln == 'pass': return []
        if ln == '':
            continue
        list.append(parseClass(ln))
    return list

param_splitter = ' = '

class PerLineParser:
    """ Class which parses 1 line of source code """
    def value(self):
        if self.m: return self
        else: return None
    def asText(self, stripFrameWinIdPrefix=''):
        """ Source representation of parsed line """
        return ''
    def getIdPrefix(self, name):
        return 'wxID_%s'%string.upper(name)
    def checkId(self, id, idPrfx):
        return id not in EventCollections.reservedWxNames and Utils.startswith(id, idPrfx)
    def prependFrameWinId(self, frame):
        pass

    def __repr__(self):
        return self.asText()

    def renameCompName2(self, old_value, new_value):
        """ notification of a rename, override to catch renames to vars and params
            All parse lines should be notified of renames, not just entries
            which have that name """
        if self.comp_name == old_value:
            self.comp_name = new_value

    def renameFrameName(self, old_value, new_value):
        self.frame_name = new_value

    def renameWindowId(self, windowid, old_frame_name, new_frame_name, old_ctrl_name, new_ctrl_name):
        xtra = windowid[len(Utils.windowIdentifier(old_frame_name, old_ctrl_name)):]
        return Utils.windowIdentifier(new_frame_name, new_ctrl_name)+xtra

    def extractKVParams(self, paramsStr):
        params = safesplitfields(paramsStr, ',')
        result = {}
        for param in params:
            try:
                sidx = string.index(param, '=')
            except ValueError:
                pass
            else:
                result[string.strip(param[:sidx])] = string.strip(param[sidx+1:])
        return result

    def KVParamsAsText(self, params):
        kvlist = []
        sortedkeys = params.keys()
        sortedkeys.sort()
        for key in sortedkeys:
            kvlist.append(Preferences.cgKeywordArgFormat%{'keyword': key,
                                                          'value': params[key]})
        return string.join(kvlist, ', ')

idc = '[A-Za-z_][A-Za-z0-9_]*'
is_constr = re.compile('^[ \t]*self[.](?P<name>'+idc+')[ \t]*=[ \t]*(?P<class>'+\
  idc+')\((?P<params>.*)\)$')
is_constr_frm = re.compile('^[ \t]*(?P<class>'+idc+\
  ')[.]__init__\(self,[ \t]*(?P<params>.*)\)$')

class ConstructorParse(PerLineParser):
    def __init__(self, line=None, comp_name='', class_name='', params=None):
        self.comp_name = comp_name
        self.class_name = class_name
        if params is None: self.params = {}
        else:              self.params = params

        if line:
            self.m = is_constr.search(line)
            if self.m:
                self.comp_name = self.m.group('name')
                self.class_name = self.m.group('class')
                self.params = self.extractKVParams(self.m.group('params'))
            else:
                self.m = is_constr_frm.search(line)
                if self.m:
                    self.comp_name = ''
                    self.class_name = self.m.group('class')
                    self.params = self.extractKVParams(self.m.group('params'))

    def renameCompName2(self, old_value, new_value):
        if self.params.has_key('parent') and \
              self.params['parent'] == Utils.srcRefFromCtrlName(old_value):
            self.params['parent'] = Utils.srcRefFromCtrlName(new_value)
        if self.comp_name == old_value:
            self.comp_name = new_value
            if self.params.has_key('name'):
                self.params['name'] = `new_value`
            if self.params.has_key('id') and \
                  self.params['id'] not in EventCollections.reservedWxNames:
                self.params['id'] = \
                  self.params['id'][:-len(old_value)]+string.upper(new_value)

    def prependFrameWinId(self, frame):
        idPrfx = self.getIdPrefix(frame)
        if self.params.has_key('id') and \
              self.params['id'] not in EventCollections.reservedWxNames:
            self.params['id'] = idPrfx + self.params['id']

    def asText(self, stripFrameWinIdPrefix=''):
        if stripFrameWinIdPrefix:
            idPrfx = self.getIdPrefix(stripFrameWinIdPrefix)
            params = {}
            params.update(self.params)
            if params.has_key('id') and self.checkId(params['id'], idPrfx):
                params['id'] = params['id'][len(idPrfx):]
        else:
            params = self.params

        if self.comp_name:
            return 'self.%s = %s(%s)' %(self.comp_name, self.class_name,
              self.KVParamsAsText(params))
        else:
            return '%s.__init__(self, %s)' %(self.class_name,
              self.KVParamsAsText(params))

is_constr_col = re.compile('^[ \t]*self._init_coll_(?P<meth>'+idc+\
  ')[.]__init__\(self,[ \t]*(?P<params>.*)\)$')

coll_init = '_init_coll_'
idp = '[A-Za-z_][A-Za-z0-9_.]*'
is_prop = re.compile('^[ \t]*self[.](?P<name>'+idp+')[ \t]*\([ \t]*(?P<params>.*)[ \t]*\)$')
class PropertyParse(PerLineParser):
    def __init__(self, line=None, comp_name='', prop_setter='', params=None, prop_name=''):
        self.comp_name = comp_name
        self.prop_setter = prop_setter
        if params is None: self.params = []
        else:              self.params = params
        self.params = params
        self.prop_name = prop_name
        if line:
            self.m = is_prop.search(line)
            if self.m:
                self.params = safesplitfields(self.m.group('params'), ',')
                compsetter = string.split(self.m.group('name'), '.')

                if len(compsetter) < 1: raise 'atleast 1 required '+`compsetter`
                if len(compsetter) == 1:
                    self.comp_name = ''
                    self.prop_setter = compsetter[0]
                elif len(compsetter) == 2:
                    self.comp_name = compsetter[0]
                    self.prop_setter = compsetter[1]
                else: raise 'Too many attribute levels'

    def renameCompName2(self, old_value, new_value):
        # XXX This is ugly but has to do until a better
        # XXX strategy is conceived.
        # XXX The problem is that the useful logic is in the
        # XXX companion which is not available for the clipboard
        # XXX The source's ctrl needs to be renamed for a companion
        # XXX to be created.

        # Rename references to ctrl in parameters of property
        oldCtrlSrcRef = Utils.srcRefFromCtrlName(old_value)
        newCtrlSrcRef = Utils.srcRefFromCtrlName(new_value)

        for idx in range(len(self.params)):
            segs = string.split(self.params[idx], oldCtrlSrcRef)
            if len(segs) > 1:
                lst = [segs[0]]
                for s in segs[1:]:
                    if s and s[0] in string.letters+string.digits+'_':
                        lst[-1] = lst[-1] + s
                    else:
                        lst.append(s)
                self.params[idx] = string.join(lst, newCtrlSrcRef)

            # Handle case where _init_coll_* methods are used as parameters
            param = self.params[idx]
            if Utils.startswith(param, 'self.'+coll_init):
                nameEnd = string.rfind(param, '_')
                name = param[16:nameEnd]
                if name == old_value:
                    self.params[idx] = 'self.'+coll_init+new_value+param[nameEnd:]

        PerLineParser.renameCompName2(self, old_value, new_value)

    def asText(self, stripFrameWinIdPrefix=''):
        return '%s.%s(%s)' %(Utils.srcRefFromCtrlName(self.comp_name),
                self.prop_setter, string.join(self.params, ', '))

def ctrlNameFromMeth(meth):
    return string.join(string.split(meth, '_')[3:-1], '_')

is_coll_init = re.compile('^[ \t]*self[.](?P<method>'+coll_init+idp+')[ \t]*\((?P<comp_name>'+idp+')[ \t,]*(?P<params>.*)\)$')

class CollectionInitParse(PerLineParser):
    def __init__(self, line=None, comp_name='', method='', params=None, prop_name=''):
        self.comp_name = comp_name
        self.method = method
        if params is None: self.params = []
        else:              self.params = params
        self.prop_name = prop_name
        if line:
            self.m = is_coll_init.search(line)
            if self.m:
                self.params = safesplitfields(self.m.group('params'), ',')
                self.method = self.m.group('method')
                self.comp_name = self.m.group('comp_name')[5:]
                self.prop_name = self.method[len(coll_init)+len(self.comp_name)+1:]

    def getPropName(self):
        return self.method[len(coll_init)+len(self.comp_name)+1:]

    def renameCompName2(self, old_value, new_value):
        if self.comp_name == old_value:
            self.comp_name = new_value
            self.method = '%s%s_%s'%(coll_init, new_value, self.prop_name)

    def asText(self, stripFrameWinIdPrefix=false):
        return 'self.%s(%s)' %(self.method,
             string.join([Utils.srcRefFromCtrlName(self.comp_name)]+self.params, ', '))

# Because the object name of some collection items cannot be directly derived
# from the source, the information is attached to the items
def decorateParseItems(parseItems, ctrlName, frameName):
    for parseItem in parseItems:
        parseItem.ctrl_name = ctrlName
        parseItem.frame_name = frameName

#item_parent = 'parent'
is_coll_item_init = re.compile('^[ \t]*(?P<ident>'+idp+')[.](?P<method>'+idc+')[ \t]*\([ \t,]*(?P<params>.*)\)$')
class CollectionItemInitParse(PerLineParser):
    def __init__(self, line=None, comp_name='', method='', params=None):
        self.comp_name = comp_name
        self.ctrl_name = self.frame_name = '&None&'
        self.method = method
        if params is None: self.params = {}
        else: self.params = params
        if line:
            self.m = is_coll_item_init.search(line)
            if self.m:
                self.comp_name = self.m.group('ident')
                self.method = self.m.group('method')
                self.params = self.extractKVParams(self.m.group('params'))

    def renameFrameName(self, old_value, new_value):
        PerLineParser.renameFrameName(self, old_value, new_value)
        if self.params.has_key('id'):
            self.params['id'] = self.renameWindowId(self.params['id'],
                old_value, new_value, self.ctrl_name, self.ctrl_name)

    def renameCompName2(self, old_value, new_value):
        # Regenerate window ids
        if self.ctrl_name == old_value:
            self.ctrl_name = new_value
            if self.params.has_key('id'):
                self.params['id'] = self.renameWindowId(self.params['id'],
                      self.frame_name, self.frame_name, old_value, new_value)

        # Check for references
        src_old = Utils.srcRefFromCtrlName(old_value)
        for key, val in self.params.items()[:]:
            if val == src_old:
                self.params[key] = Utils.srcRefFromCtrlName(new_value)

    def prependFrameWinId(self, frame):
        idPrfx = self.getIdPrefix(frame)
        if self.params.has_key('id') and \
              self.params['id'] not in EventCollections.reservedWxNames:
            self.params['id'] = idPrfx + self.params['id']

    def asText(self, stripFrameWinIdPrefix=''):
        if stripFrameWinIdPrefix:
            idPrfx = self.getIdPrefix(stripFrameWinIdPrefix)
            params = {}
            params.update(self.params)
            if params.has_key('id') and self.checkId(params['id'], idPrfx):
                params['id'] = params['id'][len(idPrfx):]
        else:
            params = self.params
        return '%s.%s(%s)' %(self.comp_name, self.method, self.KVParamsAsText(params))

is_event2p = re.compile('^[ \t]*EVT_(?P<evtname>'+idc+')[ \t]*\([ \t]*(?P<name>'+\
  idp+')[ \t]*\,[ \t]*self[.](?P<func>'+idp+')\)$')
# EVT_EVTNAME(self.win, ID, self.OnEvt)
is_event3p = re.compile('^[ \t]*EVT_(?P<evtname>'+idc+')[ \t]*\([ \t]*(?P<name>'+\
  idp+')[ \t]*\,(?P<wid>.*)[ \t]*\,[ \t]*self[.](?P<func>'+idp+')\)$')
class EventParse(PerLineParser):
    def __init__(self, line=None, comp_name='', event_name='',
      trigger_meth = '', windowid = None):
        self.comp_name = comp_name
        self.ctrl_name = self.frame_name = '&None&'
        self.event_name = event_name
        self.trigger_meth = trigger_meth
        self.prev_trigger_meth = ''
        self.windowid = windowid
        self.show_scope = 'this' # can be 'all', 'same', 'this'
        if line:
            self.m = is_event2p.search(line)
            if self.m:
                self.trigger_meth = self.m.group('func')
            else:
                self.m = is_event3p.search(line)
                if self.m:
                    self.windowid = string.strip(self.m.group('wid'))
                    self.trigger_meth = self.m.group('func')
                else: return

            if self.m.group('name') != 'self':
                self.comp_name = self.m.group('name')[5:]

            self.event_name = self.m.group('evtname')

    def renameFrameName(self, old_value, new_value):
        PerLineParser.renameFrameName(self, old_value, new_value)
        if self.windowid:
            self.windowid = self.renameWindowId(self.windowid,
                old_value, new_value, self.ctrl_name, self.ctrl_name)

    def renameCompName2(self, old_value, new_value):
        if self.ctrl_name == old_value:
            self.ctrl_name = new_value
            if self.comp_name:
                self.comp_name = new_value
            # Check for command events
            if self.windowid:
                self.windowid = self.renameWindowId(self.windowid,
                      self.frame_name, self.frame_name, old_value, new_value)

    def prependFrameWinId(self, frame):
        if self.windowid:
            idPrfx = self.getIdPrefix(frame)
            if self.windowid not in EventCollections.reservedWxNames:
                self.windowid = idPrfx + self.windowid

    def asText(self, stripFrameWinIdPrefix=''):
        if self.windowid:
            windowid = self.windowid
            if stripFrameWinIdPrefix:
                idPrfx = self.getIdPrefix(stripFrameWinIdPrefix)
                if self.checkId(windowid, idPrfx):
                    windowid = windowid[len(idPrfx):]

            return 'EVT_%s(%s, %s, self.%s)' %(self.event_name,
              Utils.srcRefFromCtrlName(self.comp_name), windowid, self.trigger_meth)
        else:
            return 'EVT_%s(%s, self.%s)' %(self.event_name,
              Utils.srcRefFromCtrlName(self.comp_name), self.trigger_meth)

def test():
##    PLP = PerLineParser()
##    print PLP.extractKVParams('a = 10, b = 20') == {'a': '10', 'b': '20'}
##    print PLP.extractKVParams('a = "b\'c", b = "a=b"') == {'a': '"b\'c"', 'b': '"a=b"'}

    cp = ConstructorParse("self.menu1 = wxMenu(title = '')")
    print cp.asText('wxFrame1')
    cp = ConstructorParse("self.button1 = wxButton(id = wxID_WXFRAME1BUTTON1, label = 'button1', name = 'button1', parent = self, pos = wxPoint(232, 168), size = wxSize(75, 23), style = 0)")
    print cp.asText('wxFrame1')
    cp2 = ConstructorParse(cp.asText('wxFrame1'))
    cp2.prependFrameWinId('wxFrame2')
    print cp2.asText()
    ciip = CollectionItemInitParse("parent.Append(checkable = false, helpString = '', id = wxID_WXFRAME1MENU1ITEMS0, item = 'Items0')")
    print ciip.asText('wxFrame1')
    ciip2 = CollectionItemInitParse(ciip.asText('wxFrame1'))
    ciip2.prependFrameWinId('wxFrame2')
    print ciip2.asText()
    ep = EventParse("EVT_MENU(self, wxID_WXFRAME1MENU1ITEMS0, self.OnMenu1items0Menu)")
    print ep.asText('wxFrame1')
    ep2 = EventParse(ep.asText('wxFrame1'))
    ep2.prependFrameWinId('wxFrame2')
    print ep2.asText()

if __name__ == '__main__':
    test()
