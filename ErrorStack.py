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
import string, re, os, sys, pprint
from ShellEditor import PseudoFile

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

##class PseudoFile:
##    """ Base class for file like objects to facilitate StdOut for the Shell."""
##    def __init__(self, output = None):
##        if output is None: output = []
##        self.output = output
##
##    def writelines(self, l):
##        map(self.write, l)
##    
##    def write(s):
##        pass
##
##    def flush(self):
##        pass

class RecFile(PseudoFile):
    def write(self, s):
        self.output.append(s)
    
    def readlines(self):
        return self.output

                
class StackErrorParser:
    def __init__(self, lines):
        self.lines = lines
        self.stack = []
        self.error = ()
        self.parse()

    def printError(self):
        print self.error
        for se in self.stack:
            print se
            
    def __repr__(self):
        return `self.error`+'\n'+pprint.pformat(self.stack)

        
#    def write(self, s):
#        self.lines.append(s)

def buildErrorList(lines):
    errs = []
    currerr = []
    
    lines.reverse()
    for line in lines:
        if string.strip(line) == tb_id:
            errs.append(currerr)
            currerr = []
        else:
            currerr.append(line)
    errs.reverse()

    # undo :)
    lines.reverse()

    res = []
    for err in errs:
        err.reverse()
        res.append(StdErrErrorParser(err))
    return res

def errorList(stderr):
    return buildErrorList(stderr.readlines())


class StdErrErrorParser(StackErrorParser):    
    def parse(self):
        if len(self.lines) >= 2:
            self.error = list(string.split(self.lines.pop(), ': '))
#            self.error.append(string.find(self.lines.pop(), '^'))
            for idx in range(0, len(self.lines) -1):
                mo = fileLine.match(self.lines[idx])
                if mo:
                    self.stack.append(StackEntry(mo.group('filename'), 
                          int(mo.group('lineno')), self.lines[idx + 1]))

# Limit stack size / processing time
# Zero to ignore limit
max_stack_depth = 0
max_lines_to_process = 0

class CrashTraceLogParser(StackErrorParser):
    """ Build a stack from a trace file built with option -T """
    def parse(self):
        lines = self.lines
        stack = self.stack = []
        fileSize = len(lines)
        self.error = ('Core dump stack', 'trace file size: '+`fileSize`)

        baseDir = string.strip(lines[0])
        del lines[0]
        
        lines.reverse()

        cnt = 0
        while len(lines):
            cnt = cnt + 1
            if max_lines_to_process and cnt >= max_lines_to_process:
                break
            line = lines[0]
            del lines[0]
            try:
                file, lineno, frameid, event, arg = string.split(line, '|')[:5]
            except:
                print 'Error on line', cnt, line
                break
            if event == 'call':
                if not os.path.isabs(file):
                    file = os.path.join(baseDir, file)
                try: code = open(file).readlines()[int(lineno)-1]
                except IOError: code = ''
                stack.append( StackEntry(file, int(lineno), code) )
                if max_stack_depth and len(stack) >= max_stack_depth:
                    break
            elif event == 'return':
                idx = 0
                while 1:
                    try:
                        _file, _lineno, _frameid, _event = string.split(lines[idx], '|')[:4]
                    except:
                        print 'Error on find', cnt, lines[idx]
                        break

                    if _file == file and _frameid == frameid and _event == 'call':
                        del lines[:idx+1]
                        cnt = cnt + idx
                        break

                    idx = idx + 1
                    if idx >= len(lines):
                        print 'Call not found'
                        del lines[:]
                        break

        if len(stack):
            stack.reverse()
        else:
            self.error = ('Empty (resolved) stack', 'trace file size: '+`fileSize`)
        

def crashError(file):
    try:
        lines = open(file).readlines()
        ctlp = CrashTraceLogParser(lines)
        open(file+'.stack', 'w').write(`ctlp`)
        return [ctlp]
    except IOError:
        return []

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

test()