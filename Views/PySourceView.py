#----------------------------------------------------------------------
# Name:        PySourceView.py                                         
# Purpose:     Views for editing source code                           
#                                                                      
# Author:      Riaan Booysen                                           
#                                                                      
# Created:     2000/04/26                                              
# RCS-ID:      $Id$ 
# Copyright:   (c) 1999, 2000 Riaan Booysen                            
# Licence:     GPL                                                     
#----------------------------------------------------------------------

from wxPython.wx import *
from wxPython.stc import *
import os, string
import EditorViews, ProfileView, Search, Help, Preferences
from StyledTextCtrls import PythonStyledTextCtrlMix, BrowseStyledTextCtrlMix, HTMLStyledTextCtrlMix, FoldingStyledTextCtrlMix, CPPStyledTextCtrlMix, idWord, new_stc, old_stc
from PrefsKeys import keyDefs
import methodparse
import time
import wxNamespace
from Debugger.Breakpoint import bplist

simpleAppText = '''

if __name__ == '__main__':
    app = wxPySimpleApp()
    frame = create(None)
    frame.Show(true)
    app.MainLoop()'''
    
indentLevel = 4
endOfLines = {  wxSTC_EOL_CRLF : '\r\n',
                wxSTC_EOL_CR : '\r',
                wxSTC_EOL_LF : '\n'}

brkPtMrk = 1
stepPosMrk = 2
tmpBrkPtMrk = 3
#brwsIndc = 0

#wxID_PYTHONSOURCEVIEW, 
[wxID_CPPSOURCEVIEW, wxID_HTMLSOURCEVIEW, wxID_TEXTVIEW, wxID_SOURCECUT, 
 wxID_SOURCECOPY, wxID_SOURCEPASTE, wxID_SOURCEUNDO, wxID_SOURCEREDO] \
 = map(lambda x: wxNewId(), range(8))

class EditorStyledTextCtrl(wxStyledTextCtrl, EditorViews.EditorView):
    refreshBmp = 'Images/Editor/Refresh.bmp'
    undoBmp = 'Images/Shared/Undo.bmp'
    redoBmp = 'Images/Shared/Redo.bmp'
    cutBmp = 'Images/Shared/Cut.bmp'
    copyBmp = 'Images/Shared/Copy.bmp'
    pasteBmp = 'Images/Shared/Paste.bmp'
    findBmp = 'Images/Shared/Find.bmp'
    findAgainBmp = 'Images/Shared/FindAgain.bmp'
    def __init__(self, parent, wId, model, actions, defaultAction = -1):
        wxStyledTextCtrl.__init__(self, parent, wId, style = wxCLIP_CHILDREN)
        a =  (('Refresh', self.OnRefresh, self.refreshBmp, keyDefs['Refresh']),
              ('-', None, '', ()),
              ('Undo', self.OnEditUndo, self.undoBmp, ()),
              ('Redo', self.OnEditRedo, self.redoBmp, ()),
              ('-', None, '', ()),
              ('Cut', self.OnEditCut, self.cutBmp, ()),
              ('Copy', self.OnEditCopy, self.copyBmp, ()),
              ('Paste', self.OnEditPaste, self.pasteBmp, ()),
              ('-', None, '', ()),
              ('Find', self.OnFind, self.findBmp, keyDefs['Find']),
              ('Find again', self.OnFindAgain, self.findAgainBmp, keyDefs['FindAgain']))

        EditorViews.EditorView.__init__(self, model, a + actions, defaultAction)

        self.SetEOLMode(wxSTC_EOL_LF)
        self.eol = endOfLines[self.GetEOLMode()]

        self.pos = 0
        self.nonUserModification  = false 

        self.lastSearchResults = []
        self.lastSearchPattern = ''
        self.lastMatchPosition = None

        self.lastStart = 0


    def setReadOnly(self, val):
        EditorViews.EditorView.readOnly(self, val)
        self.SetEditable(val)

    def getModelData(self):
        return self.model.data
    
    def setModelData(self, data):
        self.model.data = data

    def refreshCtrl(self):
        self.pos = self.GetCurrentPos() 
#        line = self.GetCurrentLine()
        prevVsblLn = self.GetFirstVisibleLine()
        
        self.SetText(self.getModelData())
        self.EmptyUndoBuffer()
        self.GotoPos(self.pos)
        curVsblLn = self.GetFirstVisibleLine()
        self.ScrollBy(0, prevVsblLn - curVsblLn)
        
        self.nonUserModification = false 
        self.updatePageName()

    def refreshModel(self):
        if self.isModified():
            self.model.modified = true
        self.nonUserModification = false 
        
        # hack to stop wxSTC from eating the last character
        self.InsertText(self.GetTextLength(), ' ')
        
        self.setModelData(self.GetText())
        self.EmptyUndoBuffer()
        EditorViews.EditorView.refreshModel(self) 
        
        # Remove from modified views list
        if self.model.viewsModified.count(self.viewName):
             self.model.viewsModified.remove(self.viewName)
        
        self.updateEditor()

    def gotoLine(self, lineno, offset = -1):
        self.GotoLine(lineno)
        vl = self.GetFirstVisibleLine()
        self.ScrollBy(0, lineno -  vl)
        if offset != -1: self.SetCurrentPosition(self.GetCurrentPos()+offset+1)
        
    def selectSection(self, lineno, start, word):
        self.gotoLine(lineno)
        length = len(word)
        startPos = self.GetLineStartPos(lineno) + start
        endPos = startPos + length
        self.SetSelection(startPos, endPos)

        self.SetFocus()

    def selectLine(self, lineno):
        self.GotoLine(lineno)
        #sp = self.GetLineStartPos(lineno)
        #ep = self.GetLineStartPos(lineno+1)-1
        #self.SetSelection(sp, ep)

    def updatePageName(self):
        currName = self.notebook.GetPageText(self.pageIdx)
        if self.isModified(): newName = '~%s~' % self.viewName
        else: newName = self.viewName

        if currName != newName:
            if newName == self.viewName:
                if self.model.viewsModified.count(self.viewName):
                    self.model.viewsModified.remove(self.viewName)
            else:
                if not self.model.viewsModified.count(self.viewName):
                    self.model.viewsModified.append(self.viewName)
            self.notebook.SetPageText(self.pageIdx, newName)
            self.notebook.Refresh()
            self.updateEditor()

    def updateStatusBar(self):
        pos = self.GetCurrentPos()
        ln = self.GetLineFromPos(pos)
        st = pos - self.GetLineStartPos(ln) 
#        self.model.editor.updateStatusRowCol(st + 1, ln + 1)

    def updateEditor(self):
        self.model.editor.updateModulePage(self.model)
        self.model.editor.updateTitle()
    
    def updateViewState(self):
        self.updatePageName()
        self.updateStatusBar()

    def insertCodeBlock(self, text):
        cp = self.GetCurrentPos()
        ln = self.GetLineFromPos(cp)
        indent = cp - self.GetLineStartPos(ln)
        lns = string.split(text, self.eol)
        text = string.join(lns, self.eol+indent*' ')

        selTxtPos = string.find(text, '# Your code')
        self.InsertText(cp, text)  
        self.nonUserModification = true
        self.updateViewState()
        self.SetFocus()
        if selTxtPos != -1:
            self.SetSelection(cp + selTxtPos, cp + selTxtPos + 11)

    def isModified(self):
        return self.GetModified() or self.nonUserModification

#---Block commands----------------------------------------------------------

    def reselectSelectionAsBlock(self):
        selStartPos, selEndPos = self.GetSelection()
        selStartLine = self.GetLineFromPos(selStartPos)
        startPos = self.GetLineStartPos(selStartLine)
        selEndLine = self.GetLineFromPos(selEndPos)
        if selEndPos != self.GetLineStartPos(selEndLine):
            selEndLine = selEndLine + 1
        endPos = self.GetLineStartPos(selEndLine)
#        if endPos > startPos: endPos = endPos -1
        self.SetSelection(startPos, endPos)
        return selStartLine, selEndLine

    def processSelectionBlock(self, func):
        self.BeginUndoAction()
        try:
            sls, sle = self.reselectSelectionAsBlock()
            textLst = func(string.split(self.GetSelectedText(), self.eol))[:-1]
            self.ReplaceSelection(string.join(textLst, self.eol)+self.eol)
            if sle > sls: 
                self.SetSelection(self.GetLineStartPos(sls),
                  self.GetLineStartPos(sle)-1)                  
        finally:
            self.EndUndoAction()

#-------Canned events-----------------------------------------------------------

    def OnRefresh(self, event):
##        t1 = time.time()
##        for i in range(1):
        self.refreshModel()
##        t2 = time.time()
####        print t2 - t1
        

    def OnEditCut(self, event):
        self.Cut()   

    def OnEditCopy(self, event):
        self.Copy()   

    def OnEditPaste(self, event):
        self.Paste()

    def OnEditUndo(self, event):
        self.Undo()

    def OnEditRedo(self, event):
        self.Redo()
                       
    def OnFind(self, event):
        s, e = self.GetSelection()
        if s == e:
            txt = self.lastSearchPattern
        else:
            txt = self.GetSelectedText()
        dlg = wxTextEntryDialog(self.model.editor, 'Enter text:', 
          'Find in module', txt)
        try:
            if dlg.ShowModal() == wxID_OK:
                self.lastSearchResults = Search.findInText(\
                  string.split(self.GetText(), self.eol), dlg.GetValue(), false)
                self.lastSearchPattern = dlg.GetValue()
                if len(self.lastSearchResults):
                    self.lastMatchPosition = 0
            else:
                return
        finally:
            dlg.Destroy()

##        print self.lastMatchPosition, self.lastSearchResults
        if self.lastMatchPosition is not None and \
          len(self.lastSearchResults) > self.lastMatchPosition:
            pos = self.lastSearchResults[self.lastMatchPosition]
            self.selectSection(pos[0], pos[1], self.lastSearchPattern)
        else:
            dlg = wxMessageDialog(self.model.editor, 'No matches',
                      'Find in module', wxOK | wxICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()

    def OnFindAgain(self, event):
        if self.lastMatchPosition is None:
            self.OnFind(event)
        else: 
            if self.lastMatchPosition < len(self.lastSearchResults) -1:
                self.lastMatchPosition = self.lastMatchPosition + 1
                pos = self.lastSearchResults[self.lastMatchPosition]
                self.selectSection(pos[0], pos[1], self.lastSearchPattern)
            else:
                dlg = wxMessageDialog(self.model.editor, 'No further matches',
                          'Find in module', wxOK | wxICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.lastMatchPosition = None

class PythonSourceView (EditorStyledTextCtrl,
                        PythonStyledTextCtrlMix,
                        BrowseStyledTextCtrlMix,
                        FoldingStyledTextCtrlMix):
    viewName = 'Source'
    breakBmp = 'Images/Debug/Breakpoints.bmp'
    runCrsBmp = 'Images/Editor/RunToCursor.bmp'
    runAppBmp = 'Images/Debug/RunApp.bmp'
    runBmp = 'Images/Debug/Run.bmp'
    compileBmp = 'Images/Debug/Compile.bmp'
    debugBmp = 'Images/Debug/Debug.bmp'
    modInfoBmp = 'Images/Modules/InfoBlock.bmp'
    profileBmp = 'Images/Debug/Profile.bmp'

    def __init__(self, parent, model):
        if hasattr(model, 'app') and model.app:
            a2 = (('Run application', self.OnRunApp, self.runAppBmp,
                   keyDefs['RunApp']),)
        else:
            a2 = ()
        a1 = (('-', None, '', ()),
              ('Comment', self.OnComment, '-', keyDefs['Comment']),
              ('Uncomment', self.OnUnComment, '-', keyDefs['Uncomment']),
              ('Indent', self.OnIndent, '-', keyDefs['Indent']),
              ('Dedent', self.OnDedent, '-', keyDefs['Dedent']),
              ('-', None, '-', ()),
              ('Profile', self.OnProfile, self.profileBmp, ()),
              ('Compile', self.OnCompile, self.compileBmp,
               keyDefs['Compile']))
        a3 = (('Run module', self.OnRun, self.runBmp, keyDefs['RunMod']),
              ('Run module with parameters', self.OnRunParams, '-', ()),
              ('Debug', self.OnDebug, self.debugBmp, keyDefs['Debug']),
              ('Debug with parameters', self.OnDebugParams, '-', ()),
              ('-', None, '', ()),
              ('Run to cursor', self.OnRunToCursor, self.runCrsBmp, ()),
              ('Toggle breakpoint', self.OnSetBreakPoint, self.breakBmp,
               keyDefs['ToggleBrk']),
              ('Load breakpoints', self.OnLoadBreakPoints, '-', ()),
              ('Save breakpoints', self.OnSaveBreakPoints, '-', ()),
              ('-', None, '', ()),
              ('+View whitespace', self.OnViewWhitespace, '-', ()),
              ('+View EOL characters', self.OnViewEOL, '-', ()),
              ('-', None, '-', ()),
              ('Add module info', self.OnAddModuleInfo, self.modInfoBmp, ()),
              ('Add comment line', self.OnAddCommentLine, '-',
               keyDefs['DashLine']),
              ('Add simple app', self.OnAddSimpleApp, '-', ()),
              ('-', None, '-', ()),
              ('Context help', self.OnContextHelp, '-',
               keyDefs['ContextHelp']))


        wxID_PYTHONSOURCEVIEW = wxNewId()
        
        EditorStyledTextCtrl.__init__(self, parent, wxID_PYTHONSOURCEVIEW, 
          model, a1 + a2 + a3, -1)
        PythonStyledTextCtrlMix.__init__(self, wxID_PYTHONSOURCEVIEW, 0)
        BrowseStyledTextCtrlMix.__init__(self)
        FoldingStyledTextCtrlMix.__init__(self, wxID_PYTHONSOURCEVIEW, 2)
        
        # Initialize breakpoints from file and running debugger
        filename = self.model.filename #string.lower(self.model.filename)
        self.breaks = bplist.getFileBreakpoints(filename)
        self.tryLoadBreakpoints()
        #filename = string.lower(self.model.filename)
        #for file, lineno in bplist.keys():
        #    if file == filename:
        #        for bp in bdb.Breakpoint.bplist[(file, lineno)]:
        #            self.breaks[lineno] = bp

        self.lsp = 0
        self.lastRunParams = ''
        self.lastDebugParams = ''
        
        self.SetMarginType(1, wxSTC_MARGIN_SYMBOL)
        self.SetMarginWidth(1, 12)
        self.SetMarginSensitive(1, true)
        self.MarkerDefine(brkPtMrk, wxSTC_MARK_CIRCLE, 'BLACK', 'RED')
        self.MarkerDefine(stepPosMrk, wxSTC_MARK_SHORTARROW, 'NAVY', 'BLUE')
        self.MarkerDefine(tmpBrkPtMrk, wxSTC_MARK_CIRCLE, 'BLACK', 'BLUE')
        self.CallTipSetBackground(wxColour(255, 255, 232))
        if new_stc:
            self.AutoCompSetIgnoreCase(true)

        # Don't use event, override method from Browser parent
##        EVT_KEY_DOWN(self, self.OnKeyPressed) 
        
        EVT_STC_CHARADDED(self, wxID_PYTHONSOURCEVIEW, self.OnAddChar)

##        EVT_STC_CMDKEY(self, wxID_PYTHONSOURCEVIEW, self.OnKeyPressed)
        self.active = true

    def refreshCtrl(self):
        EditorStyledTextCtrl.refreshCtrl(self)    
        self.setInitialBreakpoints()
        
    def processComment(self, textLst):
        return map(lambda l: '##%s'%l, textLst)

    def processUncomment(self, textLst):
        for idx in range(len(textLst)):
            if len(textLst[idx]) >= 2 and textLst[idx][:2] == '##':
                textLst[idx] = textLst[idx][2:]
        return textLst

    def processIndent(self, textLst):
        return map(lambda l: '%s%s'%(indentLevel*' ', l), textLst)

    def processDedent(self, textLst):
        for idx in range(len(textLst)):
            if len(textLst[idx]) >= indentLevel and \
              textLst[idx][:indentLevel] == indentLevel*' ':
                textLst[idx] = textLst[idx][indentLevel:]
        return textLst

    def getAttribs(self, cls, partial):
        loopCls = cls
        list = []
        while loopCls:
            list.extend(loopCls.methods.keys() + loopCls.attributes.keys())
            if len(loopCls.super):
                prnt = loopCls.super[0]
                if type(prnt) == type(self): # :)
                    loopCls = prnt
                else:
                    loopCls = None
            else:
                loopCls = None

        sel = ''
        if partial:
            for key in list:
##                print key[:len(partial)], partial
                if key[:len(partial)] == partial:
                    sel = key
                    break

        uniqueDct = {}
        for attr in list:
            uniqueDct[attr] = None
        
        return uniqueDct.keys(), sel
    
    def checkCallTipHighlight(self):
        if self.CallTipActive():
            pass
##            pos = self.GetCurrentPos()
##            lnNo = self.GetCurrentLine()
##            lnStPs = self.GetLineStartPos(lnNo)
##            line = self.GetCurrentLineText()[0]
##            piv = pos - lnStPs
##            start, length = idWord(line, piv, lnStPs)
##            startLine = start-lnStPs
##            word = line[startLine:startLine+length]
##            print word, line[piv-1]
##            cls = self.model.getModule().getClassForLineNo(lnNo)
##            
##            self.CallTipSetHighlight(0, len(sigLst[1])

    def checkCallTip(self):
        print 'checkCallTip'
        pos = self.GetCurrentPos()
        lnNo = self.GetCurrentLine()
        lnStPs = self.GetLineStartPos(lnNo)
        line = self.GetCurrentLineText()[0]
        piv = pos - lnStPs
        start, length = idWord(line, piv, lnStPs)
        startLine = start-lnStPs
        word = line[startLine:startLine+length]
        print word, line[piv-1]
        module = self.model.getModule()
        cls = module.getClassForLineNo(lnNo)
        if cls and line[piv-1] == '(':
            print 'got ('
            dot = string.rfind(line, '.', 0, piv)
            if dot != -1 and line[dot-4:dot] == 'self':
                meth = line[dot+1:piv-1]
                print 'self', meth
                if cls.methods.has_key(meth):
##                    print 'has meth', `cls.methods[meth].signature`
                    sigLst = methodparse.safesplitfields(cls.methods[meth].signature, ',')
##                    print sigLst
                    if len(sigLst) > 1:
                        self.CallTipShow(pos, string.join(sigLst[1:], ', '))
                        self.currParamList = sigLst[1:]
                        self.checkCallTipHighlight()

    def checkCodeComp(self):
        pos = self.GetCurrentPos()
        lnNo = self.GetCurrentLine()
        lnStPs = self.GetLineStartPos(lnNo)
        line = self.GetCurrentLineText()[0]
        piv = pos - lnStPs
        start, length = idWord(line, piv, lnStPs)
        startLine = start-lnStPs
        word = line[startLine:startLine+length]
##        print word
        module = self.model.getModule()
        cls = module.getClassForLineNo(lnNo)
        if not cls: return
        dot = string.rfind(line, '.', 0, piv)
        if dot != -1:
            if line[dot-4:dot] == 'self':
                partial = line[dot+1:piv]
##                print partial
                list, sel = self.getAttribs(cls, partial)

                if old_stc:
                    self.AutoCompShow(string.join(list, ' '))
                else:
                    self.AutoCompShow(len(partial), string.join(list, ' '))
                if sel:
                    if new_stc:
                        print 'auto selecting', partial, sel
                        self.AutoCompSelect(partial)
        else:
            blnk = string.rfind(line, ' ', 0, piv)
            partial = line[blnk+1:piv]
            list = wxNamespace.getWxNameSpace()
            if old_stc:
                self.AutoCompShow(string.join(list, ' '))
            else:
                self.AutoCompShow(len(partial), string.join(list, ' '))
                self.AutoCompSelect(partial)

#-------Browsing--------------------------------------------------------
    def StyleVeto(self, style):
##        print 'STC: StyleVeto'
        return style != 11

    def BrowseClick(self, word, line, lineNo, start, style):
        """ Overridden from BrowseStyledTextCtrlMix, jumps to declaration or
            opens module
            
            Currently only the open module is inspected, classes declared 
            outside the scope of the active module are inaccessible.
        """
        module = self.model.getModule()
        if line[start-5: start] == 'self.':
            cls = module.getClassForLineNo(lineNo)
            if cls:
                self.doClearBrwsLn()
                if cls.attributes.has_key(word):
                    self.GotoLine(cls.attributes[word][0].start-1)
                elif cls.methods.has_key(word):
                    self.GotoLine(cls.methods[word].start-1)
                else:
                    found, cls, block = module.find_declarer(cls, word, None)
                    if found:
                        if type(block) == type([]):
                            self.GotoLine(block[0].start-1)
                        else:
                            self.GotoLine(block.start-1)
                return true
        # Imports
        elif module.imports.has_key(word):
            # XXX Should rather examine path to find module instead
            # XXX of implicit path
            self.doClearBrwsLn()
            self.model.editor.openOrGotoModule(word+'.py')
            return true
        # Classes
        elif module.classes.has_key(word):
            self.doClearBrwsLn()
            self.GotoLine(module.classes[word].block.start-1)
            return true
        # Global functions
        elif module.functions.has_key(word):
            self.doClearBrwsLn()
            self.GotoLine(module.functions[word].start-1)
            return true
        # Global namespace including wxPython declarations
        elif globals().has_key(word):
            self.doClearBrwsLn()
            obj = globals()[word]
            editor = self.model.editor
            if hasattr(obj, '__init__'):
                mod = editor.openOrGotoModule(
                    obj.__init__.im_func.func_code.co_filename)
                mod.views['Source'].GotoLine(
                    obj.__init__.im_func.func_code.co_firstlineno -1)
            elif hasattr(obj, 'func_code'):
                mod = editor.openOrGotoModule(obj.func_code.co_filename)
                mod.views['Source'].GotoLine(obj.func_code.co_firstlineno -1)
#            print dir(obj)
#            self.GotoLine(globals()[word].block.start-1)
            return true
            
                        
#-------Debugger--------------------------------------------------------
    def setInitialBreakpoints(self):
        # Adds markers where the breakpoints are located.
        for brk in self.breaks.listBreakpoints():
            if brk['temporary']: mrk = tmpBrkPtMrk
            else: mrk = brkPtMrk
            self.MarkerAdd(bp['lineno'] - 1, mrk)

    #def setBdbBreakpoints(self):
    #    for bp in self.breaks.values():
    #        self.MarkerAdd(bp.line -1, brkPtMrk)

    def deleteBreakPoint(self, lineNo):
        self.breaks.deleteBreakpoints(lineNo)
        debugger = self.model.editor.debugger
        if debugger:
            # Try to apply to the running debugger.
            filename = self.model.filename #string.lower(self.model.filename)
            debugger.deleteBreakpoints(filename, lineNo)
        self.MarkerDelete(lineNo - 1, brkPtMrk)
        self.MarkerDelete(lineNo - 1, tmpBrkPtMrk)

#        ln = self.MarkerLineFromHandle(self.breaks[lineClicked])
        #if self.breaks.has_key(lineNo):
        #    bp = self.breaks[lineNo]
        #    if bp.temporary:
        #        self.MarkerDelete(lineNo - 1, tmpBrkPtMrk)
        #    else:
        #        self.MarkerDelete(lineNo - 1, brkPtMrk)

        #debugger = self.model.editor.debugger
        #if debugger:
        #    if self.breaks.has_key(lineNo):
        #        bp = self.breaks[lineNo]
        #        debugger.clear_break(bp.file, bp.line)
        #        debugger.breakpts.refreshList()
        #else:
        #    self.breaks[lineNo].deleteMe()
        
        #del self.breaks[lineNo]
    
    def addBreakPoint(self, lineNo, temp = 0):
        self.breaks.setBreakpoint(lineNo, temp)
        debugger = self.model.editor.debugger
        if debugger:
            # Try to apply to the running debugger.
            filename = self.model.filename #string.lower(self.model.filename)
            debugger.setBreakpoint(filename, lineNo, temp)
        if temp: mrk = tmpBrkPtMrk
        else: mrk = brkPtMrk
        self.MarkerAdd(lineNo - 1, mrk)

        #filename = string.lower(self.model.filename)
        #debugger = self.model.editor.debugger
        #if debugger:
        #    self.breaks[lineNo] = debugger.set_breakpoint_here(
        #        filename, lineNo, temp)
        #else:
        #    self.breaks[lineNo] = bdb.Breakpoint(filename, lineNo, temp)

    def tryLoadBreakpoints(self):
        fn = self.getBreakpointFilename()
        rval = self.breaks.loadBreakpoints(fn)
        if rval:
            self.setInitialBreakpoints()
        return rval

        #if os.path.exists(fn):
        #    self.breaks = pickle.load(open(fn))
        #    self.setInitialBreakpoints()
        #    BrkPt = bdb.Breakpoint
        #    for lineNo, brk in self.breaks.items():
        #        BrkPt.bpbynumber.append(brk)
        #        if BrkPt.bplist.has_key((brk.file, brk.line)):
        #            BrkPt.bplist[brk.file, brk.line].append(brk)
        #        else:
        #            BrkPt.bplist[brk.file, brk.line] = [brk]
        #    return true
        #else:
        #    self.breaks = {}
        #    return false

    def saveBreakpoints(self):
        # XXX This is not yet called automatically on saving a module,
        # should it be ?
        fn = self.getBreakpointFilename()
        self.breaks.saveBreakpoints(fn)
        
        #import pickle
        #if len(self.breaks):
        #    pickle.dump(self.breaks, open(fn, 'w'))
        #elif os.path.exists(fn):
        #    os.remove(fn)
        
    def clearStepPos(self, lineNo):
        if lineNo < 0:
            lineNo = 0
        self.MarkerDelete(lineNo, stepPosMrk)

    def setStepPos(self, lineNo):
        if lineNo < 0:
            lineNo = 0
        self.MarkerAdd(lineNo, stepPosMrk)
            
            
#-------Events------------------------------------------------------------------
    def OnMarginClick(self, event):
        if event.GetMargin() == 1:
            lineClicked = self.GetLineFromPos(event.GetPosition()) + 1
            if self.breaks.hasBreakpoint(lineClicked):
                self.deleteBreakPoint(lineClicked)
            else:
                self.addBreakPoint(lineClicked)
        else: 
            FoldingStyledTextCtrlMix.OnMarginClick(self, event)
            
    def OnSetBreakPoint(self, event):
        line = self.GetLineFromPos(self.GetCurrentPos()) + 1
        if self.breaks.hasBreakpoint(line):
            self.deleteBreakPoint(line)
        else:
            self.addBreakPoint(line)

    def OnRunToCursor(self, event):
        line = self.GetLineFromPos(self.GetCurrentPos()) + 1
        if not self.breaks.hasBreakpoint(line):
            self.addBreakPoint(line, 1)
        self.OnDebug(event, autocont=1)
#        else return  
        # XXX Case where module is run, outside app

    def OnRun(self, event):
        if not self.model.savedAs: #modified or len(self.model.viewsModified):
            wxMessageBox('Cannot run an unsaved module.')
            return
        self.model.run()

    def OnRunParams(self, event):
        if not self.model.savedAs: #modified or len(self.model.viewsModified):
            wxMessageBox('Cannot run an unsaved module.')
            return
        dlg = wxTextEntryDialog(self.model.editor, 'Parameters:', 
          'Run with parameters', self.lastRunParams)
        try:
            if dlg.ShowModal() == wxID_OK:
                self.lastRunParams = dlg.GetValue()
                self.model.run(self.lastRunParams)
        finally:
            dlg.Destroy()

    def OnRunApp(self, event):
        if not self.model.app.savedAs: #modified or len(self.model.viewsModified):
            wxMessageBox('Cannot run an unsaved application.')
            return
        wxBeginBusyCursor()
        try:
            self.model.app.run()
        finally:
            wxEndBusyCursor()

    def OnDebug(self, event, autocont=0):
        if not self.model.savedAs or self.model.modified or \
          len(self.model.viewsModified):
            wxMessageBox('Cannot debug an unsaved or modified module.')
            return
        was_running = self.model.debug()
        if autocont or was_running:
            debugger = self.model.editor.debugger
            debugger.setContinue()

    def OnDebugParams(self, event):
        if not self.model.savedAs or self.model.modified or \
          len(self.model.viewsModified):
            wxMessageBox('Cannot debug an unsaved or modified module.')
            return
        dlg = wxTextEntryDialog(self.model.editor, 'Parameters:', 
          'Debug with parameters', self.lastDebugParams)
        try:
            if dlg.ShowModal() == wxID_OK:
                self.lastDebugParams = dlg.GetValue()
                self.model.debug(methodparse.safesplitfields(
                    self.lastDebugParams, ' '))
        finally:
            dlg.Destroy()

    def OnCompile(self, event):
        if not self.model.savedAs or self.model.modified or \
          len(self.model.viewsModified):
            wxMessageBox('Cannot compile an unsaved or modified module.')
            return
        self.model.compile()

    def OnProfile(self, event):
        stats = self.model.profile()
        resName = 'Profile stats'
        if not self.model.views.has_key(resName):
            resultView = self.model.editor.addNewView(resName, 
              ProfileView.ProfileStatsView)
        else:
            resultView = self.model.views[resName]
        resultView.tabName = resName
        resultView.stats = stats
        resultView.refresh()
        resultView.focus()

    def OnContextHelp(self, event):
        pos = self.GetCurrentPos()
        lnNo = self.GetCurrentLine()
        lnStPs = self.GetLineStartPos(lnNo)
        line = self.GetCurrentLineText()[0]
        piv = pos - lnStPs
        start, length = idWord(line, piv, lnStPs)
        startLine = start-lnStPs
        word = line[startLine:startLine+length]
        Help.showContextHelp(self.model.editor, self.model.editor.palette.toolBar, word)

    def OnComment(self, event):
        self.processSelectionBlock(self.processComment)
                
    def OnUnComment(self, event):
        self.processSelectionBlock(self.processUncomment)
    
    def OnIndent(self, event):
        self.processSelectionBlock(self.processIndent)
                
    def OnDedent(self, event):
        self.processSelectionBlock(self.processDedent)

    def OnAddSimpleApp(self, event):
        self.BeginUndoAction()
        try: self.InsertText(self.GetTextLength(), simpleAppText)
        finally: self.EndUndoAction()
        
    def OnStyle(self, event):
        pass

    def OnAddModuleInfo(self, event):
        self.refreshModel() 
        prefs = Preferences.staticInfoPrefs.copy() 
        self.model.addModuleInfo(prefs)
        self.updateEditor()

    def OnUpdateUI(self, event):
##        print 'STC: OnUpdateUI'
        # don't update if not fully initialised
        if hasattr(self, 'pageIdx'):
            self.updateViewState()
        
        if Preferences.braceHighLight:
            PythonStyledTextCtrlMix.OnUpdateUI(self, event)

    def OnAddChar(self, event):
##        print 'STC: OnAddChar'
        char = event.GetKey()
        # On enter indent to same indentation as line above
        # If ends in : indent xtra block
        if char == 10:
            lineNo = self.GetCurrentLine()
            pos = self.GetCurrentPos()
            prevline = self.GetLine(lineNo -1)[:-1*len(self.eol)]
            i = 0
            if string.strip(prevline):
                while prevline[i] in (' ', '\t'): i = i + 1
                indent = prevline[:i]
            else:
                indent = prevline
            if string.rstrip(prevline)[-1:] == ':':
                indent = indent + (indentLevel*' ')
            self.BeginUndoAction()
            try:
                self.InsertText(pos, indent)
                self.GotoPos(pos + len(indent))
            finally:
                self.EndUndoAction()

    def OnKeyDown(self, event):
##        print 'STC: OnKeyDown'
        key = event.KeyCode()
##        if self.CallTipActive():
##            print 'tip active'
##            event.Skip()
##            return
        if key == 32 and event.ControlDown():
            # Tips
            if event.ShiftDown():
                self.checkCallTip()
            # Code completion
            else:
                self.checkCodeComp()
        # Tabbed indent
        elif key == 9:
            pos = self.GetCurrentPos()
            self.InsertText(pos, indentLevel*' ')
            if old_stc:
                self.SetCurrentPosition(pos + indentLevel)
            else:
                self.SetSelectionStart(pos + indentLevel)
            if not self.AutoCompActive(): return
        # Smart delete
        elif key == 8:
            line = self.GetCurrentLineText()
            if len(line): line = line[0]
            else: line = ''
            pos = self.GetCurrentPos()
            #ignore indenting when at start of line
            if self.GetLineStartPos(self.GetLineFromPos(pos)) != pos:
                pos = pos -1
                ln = self.GetLineFromPos(pos)
                ls = self.GetLineStartPos(ln)
                st = pos - ls
                if not string.strip(line[:st]):
                    self.SetSelection(ls + st/4*4, pos+1)
                    self.ReplaceSelection('')
                    return
        event.Skip()            
        BrowseStyledTextCtrlMix.OnKeyDown(self, event)

#---Meta comment----------------------------------------------------------------
    def OnAddCommentLine(self, event):
        pos = self.GetCurrentPos()
        ln = self.GetLineFromPos(pos)
        ls = self.GetLineStartPos(ln)
        self.InsertText(ls, '#-------------------------------------------'
                                    '------------------------------------'+'\n')
        self.SetCurrentPosition(ls+4)
    
    def OnViewWhitespace(self, event):
        miid = self.menu.FindItem('View whitespace')
        if self.menu.IsChecked(miid):
            mode = wxSTC_WS_INVISIBLE
            self.menu.Check(miid, false)
        else:
            mode = wxSTC_WS_VISIBLEALWAYS
            self.menu.Check(miid, true)
        
        self.SetViewWhiteSpace(mode)
#        self.menu.Check(miid, not self.menu.IsChecked(miid))

    def OnViewEOL(self, event):
        miid = self.menu.FindItem('View EOL characters')
        check = not self.menu.IsChecked(miid)
        self.menu.Check(miid, check)
        self.SetViewEOL(check)
        
    def underlineWord(self, start, length):
        start, length = BrowseStyledTextCtrlMix.underlineWord(self, start, length)
        if self.model.editor.debugger:
            word, line, lnNo, wordStart = self.getStyledWordElems(start, length)
            self.IndicatorSetColour(0, wxRED)
            try:
                val = self.model.editor.debugger.getVarValue(word)
            except Exception, message:
                val = str(message)
            if val:
                self.model.editor.statusBar.setHint(val)
        else:
            self.IndicatorSetColour(0, wxBLUE)
                
        return start, length
    
    def getBreakpointFilename(self):
        return os.path.splitext(self.model.filename)[0]+'.brk'

    def OnSaveBreakPoints(self, event):
        self.saveBreakpoints()
        
    def OnLoadBreakPoints(self, event):
        self.tryLoadBreakpoints()
        
class HTMLSourceView(EditorStyledTextCtrl, HTMLStyledTextCtrlMix):
    viewName = 'HTML'
    def __init__(self, parent, model):
        EditorStyledTextCtrl.__init__(self, parent, wxID_HTMLSOURCEVIEW, 
          model, (('Refresh', self.OnRefresh, '-', keyDefs['Refresh']),), -1)
        HTMLStyledTextCtrlMix.__init__(self, wxID_HTMLSOURCEVIEW)
        self.active = true

    def OnUpdateUI(self, event):
        # don't update if not fully initialised
        if hasattr(self, 'pageIdx'):
            self.updateViewState()

        if Preferences.braceHighLight:
            HTMLStyledTextCtrlMix.OnUpdateUI(self, event)

class CPPSourceView(EditorStyledTextCtrl, CPPStyledTextCtrlMix):
    viewName = 'Source'
    def __init__(self, parent, model):
        EditorStyledTextCtrl.__init__(self, parent, wxID_CPPSOURCEVIEW, 
          model, (('Refresh', self.OnRefresh, '-', keyDefs['Refresh']),), -1)
        CPPStyledTextCtrlMix.__init__(self, wxID_CPPSOURCEVIEW)
        self.active = true

    def OnUpdateUI(self, event):
        # don't update if not fully initialised
        if hasattr(self, 'pageIdx'):
            self.updateViewState()
##        CPPStyledTextCtrlMix.OnUpdateUI(self, event)

class HPPSourceView(CPPSourceView):
    viewName = 'Header'
    def __init__(self, parent, model):
        CPPSourceView.__init__(self, parent, model)

    def refreshCtrl(self):
        self.pos = self.GetCurrentPos() 
#        line = self.GetCurrentLine()
        prevVsblLn = self.GetFirstVisibleLine()
        
        self.SetText(self.model.headerData)
        self.EmptyUndoBuffer()
        self.GotoPos(self.pos)
        curVsblLn = self.GetFirstVisibleLine()
        self.ScrollBy(0, prevVsblLn - curVsblLn)
        
        self.nonUserModification = false 
        self.updatePageName()
        

class TextView(EditorStyledTextCtrl):
    viewName = 'Text'
    def __init__(self, parent, model):
        EditorStyledTextCtrl.__init__(self, parent, wxID_TEXTVIEW, 
          model, (), 0)
        self.active = true
        EVT_STC_UPDATEUI(self, wxID_TEXTVIEW, self.OnUpdateUI)
    
    def OnUpdateUI(self, event):
        # don't update if not fully initialised
        if hasattr(self, 'pageIdx'):
            self.updateViewState()
        
class TstPythonSourceView(EditorStyledTextCtrl, PythonStyledTextCtrlMix, BrowseStyledTextCtrlMix):
    viewName = 'Source'
    def __init__(self, parent, model):
        EditorStyledTextCtrl.__init__(self, parent, wxID_PYTHONSOURCEVIEW, 
          model, (), 0)
        PythonStyledTextCtrlMix.__init__(self)
        BrowseStyledTextCtrlMix.__init__(self)
        self.active = true
        EVT_STC_UPDATEUI(self, wxID_PYTHONSOURCEVIEW, self.OnUpdateUI)
        EVT_STC_CHARADDED(self, wxID_PYTHONSOURCEVIEW, self.OnAddChar)

    def OnUpdateUI(self, event):
        # don't update if not fully initialised
        if hasattr(self, 'pageIdx'):
            self.updateViewState()

    def setStepPos(self, lineNo):
        pass
        
    def OnAddChar(self, event):
        char = event.GetKey()
        lineNo = self.GetCurrentLine()
        pos = self.GetCurrentPos()
        # On enter indent to same indentation as line above
        # If ends in : indent xtra block
        if char == 10:
            prevline = self.GetLine(lineNo -1)[:-1*len(self.eol)]
            i = 0
            if string.strip(prevline):
                while prevline[i] in (' ', '\t'): i = i + 1
                indent = prevline[:i]
            else:
                indent = prevline
            if string.rstrip(prevline)[-1:] == ':':
                indent = indent + (indentLevel*' ')
            self.BeginUndoAction()
            try:
                self.InsertText(pos, indent)
                self.GotoPos(pos + len(indent))
            finally:
                self.EndUndoAction()

    def OnKeyDown(self, event):
        key = event.KeyCode()
        if key == 32 and event.ControlDown():
            pos = self.GetCurrentPos()
            # Tips
            if event.ShiftDown():
                self.CallTipShow(pos, 'param1, param2')
            # Code completion
            else:
                module = self.model.getModule()
                self.AutoCompShow(string.join(module.classes.keys(),
                  ' '))
        elif key == 9:
            pos = self.GetCurrentPos()
            self.InsertText(pos, indentLevel*' ')
            self.SetCurrentPosition(pos + indentLevel)
            return
        elif key == 8:
            line = self.GetCurrentLineText()
            if len(line): line = line[0]
            else: line = ''
            pos = self.GetCurrentPos()
            #ignore indenting when at start of line
            if self.GetLineStartPos(self.GetLineFromPos(pos)) != pos:
                pos = pos -1
                ln = self.GetLineFromPos(pos)
                ls = self.GetLineStartPos(ln)
                st = pos - ls
                if not string.strip(line[:st]):
                    self.SetSelection(ls + st/4*4, pos+1)
                    self.ReplaceSelection('')
                    return
        event.Skip()            
        BrowseStyledTextCtrlMix.OnKeyDown(self, event)
