#-----------------------------------------------------------------------------
# Name:        FindReplaceDlg.py
# Purpose:
#
# Author:      Tim Hochberg
#
# Created:     2001/29/08
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2004 Tim Hochberg
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Dialog:FindReplaceDlg

from wxPython.wx import *
from wxPython.lib.anchors import LayoutAnchors

import os, string

import Preferences, Utils
from FindReplaceEngine import FindError

import Search

true, false  = 1, 0

# XXX Should this return an indication of matches found?
def find(parent, finder, view):
    dlg = FindReplaceDlg(parent, finder, view)
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()

def findAgain(parent, finder, view):
    if len(finder.findHistory) == 1:
        find(parent, finder, view)
    else:
        try:
            finder.findNextInSource(view)
        except FindError, err:
            wxMessageBox(str(err), 'Find/Replace', wxOK | wxICON_INFORMATION, view)


[wxID_FINDREPLACEDLG, wxID_FINDREPLACEDLGBTNBROWSE, 
 wxID_FINDREPLACEDLGBTNBUILDINFIND, wxID_FINDREPLACEDLGBTNFINDINFILES, 
 wxID_FINDREPLACEDLGCANCELBTN, wxID_FINDREPLACEDLGCASESENSITIVECB, 
 wxID_FINDREPLACEDLGCHKRECURSIVESEARCH, wxID_FINDREPLACEDLGCLOSEONFOUNDCB, 
 wxID_FINDREPLACEDLGCMBFILEFILTER, wxID_FINDREPLACEDLGCMBFOLDER, 
 wxID_FINDREPLACEDLGDIRECTIONRB, wxID_FINDREPLACEDLGFINDALLBTN, 
 wxID_FINDREPLACEDLGFINDBTN, wxID_FINDREPLACEDLGFINDTXT, 
 wxID_FINDREPLACEDLGOPTIONSSB, wxID_FINDREPLACEDLGREGEXPRCB, 
 wxID_FINDREPLACEDLGREPLACEALLBTN, wxID_FINDREPLACEDLGREPLACEBTN, 
 wxID_FINDREPLACEDLGREPLACETXT, wxID_FINDREPLACEDLGSCOPERB, 
 wxID_FINDREPLACEDLGSTATICTEXT1, wxID_FINDREPLACEDLGSTATICTEXT2, 
 wxID_FINDREPLACEDLGSTATICTEXT3, wxID_FINDREPLACEDLGSTATICTEXT4, 
 wxID_FINDREPLACEDLGWHOLEWORDSCB, wxID_FINDREPLACEDLGWILDCARDCB, 
 wxID_FINDREPLACEDLGWRAPCB, 
] = map(lambda _init_ctrls: wxNewId(), range(27))

class FindReplaceDlg(wxDialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_FINDREPLACEDLG, name='FindReplaceDlg',
              parent=prnt, pos=wxPoint(323, 272), size=wxSize(364, 273),
              style=wxDEFAULT_DIALOG_STYLE, title='Find/Replace')
        self.SetAutoLayout(true)
        self.SetClientSize(wxSize(364, 273))

        self.findTxt = wxComboBox(choices=[], id=wxID_FINDREPLACEDLGFINDTXT,
              name='findTxt', parent=self, pos=wxPoint(88, 4), size=wxSize(239,
              23), style=0, value='')

        self.replaceTxt = wxComboBox(choices=[],
              id=wxID_FINDREPLACEDLGREPLACETXT, name='replaceTxt', parent=self,
              pos=wxPoint(88, 28), size=wxSize(269, 23), style=0, value='')
        EVT_KEY_UP(self.replaceTxt, self.OnFindtxtChar)

        self.cmbFolder = wxComboBox(choices=[], id=wxID_FINDREPLACEDLGCMBFOLDER,
              name='cmbFolder', parent=self, pos=wxPoint(88, 51),
              size=wxSize(239, 23), style=0, validator=wxDefaultValidator,
              value='')
        self.cmbFolder.SetLabel('')
        self.cmbFolder.SetToolTipString('Insert path to find in files')

        self.cmbFileFilter = wxComboBox(choices=[],
              id=wxID_FINDREPLACEDLGCMBFILEFILTER, name='cmbFileFilter',
              parent=self, pos=wxPoint(88, 74), size=wxSize(269, 23), style=0,
              validator=wxDefaultValidator, value='*.py')
        self.cmbFileFilter.SetLabel('*.py')
        self.cmbFileFilter.SetToolTipString('Files that will be included in search')

        self.directionRB = wxRadioBox(choices=['Forward', 'Backward'],
              id=wxID_FINDREPLACEDLGDIRECTIONRB, label='Direction',
              majorDimension=1, name='directionRB', parent=self,
              point=wxPoint(8, 103), size=wxSize(104, 64),
              style=wxRA_SPECIFY_COLS, validator=wxDefaultValidator)
        EVT_RADIOBOX(self.directionRB, wxID_FINDREPLACEDLGDIRECTIONRB,
              self.OnDirectionrbRadiobox)

        self.scopeRB = wxRadioBox(choices=['All', 'Selected'],
              id=wxID_FINDREPLACEDLGSCOPERB, label='Scope', majorDimension=1,
              name='scopeRB', parent=self, point=wxPoint(8, 195),
              size=wxSize(104, 64), style=wxRA_SPECIFY_COLS,
              validator=wxDefaultValidator)
        EVT_RADIOBOX(self.scopeRB, wxID_FINDREPLACEDLGSCOPERB,
              self.OnScoperbRadiobox)

        self.optionsSB = wxStaticBox(id=wxID_FINDREPLACEDLGOPTIONSSB,
              label='Options', name='optionsSB', parent=self, pos=wxPoint(120,
              103), size=wxSize(144, 158), style=0)

        self.caseSensitiveCB = wxCheckBox(id=wxID_FINDREPLACEDLGCASESENSITIVECB,
              label='Case sensitive', name='caseSensitiveCB', parent=self,
              pos=wxPoint(125, 120), size=wxSize(120, 19), style=0)
        EVT_CHECKBOX(self.caseSensitiveCB, wxID_FINDREPLACEDLGCASESENSITIVECB,
              self.OnCasesensitivecbCheckbox)

        self.wholeWordsCB = wxCheckBox(id=wxID_FINDREPLACEDLGWHOLEWORDSCB,
              label='Whole words', name='wholeWordsCB', parent=self,
              pos=wxPoint(125, 138), size=wxSize(120, 19), style=0)
        EVT_CHECKBOX(self.wholeWordsCB, wxID_FINDREPLACEDLGWHOLEWORDSCB,
              self.OnWholewordscbCheckbox)

        self.wildcardCB = wxCheckBox(id=wxID_FINDREPLACEDLGWILDCARDCB,
              label='Wildcards', name='wildcardCB', parent=self,
              pos=wxPoint(125, 156), size=wxSize(120, 19), style=0)
        EVT_CHECKBOX(self.wildcardCB, wxID_FINDREPLACEDLGWILDCARDCB,
              self.OnWildcardcbCheckbox)

        self.regExprCB = wxCheckBox(id=wxID_FINDREPLACEDLGREGEXPRCB,
              label='Regular expressions', name='regExprCB', parent=self,
              pos=wxPoint(125, 174), size=wxSize(131, 19), style=0)
        EVT_CHECKBOX(self.regExprCB, wxID_FINDREPLACEDLGREGEXPRCB,
              self.OnRegexprcbCheckbox)

        self.wrapCB = wxCheckBox(id=wxID_FINDREPLACEDLGWRAPCB,
              label='Wrap search', name='wrapCB', parent=self, pos=wxPoint(125,
              191), size=wxSize(120, 21), style=0)
        EVT_CHECKBOX(self.wrapCB, wxID_FINDREPLACEDLGWRAPCB,
              self.OnWrapcbCheckbox)

        self.closeOnFoundCB = wxCheckBox(id=wxID_FINDREPLACEDLGCLOSEONFOUNDCB,
              label='Close on found', name='closeOnFoundCB', parent=self,
              pos=wxPoint(125, 211), size=wxSize(120, 19), style=0)
        EVT_CHECKBOX(self.closeOnFoundCB, wxID_FINDREPLACEDLGCLOSEONFOUNDCB,
              self.OnCloseonfoundcbCheckbox)

        self.chkRecursiveSearch = wxCheckBox(id=wxID_FINDREPLACEDLGCHKRECURSIVESEARCH,
              label='Recursive search', name='chkRecursiveSearch', parent=self,
              pos=wxPoint(125, 233), size=wxSize(120, 14), style=0)
        self.chkRecursiveSearch.SetValue(false)

        self.findBtn = wxButton(id=wxID_FINDREPLACEDLGFINDBTN, label='Find',
              name='findBtn', parent=self, pos=wxPoint(270, 101),
              size=wxSize(83, 23), style=0)
        EVT_BUTTON(self.findBtn, wxID_FINDREPLACEDLGFINDBTN,
              self.OnFindbtnButton)
        EVT_KEY_UP(self.findBtn, self.OnFindtxtChar)

        self.findAllBtn = wxButton(id=wxID_FINDREPLACEDLGFINDALLBTN,
              label='Find all', name='findAllBtn', parent=self, pos=wxPoint(270,
              129), size=wxSize(84, 23), style=0)
        EVT_BUTTON(self.findAllBtn, wxID_FINDREPLACEDLGFINDALLBTN,
              self.OnFindallbtnButton)

        self.btnFindInFiles = wxButton(id=wxID_FINDREPLACEDLGBTNFINDINFILES,
              label='Find in files', name='btnFindInFiles', parent=self,
              pos=wxPoint(270, 156), size=wxSize(84, 23), style=0)
        EVT_BUTTON(self.btnFindInFiles, wxID_FINDREPLACEDLGBTNFINDINFILES,
              self.OnFindInFiles)

        self.replaceBtn = wxButton(id=wxID_FINDREPLACEDLGREPLACEBTN,
              label='Replace', name='replaceBtn', parent=self, pos=wxPoint(270,
              183), size=wxSize(83, 23), style=0)
        EVT_BUTTON(self.replaceBtn, wxID_FINDREPLACEDLGREPLACEBTN,
              self.OnReplacebtnButton)

        self.replaceAllBtn = wxButton(id=wxID_FINDREPLACEDLGREPLACEALLBTN,
              label='Replace all', name='replaceAllBtn', parent=self,
              pos=wxPoint(270, 210), size=wxSize(83, 23), style=0)
        EVT_BUTTON(self.replaceAllBtn, wxID_FINDREPLACEDLGREPLACEALLBTN,
              self.OnReplaceallbtnButton)

        self.cancelBtn = wxButton(id=wxID_FINDREPLACEDLGCANCELBTN,
              label='Cancel', name='cancelBtn', parent=self, pos=wxPoint(270,
              238), size=wxSize(83, 23), style=0)
        EVT_BUTTON(self.cancelBtn, wxID_FINDREPLACEDLGCANCELBTN,
              self.OnCancelbtnButton)

        self.staticText2 = wxStaticText(id=wxID_FINDREPLACEDLGSTATICTEXT2,
              label='Text to find', name='staticText2', parent=self,
              pos=wxPoint(8, 8), size=wxSize(80, 20), style=0)

        self.staticText1 = wxStaticText(id=wxID_FINDREPLACEDLGSTATICTEXT1,
              label='Replace with', name='staticText1', parent=self,
              pos=wxPoint(8, 32), size=wxSize(80, 15), style=0)

        self.staticText3 = wxStaticText(id=wxID_FINDREPLACEDLGSTATICTEXT3,
              label='Files to find in', name='staticText3', parent=self,
              pos=wxPoint(8, 56), size=wxSize(80, 13), style=0)

        self.staticText4 = wxStaticText(id=wxID_FINDREPLACEDLGSTATICTEXT4,
              label='File filter', name='staticText4', parent=self,
              pos=wxPoint(8, 80), size=wxSize(80, 15), style=0)

        self.btnBuildInFind = wxButton(id=wxID_FINDREPLACEDLGBTNBUILDINFIND,
              label='...', name='btnBuildInFind', parent=self, pos=wxPoint(329,
              4), size=wxSize(27, 21), style=0)
        self.btnBuildInFind.SetToolTipString('Build-in ready to run searches')
        EVT_BUTTON(self.btnBuildInFind, wxID_FINDREPLACEDLGBTNBUILDINFIND,
              self.OnBuildInFind)

        self.btnBrowse = wxButton(id=wxID_FINDREPLACEDLGBTNBROWSE, label='...',
              name='btnBrowse', parent=self, pos=wxPoint(329, 51),
              size=wxSize(27, 21), style=0)
        self.btnBrowse.SetToolTipString('Folders tree')
        EVT_BUTTON(self.btnBrowse, wxID_FINDREPLACEDLGBTNBROWSE, self.OnBrowse)

    def __init__(self, parent, engine, view, bModeFindReplace = 1):
        self._init_ctrls(parent)
        self.engine = engine
        self.view = view
        # Bind enter event using acceleratorTable
        wxID_FINDRETURN = wxNewId()
        EVT_MENU(self, wxID_FINDRETURN, self.OnFindtxtTextEnter)
        self.findTxt.SetAcceleratorTable(wxAcceleratorTable([(wxACCEL_NORMAL, WXK_RETURN, wxID_FINDRETURN)]))
        wxID_REPLACERETURN = wxNewId()
        EVT_MENU(self, wxID_REPLACERETURN, self.OnReplacetxtTextEnter)
        self.replaceTxt.SetAcceleratorTable(wxAcceleratorTable([(wxACCEL_NORMAL, WXK_RETURN, wxID_FINDRETURN)]))
        # Set controls based on engine
        self.setComboBoxes('init')
        self.caseSensitiveCB.SetValue(engine.case)
        self.wholeWordsCB.SetValue(engine.word)
        self.regExprCB.SetValue(engine.mode == 'regex')
        self.wildcardCB.SetValue(engine.mode == 'wildcard')
        self.wrapCB.SetValue(engine.wrap)
        self.closeOnFoundCB.SetValue(engine.closeOnFound)
        self.directionRB.SetSelection(engine.reverse)
        self.scopeRB.SetSelection(self.engine.selection)
        # Check if the view is a package
        if hasattr(view, 'viewName'):
            if view.viewName in ("Package", "Application"):
                self.replaceTxt.Enable(false)
                self.findBtn.Enable(false)
                self.replaceBtn.Enable(false)
                self.replaceAllBtn.Enable(false)
                self.findAllBtn.SetDefault()
            else:
                # Otherwise, for findTxt, use the selected text if it's all on one
                # line, otherwise use the most recent item in the history.
                text = view.GetSelectedText()
                selStart, selEnd = self.view.GetSelection()
                if selStart != selEnd and '\n' not in text:
                    self.findTxt.SetValue(text)
                    self.findTxt.SetMark(0, len(text))
                # Use this region for future search replaces over selected.
                engine.setRegion(view, view.GetSelection())
                self.findBtn.SetDefault()

        # Give the find entry focus
        self.findTxt.SetFocus()

        wxID_DOFIND = wxNewId()
        wxID_DOREPLACE = wxNewId()
        EVT_MENU(self, wxID_DOFIND, self.OnFindbtnButton)
        EVT_MENU(self, wxID_DOREPLACE, self.OnReplacebtnButton)
        # bug in wxPython, esc key not working
        self.SetAcceleratorTable(
              wxAcceleratorTable([ Utils.setupCloseWindowOnEscape(self),
                                  (wxACCEL_NORMAL, WXK_F3, wxID_DOFIND),
                                  (wxACCEL_CTRL, WXK_F3, wxID_DOREPLACE),
                                  ]))

        #woraround for above bug, bind key evt to all ctrls
        for ctrl in (self.findTxt, self.replaceTxt, self.directionRB, self.scopeRB,
                     self.optionsSB, self.caseSensitiveCB, self.wholeWordsCB,
                     self.wildcardCB, self.regExprCB, self.wrapCB,
                     self.closeOnFoundCB, self.findBtn, self.findAllBtn,
                     self.replaceBtn, self.replaceAllBtn, self.cancelBtn):
            EVT_KEY_UP(ctrl, self.OnFindtxtChar)

        if not bModeFindReplace:
            self.findAllBtn.Enable(false)
            self.findBtn.Enable(false)
            self.replaceBtn.Enable(false)
            self.replaceAllBtn.Enable(false)
            self.engine.closeOnFound = true
            self.closeOnFoundCB.SetValue(engine.closeOnFound)
            self.directionRB.Enable(false)
            self.scopeRB.Enable(false)
            self.btnFindInFiles.SetDefault()

        self.Center()

        self._mapBuildInFinds = {
            'Derived classes':'\s*class\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(.*[^a-zA-Z0-9_]?XXXX[^a-zA-Z0-9_]?.*\)',
            'Class definition':'\s*class\s+XXXX(\s|[^a-zA-Z0-9_])',
            'Function\method definition':'\s*def\s+XXXX(\s|[^a-zA-Z0-9_])',
            'Class member':'(\s|[^a-zA-Z0-9_])self\.+XXXX(\s|[^a-zA-Z0-9_])'
        }

    def SetWorkingFolder(self, folder):
        self.cmbFolder.SetValue(folder)

    def setComboBoxes(self, setWhat):
        # We discard the empty item at the start of the history unless
        # It's the only item -- this make the list box look better.
        self.findTxt.Clear()
        history = self.engine.findHistory[1:] or ['']
        history.reverse()
        for x in history:
            self.findTxt.Append(x)
        self.findTxt.SetValue(history[0])
        self.findTxt.SetMark(0, len(history[0]))

        try:
            working_folder = os.path.dirname(self.view.model.localFilename())
        except:
            working_folder = ''

        self.cmbFolder.Clear()
        history = self.engine.folderHistory[1:] or [working_folder]
        history.reverse()
        for x in history:
            self.cmbFolder.Append(x)
        self.cmbFolder.SetValue(history[0])

        history = self.engine.suffixHistory[1:] or ['*.py']
        history.reverse()
        for x in history:
            self.cmbFileFilter.Append(x)
        self.cmbFileFilter.SetValue(history[0])

        if setWhat in ['init', 'replace']:
            self.replaceTxt.Clear()
            history = self.engine.replaceHistory[1:] or ['']
            history.reverse()
            for x in history:
                self.replaceTxt.Append(x)
            self.replaceTxt.SetValue(history[0])

    def OnCancelbtnButton(self, event):
        self.EndModal(wxID_CANCEL)

    def OnFindbtnButton(self, event):
        self.find()

    def find(self):
        try:
            pattern = self.findTxt.GetValue()
            self.engine.findInSource(self.view, pattern)
            self.setComboBoxes('find')
            if self.engine.closeOnFound and not self.replaceTxt.GetValue():
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
        self.setComboBoxes('find')
        self.EndModal(wxID_OK)

    def replace(self):
        try:
            pattern = self.findTxt.GetValue()
            replacement = self.replaceTxt.GetValue()
            self.engine.replaceInSource(self.view, pattern, replacement)
            self._checkSelectionDlgOverlap()
            self.setComboBoxes('replace')
        except FindError, err:
            wxMessageBox(str(err), 'Find/Replace', wxOK | wxICON_INFORMATION, self)

    def replaceAll(self):
        pattern = self.findTxt.GetValue()
        replacement = self.replaceTxt.GetValue()
        self.engine.replaceAllInSource(self.view, pattern, replacement)
        self.setComboBoxes('replace')
        self.EndModal(wxID_OK)

    def findInFiles(self):
        names = []
        pattern = self.findTxt.GetValue()
        bRecursive = self.chkRecursiveSearch.GetValue()
        file_filter = string.split(self.cmbFileFilter.GetValue(), ';')
        folder = [self.cmbFolder.GetValue()]
        self.engine.addFolder(folder[0])
        self.engine.addSuffix(self.cmbFileFilter.GetValue())
        dlg = wxProgressDialog("Building file list from directory '%s'" % (folder[0]),
                       'Searching...', 100, self.view,
                        wxPD_CAN_ABORT | wxPD_APP_MODAL | wxPD_AUTO_HIDE)
        try:
            iterDirFiles = Search.listFiles(folder, file_filter, 1, bRecursive)
            iStep = 0
            for sFile in iterDirFiles:
                names.append(sFile)
                if iStep < 100 and not dlg.Update(iStep):
                    #self.view.model.editor.setStatus('Search aborted')
                    break
                iStep = iStep + 1
        finally:
            dlg.Destroy()
        self.engine.findAllInFiles(names, self.view, pattern )
        self.setComboBoxes('findInFiles')
        if self.engine.closeOnFound:
            self.EndModal(wxID_OK)


    def _validate(self, what):
        ##Doesn't matter how we want to search we need smth to search to.
        if not self.findTxt.GetValue():
            wxMessageBox('There is nothing to find.', 'Boa - Find/Replace')
            return false
        if what in ['find', 'findAll']:
            pass
        elif what in ['replace', 'replaceAll']:
            if not self.replaceTxt.GetValue():
                wxMessageBox('There is nothing to replace with.', 'Boa - Find/Replace')
                return false
        elif what == 'findInFiles':
            if not os.path.isdir( self.cmbFolder.GetValue() ):
                wxMessageBox('The folder you entered is not valid folder.', 'Boa - Find/Replace' )
                return false
        else:
            pass
        return true

    def OnDirectionrbRadiobox(self, event):
        self.engine.reverse = self.directionRB.GetSelection()

    def OnCasesensitivecbCheckbox(self, event):
        self.engine.case = self.caseSensitiveCB.GetValue()

    def OnWholewordscbCheckbox(self, event):
        self.engine.word = self.wholeWordsCB.GetValue()

    def OnRegexprcbCheckbox(self, event):
        if self.regExprCB.GetValue():
            self.wildcardCB.SetValue(0)
        mode = {(0,0) : 'text', (1,0) : 'regex', (0,1) : 'wildcard'}[
                    (self.regExprCB.GetValue(), self.wildcardCB.GetValue())]
        self.engine.mode = mode

    def OnFindtxtTextEnter(self, event):
        if self.view.viewName in ('Package', 'Application'):
            if self._validate('findAll'):
                self.findAll()
        else:
            if self._validate('find'):
                self.find()

    def OnReplacebtnButton(self, event):
        if self._validate('replace'):
            self.replace()

    def OnFindallbtnButton(self, event):
        if self._validate('findAll'):
            self.findAll()

    def OnReplacetxtTextEnter(self, event):
        if self._validate('replace'):
            self.replace()

    def OnReplaceallbtnButton(self, event):
        if self._validate('replaceAll'):
            self.replaceAll()

    def OnFindInFiles(self, event):
        if self._validate('findInFiles'):
            self.findInFiles()

    def OnScoperbRadiobox(self, event):
        self.engine.selection = self.scopeRB.GetSelection()

    def OnWrapcbCheckbox(self, event):
        self.engine.wrap = self.wrapCB.GetValue()

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
                    mcp = self.ScreenToClient(wxGetMousePosition())
                    if selStartLnNo < self.view.GetFirstVisibleLine() + \
                          self.view.LinesOnScreen()/2:
                        self.SetPosition( (dlgPos.x, selPos.y + chrHeight + self._fudgeOffset) )
                    else:
                        self.SetPosition( (dlgPos.x, selPos.y - dlgSize.y - self._fudgeOffset) )
                    self.WarpPointer(mcp.x, mcp.y)

    def OnWildcardcbCheckbox(self, event):
        if self.wildcardCB.GetValue():
            self.regExprCB.SetValue(0)
        mode = {(0,0) : 'text', (1,0) : 'regex', (0,1) : 'wildcard'}[
                    (self.regExprCB.GetValue(), self.wildcardCB.GetValue())]
        self.engine.mode = mode

    def OnFindtxtChar(self, event):
        if event.GetKeyCode() == WXK_ESCAPE:
            self.Close()
        event.Skip()

    def OnBuildInFind(self, event):
        dlg = wxSingleChoiceDialog(self, 'Find', 'Build in finds', self._mapBuildInFinds.keys())
        try:
            if dlg.ShowModal() == wxID_OK:
                selected = dlg.GetStringSelection()
                self.findTxt.SetValue(self._mapBuildInFinds[selected])
                self.regExprCB.SetValue(1)
                self.OnRegexprcbCheckbox(None)
        finally:
            dlg.Destroy()

        self.findBtn.SetFocus()


    def browseForDir(self, strFromFolder=''):
        strPath = ''
        dlgDirDialog = wxDirDialog(self)
        dlgDirDialog.SetPath( strFromFolder )
        if dlgDirDialog.ShowModal() == wxID_OK:
            strPath = dlgDirDialog.GetPath()
        dlgDirDialog.Destroy()
        return strPath

    def OnBrowse(self, event):
        strNewPath = self.browseForDir()
        if strNewPath:
            self.cmbFolder.SetValue(strNewPath)

        self.findBtn.SetFocus()


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
        def Disconnect(self, id): pass
        def setStatus(self, hint, htype='Info', ringBell=false): wxLogMessage('Editor hint: %s'%hint)

    e = PseudoEditor()
    from Models.PythonEditorModels import ModuleModel
    m = ModuleModel(testText, 'test.py', e, true)
    from Views.PySourceView import PythonSourceView
    f, v = createFramedView('Find/Replace Dlg Tester (Cancel to quit)', PythonSourceView, m, size=(600, 400))
    v.refreshCtrl()
    e.model, e.parent = m, f
    from FindReplaceEngine import FindReplaceEngine
    finder = FindReplaceEngine()
    finder.addFind('boa')
    res = 0
    while res != wxID_CANCEL:
        dlg = FindReplaceDlg(f, finder, v)
        try: res = dlg.ShowModal()
        finally: dlg.Destroy()
        if res != wxID_CANCEL: wxLogMessage('Reopening dialog for testing')
