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
import os, string, time, dis, bdb
import EditorViews, ProfileView, Search, Help, Preferences, ShellEditor
from StyledTextCtrls import PythonStyledTextCtrlMix, BrowseStyledTextCtrlMix, HTMLStyledTextCtrlMix, FoldingStyledTextCtrlMix, CPPStyledTextCtrlMix, idWord, new_stc, old_stc, object_delim
from PrefsKeys import keyDefs
import methodparse
import wxNamespace
import Utils

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
markPlaceMrk = 4
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
              ('Find again', self.OnFindAgain, self.findAgainBmp, keyDefs['FindAgain']),
              ('Mark place', self.OnMarkPlace, '-', keyDefs['MarkPlace']))

        EditorViews.EditorView.__init__(self, model, a + actions, defaultAction)

        self.SetEOLMode(wxSTC_EOL_LF)
        self.eol = endOfLines[self.GetEOLMode()]

        #self.SetCaretPeriod(0)

        self.pos = 0
        self.stepPos = 0
        self.nonUserModification  = false 

        self.lastSearchResults = []
        self.lastSearchPattern = ''
        self.lastMatchPosition = None

        ## Install the handler for refreshs.
        if wxPlatform == '__WXGTK__':
            self.paint_handler = Utils.PaintEventHandler(self)

        self.lastStart = 0

        self.MarkerDefine(markPlaceMrk, wxSTC_MARK_SHORTARROW, 'NAVY', 'YELLOW')


    def setReadOnly(self, val):
        EditorViews.EditorView.readOnly(self, val)
        self.SetEditable(val)

    def getModelData(self):
        return self.model.data
    
    def setModelData(self, data):
        self.model.data = data

    def refreshCtrl(self):
        if wxPlatform == '__WXGTK__':
            self.NoUpdateUI = 1  ## disable event handler
        self.pos = self.GetCurrentPos() 
#        line = self.GetCurrentLine()
        
        ## This code prevents circular updates on GTK
        ## It is not important under windows as the windows refresh
        ## code is more efficient.
        try:
            if self.noredraw == 1: redraw = 0
            else: redraw = 1
        except:
            redraw=1
        if redraw == 1:
            prevVsblLn = self.GetFirstVisibleLine()
            self.SetText(self.getModelData())
            self.EmptyUndoBuffer()
            self.GotoPos(self.pos)
            curVsblLn = self.GetFirstVisibleLine()
            self.ScrollBy(0, prevVsblLn - curVsblLn)
        
        self.nonUserModification = false 
        self.updatePageName()
        self.NoUpdateUI = 0  ## Enable event handler

    def refreshModel(self):
        if self.isModified():
            self.model.modified = true
        self.nonUserModification = false 
        
        # hack to stop wxSTC from eating the last character
        self.InsertText(self.GetTextLength(), ' ')
        
        self.setModelData(self.GetText())
        self.EmptyUndoBuffer()
        if wxPlatform == '__WXGTK__':
            # We are updating the model from the editor view.
            # this flag is to prevent  the model updating the view 
            self.noredraw = 1
        EditorViews.EditorView.refreshModel(self) 
        self.noredraw = 0
        
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
        sp = self.GetLineStartPos(lineno)
        ep = self.GetLineStartPos(lineno+1)-1
        self.SetSelection(sp, ep)

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
        self.refreshModel()

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
        
    def doFind(self, pattern):
        self.lastSearchResults = Search.findInText(\
          string.split(self.GetText(), self.eol), pattern, false)
        self.lastSearchPattern = pattern
        if len(self.lastSearchResults):
            self.lastMatchPosition = 0
    
    def doNextMatch(self):
        if self.lastMatchPosition is not None and \
          len(self.lastSearchResults) > self.lastMatchPosition:
            pos = self.lastSearchResults[self.lastMatchPosition]
            self.model.editor.addBrowseMarker(self.GetCurrentLine())
            self.selectSection(pos[0], pos[1], self.lastSearchPattern)
            self.lastMatchPosition = self.lastMatchPosition + 1
        else:
            dlg = wxMessageDialog(self.model.editor, 
                  'No%smatches'% (self.lastMatchPosition is not None and ' further ' or ' '),
                  'Find in module', wxOK | wxICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.lastMatchPosition = None
                       
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
                self.doFind(dlg.GetValue())
            else:
                return
        finally:
            dlg.Destroy()
        
        self.doNextMatch()

    def OnFindAgain(self, event):
        if self.lastMatchPosition is None:
            self.OnFind(event)
        else: 
            self.doNextMatch()
    
    def OnMarkPlace(self, event):
        lineno = self.GetLineFromPos(self.GetCurrentPos())
        self.MarkerAdd(lineno, markPlaceMrk)
        self.model.editor.addBrowseMarker(lineno)
        wxYield()
        self.MarkerDelete(lineno, markPlaceMrk)


class PythonSourceView(EditorStyledTextCtrl, PythonStyledTextCtrlMix, BrowseStyledTextCtrlMix, FoldingStyledTextCtrlMix):
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
            a2 = (('Run application', self.OnRunApp, self.runAppBmp, keyDefs['RunApp']),)
        else:
            a2 = ()
        a1 = (('-', None, '', ()),
              ('Comment', self.OnComment, '-', keyDefs['Comment']),
              ('Uncomment', self.OnUnComment, '-', keyDefs['Uncomment']),
              ('Indent', self.OnIndent, '-', keyDefs['Indent']),
              ('Dedent', self.OnDedent, '-', keyDefs['Dedent']),
              ('-', None, '-', ()),
              ('Profile', self.OnProfile, self.profileBmp, ()),
              ('Check source', self.OnCompile, self.compileBmp, keyDefs['CheckSource']))
        a3 = (('Run module', self.OnRun, self.runBmp, keyDefs['RunMod']),
              ('Run module with parameters', self.OnRunParams, '-', ()),
              ('Debug', self.OnDebug, self.debugBmp, keyDefs['Debug']),
              ('Debug with parameters', self.OnDebugParams, '-', ()),
              ('Step in', self.OnDebugStepIn, '-', keyDefs['DebugStep']),
              ('Step over', self.OnDebugStepOver, '-', keyDefs['DebugOver']),
              ('Step out', self.OnDebugStepOut, '-', keyDefs['DebugOut']),
              ('-', None, '', ()),
              ('Run to cursor', self.OnRunToCursor, self.runCrsBmp, ()),
              ('Toggle breakpoint', self.OnSetBreakPoint, self.breakBmp, keyDefs['ToggleBrk']),
              ('Load breakpoints', self.OnLoadBreakPoints, '-', ()),
              ('Save breakpoints', self.OnSaveBreakPoints, '-', ()),
              ('-', None, '', ()),
              ('+View whitespace', self.OnViewWhitespace, '-', ()),
              ('+View EOL characters', self.OnViewEOL, '-', ()),
              ('-', None, '-', ()),
              ('Add module info', self.OnAddModuleInfo, self.modInfoBmp, ()),
              ('Add comment line', self.OnAddCommentLine, '-', keyDefs['DashLine']),
              ('Add simple app', self.OnAddSimpleApp, '-', ()),
              ('-', None, '-', ()),
              ('Context help', self.OnContextHelp, '-', keyDefs['ContextHelp']))
            
        
        wxID_PYTHONSOURCEVIEW = wxNewId()
        
        EditorStyledTextCtrl.__init__(self, parent, wxID_PYTHONSOURCEVIEW, 
          model, a1 + a2 + a3, -1)
        PythonStyledTextCtrlMix.__init__(self, wxID_PYTHONSOURCEVIEW, 0)
        BrowseStyledTextCtrlMix.__init__(self)
        FoldingStyledTextCtrlMix.__init__(self, wxID_PYTHONSOURCEVIEW, 2)
        
        # Initialise breakpts from file and bdb.Breakpoint
        self.tryLoadBreakpoints()
        filename = string.lower(self.model.filename)
        for file, lineno in bdb.Breakpoint.bplist.keys():
            if file == filename:
                for bp in bdb.Breakpoint.bplist[(file, lineno)]:
                    self.breaks[lineno] = bp
        

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

    def getWxAttribs(self, cls, mems = None):
        if mems is None: mems = []

        for base in cls.__bases__:
            self.getWxAttribs(base, mems)

        mems.extend(dir(cls))
        return mems

    def getAttribs(self, cls):
        loopCls = cls
        lst = []
        while loopCls:
            lst.extend(loopCls.methods.keys() + loopCls.attributes.keys())
            if len(loopCls.super):
                prnt = loopCls.super[0]
                # Modules
                if type(prnt) == type(self): # :)
                    loopCls = prnt
                # Possible wxPython ancestor
                else:
                    klass = wxNamespace.getWxClass(prnt)
                    if klass:
                        lst.extend(self.getWxAttribs(klass))
                    loopCls = None
            else:
                loopCls = None

        return lst
            
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
        pos = self.GetCurrentPos()
        lnNo = self.GetCurrentLine()
        lnStPs = self.GetLineStartPos(lnNo)
        line = self.GetCurrentLineText()[0]
        piv = pos - lnStPs
        start, length = idWord(line, piv, lnStPs)
        startLine = start-lnStPs
        word = line[startLine:startLine+length]
        #print word, line[piv-1]
        module = self.model.getModule()
        cls = module.getClassForLineNo(lnNo)
        if cls and line[piv-1] == '(':
            dot = string.rfind(line, '.', 0, piv)
            if dot != -1 and line[dot-4:dot] == 'self':
                meth = line[dot+1:piv-1]
                print 'self', meth
                if cls.methods.has_key(meth):
                    sigLst = methodparse.safesplitfields(cls.methods[meth].signature, ',')
                    if len(sigLst) > 1:
                        self.CallTipShow(pos, string.join(sigLst[1:], ', '))
                        self.currParamList = sigLst[1:]
                        self.checkCallTipHighlight()

    typeMap = {'dict': dir({}), 'list': dir([]), 'string': dir(''), 
               'tuple': dir(()), 'number': dir(0)}

    def checkCodeComp(self):
        pos = self.GetCurrentPos()
        lnNo = self.GetCurrentLine()
        lnStPs = self.GetLineStartPos(lnNo)
        line = self.GetCurrentLineText()[0]
        piv = pos - lnStPs
        start, length = idWord(line, piv, lnStPs)
        startLine = start-lnStPs
        word = line[startLine:startLine+length]
        module = self.model.getModule()
        cls = module.getClassForLineNo(lnNo)
        if not cls: return
        dot = string.rfind(line, '.', 0, piv)
        if dot != -1:
            lst = []
            if line[dot-4:dot] == 'self':
                partial = line[dot+1:piv]
                lst = self.getAttribs(cls)
            else:
                # check if previous attr isn't self
                prevdot = string.rfind(line, '.', 0, dot)
                if prevdot != -1 and line[prevdot-4:prevdot] == 'self':
                    partial = line[dot+1:piv]
                    attrib = line[prevdot+1:dot]
                    # Only handling current classes attrs
                    if cls.attributes.has_key(attrib):
                        objtype = cls.attributes[attrib][0].signature
                        if self.typeMap.has_key(objtype):
                            lst = self.typeMap[objtype]
                        elif module.classes.has_key(objtype):
                            lst = self.getAttribs(module.classes[objtype])
                        else:
                            klass = wxNamespace.getWxClass(objtype)
                            if klass:
                                lst = self.getWxAttribs(klass)
            if lst:
                uniqueDct = {}
                for attr in lst:
                    uniqueDct[attr] = None
                lst = uniqueDct.keys()
                if old_stc:
                    self.AutoCompShow(string.join(lst, ' '))
                else:
                    self.AutoCompShow(len(partial), string.join(lst, ' '))
                if partial and new_stc:
                        self.AutoCompSelect(partial)
                            
        else:
            blnk = string.rfind(line, ' ', 0, piv)
            partial = line[blnk+1:piv]
            list = wxNamespace.getWxNameSpace()
            if old_stc:
                self.AutoCompShow(string.join(list, ' '))
            else:
                self.AutoCompShow(len(partial), string.join(list, ' '))
                if partial and new_stc:
                    self.AutoCompSelect(partial)

#-------Browsing----------------------------------------------------------------
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

        if self.model.editor.debugger and self.model.editor.debugger.isDebugBrowsing():
            self.model.editor.debugger.add_watch(word, true)
        elif line[start-5: start] == 'self.':
            cls = module.getClassForLineNo(lineNo)
            if cls:
                self.doClearBrwsLn()
                gotoLine = -1
                if cls.attributes.has_key(word):
                    gotoLine = cls.attributes[word][0].start-1
                elif cls.methods.has_key(word):
                    gotoLine = cls.methods[word].start-1
                else:
                    found, cls, block = module.find_declarer(cls, word, None)
                    if found:
                        if type(block) == type([]):
                            gotoLine = block[0].start-1
                        else:
                            gotoLine = block.start-1
                if gotoLine != -1:
                    self.model.editor.addBrowseMarker(lineNo)#self.GetCurrentLine())
                    self.GotoLine(gotoLine)
                return true
        # Imports
        elif module.imports.has_key(word):
            # XXX Should rather examine path to find module instead of implicit 
            # XXX path
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
            if hasattr(obj, '__init__'):
                mod = self.model.editor.openOrGotoModule(obj.__init__.im_func.func_code.co_filename)
                mod.views['Source'].GotoLine(obj.__init__.im_func.func_code.co_firstlineno -1)
            elif hasattr(obj, 'func_code'):
                mod = self.model.editor.openOrGotoModule(obj.func_code.co_filename)
                mod.views['Source'].GotoLine(obj.func_code.co_firstlineno -1)
#            print dir(obj)
#            self.GotoLine(globals()[word].block.start-1)
            return true

    def goto(self, gotoLine):
        self.GotoLine(gotoLine)

    def underlineWord(self, start, length):
        start, length = BrowseStyledTextCtrlMix.underlineWord(self, start, length)
        if self.model.editor.debugger and self.model.editor.debugger.isDebugBrowsing():
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

    def getBrowsableText(self, line, piv, lnStPs):
        if self.model.editor.debugger and self.model.editor.debugger.isDebugBrowsing():
            return idWord(line, piv, lnStPs, object_delim)
        else:
            return BrowseStyledTextCtrlMix.getBrowsableText(self, line, piv, lnStPs)
                        
#-------Debugger----------------------------------------------------------------
    def setInitialBreakpoints(self):
        for bp in self.breaks.values():
            self.MarkerAdd(bp.line -1, brkPtMrk)

    def setBdbBreakpoints(self):
        for bp in self.breaks.values():
            self.MarkerAdd(bp.line -1, brkPtMrk)

    def deleteBreakPoint(self, lineNo):
        if not self.breaks.has_key(lineNo):
            return
        
        bp = self.breaks[lineNo]
        if bp.temporary:
            self.MarkerDelete(lineNo - 1, tmpBrkPtMrk)
        else:
            self.MarkerDelete(lineNo - 1, brkPtMrk)

        if self.model.editor.debugger:
            bp = self.breaks[lineNo]
            res = self.model.editor.debugger.clear_break(bp.file, bp.line)
            if res: print res 
            self.model.editor.debugger.breakpts.refreshList()
        else:
            self.breaks[lineNo].deleteMe()
        
        del self.breaks[lineNo]        
    
    def addBreakPoint(self, lineNo, temp = 0):
        if temp:
            mrk = tmpBrkPtMrk
        else:
            mrk = brkPtMrk
        hnd = self.MarkerAdd(lineNo - 1, mrk)
        filename = string.lower(self.model.filename)

        if self.model.editor.debugger:
            self.breaks[lineNo] = self.model.editor.debugger.set_breakpoint_here(\
              filename, lineNo, temp)        
        else:
            self.breaks[lineNo] = \
              bdb.Breakpoint(filename, lineNo, temp)

    def tryLoadBreakpoints(self):    
        import pickle
        fn = self.getBreakpointFilename()
        update = false
        if os.path.exists(fn):
            self.breaks = pickle.load(open(fn))
            self.setInitialBreakpoints()
            BrkPt = bdb.Breakpoint
            for lineNo, brk in self.breaks.items():
                if self.model.editor.debugger:
                    self.model.editor.debugger.set_break(brk.file, lineNo)
                    update = true
                else:
                    BrkPt.bpbynumber.append(brk)
                    if BrkPt.bplist.has_key((brk.file, brk.line)):
                        BrkPt.bplist[brk.file, brk.line].append(brk)
                    else:
                        BrkPt.bplist[brk.file, brk.line] = [brk]
            if update:
                self.model.editor.debugger.breakpts.refreshList()
                
            return true
        else:
            self.breaks = {}
            return false

    def saveBreakpoints(self):
        # XXX This is not yet called automatically on saving a module, should it be ?
        import pickle
        fn = self.getBreakpointFilename()
        if len(self.breaks):
            pickle.dump(self.breaks, open(fn, 'w'))
        elif os.path.exists(fn):
            os.remove(fn)
        
    def setStepPos(self, lineNo):
        if self.stepPos != lineNo:
            if self.stepPos:
                self.MarkerDelete(self.stepPos, stepPosMrk)
            if lineNo:
                self.MarkerAdd(lineNo, stepPosMrk)
        self.stepPos = lineNo
            
    def getBreakpointFilename(self):
        return os.path.splitext(self.model.filename)[0]+'.brk'    

    def disableSource(self, doDisable):
        self.SetReadOnly(doDisable)
        self.grayout(doDisable)
        
#-------Events------------------------------------------------------------------
    def OnMarginClick(self, event):
        if event.GetMargin() == 1:
            lineClicked = self.GetLineFromPos(event.GetPosition()) + 1
            if self.breaks.has_key(lineClicked):
                self.deleteBreakPoint(lineClicked)
            else:
                self.addBreakPoint(lineClicked)
        else: 
            FoldingStyledTextCtrlMix.OnMarginClick(self, event)
            
    def OnSetBreakPoint(self, event):
        line = self.GetLineFromPos(self.GetCurrentPos()) + 1
        if self.breaks.has_key(line):
            self.deleteBreakPoint(line)
        else:
            self.addBreakPoint(line)

    def OnRunToCursor(self, event):
        line = self.GetLineFromPos(self.GetCurrentPos()) + 1
        if not self.breaks.has_key(line):
            self.addBreakPoint(line, 1)
        if self.model.defaultName == 'App':
            self.model.editor.debugger.debug_file(self.model.filename)
        elif self.model.app:
            self.model.editor.debugger.debug_file(self.model.app.filename)
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

    def OnDebug(self, event):
        if not self.model.savedAs or self.model.modified or \
          len(self.model.viewsModified):
            wxMessageBox('Cannot debug an unsaved or modified module.')
            return
        self.model.debug()

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
                self.model.debug(methodparse.safesplitfields(self.lastDebugParams, ' '))
        finally:
            dlg.Destroy()

    def OnDebugStepIn(self, event):
        if self.model.editor.debugger:
            self.model.editor.debugger.OnStep(event)
            
    def OnDebugStepOver(self, event):
        if self.model.editor.debugger:
            self.model.editor.debugger.OnOver(event)

    def OnDebugStepOut(self, event):
        if self.model.editor.debugger:
            self.model.editor.debugger.OnOut(event)

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
        ## This event handler may be disabled (execption handler allows
		## for the case where the flag is not defined.
        try:
            if self.NoUpdateUI == 1:
                return
        except:
            pass
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
                indent = prevline[:-1]
            if string.rstrip(prevline)[-1:] == ':':
                indent = indent + (indentLevel*' ')
            self.BeginUndoAction()
            try:
                self.InsertText(pos, indent)
                self.GotoPos(pos + len(indent))
            finally:
                self.EndUndoAction()

    keymap={81:chr(64),56:chr(91),57:chr(93),55:chr(123),48:chr(125),
            219:chr(92),337:chr(126),226:chr(124)}
    def OnKeyDown(self, event):
##        print 'STC: OnKeyDown'
        key = event.KeyCode()
##        if self.CallTipActive():
##            print 'tip active'
##            event.Skip()
##            return

        caretPos = self.GetCurrentPos()
        if Preferences.handleSpecialEuropeanKeys and event.AltDown() and \
              event.ControlDown():
            if self.keymap.has_key(key):
                self.InsertText(caretPos, self.keymap[key])
                self.SetCurrentPos(self.GetCurrentPos()+1)
                self.SetSelectionStart(self.GetCurrentPos())

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
        
    def OnSaveBreakPoints(self, event):
        self.saveBreakpoints()
        
    def OnLoadBreakPoints(self, event):
        self.tryLoadBreakpoints()

class PythonDisView(EditorStyledTextCtrl, PythonStyledTextCtrlMix):#, BrowseStyledTextCtrlMix, FoldingStyledTextCtrlMix):
    viewName = 'Disassemble'
    breakBmp = 'Images/Debug/Breakpoints.bmp'
    def __init__(self, parent, model):
        wxID_PYTHONDISVIEW = wxNewId()
        
        EditorStyledTextCtrl.__init__(self, parent, wxID_PYTHONDISVIEW, 
          model, (), -1)
        PythonStyledTextCtrlMix.__init__(self, wxID_PYTHONDISVIEW, -1)
        
##        self.SetMarginType(1, wxSTC_MARGIN_SYMBOL)
##        self.SetMarginWidth(1, 12)
##        self.SetMarginSensitive(1, true)
##        self.MarkerDefine(brkPtMrk, wxSTC_MARK_CIRCLE, 'BLACK', 'RED')
##        self.MarkerDefine(stepPosMrk, wxSTC_MARK_SHORTARROW, 'NAVY', 'BLUE')
##        self.MarkerDefine(tmpBrkPtMrk, wxSTC_MARK_CIRCLE, 'BLACK', 'BLUE')
#        self.setReadOnly(true)
        self.active = true

    def refreshModel(self):
        # Do not update model
        pass
        
    def getModelData(self):
        try:
            code = compile(self.model.data, self.model.filename, 'exec')
        except:
            oldOut = sys.stdout
            sys.stdout = ShellEditor.PseudoFileOutStore()
            try:
                print "''' Code does not compile\n\n    Disassembly of Traceback:\n'''"
                try:
                    dis.distb(sys.exc_info()[2])
                except:
                    print "''' Could not disassemble traceback '''\n"
                return sys.stdout.read()
            finally:
                sys.stdout = oldOut
            
        oldOut = sys.stdout
        sys.stdout = ShellEditor.PseudoFileOutStore()
        try:
            try:
                dis.disco(code)
            except:
                raise
            return sys.stdout.read()
        finally:
            sys.stdout = oldOut
        
        return 'Invisible code'
            
    def setModelData(self, data):
        pass

##    def refreshCtrl(self):
##                m = __import__(os.path.basename(os.path.splitext(pycFile)))
##                d = dis.dis(m)
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
