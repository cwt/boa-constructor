
import os

try: from cPickle import Pickler, Unpickler
except: from pickle import Pickler, Unpickler


class FileBreakpointList:
    def __init__(self):
        self.lines = {}  # lineno -> [{'temporary', 'cond', 'enabled'}]

    def loadBreakpoints(self, fn):
        try:
            if os.path.exists(fn):
                f = open(fn, 'rb')
                u = Unpickler(f)
                newlines = u.load()
                # The following line isn't 100% accurate
                # when multiple breakpoints are set on a
                # single line.
                self.lines.update(newlines)
                return 1
            else:
                return 0
        except:
            self.lines = {}
            return 0

    def saveBreakpoints(self, fn):
        try:
            if len(self.lines):
                savelines = {}
                # Filter out the temporary lines when saving.
                for lineno, linebreaks in self.lines.items():
                    savelines[lineno] = saveline = []
                    for brk in linebreaks:
                        if not brk['temporary']:
                            saveline.append(brk)
                f = open(fn, 'wb')
                p = Pickler(f)
                p.dump(savelines)
            else:
                os.remove(fn)
        except:
            pass

    def setBreakpoint(self, lineno, temp=0, cond=None):
        newbrk = {'temporary':temp, 'cond':cond, 'enabled':1}
        if self.lines.has_key(lineno):
            linebreaks = self.lines[lineno]
            for brk in linebreaks:
                if brk['temporary'] == temp and brk['cond'] == cond:
                    # Already added.
                    return
            linebreaks.append(newbrk)
        else:
            self.lines[lineno] = linebreaks = [newbrk]

    def deleteBreakpoints(self, lineno):
        if self.lines.has_key(lineno):
            del self.lines[lineno]

    def enableBreakpoints(self, lineno, enable=1):
        if self.lines.has_key(lineno):
            linebreaks = self.lines[lineno]
            for brk in linebreaks:
                brk['enabled'] = enable

    def listBreakpoints(self):
        rval = []
        for lineno, linebreaks in self.lines.items():
            for brk in linebreaks:
                brkinfo = {'lineno':lineno}
                brkinfo.update(brk)
                rval.append(brkinfo)
        return rval

    def hasBreakpoint(self, lineno):
        return self.lines.has_key(lineno)

    def clearTemporaryBreakpoints(self):
        for linebreaks in self.lines.values():
            idx = 0
            while idx < len(linebreaks):
                brk = linebreaks[idx]
                if brk['temporary']:
                    del linebreaks[idx]
                else:
                    idx = idx + 1

    def clearAllBreakpoints(self):
        self.lines = {}


class BreakpointList:
    def __init__(self):
        self.files = {}  # filename -> FileBreakpointList

    def setBreakpoint(self, filename, lineno, temp=0, cond=None):
        filelist = self.getFileBreakpoints(filename)
        filelist.setBreakpoint(lineno, temp, cond)

    def deleteBreakpoints(self, filename, lineno):
        if self.files.has_key(filename):
            filelist = self.files[filename]
            filelist.deleteBreakpoints(lineno)

    def enableBreakpoints(self, filename, lineno, enable=1):
        if self.files.has_key(filename):
            filelist = self.files[filename]
            filelist.enableBreakpoints(lineno, enable)

    def clearTemporaryBreakpoints(self):
        for filelist in self.files.values():
            filelist.clearTemporaryBreakpoints()

    def getFileBreakpoints(self, filename):
        if self.files.has_key(filename):
            return self.files[filename]
        else:
            self.files[filename] = filelist = FileBreakpointList()
            return filelist

    def hasBreakpoint(self, filename, lineno):
        if self.files.has_key(filename):
            filelist = self.files[filename]
            return filelist.hasBreakpoint(lineno)
        return 0

    def getBreakpointList(self, fn=None):
        '''Returns a list designed to pass to the setAllBreakpoints()
        debugger method.'''
        rval = []
        for filename, filelist in self.files.items():
            if fn is None or filename == fn:
                for lineno, linebreaks in filelist.lines.items():
                    for brk in linebreaks:
                        brkinfo = {'filename': filename,
                                   'lineno': lineno}
                        brkinfo.update(brk)
                        rval.append(brkinfo)
        return rval


# ??? Should this be a global variable?
bplist = BreakpointList()
