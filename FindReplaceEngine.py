#-----------------------------------------------------------------------------
# Name:        FindReplaceEngine.py
# Purpose:     
#
# Author:      Tim Hochberg
#
# Created:     2001/29/08
# RCS-ID:      $Id$
# Copyright:   (c) 2001 Tim Hochberg
# Licence:     GPL
#-----------------------------------------------------------------------------
import os, re, string

from wxPython.wx import *

from FindResults import FindResults
import Utils

class FindError(ValueError):
    pass

def _fix(match, offset, length, selectionStart):
    if match is None: 
        return None
    r = []
    try:
        for i in match.span():
            r.append((i + offset) % length + selectionStart)
    except:pass
    return tuple(r)
        
class FindReplaceEngine:
    
    def __init__(self, case=0, word=0, regex=0, wrap=1, reverse=0):
        self.case = 0
        self.word = 0
        self.regex = 0
        self.wrap = 1
        self.closeOnFound = 0
        self.reverse = 0
        self.selection = 0
        self.lastFind = ""
        self.lastReplace = ""
        self.suffixes = [".py"]
        
        self.loadOptions()
        
    def findInSource(self, view, pattern):
        self.lastFind = pattern
        if self.selection:
            result = self._find(view.GetSelectedText(), pattern, 0, view.GetSelection()[0])
        else:
            start = view.GetSelection()[not self.reverse]
            result = self._find(view.GetText(), pattern, start, 0)
        if result is None:
            raise FindError("'%s' not found" % pattern)
        view.model.editor.addBrowseMarker(view.GetCurrentLine())

        if (result[0] < view.GetCurrentPos() and not self.reverse and self.wrap) or \
           (result[0] > view.GetCurrentPos() and self.reverse and self.wrap):
            view.model.editor.statusBar.setHint('Search wrapped', 'Warning', ringBell=1)

        view.SetSelection(result[0], result[1])
        
    def findNextInSource(self, view):
        self.findInSource(view, self.lastFind)

    def _findAllInSource(self, text, pattern, selectionStart):
        viewResults = []
        for s, e in self._findAll(text, pattern, 0, selectionStart):
            t = text[:s]
            lineNo = string.count(t, '\n')
            left = max(string.rfind(t, '\n'), 0) + 1
            index = s - left
            line = string.split(text[left:], "\n", 1)[0]
            viewResults.append((lineNo+1, index+1, line))
        return viewResults
            
    def findAllInSource(self, view, pattern):
        self.lastFind = pattern
        if self.selection:
            results = self._findAllInSource(view.GetSelectedText(), pattern, 
                                            view.GetSelection()[0])
        else:
            results = self._findAllInSource(view.GetText(), pattern, 0)
        name = 'Results: ' + pattern
        if not view.model.views.has_key(name):
            resultView = view.model.editor.addNewView(name, FindResults)
        else:
            resultView = view.model.views[name]
        resultView.tabName = name
        resultView.results = {view.model.filename : results} # XXX should this be viewName?
        resultView.findPattern = pattern
        resultView.refresh()
        resultView.focus() 

    def replaceInSource(self, view, pattern, new):
        self.lastReplace = new
        self.lastFind = pattern
        # GetSelectedText returns bogus string when nothing is selected
        selRange = view.GetSelection()
        selText = selRange[0] != selRange[1] and view.GetSelectedText() or ''
        # Only select for the first replace
##        # XXX Should maybe use _find to determine if current selection
##        # XXX is a match
##        
##        try: self._find(selText, pattern, 0, 0)
##        except FindError: pass
##        else:
##        if selText and ((selText == pattern and self.case) or \
##          (string.lower(selText) == string.lower(pattern) and not self.case)):
        if self._find(selText, pattern, 0, 0) is not None:
            if self.selection:
                result = self._find(selText, pattern, 0, selRange[0])
            else:
                start = selRange[self.reverse]
                result = self._find(view.GetText(), pattern, start, 0)
            if result is None:
                raise FindError("'%s' not found" % pattern)
            view.SetSelection(result[0], result[1])
            compiled = self._compile(pattern)
            if self.regex:
                new = compiled.sub(new, view.GetSelectedText())
            view.ReplaceSelection(new)
            
        # Attempt to find the next replacement
        try:
            self.findInSource(view, pattern)
        except FindError:
            pass
 
    def replaceAllInSource(self, view, pattern, new):
        self.lastFind = pattern
        self.lastReplace = new
        text = view.GetText()
        # Replace from the end so that we can do the replace in place without
        # the indices getting messed up.
        self.reverse, oldReverse = 1, self.reverse
        if self.selection:
            results = self._findAll(view.GetSelectedText(), pattern, 0, view.GetSelection()[0])
        else:
            results = self._findAll(view.GetText(), pattern, 0, 0)
        self.reverse = oldReverse
        compiled = self._compile(pattern)
        if results == []:
            return
        view.model.editor.addBrowseMarker(view.GetCurrentLine())
        for item in results: 
            view.SetSelection(item[0], item[1])
            n = new
            if self.regex:
                n = compiled.sub(new, view.GetSelectedText())
            view.ReplaceSelection(n)
        view.model.editor.statusBar.setHint("%s items replaced" % len(results))
    
    def findNamesInPackage(self, view):
        names = []
        packages = [os.path.dirname(view.model.assertLocalFile())]
        for base in packages:
            for p in map(lambda n, base=base: os.path.join(base, n), os.listdir(base)):
            #for p in [os.path.join(base, n) for n in os.listdir(base)]: #1.5.2 support
                if os.path.isfile(p) and os.path.splitext(p)[1] in self.suffixes:
                    names.append(p)
                elif os.path.isdir(p) and os.path.isfile(os.path.join(base, "__init__.py")):
                    packages.append(p)
        names.sort()
        return names
        
    def findAllInFiles(self, names, view, pattern):
        self.lastFind = pattern
        results = {}
        # Setup progress dialog
        dlg = wxProgressDialog("Finding all in package '%s'" % os.path.dirname(view.model.filename),
                               'Searching...',
                                len(names),
                                view,
                                wxPD_CAN_ABORT | wxPD_APP_MODAL | wxPD_AUTO_HIDE)
        try:
            for i in range(len(names)):
                filename = self._getValidFilename(names[i])
                if not filename: continue
                results[names[i]] = self._findAllInSource(open(filename).read(), pattern, 0)
                if not dlg.Update(i):
                    view.model.editor.statusBar.setHint("Search aborted")
                    break
            name = 'Results: ' + pattern
            if not view.model.views.has_key(name):
                resultView = view.model.editor.addNewView(name, FindResults)
            else:
                resultView = view.model.views[name]
            resultView.tabName = name
            resultView.results = results
            resultView.findPattern = pattern
            resultView.refresh()
            resultView.focus()            
        finally:
            dlg.Destroy()
        name = 'Results: ' + pattern
        if not view.model.views.has_key(name):
            resultView = view.model.editor.addNewView(name, FindResults)
        else:
            resultView = view.model.views[name]

    def findAllInPackage(self, view, pattern):
        self.findAllInFiles(self.findNamesInPackage(view), view, pattern)
 
    def findAllInApp(self, view, pattern):
        modules = view.model.modules.keys()
        modules.sort()
        names = map(view.model.moduleFilename, modules)
        #names = [view.model.moduleFilename(m) for m in modules]
        self.findAllInFiles(names, view, pattern)

    
    def _compile(self, pattern):
        flags = [re.IGNORECASE, 0][self.case]
        if not self.regex:
            pattern = re.escape(pattern)
        if self.word:
            pattern = r"\b%s\b" % pattern
        return re.compile(pattern, flags)

    def _processText(self, text, start):
        before, after = text[:start], text[start:]
        if self.wrap:
            offset = start
            domain = after + before
        elif not self.reverse:
            offset = start
            domain = after
        else:
            offset = 0
            domain = before
        return domain, offset
            
    def _findAll(self, text, pattern, start, selectionStart):
        compiled = self._compile(pattern)
        domain, offset = self._processText(text, start)
        matches = []
        start = 0
        while 1:
            s = compiled.search(domain, start)
            if s is None or s.end() == 0: 
                break
            start = s.end()
            matches.append(_fix(s, offset, len(text), selectionStart))
        if self.reverse:
            matches.reverse()
        return matches
        
    def _find(self, text, pattern, start, selectionStart): 
        if self.reverse:
            return (self._findAll(text, pattern, start, selectionStart) + [None])[0]
        compiled = self._compile(pattern)
        domain, offset = self._processText(text, start)
        return _fix(compiled.search(domain), offset, len(text), selectionStart)

    def loadOptions(self):
        try:
            conf = Utils.createAndReadConfig('Explorer')
            if conf.has_section('finder'): 
                self.wrap = conf.getint('finder', 'wrap')
                self.closeOnFound = conf.getint('finder', 'closeonfound')
        except:
            print 'Problem loading finder options'

    def saveOptions(self):
        try:
            conf = Utils.createAndReadConfig('Explorer')
            if not conf.has_section('finder'): conf.add_section('finder')
            conf.set('finder', 'wrap', self.wrap)
            conf.set('finder', 'closeonfound', self.closeOnFound)
            conf.write(open(conf.confFile, 'w'))
        except Exception, err:
            print 'Problem saving finder options: %s' % err

    def _getValidFilename(self, filename):
        protsplit = string.split(filename, '://')
        if len(protsplit) > 1:
            if protsplit[0] != 'file' or len(protsplit) > 2:
                wxLogWarning('%s not searched, only local files allowed'%filename)
                return ''
            return protsplit[1]
        return filename

   
   
   