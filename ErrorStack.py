#-----------------------------------------------------------------------------
# Name:        ErrorStack.py
# Purpose:     
#                
# Author:      Riaan Booysen
#                
# Created:     2000/05/29
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
import string
import re
import sys

if sys.version[:2] == '2.':
    tb_id = 'Traceback (most recent call last):'
else:
    tb_id = 'Traceback (innermost last):'

fileLine = re.compile('  File "(?P<filename>.+)", line (?P<lineno>[0-9]+)')

class StackEntry:
    def __init__(self, file = '', lineNo = 0, line = ''):
        self.file = file
        self.line = line
        self.lineNo = lineNo
    
    def __repr__(self):
        return 'File "%s", line %d\n%s' % (self.file, self.lineNo, self.line)

class PseudoFile:
    """ Base class for file like objects to facilitate StdOut for the Shell."""
    def __init__(self, output = None):
        if output is None: output = []
        self.output = output

    def writelines(self, l):
        map(self.write, l)
    
    def write(s):
        pass

    def flush(self):
        pass

class RecFile(PseudoFile):
    def write(self, s):
        self.output.append(s)
    
    def readlines(self):
        return self.output

                
class ErrorParser:
    def __init__(self, lines):
        self.lines = lines
        self.stack = []
        self.error = ()
        self.parse()
        
#    def write(self, s):
#        self.lines.append(s)
    
    def parse(self):
        if len(self.lines) >= 2:
            self.error = list(string.split(self.lines.pop(), ': '))
#            self.error.append(string.find(self.lines.pop(), '^'))
            for idx in range(0, len(self.lines) -1):
                mo = fileLine.match(self.lines[idx])
                if mo:
                    self.stack.append(StackEntry(mo.group('filename'), 
                          int(mo.group('lineno')), self.lines[idx + 1]))

    def printError(self):
        print self.error
        for se in self.stack:
            print se

def errorList(stderr):
    errs = []
    currerr = []
    lines = stderr.readlines()
    print lines
    lines.reverse()
    for line in lines:
        if string.strip(line) == tb_id:
            errs.append(currerr)
            currerr = []
        else:
            currerr.append(line)
    errs.reverse()

    res = []
    for err in errs:
        err.reverse()
        res.append(ErrorParser(err))
    return res
    
    
def test():
    class pf:
        def __init__(self, data):
            self.data = data
        def readlines(self):
            return self.data
            
    tb = [tb_id+'\n',
          '  File "Views\AppViews.py", line 172, in OnRun\n',
          '    self.model.run()\n',
          '  File "EditorModels.py", line 548, in run\n',
          "    self.checkError(c, 'Ran')",
          '  File "EditorModels.py", line 513, in checkError\n',
          '    err.parse()\n',
          'AttributeError: parse\n',
          tb_id+'\n',
          '  File "Views\AppViews.py", line 172, in OnRun\n',
          '    self.model.run()\n',
          '  File "EditorModels.py", line 548, in run\n',
          "    self.checkError(c, 'Ran')",
          '  File "EditorModels.py", line 513, in checkError\n',
          '    err.parse()\n',
          'AttributeError: parse\n']
    return errorList(pf(tb))