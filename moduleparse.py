#----------------------------------------------------------------------
# Name:        moduleparse.py
# Purpose:     
#
# Author:      Riaan Booysen, based on 'pyclbr.py'
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

'''Parse one Python file and retrieve classes and methods,
store the code spans and facilitate the extraction and replacement of
method bodies

This file is heavly based on 'pyclbr.py' from the standard python lib

BUGS
Methods within methods not handled

<from pyclbr.py>
Continuation lines are not dealt with at all and strings may confuse
the hell out of the parser, but it usually works.''' # ' <-- bow to font lock

import os, sys
import imp
import re
import string
from types import IntType, StringType

id = '[A-Za-z_][A-Za-z0-9_]*'	# match identifier
blank_line = re.compile('^[ \t]*($|#)')
is_class = re.compile('^class[ \t]+(?P<id>%s)[ \t]*(?P<sup>\([^)]*\))?[ \t]*:'%id)
is_method = re.compile('^[ \t]*def[ \t]+(?P<id>%s)[ \t]*\((?P<sig>.*)\)[ \t]*[:][ \t]*$'%id) 
is_func = re.compile('^def[ \t]+(?P<id>%s)[ \t]*\((?P<sig>.*)\)[ \t]*[:][ \t]*$'%id) 
is_attrib = re.compile('[ \t]*self[.](?P<name>%s)[ \t]*='%id) 
is_import = re.compile('^import[ \t]*(?P<imp>[^#;]+)')
is_from = re.compile('^from[ \t]+(?P<module>%s([ \t]*\\.[ \t]*%s)*)[ \t]+import[ \t]+(?P<imp>[^#;]+)'%(id, id))
dedent = re.compile('^[^ \t]')
indent = re.compile('^[^ \t]*')
is_doc_quote = re.compile("'''")
id_doc_quote_dbl = re.compile('"""')
is_todo = re.compile('^[ \t]*# XXX')
list = '[A-Za-z_][A-Za-z0-9_]*'	# match identifier
is_wid = re.compile('^\[(?P<wids>.*)\][ \t]*[=][ \t]*NewIds[(](?P<count>\d+)[)]$')

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

def NewIds(cnt):
    l = []
    for i in range(cnt):
        l.append(i)
    return l

def NewIds(cnt):
    return map(lambda _init_ctrls: NewId(), range(cnt))
    
class CodeBlock:
    def __init__(self, sig, start, end):
        self.signature = sig
        self.start = start
        self.end = end
    
    def renumber(self, from_line, increment):
        if self.start > from_line:
            self.start = self.start + increment
            self.end = self.end + increment
        elif self.end > from_line:
            self.end = self.end + increment
            
# each Python class is represented by an instance of this class
class Class:
    '''Class to represent a Python class.'''
    def __init__(self, module, name, super, file, lineno):
        self.module = module
        self.name = name
        if super is None:
	    super = []
        self.super = super
        self.methods = {}
        self.method_order = []
        self.attributes = {}
        self.file = file
        self.block = CodeBlock('', lineno, lineno)
        self.extent = lineno
    
    def extend_extent(self, lineno):
        if lineno > self.extent: self.extent = lineno                

    def _addmethod(self, name, sig, linestart, lineend = None):
        if not lineend: lineend = linestart
        self.methods[name] = CodeBlock(sig, linestart, lineend)
        self.method_order.append(name)
        self.extend_extent(lineend)

    def _endmethod(self, name, lineend):
        self.methods[name].end = lineend
        self.extend_extent(lineend)

def Test2():
    pass
    
class Module:
    """ Represents a Python module.
        
        Parses and maintains dictionaries of the classes and 
        functions defined in a module. """
        
        
    def finaliseEntry(self, cur_class, cur_meth, cur_func, lineno):
        """ When a new structure is encountered, finalise the current
            structure, whatever it is. """ 
        if cur_class:
            if cur_meth:
                cur_class._endmethod(cur_meth, lineno -1)
                cur_meth = ''
            cur_class.block.end = lineno
            cur_class = None
            cur_func = ''
        elif cur_func:
            self.functions[cur_func].end = lineno -1
            cur_func = ''
        
        return cur_class, cur_meth, cur_func


    def readline(self):
        line = self.source[self.lineno]
        self.lineno = self.lineno + 1
        return line	# remove line feed        

    def __init__(self, module, modulesrc, classes = {}, class_order = [], 
      file = ''):
        self.classes = {}#classes
        self.class_order = []#class_order
        self.functions = {}
        self.function_order = []
        self.imports = {}
        self.todos = []
        self.wids = []
        cur_class = None
        cur_meth = ''
        cur_func = ''
        imports = []
        self.lineno = 0
        self.source = modulesrc
        while self.lineno < len(self.source):
            line = string.rstrip(self.readline())

            res = is_todo.match(line)
            if res:
                self.todos.append((self.lineno, string.strip(line[res.span()[1]:])))
                continue

            if blank_line.match(line):
                # ignore blank (and comment only) lines
                continue

            res = is_class.match(line)
            if res:
                # we found a class definition
                cur_class, cur_meth, cur_func = self.finaliseEntry(cur_class, 
                  cur_meth, cur_func, self.lineno)
                class_name = res.group('id')
                inherit = res.group('sup')
                if inherit:
                    # the class inherits from other classes
                    inherit = string.strip(inherit[1:-1])
                    names = []
                    for n in string.split(inherit, ','):
                        n = string.strip(n)
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
                cur_class = Class(module, class_name, inherit, file, self.lineno)
                cur_meth = ''
                self.classes[class_name] = cur_class
                self.class_order.append(class_name)
                continue

            res = is_func.match(line)
            if res:
                cur_class, cur_meth, cur_func = self.finaliseEntry(cur_class, 
                  cur_meth, cur_func, self.lineno)
                func_name = res.group('id')
                cur_func = func_name
                self.functions[func_name] = CodeBlock(res.group('sig'), 
                  self.lineno, 0)
                self.function_order.append(func_name)
                continue

            res = is_method.match(line)
            if res:
                # found a method definition
                if cur_class:
                    # and we know the class it belongs to
                    if cur_meth:
                        cur_class._endmethod(cur_meth, self.lineno -1)
                    meth_name = res.group('id')
                    cur_class._addmethod(meth_name, res.group('sig'), self.lineno)
                    cur_meth = meth_name
                continue

            res = is_attrib.match(line)
            if res:
                # found a attribute binding
                if cur_class:
                    # and we know the class it belongs to
                    cur_class.attributes[res.group('name')] = CodeBlock('', 
                      self.lineno, self.lineno)
                           
                continue

            res = is_import.match(line)
            if res:
                # import module
                for n in string.splitfields(res.group('imp'), ','):
                    n = string.strip(n)
                    self.imports[n] = [self.lineno]
                continue

            res = is_from.match(line)
            if res:
                # from module import stuff
                mod = res.group('module')
                if not self.imports.has_key(mod):
                    self.imports[mod] = [self.lineno]

##                names = string.splitfields(res.group('imp'), ',')
##                for n in names:
##                    n = string.strip(n)
##                    self.imports[mod].append(n)
                continue

            res = is_wid.match(line)
            if res:
                self.wids.append((self.lineno, res))
	    
            if dedent.match(line):
                # end of class definition
                cur_class, cur_meth, cur_func = self.finaliseEntry(cur_class, 
                  cur_meth, cur_func, self.lineno)

        # if it's the last class in the source, it will not dedent
        # check manually
        cur_class, cur_meth, cur_func = self.finaliseEntry(cur_class, cur_meth, 
          cur_func, self.lineno +1)

    def extractClassBody(self, class_name):
         block = self.classes[class_name].block
         return self.source[block.start:block.end]

    def addMethod(self, class_name, method_name, method_params, method_body):
        new_length = len(method_body) + 2
        if not method_body: return
        a_class = self.classes[class_name]
        
        # Add a method code block
        ins_point = a_class.extent + 1
        a_class._addmethod(method_name, method_params, ins_point, ins_point + \
          new_length)
        
        # Add in source
        self.source[ins_point : ins_point] = \
          ['    def %s(%s):' % (method_name, method_params)] + method_body + ['']
          
        # renumber code blocks
        self.renumber(new_length, ins_point)
          
    def extractMethodBody(self, class_name, method_name):
	block = self.classes[class_name].methods[method_name]
	return self.source[block.start:block.end]

    def renumber(self, deltaLines, start):
        if deltaLines:
            for cls in self.classes.values():
                cls.block.renumber(start, deltaLines)
                for block in cls.methods.values():
                    block.renumber(start, deltaLines)
                for block in cls.attributes.values():
                    block.renumber(start, deltaLines)
            for func in self.functions.values():
                func.renumber(func.start, deltaLines)

    def replaceBody(self, name, code_block_dict, new_body, ):
        newLines = len(new_body)
        if not new_body: return
        code_block = code_block_dict[name]
        prevLines = code_block.end - code_block.start
        deltaLines = newLines - prevLines

        self.source[code_block.start : code_block.end] = new_body
        
        self.renumber(deltaLines, code_block.start)

    def replaceMethodBody(self, class_name, method_name, new_body):
        self.replaceBody(method_name, self.classes[class_name].methods, new_body)
        
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
        if len(self.class_order): 
          classStart = self.classes[self.class_order[0]].block.start -1
        else:
          classStart = len(self.source)  

        if len(self.function_order): 
          funcStart = self.functions[self.function_order[0]].start -1
        else:
          funcStart = len(self.source)  

        modTop = self.source[:min(classStart, funcStart)]
        l = []
        for i in modTop:
            if not string.strip(i):
                l.append('<P>')
            else:
                l.append(i)
                
        return self.searchDoc(string.join(l))#, '<BR>'))
        
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

        cb = string.join(self.source[cls.block.start: min(methStart, 
          cls.block.end)])
        
        return self.searchDoc(cb)
                        
    def getClassMethDoc(self, class_name, meth_name):
        """ Extract the doc string for a method """
        cb = string.join(self.extractMethodBody(class_name, meth_name))
        return self.searchDoc(cb)
    
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
        meth = self.classes[class_name].methods[old_method_name]
        idx = meth.start -1
        self.source[idx] = string.replace(self.source[idx], old_method_name, 
          new_method_name, 1)
        del self.classes[class_name].methods[old_method_name]
        self.classes[class_name].methods[new_method_name] = meth
        #rename order
        idx = self.classes[class_name].method_order.index(old_method_name)
        del self.classes[class_name].method_order[idx]
        self.classes[class_name].method_order.insert(idx, new_method_name)
        
    
    def replaceFunctionBody(self, func_name, new_body):
        self.replaceBody(func_name, self.functions, new_body)

    def travTilBase(self, name, classes, root):
        """ Recursive method that traverses the class hierarchy """
        if len(classes[name].super) == 0:
            if not root.has_key(name):
                root[name] = {}
            return root[name]
        else:
            for super in classes[name].super:
                #base class of this module
                if type(super) is StringType:
                    if not root.has_key(super):
                        root[super] = {name: {}}
                    elif not root[super].has_key(name):
                        root[super][name] = {}
                    
                    continue 
                else:
                    c = self.travTilBase(super.name, classes, root)
                    if not c.has_key(name):
                        c[name] = {}
                    return c[name]
            return root[super][name]

    def createHierarchy(self):
        """ Build the inheritance hierarchy """
        hierc = {}
        for cls in self.classes.keys():
            self.travTilBase(cls, self.classes, hierc)
        
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

