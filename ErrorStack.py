import string
import re

fileLine = re.compile('[ ]*File "(?P<filename>.+)", line (?P<lineno>[0-9]+)')

class StackEntry:
    def __init__(self, file = '', lineNo = 0, line = ''):
        self.file = file
        self.line = line
        self.lineNo = lineNo
    
    def __repr__(self):
        return 'File "%s", line %d\n%s' % (self.file, self.lineNo, self.line)

class PseudoFile:
    """ Base class for file like objects to facilitate StdOut for the Shell."""
    def __init__(self, output):
        self.output = output

    def writelines(self, l):
        map(self.write, l)
    
    def write(s):
        pass

    def flush(self):
        pass
                
class ErrorParser(PseudoFile):
    def __init__(self):
        self.lines = []
        self.stack = []
        self.error = ()
        
    def write(self, s):
        self.lines.append(s)
    
    def parse(self):
        if len(self.lines) >= 2:
            self.error = list(string.split(self.lines.pop(), ': '))
            self.error.append(string.find(self.lines.pop(), '^'))
            for idx in range(0, len(self.lines), 2):
                mo = fileLine.match(self.lines[idx])
                self.stack.append(StackEntry(mo.group('filename'), 
                  int(mo.group('lineno')), self.lines[idx + 1]))

    def printError(self):
        print self.error
        for se in self.stack:
            print se
