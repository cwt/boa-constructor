#-----------------------------------------------------------------------------
# Name:        FindReplaceDlg.py
# Purpose:     
#
# Author:      Tim Hochberg
#
# Created:     2001/29/08
# RCS-ID:      $Id$
# Copyright:   (c) 2001 Tim Hochberg
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Dialog:FindReplaceDlg

from wxPython.wx import *
from wxPython.lib.anchors import LayoutAnchors
from FindReplaceEngine import FindError

# XXX Should this return an indication of matches found?
def find(parent, finder, view):
    dlg = FindReplaceDlg(parent, finder, view)
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()

def findAgain(parent, finder, view):
    if finder.lastFind == "":
        find(parent, finder, view)
    else:
        try:
            finder.findNextInSource(view)
        except FindError, err:
            wxMessageBox(str(err), 'Find/Replace', wxOK | wxICON_INFORMATION, view)
    

[wxID_FINDREPLACEDLG, wxID_FINDREPLACEDLGCANCELBTN, wxID_FINDREPLACEDLGCASESENSITIVECB, wxID_FINDREPLACEDLGCLOSEONFOUNDCB, wxID_FINDREPLACEDLGDIRECTIONRB, wxID_FINDREPLACEDLGFINDALLBTN, wxID_FINDREPLACEDLGFINDBTN, wxID_FINDREPLACEDLGFINDTXT, wxID_FINDREPLACEDLGOPTIONSSB, wxID_FINDREPLACEDLGREGEXPRCB, wxID_FINDREPLACEDLGREPLACEALLBTN, wxID_FINDREPLACEDLGREPLACEBTN, wxID_FINDREPLACEDLGREPLACETXT, wxID_FINDREPLACEDLGSCOPERB, wxID_FINDREPLACEDLGSTATICTEXT1, wxID_FINDREPLACEDLGSTATICTEXT2, wxID_FINDREPLACEDLGWHOLEWORDSCB, wxID_FINDREPLACEDLGWRAPCB] = map(lambda _init_ctrls: wxNewId(), range(18))

class FindReplaceDlg(wxDialog):
    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxDialog.__init__(self, id = wxID_FINDREPLACEDLG, name = 'FindReplaceDlg', parent = prnt, pos = wxPoint(415, 262), size = wxSize(372, 220), style = wxDEFAULT_DIALOG_STYLE, title = 'Find/Replace Dialog')
        self._init_utils()
        self.SetAutoLayout(true)
        self.SetClientSize(wxSize(364, 193))

        self.staticText1 = wxStaticText(id = wxID_FINDREPLACEDLGSTATICTEXT1, label = 'Replace with', name = 'staticText1', parent = self, pos = wxPoint(8, 32), size = wxSize(62, 13), style = 0)

        self.directionRB = wxRadioBox(choices = ['Forward', 'Backward'], id = wxID_FINDREPLACEDLGDIRECTIONRB, label = 'Direction', majorDimension = 1, name = 'directionRB', parent = self, point = wxPoint(8, 56), size = wxSize(112, 64), style = wxRA_SPECIFY_COLS, validator = wxDefaultValidator)
        EVT_RADIOBOX(self.directionRB, wxID_FINDREPLACEDLGDIRECTIONRB, self.OnDirectionrbRadiobox)

        self.scopeRB = wxRadioBox(choices = ['All', 'Selected'], id = wxID_FINDREPLACEDLGSCOPERB, label = 'Scope', majorDimension = 1, name = 'scopeRB', parent = self, point = wxPoint(8, 120), size = wxSize(112, 64), style = wxRA_SPECIFY_COLS, validator = wxDefaultValidator)
        EVT_RADIOBOX(self.scopeRB, wxID_FINDREPLACEDLGSCOPERB, self.OnScoperbRadiobox)

        self.optionsSB = wxStaticBox(id = wxID_FINDREPLACEDLGOPTIONSSB, label = 'Options', name = 'optionsSB', parent = self, pos = wxPoint(128, 56), size = wxSize(136, 128), style = 0)

        self.caseSensitiveCB = wxCheckBox(id = wxID_FINDREPLACEDLGCASESENSITIVECB, label = 'Case sensitive', name = 'caseSensitiveCB', parent = self, pos = wxPoint(136, 72), size = wxSize(120, 19), style = 0)
        EVT_CHECKBOX(self.caseSensitiveCB, wxID_FINDREPLACEDLGCASESENSITIVECB, self.OnCasesensitivecbCheckbox)

        self.wholeWordsCB = wxCheckBox(id = wxID_FINDREPLACEDLGWHOLEWORDSCB, label = 'Whole words', name = 'wholeWordsCB', parent = self, pos = wxPoint(136, 92), size = wxSize(120, 19), style = 0)
        EVT_CHECKBOX(self.wholeWordsCB, wxID_FINDREPLACEDLGWHOLEWORDSCB, self.OnWholewordscbCheckbox)

        self.regExprCB = wxCheckBox(id = wxID_FINDREPLACEDLGREGEXPRCB, label = 'Regular expressions', name = 'regExprCB', parent = self, pos = wxPoint(136, 112), size = wxSize(120, 19), style = 0)
        EVT_CHECKBOX(self.regExprCB, wxID_FINDREPLACEDLGREGEXPRCB, self.OnRegexprcbCheckbox)

        self.wrapCB = wxCheckBox(id = wxID_FINDREPLACEDLGWRAPCB, label = 'Wrap search', name = 'wrapCB', parent = self, pos = wxPoint(136, 132), size = wxSize(120, 19), style = 0)
        EVT_CHECKBOX(self.wrapCB, wxID_FINDREPLACEDLGWRAPCB, self.OnWrapcbCheckbox)

        self.closeOnFoundCB = wxCheckBox(id = wxID_FINDREPLACEDLGCLOSEONFOUNDCB, label = 'Close on found', name = 'closeOnFoundCB', parent = self, pos = wxPoint(136, 152), size = wxSize(120, 19), style = 0)
        EVT_CHECKBOX(self.closeOnFoundCB, wxID_FINDREPLACEDLGCLOSEONFOUNDCB, self.OnCloseonfoundcbCheckbox)

        self.findBtn = wxButton(id = wxID_FINDREPLACEDLGFINDBTN, label = 'Find', name = 'findBtn', parent = self, pos = wxPoint(280, 64), size = wxSize(75, 23), style = 0)
        EVT_BUTTON(self.findBtn, wxID_FINDREPLACEDLGFINDBTN, self.OnFindbtnButton)

        self.findAllBtn = wxButton(id = wxID_FINDREPLACEDLGFINDALLBTN, label = 'Find all', name = 'findAllBtn', parent = self, pos = wxPoint(280, 88), size = wxSize(75, 23), style = 0)
        EVT_BUTTON(self.findAllBtn, wxID_FINDREPLACEDLGFINDALLBTN, self.OnFindallbtnButton)

        self.replaceBtn = wxButton(id = wxID_FINDREPLACEDLGREPLACEBTN, label = 'Replace', name = 'replaceBtn', parent = self, pos = wxPoint(280, 112), size = wxSize(75, 23), style = 0)
        EVT_BUTTON(self.replaceBtn, wxID_FINDREPLACEDLGREPLACEBTN, self.OnReplacebtnButton)

        self.replaceAllBtn = wxButton(id = wxID_FINDREPLACEDLGREPLACEALLBTN, label = 'Replace all', name = 'replaceAllBtn', parent = self, pos = wxPoint(280, 136), size = wxSize(75, 23), style = 0)
        EVT_BUTTON(self.replaceAllBtn, wxID_FINDREPLACEDLGREPLACEALLBTN, self.OnReplaceallbtnButton)

        self.cancelBtn = wxButton(id = wxID_FINDREPLACEDLGCANCELBTN, label = 'Cancel', name = 'cancelBtn', parent = self, pos = wxPoint(280, 160), size = wxSize(75, 23), style = 0)
        EVT_BUTTON(self.cancelBtn, wxID_FINDREPLACEDLGCANCELBTN, self.OnCancelbtnButton)

        self.findTxt = wxTextCtrl(id = wxID_FINDREPLACEDLGFINDTXT, name = 'findTxt', parent = self, pos = wxPoint(80, 4), size = wxSize(276, 21), style = wxTE_PROCESS_ENTER, value = '')
        EVT_TEXT_ENTER(self.findTxt, wxID_FINDREPLACEDLGFINDTXT, self.OnFindtxtTextEnter)

        self.replaceTxt = wxTextCtrl(id = wxID_FINDREPLACEDLGREPLACETXT, name = 'replaceTxt', parent = self, pos = wxPoint(80, 28), size = wxSize(276, 21), style = wxTE_PROCESS_ENTER, value = '')
        EVT_TEXT_ENTER(self.replaceTxt, wxID_FINDREPLACEDLGREPLACETXT, self.OnReplacetxtTextEnter)

        self.staticText2 = wxStaticText(id = wxID_FINDREPLACEDLGSTATICTEXT2, label = 'Text to find', name = 'staticText2', parent = self, pos = wxPoint(8, 8), size = wxSize(53, 20), style = 0)

    def __init__(self, parent, engine, view):
        self._init_ctrls(parent)
        self.engine = engine
        self.view = view
        # Set controls based on engine
        self.replaceTxt.SetValue(self.engine.lastReplace)
        self.replaceTxt.SetSelection(0, len(self.engine.lastReplace))
        self.caseSensitiveCB.SetValue(engine.case)
        self.wholeWordsCB.SetValue(engine.word)
        self.regExprCB.SetValue(engine.regex)
        self.wrapCB.SetValue(engine.wrap)
        self.closeOnFoundCB.SetValue(engine.closeOnFound)
        self.directionRB.SetSelection(engine.reverse)
        self.scopeRB.SetSelection(self.engine.selection)
        # Check if the view is a package
        if view.viewName in ("Package", "Application"):
            self.replaceTxt.Enable(false)
            self.findBtn.Enable(false)
            self.findAllBtn.SetDefault()
            self.replaceBtn.Enable(false)
            self.replaceAllBtn.Enable(false)
        else:
            self.findBtn.SetDefault()
            # Give the find entry focus
        self.findTxt.SetFocus() 

        text = self.engine.lastFind
        if self.view.viewName not in ("Package", "Application"):
            selStart, selEnd = self.view.GetSelection()
            if selStart != selEnd and self.view.LineFromPosition(selStart) == \
                  self.view.LineFromPosition(selEnd):
                text = self.view.GetSelectedText()

        self.findTxt.SetValue(text)
        self.findTxt.SetSelection(0, len(self.findTxt.GetValue()))

        wxID_CLOSEFIND = wxNewId()
        wxID_DOFIND = wxNewId()
        wxID_DOREPLACE = wxNewId()
        EVT_MENU(self, wxID_CLOSEFIND, self.OnCloseFind)
        EVT_MENU(self, wxID_DOFIND, self.OnFindbtnButton)
        EVT_MENU(self, wxID_DOREPLACE, self.OnReplacebtnButton)
        self.SetAcceleratorTable(
              wxAcceleratorTable([(wxACCEL_NORMAL, WXK_ESCAPE, wxID_CLOSEFIND),
                                  (wxACCEL_NORMAL, WXK_F3, wxID_DOFIND),
                                  (wxACCEL_CTRL, WXK_F3, wxID_DOREPLACE),
                                  ]))
        self.Center()

    def OnCancelbtnButton(self, event):
        self.EndModal(wxID_CANCEL)

    def OnFindbtnButton(self, event):
        self.find()
        
    def find(self):
        try:
            pattern = self.findTxt.GetValue()
            self.engine.findInSource(self.view, pattern)
            if self.engine.closeOnFound:
                self.EndModal(wxID_OK)
            else:
                self._checkSelectionDlgOverlap()
        except FindError, err:
            wxMessageBox(str(err), 'Find/Replace', wxOK | wxICON_INFORMATION, self)

    def findAll(self):   
        pattern = self.findTxt.GetValue()
        if self.view.viewName == "Package":
            self.engine.findAllInPackage(self.view, pattern)
        elif self.view.viewName == "Application":
            self.engine.findAllInApp(self.view, pattern)
        else:
            self.engine.findAllInSource(self.view, pattern)
        self.EndModal(wxID_OK)

    def replace(self):
        try:
            pattern = self.findTxt.GetValue()
            replacement = self.replaceTxt.GetValue()
            self.engine.replaceInSource(self.view, pattern, replacement)
            self._checkSelectionDlgOverlap()
        except FindError, err:
            wxMessageBox(str(err), 'Find/Replace', wxOK | wxICON_INFORMATION, self)

    def replaceAll(self):
        pattern = self.findTxt.GetValue()
        replacement = self.replaceTxt.GetValue()
        self.engine.replaceAllInSource(self.view, pattern, replacement)
        self.EndModal(wxID_OK)

    def OnDirectionrbRadiobox(self, event):
        self.engine.reverse = self.directionRB.GetSelection()

    def OnOriginrbRadiobox(self, event):
        pass # XXX move to RB

    def OnCasesensitivecbCheckbox(self, event):
        self.engine.case = self.caseSensitiveCB.GetValue()

    def OnWholewordscbCheckbox(self, event):
        self.engine.word = self.wholeWordsCB.GetValue()

    def OnRegexprcbCheckbox(self, event):
        self.engine.regex = self.regExprCB.GetValue()

    def OnFindtxtTextEnter(self, event):
        if self.view.viewName in ("Package", "Application"):
            self.findAll()
        else:
            self.find()

    def OnReplacebtnButton(self, event):
        self.replace()

    def OnFindallbtnButton(self, event):
        self.findAll()

    def OnReplacetxtTextEnter(self, event):
        self.replace()

    def OnReplaceallbtnButton(self, event):
        self.replaceAll()

    def OnScoperbRadiobox(self, event):
        self.engine.selection = self.scopeRB.GetSelection()

    def OnWrapcbCheckbox(self, event):
        self.engine.wrap = self.wrapCB.GetValue()

    def OnCloseFind(self, event):
        self.Close()

    def OnCloseonfoundcbCheckbox(self, event):
        self.engine.closeOnFound = self.closeOnFoundCB.GetValue()
    
    _fudgeOffset = 6
    def _checkSelectionDlgOverlap(self):
        if self.view.viewName not in ('Package', 'Application'):
            selStart, selEnd = self.view.GetSelection()
            selStartLnNo = self.view.LineFromPosition(selStart)
            if selStart != selEnd and selStartLnNo == self.view.LineFromPosition(selEnd):
                chrHeight = self.view.GetCharHeight()
                selPos = self.view.ClientToScreen(self.view.PointFromPosition(selStart))
                selSize = wxSize(self.view.ClientToScreen(
                      self.view.PointFromPosition(selEnd)).x - selPos.x, chrHeight)
                dlgPos, dlgSize = self.GetPosition(), self.GetSize()
                r = wxIntersectRect((selPos.x, selPos.y, selSize.x, selSize.y), 
                                    (dlgPos.x, dlgPos.y, dlgSize.x, dlgSize.y))
                if r is not None:
                    # simply moves dialog above or below selection
                    # sometimes rather moving it to the sides would be more 
                    # appropriate
                    if selStartLnNo < self.view.GetFirstVisibleLine() + \
                          self.view.LinesOnScreen()/2:
                        self.SetPosition( (dlgPos.x, selPos.y + chrHeight + self._fudgeOffset) )
                    else:
                        self.SetPosition( (dlgPos.x, selPos.y - dlgSize.y - self._fudgeOffset) )
                                    

if __name__ == '__main__':
    app = wxPySimpleApp()

    testText = '''Find replace dialog test


    
Boa boa keyboard        bOa boa keyboard        boA boa keyboard
quick brown fox jumps over the lazy dog
\n\n\n\n\n\n\n\n
Boa Constructor         Boa Constructor         Boa Constructor
'''
    # Create a simple test environment (RB)
    
    def createFramedView(caption, View, model, parent=None, size=wxDefaultSize):
        f = wxFrame(parent, -1, caption, size=size)
        v = View(f, model)
        f.Center()
        f.Show(1)
        return f, v
    
    class PseudoStatusBar:
        def setHint(self, hint, htype='Info'): wxLogMessage('Editor hint: %s'%hint)
    class PseudoEditor:
        def __init__(self): self.statusBar = PseudoStatusBar()
        def addBrowseMarker(self, lineNo): pass
        def addNewView(self, name, View): return createFramedView(name, View, self.model, self.parent, (400, 200))[1]
            
    e = PseudoEditor()
    from EditorModels import ModuleModel
    m = ModuleModel(testText, 'test.py', e, true)
    from Views.PySourceView import PythonSourceView
    f, v = createFramedView('Find/Replace Dlg Tester (Cancel to quit)', PythonSourceView, m, size=(600, 400))
    v.refreshCtrl()
    e.model, e.parent = m, f
    from FindReplaceEngine import FindReplaceEngine
    finder = FindReplaceEngine()
    finder.lastFind = 'boa'
    res = 0
    while res != wxID_CANCEL:
        dlg = FindReplaceDlg(f, finder, v)
        try: res = dlg.ShowModal()
        finally: dlg.Destroy()
        if res != wxID_CANCEL: wxLogMessage('Reopening dialog for testing')
       