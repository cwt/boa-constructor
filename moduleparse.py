#----------------------------------------------------------------------
# Name:        moduleparse.py
# Purpose:
#
# Author:      Riaan Booysen, based on 'pyclbr.py'
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   Changes (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

"""Parse one Python file and retrieve classes and methods,
store the code spans and facilitate the manipulation of method bodies

This module is heavly based on 'pyclbr.py' from the standard python lib

BUGS
Nested methods and classes not handled

<from pyclbr.py>
Continuation lines are not dealt with at all and strings may confuse
the hell out of the parser, but it usually works.

Continuation lines are now handled for class, method and function defs
"""

# XXX Dedented block (0 indent) should trigger end of class/func

import os, sys
import imp
import re
import string, pprint
from types import IntType, StringType    #id([][,]id)*

import methodparse

id = '[A-Za-z_][A-Za-z0-9_]*'
obj_def = '[A-Za-z_][A-Za-z0-9_.]*'
blank_line = re.compile('^[ \t]*($|#)')
is_class = re.compile('^[ \t]*class[ \t]+(?P<id>%s)[ \t]*(?P<sup>\([^)]*\))?[ \t]*:'%id)
is_class_start = re.compile('^[ \t]*class[ \t]+(?P<id>%s)[ \t]*[\(\:]'%id)
is_method = re.compile('^[ \t]*def[ \t]+(?P<id>%s)[ \t]*\((?P<sig>.*)\)[ \t]*[:][ \t]*$'%id)
is_method_start = re.compile('^[ \t]*def[ \t]+(?P<id>%s)[ \t]*\('%id)
is_func = re.compile('^def[ \t]+(?P<id>%s)[ \t]*\((?P<sig>.*)\)[ \t]*[:][ \t]*$'%id)
is_func_start = re.compile('^def[ \t]+(?P<id>%s)[ \t]*\('%id)
is_attrib = re.compile('[ \t]*self[.](?P<name>%s)[ \t]*=[ \t]*'%id)
is_attrib_from_call = re.compile('[ \t]*self[.](?P<name>%s)[ \t]*=[ \t]*(?P<classpath>%s)\('%(id, obj_def))
is_name = re.compile('[ \t]*(?P<name>%s)[ \t]*=[ \t]*'%id)
#are_names = re.compile('[ \t]*((?P<names>%s)[ \t]*[,][ \t]*)+(?P<lastname>%s)[ \t]*)*=[ \t]*'%(id, id))
is_import = re.compile('^[ \t]*import[ \t]*(?P<imp>[^#;]+)')
is_from = re.compile('^[ \t]*from[ \t]+(?P<module>%s([ \t]*\\.[ \t]*%s)*)[ \t]+import[ \t]+(?P<imp>[^#;]+)'%(id, id))
dedent = re.compile('^[^ \t]')
indent = re.compile('^[^ \t]*')
is_doc_quote = re.compile("'''")
id_doc_quote_dbl = re.compile('"""')
is_todo = re.compile('^[ \t]*# XXX')
is_wid = re.compile('^\[(?P<wids>.*)\][ \t]*[=][ \t]*wxNewId[(](?P<count>\d+)[)]$')
is_break_line = re.compile('^#-+(?P<descr>.*%s)-+$'%obj_def)

sq3string = r"(\b[rR])?'''([^'\\]|\\.|'(?!''))*(''')?"
dq3string = r'(\b[rR])?"""([^"\\]|\\.|"(?!""))*(""")?'
is_doc = re.compile('(?P<string>%s|%s)' % (sq3string, dq3string))

# XXX Provide for lines between entries
sep_line = '#[-]+.*'
#blk_line = '#'
str_name = '# Name:[ \t]*(?P<name>.*)'
str_purpose = '# Purpose:[ \t]*(?P<purpose>.*)'
str_author = '# Author:[ \t]*(?P<author>.*)'
str_created = '# Created:[ \t]*(?P<created>.*)'
str_rcs_id = '# RCS-ID:[ \t]*(?P<rcs_id>.*)'
str_copyright = '# Copyright:[ \t]*(?P<copyright>.*)'
str_licence = '# Licence:[ \t]*(?P<licence>[^#]*#[-]+)'

is_info = re.compile(sep_line + str_name + str_purpose + str_author + \
  str_created + str_rcs_id + str_copyright + str_licence, re.DOTALL)

def wxNewIds(cnt):
    l = []
    for i in range(cnt):
        l.append(i)
    return l

def wxNewIds(cnt):
    return map(lambda _init_ctrls: NewId(), range(cnt))

##def wxNewIds(cnt):
##    return [wxNewId() for x in range(cnt)]

class CodeBlock:
    def __init__(self, sig, start, end):
        self.signature = sig
        self.start = start
        self.end = end
        # XXX renumber
        self.locals = {}
    
    def __repr__(self):
        return '[%d - %d]'%(self.start, self.end)

    def renumber(self, from_line, increment):
        if self.start > from_line:
            self.start = self.start + increment
            self.end = self.end + increment
        elif self.end > from_line:
            self.end = self.end + increment
        for attr in self.locals.values():
            attr.renumber(from_line, increment)

    def contains(self, line):
        return line >= self.start and line <= self.end

    def size(self):
        return self.end - self.start

    def localnames(self):
        return filter(lambda s, locls=self.locals.keys(): s not in locls,
           map(lambda s: string.split(s, '=')[0],
           methodparse.safesplitfields(self.signature, ',')))+self.locals.keys()

class Attrib:
    def __init__(self, name, lineno, objtype = ''):
        self.name = name
        self.lineno = lineno
        self.objtype = objtype

    def renumber(self, from_line, increment):
        if self.lineno > from_line:
            self.lineno = self.lineno + increment

# each Python class is represented by an instance of this class
class Class:
    """ Class to represent a Python class. """
    def __init__(self, module, name, super, file, lineno):
        self.module = module
        self.name = name
        if super is None:
            super = []
        self.super = super
        self.methods = {}
        self.method_order = []
        self.attributes = {}
        self.class_attributes = {}
        self.file = file
        self.block = CodeBlock('', lineno, lineno)
        self.extent = lineno

    def __repr__(self):
        return self.name+`self.block`+'\n'+string.join(map(lambda meth, meths=self.methods: '    '+meth+`meths[meth]`, self.method_order), '\n')

    def extend_extent(self, lineno):
        if lineno > self.extent: self.extent = lineno

    def add_method(self, name, sig, linestart, lineend = None, to_bottom = 1):
        if not lineend: lineend = linestart
        self.methods[name] = CodeBlock(sig, linestart, lineend)
        if to_bottom:
            self.method_order.append(name)
            self.extend_extent(lineend)
        else:
            self.method_order.insert(0, name)
            self.extent = self.extent + (lineend - linestart)

    def end_method(self, name, lineend):
        self.methods[name].end = lineend
        self.extend_extent(lineend)

    def remove_method(self, name):
        self.extent = self.extent - self.methods[name].size()
        del self.methods[name]
        self.method_order.remove(name)

    def add_attr(self, name, lineno, thetype = ''):
        if self.attributes.has_key(name):
            self.attributes[name].append(CodeBlock(thetype, lineno, lineno))
        else:
            self.attributes[name] = [CodeBlock(thetype, lineno, lineno)]

    def add_class_attr(self, name, lineno, thetype = ''):
        if self.class_attributes.has_key(name):
            self.class_attributes[name].append(CodeBlock(thetype, lineno, lineno))
        else:
            self.class_attributes[name] = [CodeBlock(thetype, lineno, lineno)]

    def add_local(self, name, meth, lineno, thetype = ''):
        if self.methods.has_key(meth):
            if not self.methods[meth].locals.has_key(name):
                self.methods[meth].locals[name] = Attrib(name, lineno, thetype)

    def renumber(self, start, deltaLines):
        self.block.renumber(start, deltaLines)
        for block in self.methods.values():
            block.renumber(start, deltaLines)
        for attr_lst in self.attributes.values():
            for block in attr_lst:
                block.renumber(start, deltaLines)

    def getMethodForLineNo(self, line_no):
        for name, meth in self.methods.items():
            if meth.contains(line_no):
                return name, meth
        return '', None

class Test2: pass

class Module:
    """ Represents a Python module.

    Parses and maintains dictionaries of the classes and
    functions defined in a module. """

    def finaliseEntry(self, cur_class, cur_meth, cur_func, lineno):
        """ When a new structure is encountered, finalise the current
        structure, whatever it is. """
        if cur_class:
            # Gobble up blank lines
            lineno = lineno - 1
            while not string.strip(self.source[lineno - 1]):
                lineno = lineno - 1

            if cur_meth:
                cur_class.end_method(cur_meth, lineno)
                cur_meth = ''
            cur_class.block.end = lineno

            cur_class = None
            cur_func = None

        elif cur_func:
            cur_func.end = lineno -1
            cur_func = None

        return cur_class, cur_meth, cur_func


    def readline(self):
        line = self.source[self.lineno]
        self.lineno = self.lineno + 1
        return line

    def decomment(self, line):
        return methodparse.safesplitfields(line, '#', returnBlanks = 1)[0]

    line_conts = (',', '\\', '(')
    def readcontinuedlines(self, lineno, terminator):
        contline = ''
        while lineno < len(self.source):
            line = string.rstrip(self.decomment(self.source[lineno]))
            if line:
                if line[-1] in self.line_conts:
                    contline = contline + line
                    lineno = lineno + 1
                    continue
                elif line[-1] in string.digits+string.letters+'_':
                    contline = contline + line
                    lineno = lineno + 1
                    continue
                elif line[-1] == terminator:
                    contline = contline + line
                    return lineno, contline
                else:
                    break
            else:
                lineno = lineno + 1
                continue

        return -1, ''

    def __init__(self, module, modulesrc):#, classes = {}, class_order = [], file = ''):
        self.classes = {}#classes
        self.class_order = []#class_order
        self.functions = {}
        self.function_order = []
        self.imports = {}
        self.todos = []
        self.wids = []
        self.name = module
        self.globals = {}
        self.global_order = []
        self.break_lines = {}

        cur_class = None
        cur_meth = ''
        cur_func = None
        file = ''
        self.lineno = 0
        self.source = modulesrc
        self.loc = 0
        while self.lineno < len(self.source):
            self.loc = self.loc + 1
            line = string.rstrip(self.readline())

            cont, cur_class, cur_meth, cur_func = self.parseLine(module, file,
                  line, self.lineno, cur_class, cur_meth, cur_func)
                        
        # if it's the last class in the source, it will not dedent
        # check manually
        cur_class, cur_meth, cur_func = self.finaliseEntry(cur_class, cur_meth,
          cur_func, self.lineno +1)

#        print self.imports

    def parseLineIsolated(self, line, lineno):
        cls = self.getClassForLineNo(lineno)
        if cls:
            mthName, mth = cls.getMethodForLineNo(lineno)
            return self.parseLine('', '', line, lineno, cls, mthName, None)
        else:
            fnc = self.getFunctionForLineNo(lineno)
            if fnc:
                return self.parseLine('', '', line, lineno, None, '', fnc)
        return self.parseLine('', '', line, lineno, None, '', None)
                
                

    def parseLine(self, module, file, line, lineno, cur_class, cur_meth, cur_func):
        res = is_todo.match(line)
        if res:
            self.todos.append((lineno,
                  string.strip(line[res.span()[1]:])))
            return 0, cur_class, cur_meth, cur_func

        if blank_line.match(line):
            # ignore blank (and comment only) lines
            self.loc = self.loc - 1
            if len(line) == 80:
                res = is_break_line.match(line)
                if res:
                    self.break_lines[lineno] = res.group('descr')
                
            return 0, cur_class, cur_meth, cur_func

##            if dedent.match(line):
##                print 'dedent', self.lineno

        res2 = is_class_start.match(line)
        if res2:
            res = is_class.match(line)
            if not res:
                # check for line conts
                lno, contl = self.readcontinuedlines(lineno-1, ':')
                if lno == -1:
                    return 0, cur_class, cur_meth, cur_func
                class_name = res2.group('id')
                inherit = contl[string.find(contl,
                     '('):string.rfind(contl, ')')+1]
            else:
                class_name = res.group('id')
                inherit = res.group('sup')

            # we found a class definition
            cur_class, cur_meth, cur_func = self.finaliseEntry(cur_class,
              cur_meth, cur_func, lineno)
            if inherit:
                # the class inherits from other classes
                inherit = string.strip(inherit[1:-1])
                names = []
                for n in string.split(inherit, ','):
                    n = string.strip(n)
                    if n:
                        if self.classes.has_key(n):
                            # we know this super class
                            n = self.classes[n]
                        else:
                            c = string.splitfields(n, '.')
                            if len(c) > 1:
                                # super class is of the
                                # form module.class:
                                # look in module for class
                                m = c[-2]
                                c = c[-1]
                        names.append(n)
                inherit = names
            # remember this class

# An attempt at maintaining state on the fly 
#(way to much effort, must be done for every parsed type)
##           order = -1
##            for cn in self.class_order[:]:
##                c = self.classes[cn]
##                if c.block.start == lineno:
##                    print 'inplace class rename %d'%lineno
##                    # we are replacing (renaming) a class in-place
##                    if c.name != class_name:
##                        del self.classes[c.name]
##                        self.classes[class_name] = c
##                        
##                        idx = self.class_order.index(c.name)
##                        del self.class_order[idx]
##                        self.class_order.insert(idx, class_name)
##                        
##                    c.name = class_name
##                    c.super = inherit
##                    return 0, cur_class, cur_meth, cur_func
##                
##                if lineno < c.block.start and order == -1:
##                    print 'non append order %d above %s:%d'%(lineno, c.name, c.block.start)
##                    order = self.class_order.index(cn)
##            else:
            cur_class = Class(module, class_name, inherit, file, lineno)
            cur_meth = ''
            self.classes[class_name] = cur_class
            self.class_order.append(class_name)
##            if order == -1:
##                self.class_order.append(class_name)
##            else:
##                self.class_order.insert(order, class_name)
                
            return 0, cur_class, cur_meth, cur_func

        res2 = is_func_start.match(line)
        if res2:
            res = is_func.match(line)
            if not res:
                lno, contl = self.readcontinuedlines(lineno-1, ':')
                if lno == -1:
                    return 0, cur_class, cur_meth, cur_func
                res_group_id = res2.group('id')
                res_group_sig = contl[string.find(contl,
                      '(')+1:string.rfind(contl, ')')]
            else:
                res_group_id = res.group('id')
                res_group_sig = res.group('sig')

            cur_class, cur_meth, cur_func = self.finaliseEntry(cur_class,
              cur_meth, cur_func, lineno)
            func_name = res_group_id
            cur_func = self.functions[func_name] = CodeBlock(res_group_sig, lineno, 0)
            self.function_order.append(func_name)
            return 0, cur_class, cur_meth, cur_func

        res2 = is_method_start.match(line)
        if res2:
            res = is_method.match(line)
            if not res:
                lno, contl = self.readcontinuedlines(lineno-1, ':')
                if lno == -1:
                    return 0, cur_class, cur_meth, cur_func
                res_group_id = res2.group('id')
                res_group_sig = contl[string.find(contl,
                      '(')+1:string.rfind(contl, ')')]
            else:
                res_group_id = res.group('id')
                res_group_sig = res.group('sig')

            # found a method definition
            if cur_class:
                # and we know the class it belongs to
                if cur_meth:
                    cur_class.end_method(cur_meth, lineno -1)
                meth_name = res_group_id
                cur_class.add_method(meth_name, res_group_sig, lineno)
                cur_meth = meth_name
            return 0, cur_class, cur_meth, cur_func

        res = is_attrib_from_call.match(line)
        if res:
            # found a attribute binding
            if cur_class:
                # and we know the class it belongs to
                classpath = res.group('classpath')
                cur_class.add_attr(res.group('name'), lineno, classpath)

            return 0, cur_class, cur_meth, cur_func

        res = is_attrib.match(line)
        if res:
            # found a attribute binding with possible object type
            if cur_class:
                # and we know the class it belongs to
                # try to determine type
                rem = line[res.end():]
                objtype = ''
                if rem:
                    if rem[0] in ('"', "'"): objtype = 'string'
                    elif rem[0] in string.digits: objtype = 'number'
                    elif rem[0] == '{': objtype = 'dict'
                    elif rem[0] == '[': objtype = 'list'
                    elif rem[0] == '(': objtype = 'tuple'
                    elif rem[0] in string.letters+'_': objtype = 'ref'

                cur_class.add_attr(res.group('name'), lineno, objtype)

            return 0, cur_class, cur_meth, cur_func

        res = is_import.match(line)
        if res:
            # import module
            for n in string.splitfields(res.group('imp'), ','):
                n = string.strip(n)
                self.imports[n] = [lineno]
            return 0, cur_class, cur_meth, cur_func

        res = is_from.match(line)
        if res:
            # from module import stuff
            mod = res.group('module')
            if not self.imports.has_key(mod):
                self.imports[mod] = [lineno]

##                names = string.splitfields(res.group('imp'), ',')
##                for n in names:
##                    n = string.strip(n)
##                    self.imports[mod].append(n)
            return 0, cur_class, cur_meth, cur_func

        res = is_wid.match(line)
        if res:
            self.wids.append((lineno, res))

        if dedent.match(line):
            # end of class definition
            cur_class, cur_meth, cur_func = self.finaliseEntry(cur_class,
              cur_meth, cur_func, lineno)

        res = is_name.match(line)
        if res:
            # found a name binding
            # class attribute
            if cur_class:
                # and we know the class it belongs to
                # try to determine type
                if cur_meth:
                    cur_class.add_local(res.group('name'), cur_meth, lineno)
                else:
                    # must be class attr
                    cur_class.add_class_attr(res.group('name'), lineno, line[res.end():])
            # function
            elif cur_func:
                name = res.group('name')
                if name not in cur_func.locals.keys():
                        cur_func.locals[name] = Attrib(name, lineno)
##                if self.functions.has_key(cur_func):
##                    if name not in self.functions[cur_func].locals.keys():
##                        self.functions[cur_func].locals[name] = Attrib(name, lineno)
            #global
            else:
                name = res.group('name')
                if not self.globals.has_key(name):
                    self.globals[name] = CodeBlock(name, self.lineno, lineno)
                    self.global_order.append(name)

            return 0, cur_class, cur_meth, cur_func
        
        return 1, cur_class, cur_meth, cur_func

    def find_declarer(self, cls, attr, value, found = 0):
        if found:
            return found, cls, value
        else:
            for base in cls.super:
                if type(base) == type(''):
                    return found, cls, value
                if base.attributes.has_key(attr):
                    return 1, base, base.attributes[attr]
                elif base.methods.has_key(attr):
                    return 1, base, base.methods[attr]
                else:
                    found, cls, value = self.find_declarer(base, attr, value, 0)
        return found, cls, value


    def extractClassBody(self, class_name):
        block = self.classes[class_name].block
        return self.source[block.start:block.end]

    def addMethod(self, class_name, method_name, method_params, method_body, to_bottom = 1):
        new_length = len(method_body) + 2
        if not method_body: return
        a_class = self.classes[class_name]
        if method_name in a_class.method_order:
            raise 'Method exists'

        # Add a method code block
        if to_bottom or not a_class.method_order:
            ins_point = a_class.extent
            pre_blank = ['']
            post_blank = []
        else:
            #print a_class.methods[a_class.method_order[0]].start, a_class.block.start
            ins_point = a_class.methods[a_class.method_order[0]].start-1
            #ins_point = a_class.block.start
            pre_blank = []
            post_blank = ['']

        # renumber code blocks
        self.renumber(new_length, ins_point)

        a_class.add_method(method_name, method_params, ins_point+1, ins_point + \
          new_length, to_bottom)

        # Add in source
        self.source[ins_point : ins_point] = \
          pre_blank + ['    def %s(%s):' % (method_name, method_params)] + \
          method_body + post_blank


    def addLine(self, line, line_no):
        self.source.insert(line_no, line)
        self.renumber(1, line_no)

    def extractMethodBody(self, class_name, method_name):
        block = self.classes[class_name].methods[method_name]
        return self.source[block.start:block.end]

    def extractFunctionBody(self, function_name):
        block = self.functions[function_name]
        return self.source[block.start:block.end]

    def renumber(self, deltaLines, start):
        if deltaLines:
            for cls in self.classes.values():
                cls.renumber(start, deltaLines)
            for func in self.functions.values():
                func.renumber(func.start, deltaLines)
            for glob in self.globals.values():
                glob.renumber(glob.start, deltaLines)

    def replaceBody(self, name, code_block_dict, new_body):
        newLines = len(new_body)
        if not new_body: return
        code_block = code_block_dict[name]
        prevLines = code_block.end - code_block.start
        deltaLines = newLines - prevLines

        self.source[code_block.start : code_block.end] = new_body

        self.renumber(deltaLines, code_block.start)

    def replaceMethodBody(self, class_name, method_name, new_body):
        if not string.strip(string.join(new_body)): new_body = ['        pass', '']
        self.replaceBody(method_name, self.classes[class_name].methods, new_body)

    def removeMethod(self, class_name, name):
        code_block = self.classes[class_name].methods[name]
        totLines = code_block.end - code_block.start + 1 # def decl

        self.source[code_block.start-1 : code_block.end] = []

        self.renumber(-totLines, code_block.start-1)

        self.classes[class_name].remove_method(name)
##        del self.classes[class_name].methods[name]
##        self.classes[class_name].method_order.remove(name)

    def searchDoc(self, body):
        m = is_doc.search(body)
        if m:
            s, e = m.span()
            return string.strip(body[s+3:e-3])
        else: return ''

    def getModuleDoc(self):
        """ Return doc string for module. Scan the area from the start of the
            file up to the first occurence of a doc string containing structure
            like func or class """
        if self.class_order:
            classStart = self.classes[self.class_order[0]].block.start -1
        else:
            classStart = len(self.source)

        if self.function_order:
            funcStart = self.functions[self.function_order[0]].start -1
        else:
            funcStart = len(self.source)

        modTop = self.source[:min(classStart, funcStart)]
        return self.searchDoc(string.join(self.formatDocStr(modTop)))

    def formatDocStr(self, lines):        
        l = []
        for line in lines:
            if not string.strip(line):
                l.append('<P>')
            else:
                l.append(line)
        return l


    def getClassDoc(self, class_name):
        #delete all method bodies
        # XXX broken, returns first doc str in class
##        cbl = self.extractClassBody(class_name)
##        for meths in self.classes[class_name].methods.values():
##            pass
        cls = self.classes[class_name]

        if len(cls.method_order):
            methStart = cls.methods[cls.method_order[0]].start
        else:
            methStart = cls.block.end

        classDoc = self.source[cls.block.start: min(methStart,
          cls.block.end)]

        return self.searchDoc(string.join(self.formatDocStr(classDoc)))

    def getClassMethDoc(self, class_name, meth_name):
        """ Extract the doc string for a method """
        methDoc = self.extractMethodBody(class_name, meth_name)
        return self.searchDoc(string.join(self.formatDocStr(methDoc)))
    
    def getFunctionDoc(self, function_name):
        funcDoc = self.extractFunctionBody(function_name)
        return self.searchDoc(string.join(self.formatDocStr(funcDoc)))

    def renameClass(self, old_class_name, new_class_name):
        cls = self.classes[old_class_name]
        idx = cls.block.start -1
        self.source[idx] = string.replace(self.source[idx], old_class_name,
          new_class_name, 1)
        cls.name = new_class_name
        del self.classes[old_class_name]
        self.classes[new_class_name] = cls
        #rename order
        idx = self.class_order.index(old_class_name)
        del self.class_order[idx]
        self.class_order.insert(idx, new_class_name)

    def renameMethod(self, class_name, old_method_name, new_method_name):
        # untested
        meth = self.classes[class_name].methods[old_method_name]
        idx = meth.start -1
        self.source[idx] = string.replace(self.source[idx], old_method_name,
          new_method_name, 1)
        del self.classes[class_name].methods[old_method_name]
        self.classes[class_name].methods[new_method_name] = meth
        #rename order
##        idx = self.classes[class_name].method_order.index(old_method_name)
##        del self.classes[class_name].method_order[idx]
##        self.classes[class_name].method_order.insert(idx, new_method_name)

        self.classes[class_name].method_order[\
          self.classes[class_name].method_order.index(old_method_name)] = new_method_name


    def addFunction(self, func_name, func_params, func_body):
#        new_length = len(func_body) + 2
        if not func_body: return

        # Add a func code block
        ins_point = len(self.source)
        self.functions[func_name] = CodeBlock(func_params,
          ins_point, ins_point+len(func_body))
        self.function_order.append(func_name)

        # Add in source
        self.source[ins_point : ins_point] = \
          ['def %s(%s):' % (func_name, func_params)] + func_body + ['']

        # renumber code blocks
#        self.renumber(new_length, ins_point)

    def replaceFunctionBody(self, func_name, new_body):
        self.replaceBody(func_name, self.functions, new_body)

    def removeFunction(self, func_name):
        cb  = self.functions[func_name]
        ins_point = cb.start
        func_size = cb.end - ins_point

        self.source[ins_point : cb.end] = []
        self.function_order.remove(func_name)
        del self.functions[func_name]

        self.renumber(func_size, ins_point)

    def ExhaustBranch(self, name, classes, path, result):
        """This method will traverse the class heirarchy, from a given
        class and build up a nested dictionary of super-classes. The
        result is intended to be inverted, i.e. the highest level
        are the super classes."""

        def AddPathToHierarchy(path, result, fn):
            """We have an exhausted path. Simply put it into the result dictionary."""
            if path[0] in result.keys():
                if len(path) > 1: fn(path[1:], result[path[0]], fn)
            else:
                for part in path:
                    result[part] = {}
                    result = result[part]

        rv = {}
        if classes.has_key(name):
            for cls in classes[name].super:
                if type(cls) == StringType:  # strings are always termination
                    rv[cls] = {}
                    exhausted = path + [cls]
                    exhausted.reverse()
                    AddPathToHierarchy(exhausted, result, AddPathToHierarchy)
                else:
                    rv [cls.name] = self.ExhaustBranch(cls.name, classes,
                        path + [cls.name], result)
        if len(rv) == 0:
            exhausted = path
            exhausted.reverse()
            AddPathToHierarchy(exhausted, result, AddPathToHierarchy)
        return rv

    def createHierarchy(self):
        """ Build the inheritance hierarchy """
        hierc = {}
        for cls in self.classes.keys():
            self.ExhaustBranch(cls, self.classes, [cls], hierc)
        return hierc

    def getInfoBlock(self):
        info_block = {}
        c = []
        for cnt in range(len(self.source)):
            if self.source[cnt][:2] == '#-': c.append(cnt)
            if len(c) ==2:
                data = string.join(self.source[c[0]:c[1]+1], os.linesep)

                info = is_info.search(data)
                if info:
                    for key in info.groupdict().keys():
                        info_block[key] = string.strip(info.group(key))
                else: return 'no info'

        return info_block

    def addImportStatement(self, impStmt):
        """ Adds an import statement to the code and internal dict if it isn't
            added yet """
        m = is_import.match(impStmt)
        impLine = ''
        if m:
            for n in string.splitfields(m.group('imp'), ','):
                n = string.strip(n)
                if not self.imports.has_key(n):
                    self.imports[n] = [self.lineno]
                    impLine = impStmt
        else:
            m = is_from.match(impStmt)
            if m:
                mod = m.group('module')
                if not self.imports.has_key(mod):
                    self.imports[mod] = [self.lineno]
                    impLine = impStmt
            else:
                raise 'Import statement invalid'

        if impLine:
            # XXX Decide on default position if module does not have
            # XXX from wxPython.wx import *
            # Add it beneath from wxPython.wx import *
            if self.imports.has_key('wxPython.wx'):
                insLine = self.imports['wxPython.wx'][0]
                self.source.insert(insLine, impLine)
                self.renumber(1, insLine)

    def getClassForLineNo(self, line_no):
        for cls in self.classes.values():
            if cls.block.contains(line_no):
                return cls
        return None

    def getFunctionForLineNo(self, line_no):
        for func in self.functions.values():
            if func.contains(line_no):
                return func
        return None

    def __repr__(self):
        return 'Module: %s\n' % self.name +\
          'Classes: \n'+pprint.pformat(self.classes)+'\n'+\
          'Functions: \n'+pprint.pformat(self.functions)+'\n'




def moduleFile(module, path=[], inpackage=0):
    """Read a module file and return a dictionary of classes.

    Search for MODULE in PATH and sys.path, read and parse the
    module and return a dictionary with one entry for each class
    found in the module.

    XXX Package code not tested
    """

##    i = string.rfind(module, '.')
##    if i >= 0:
##        # Dotted module name
##        package = string.strip(module[:i])
##        submodule = string.strip(module[i+1:])
##        parent = moduleFile(package, path, inpackage)
##        return moduleFile(submodule, parent.classes['__path__'], 1)
##    else:
    if module in sys.builtin_module_names:
        # this is a built-in module
        return Module(module, [])

    # search the path for the module
    f = None
    if inpackage:
        try:
            f, file, (suff, mode, type) = imp.find_module(module, path)
        except ImportError:
            f = None
    if f is None:
        fullpath = path + sys.path
        f, file, (suff, mode, type) = imp.find_module(module, fullpath)
#        if type == imp.PKG_DIRECTORY:
#            return Module(module, [], {'__path__': [file]}, ['__path__'])
    if type != imp.PY_SOURCE:
        # not Python source, can't do anything with this module
        f.close()
        return Module(module, [])

    mod = Module(module, f.readlines())
    f.close()
    return mod

##d = open('companions/basecompanions.py').readlines()
##m = Module('asdf', d)
