from wxPython.wx import *
##from wxPython.stc import *
##from FindReplDlgs import *

import Utils

##class StcFindDlg(FindDlg):
##    gPreviousSearch = ""
##    def __init__(self, parent, mySTC):
##        FindDlg.__init__(self, parent)
##        self.stc = mySTC
##        self.cboFind.SetValue(self.gPreviousSearch)        
##
##    def FindOptions(self):
##        options = []
##        if self.chkCase.GetValue():
##            options.append('MatchCase')
##        if self.chkWord.GetValue():
##            options.append('WholeWord')
##            
##        return {'SearchText': self.cboFind.GetValue(),
##                'Options': options}
##                
####        s = self.cboFind.GetValue()
####        if s > "":
####            i = self.stc.FindText(0,1000, s, 0,0)
####            if i > -1:
####                self.stc.SetSelectionStart(i)
####                self.stc.SetSelectionEnd(i+len(s))
####            self.gPreviousSearch = s

class Finder:
    def __init__(self):
        self.text = ''
        self.matchPos = -1
        self.matchCase = self.wholeWord = 0

    def Find(self, txt = ''):
        pass
    
    def FindNext(self):
        pass

    def FindPrev(self):
        pass

class FindReplacer(Finder):
    def Replace(self):
        pass

class STCFindReplacer(FindReplacer):
    def __init__(self, stc):
        FindReplacer.__init__(self)
        self.stc = stc

    def Find(self, txt = ''):
        dlg = wxTextEntryDialog(self.stc, 'Enter text:',
          'Find in module', txt)
        try:
            if wxPlatform == '__WXMSW__':
                te = Utils.getCtrlsFromDialog(dlg, 'wxTextCtrlPtr')[0]
                te.SetSelection(0, len(txt))
            if dlg.ShowModal() == wxID_OK:
                self.text = dlg.GetValue()
                self.matchPos = -1
                self.matchCase = false
                self.wholeWord = true
                return self.FindNext()
            else:
                return
        finally:
            dlg.Destroy()

##        dlg = StcFindDlg(self.stc, self.stc)
##        try:
##            if txt:
##                dlg.cboFind.SetValue(txt)
##            if dlg.ShowModal() == wxID_OK:
##                findOpts = dlg.FindOptions()
##                
##                self.text = findOpts['SearchText']
##                self.matchPos = -1
##                self.matchCase = 'MatchCase' in findOpts['Options']
##                self.wholeWord = 'WholeWord' in findOpts['Options']
##                
##                return self.FindNext()
##        finally:
##            dlg.Destroy()
    
    def FindNext(self):
        if self.matchPos != -1:
            start = self.matchPos
        else:
            start = 0
        pos = self.stc.FindText(self.matchPos+1, self.stc.GetTextLength(), 
              self.text, self.matchCase, self.wholeWord)
        if pos > -1 and pos < self.stc.GetTextLength():
            self.stc.SetSelectionStart(pos)
            self.stc.SetSelectionEnd(pos+len(self.text))
            self.stc.EnsureCaretVisible()

            self.matchPos = pos
            return 1
        else:
            if self.matchPos == -1:
                wxMessageBox('No match.', 'Find', wxICON_INFORMATION)
            else:
                self.matchPos = -1
                wxMessageBox('No further matches.', 'Find', wxICON_INFORMATION)
            return 0
    
    def FindPrev(self):
        pass

##class StcReplaceDlg(ReplaceDlg):
##    def __init__(self, parent, mySTC):
##        ReplaceDlg.__init__(self, parent)
##        
##    
##
###-----------------------Testing Framework ---------------------------------------------
##if __name__ == "__main__":
##    
##    class MyFrame(wxFrame):
##        def __init__(self, parent, ID, title):
##            wxFrame.__init__(self, parent, ID, title, wxDefaultPosition, wxSize(340, 500))
##            self.CreateStatusBar()
##            self.pnl = wxPanel(self, 101, wxDefaultPosition, wxDefaultSize)
##            self.stc = MySTC(self.pnl, 102)
##            self.btn1 = wxButton(self.pnl, 103, "Find Text", wxPoint(10, 420), wxDefaultSize)
##            self.btn2 = wxButton(self.pnl, 104, "Replace Text", wxPoint(210, 420), wxDefaultSize)
##            self.btn2 = wxButton(self.pnl, 105, "Find Next", wxPoint(110, 420), wxDefaultSize)
##
##
##            self.stc.AddText("we are living all in a yellow submarine (for example)\n"+
##            "we are living all in a yellow submarine (for example)")
##            
##            #how to set the background colour of Scintilla (Neil Hodgson)
##            self.stc.StyleSetBackground(wxSTC_STYLE_DEFAULT, "grey")
##            self.stc.StyleClearAll()
##
##            EVT_BUTTON(self, 103, self.OnFind)
##            EVT_BUTTON(self, 104, self.OnReplace)
##            EVT_BUTTON(self, 105, self.OnFindNext)
##            
##            self.stcf = STCFinder(self.stc)
##
##        def OnFind(self, event):
##            self.stcf.Find()
##
##        def OnFindNext(self, event):
##            self.stcf.FindNext()
##
##        def OnReplace(self, event):
##            dlg = StcReplaceDlg(self, self.stc)
##            dlg.ShowModal()
##            dlg.Destroy()
##
##    class MySTC(wxStyledTextCtrl):
##        def __init__(self, parent, ID):
##            wxStyledTextCtrl.__init__(self, parent, ID, wxDefaultPosition, wxSize(320, 400))
##
##    class MyApp(wxApp):
##        def OnInit(self):
##            frame = MyFrame(NULL, -1, "Scintilla: Find/Replace Dialog Test")
##            frame.Show(true)
##            self.SetTopWindow(frame)
##            return true
##
##
##    app = MyApp(0)
##    app.MainLoop()
