#-----------------------------------------------------------------------------
# Name:        FindReplaceDlg.py
# Purpose:
#
# Authors:      Tim Hochberg, Ianare Sevi
#
# Created:     2001/29/08
# RCS-ID:      $Id$
# Copyright:   (c) 2001 - 2006 Tim Hochberg
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Dialog:FindReplaceDlg

import wx
from wx.lib.anchors import LayoutAnchors

import os, string

import Preferences, Utils
from Utils import _

from FindReplaceEngine import FindError

import Search

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
            wx.MessageBox(str(err), _('Find/Replace'), wx.OK | wx.ICON_INFORMATION, view)


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
] = [wx.NewId() for _init_ctrls in range(27)]

class FindReplaceDlg(wx.Dialog):    
    def _init_coll_staticBoxSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.caseSensitiveCB, 0, border=3, flag=wx.BOTTOM)
        parent.AddWindow(self.wholeWordsCB, 0, border=3, flag=wx.BOTTOM)
        parent.AddWindow(self.wildcardCB, 0, border=3, flag=wx.BOTTOM)
        parent.AddWindow(self.regExprCB, 0, border=3, flag=wx.BOTTOM)
        parent.AddWindow(self.wrapCB, 0, border=3, flag=wx.BOTTOM)
        parent.AddWindow(self.closeOnFoundCB, 0, border=3, flag=wx.BOTTOM)
        parent.AddWindow(self.chkRecursiveSearch, 0, border=3, flag=wx.BOTTOM)

    def _init_coll_boxSizer7_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.directionRB, 0, border=0, flag=wx.ALIGN_CENTER)
        parent.AddWindow(self.scopeRB, 0, border=10,
              flag=wx.ALIGN_CENTER | wx.TOP)

    def _init_coll_boxSizer8_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.findBtn, 0, border=4, flag=wx.EXPAND | wx.BOTTOM)
        parent.AddWindow(self.findAllBtn, 0, border=4,
              flag=wx.EXPAND | wx.BOTTOM)
        parent.AddWindow(self.btnFindInFiles, 0, border=4,
              flag=wx.EXPAND | wx.BOTTOM)
        parent.AddWindow(self.replaceBtn, 0, border=4,
              flag=wx.EXPAND | wx.BOTTOM)
        parent.AddWindow(self.replaceAllBtn, 0, border=4,
              flag=wx.EXPAND | wx.BOTTOM)
        parent.AddWindow(self.cancelBtn, 0, border=4,
              flag=wx.EXPAND | wx.BOTTOM)

    def _init_coll_boxSizer6_Items(self, parent):
        # generated method, don't edit

        parent.AddSizer(self.boxSizer7, 0, border=5,
              flag=wx.EXPAND | wx.RIGHT | wx.LEFT)
        parent.AddSizer(self.staticBoxSizer1, 1, border=5,
              flag=wx.GROW | wx.RIGHT)
        parent.AddSizer(self.boxSizer8, 0, border=5, flag=wx.EXPAND | wx.RIGHT)

    def _init_coll_boxSizer4_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.staticText3, 0, border=0, flag=wx.ALIGN_CENTER)
        parent.AddWindow(self.cmbFolder, 1, border=0, flag=0)
        parent.AddWindow(self.btnBrowse, 0, border=3,
              flag=wx.ALIGN_CENTER | wx.LEFT)

    def _init_coll_boxSizer5_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.staticText4, 0, border=0, flag=wx.ALIGN_CENTER)
        parent.AddWindow(self.cmbFileFilter, 1, border=0, flag=0)

    def _init_coll_boxSizer3_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.staticText1, 0, border=0, flag=wx.ALIGN_CENTER)
        parent.AddWindow(self.replaceTxt, 1, border=0, flag=0)

    def _init_coll_boxSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddSizer(self.boxSizer2, 0, border=5, flag=wx.ALL | wx.EXPAND)
        parent.AddSizer(self.boxSizer3, 0, border=5,
              flag=wx.RIGHT | wx.LEFT | wx.EXPAND)
        parent.AddSizer(self.boxSizer4, 0, border=5, flag=wx.ALL | wx.EXPAND)
        parent.AddSizer(self.boxSizer5, 0, border=5,
              flag=wx.RIGHT | wx.LEFT | wx.BOTTOM | wx.EXPAND)
        parent.AddSizer(self.boxSizer6, 1, border=0, flag=wx.EXPAND)

    def _init_coll_boxSizer2_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.staticText2, 0, border=0, flag=wx.ALIGN_CENTER)
        parent.AddWindow(self.findTxt, 1, border=0, flag=wx.ALIGN_CENTER)
        parent.AddWindow(self.btnBuildInFind, 0, border=3,
              flag=wx.LEFT | wx.ALIGN_CENTER)

    def _init_sizers(self):
        # generated method, don't edit
        self.boxSizer1 = wx.BoxSizer(orient=wx.VERTICAL)

        self.boxSizer2 = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.boxSizer3 = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.boxSizer4 = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.boxSizer5 = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.boxSizer6 = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.boxSizer7 = wx.BoxSizer(orient=wx.VERTICAL)

        self.boxSizer8 = wx.BoxSizer(orient=wx.VERTICAL)

        self.staticBoxSizer1 = wx.StaticBoxSizer(box=self.optionsSB,
              orient=wx.VERTICAL)

        self._init_coll_boxSizer1_Items(self.boxSizer1)
        self._init_coll_boxSizer2_Items(self.boxSizer2)
        self._init_coll_boxSizer3_Items(self.boxSizer3)
        self._init_coll_boxSizer4_Items(self.boxSizer4)
        self._init_coll_boxSizer5_Items(self.boxSizer5)
        self._init_coll_boxSizer6_Items(self.boxSizer6)
        self._init_coll_boxSizer7_Items(self.boxSizer7)
        self._init_coll_boxSizer8_Items(self.boxSizer8)
        self._init_coll_staticBoxSizer1_Items(self.staticBoxSizer1)

        self.SetSizer(self.boxSizer1)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_FINDREPLACEDLG, name='FindReplaceDlg',
              parent=prnt, pos=wx.Point(212, 511), size=wx.Size(460, 354),
              style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER,
              title=_('Find/Replace'))
        self.SetClientSize(wx.Size(452, 327))

        self.findTxt = wx.ComboBox(choices=[], id=wxID_FINDREPLACEDLGFINDTXT,
              name='findTxt', parent=self, pos=wx.Point(88, 9),
              size=wx.Size(332, 21), style=0, value='')

        self.staticText2 = wx.StaticText(id=wxID_FINDREPLACEDLGSTATICTEXT2,
              label=_('Text to find'), name='staticText2', parent=self,
              pos=wx.Point(5, 11), size=wx.Size(83, 17), style=0)

        self.replaceTxt = wx.ComboBox(choices=[],
              id=wxID_FINDREPLACEDLGREPLACETXT, name='replaceTxt', parent=self,
              pos=wx.Point(88, 39), size=wx.Size(359, 21), style=0, value='')
        self.replaceTxt.Bind(wx.EVT_KEY_UP, self.OnFindtxtChar)

        self.staticText1 = wx.StaticText(id=wxID_FINDREPLACEDLGSTATICTEXT1,
              label=_('Replace with'), name='staticText1', parent=self,
              pos=wx.Point(5, 41), size=wx.Size(83, 17), style=0)

        self.cmbFolder = wx.ComboBox(choices=[],
              id=wxID_FINDREPLACEDLGCMBFOLDER, name='cmbFolder', parent=self,
              pos=wx.Point(88, 65), size=wx.Size(332, 21), style=0, value='')
        self.cmbFolder.SetLabel('')
        self.cmbFolder.SetToolTipString(_('Insert a path to find in files'))

        self.staticText3 = wx.StaticText(id=wxID_FINDREPLACEDLGSTATICTEXT3,
              label=_('Files to find in'), name='staticText3', parent=self,
              pos=wx.Point(5, 71), size=wx.Size(83, 17), style=0)

        self.cmbFileFilter = wx.ComboBox(choices=[],
              id=wxID_FINDREPLACEDLGCMBFILEFILTER, name='cmbFileFilter',
              parent=self, pos=wx.Point(88, 99), size=wx.Size(359, 21), style=0,
              value='*.py')
        self.cmbFileFilter.SetLabel('*.py')
        self.cmbFileFilter.SetToolTipString(_('Files that will be included in search'))

        self.staticText4 = wx.StaticText(id=wxID_FINDREPLACEDLGSTATICTEXT4,
              label=_('File filter'), name='staticText4', parent=self,
              pos=wx.Point(5, 99), size=wx.Size(83, 21), style=0)

        self.directionRB = wx.RadioBox(choices=[_('Forward'), _('Backward')],
              id=wxID_FINDREPLACEDLGDIRECTIONRB, label=_('Direction'),
              majorDimension=1, name='directionRB', parent=self, pos=wx.Point(5,
              125), size=wx.Size(91, 68), style=wx.RA_SPECIFY_COLS)
        self.directionRB.Bind(wx.EVT_RADIOBOX, self.OnDirectionrbRadiobox,
              id=wxID_FINDREPLACEDLGDIRECTIONRB)

        self.scopeRB = wx.RadioBox(choices=[_('All'), _('Selected')],
              id=wxID_FINDREPLACEDLGSCOPERB, label=_('Scope'), majorDimension=1,
              name='scopeRB', parent=self, pos=wx.Point(7, 203),
              size=wx.Size(86, 68), style=wx.RA_SPECIFY_COLS)
        self.scopeRB.Bind(wx.EVT_RADIOBOX, self.OnScoperbRadiobox,
              id=wxID_FINDREPLACEDLGSCOPERB)

        self.optionsSB = wx.StaticBox(id=wxID_FINDREPLACEDLGOPTIONSSB,
              label=_('Options'), name='optionsSB', parent=self,
              pos=wx.Point(101, 125), size=wx.Size(233, 202), style=0)

        self.caseSensitiveCB = wx.CheckBox(id=wxID_FINDREPLACEDLGCASESENSITIVECB,
              label=_('Case sensitive'), name='caseSensitiveCB', parent=self,
              pos=wx.Point(106, 142), size=wx.Size(116, 22), style=0)
        self.caseSensitiveCB.Bind(wx.EVT_CHECKBOX,
              self.OnCasesensitivecbCheckbox,
              id=wxID_FINDREPLACEDLGCASESENSITIVECB)

        self.wholeWordsCB = wx.CheckBox(id=wxID_FINDREPLACEDLGWHOLEWORDSCB,
              label=_('Whole words'), name='wholeWordsCB', parent=self,
              pos=wx.Point(106, 166), size=wx.Size(103, 22), style=0)
        self.wholeWordsCB.Bind(wx.EVT_CHECKBOX, self.OnWholewordscbCheckbox,
              id=wxID_FINDREPLACEDLGWHOLEWORDSCB)

        self.wildcardCB = wx.CheckBox(id=wxID_FINDREPLACEDLGWILDCARDCB,
              label=_('Wildcards'), name='wildcardCB', parent=self,
              pos=wx.Point(106, 190), size=wx.Size(84, 22), style=0)
        self.wildcardCB.Bind(wx.EVT_CHECKBOX, self.OnWildcardcbCheckbox,
              id=wxID_FINDREPLACEDLGWILDCARDCB)

        self.regExprCB = wx.CheckBox(id=wxID_FINDREPLACEDLGREGEXPRCB,
              label=_('Regular expressions'), name='regExprCB', parent=self,
              pos=wx.Point(106, 214), size=wx.Size(151, 22), style=0)
        self.regExprCB.Bind(wx.EVT_CHECKBOX, self.OnRegexprcbCheckbox,
              id=wxID_FINDREPLACEDLGREGEXPRCB)

        self.wrapCB = wx.CheckBox(id=wxID_FINDREPLACEDLGWRAPCB,
              label=_('Wrap search'), name='wrapCB', parent=self,
              pos=wx.Point(106, 238), size=wx.Size(102, 22), style=0)
        self.wrapCB.Bind(wx.EVT_CHECKBOX, self.OnWrapcbCheckbox,
              id=wxID_FINDREPLACEDLGWRAPCB)

        self.closeOnFoundCB = wx.CheckBox(id=wxID_FINDREPLACEDLGCLOSEONFOUNDCB,
              label=_('Close on found'), name='closeOnFoundCB',
              parent=self, pos=wx.Point(106, 262), size=wx.Size(195, 22),
              style=0)
        self.closeOnFoundCB.Bind(wx.EVT_CHECKBOX, self.OnCloseonfoundcbCheckbox,
              id=wxID_FINDREPLACEDLGCLOSEONFOUNDCB)

        self.chkRecursiveSearch = wx.CheckBox(id=wxID_FINDREPLACEDLGCHKRECURSIVESEARCH,
              label=_('Recursive search'), name='chkRecursiveSearch',
              parent=self, pos=wx.Point(106, 286), size=wx.Size(131, 22),
              style=0)
        self.chkRecursiveSearch.SetValue(False)

        self.findBtn = wx.Button(id=wxID_FINDREPLACEDLGFINDBTN, label=_('Find'),
              name='findBtn', parent=self, pos=wx.Point(339, 125),
              size=wx.Size(108, 27), style=0)
        self.findBtn.Bind(wx.EVT_BUTTON, self.OnFindbtnButton,
              id=wxID_FINDREPLACEDLGFINDBTN)
        self.findBtn.Bind(wx.EVT_KEY_UP, self.OnFindtxtChar)

        self.findAllBtn = wx.Button(id=wxID_FINDREPLACEDLGFINDALLBTN,
              label=_('Find all'), name='findAllBtn', parent=self,
              pos=wx.Point(339, 156), size=wx.Size(108, 28), style=0)
        self.findAllBtn.Bind(wx.EVT_BUTTON, self.OnFindallbtnButton,
              id=wxID_FINDREPLACEDLGFINDALLBTN)

        self.btnFindInFiles = wx.Button(id=wxID_FINDREPLACEDLGBTNFINDINFILES,
              label=_('Find in files'), name='btnFindInFiles', parent=self,
              pos=wx.Point(339, 188), size=wx.Size(108, 28), style=0)
        self.btnFindInFiles.Bind(wx.EVT_BUTTON, self.OnFindInFiles,
              id=wxID_FINDREPLACEDLGBTNFINDINFILES)

        self.replaceBtn = wx.Button(id=wxID_FINDREPLACEDLGREPLACEBTN,
              label=_('Replace'), name='replaceBtn', parent=self,
              pos=wx.Point(339, 220), size=wx.Size(108, 28), style=0)
        self.replaceBtn.Bind(wx.EVT_BUTTON, self.OnReplacebtnButton,
              id=wxID_FINDREPLACEDLGREPLACEBTN)

        self.replaceAllBtn = wx.Button(id=wxID_FINDREPLACEDLGREPLACEALLBTN,
              label=_('Replace all'), name='replaceAllBtn', parent=self,
              pos=wx.Point(339, 252), size=wx.Size(108, 28), style=0)
        self.replaceAllBtn.Bind(wx.EVT_BUTTON, self.OnReplaceallbtnButton,
              id=wxID_FINDREPLACEDLGREPLACEALLBTN)

        self.cancelBtn = wx.Button(id=wx.ID_CANCEL, label=_('Cancel'),
              name='cancelBtn', parent=self, pos=wx.Point(339, 284),
              size=wx.Size(108, 28), style=0)

        self.btnBuildInFind = wx.Button(id=wxID_FINDREPLACEDLGBTNBUILDINFIND,
              label='...', name='btnBuildInFind', parent=self, pos=wx.Point(423,
              5), size=wx.Size(24, 29), style=wx.BU_EXACTFIT)
        self.btnBuildInFind.SetToolTipString(_('Build-in ready to run searches'))
        self.btnBuildInFind.Bind(wx.EVT_BUTTON, self.OnBuildInFind,
              id=wxID_FINDREPLACEDLGBTNBUILDINFIND)

        self.btnBrowse = wx.Button(id=wxID_FINDREPLACEDLGBTNBROWSE, label='...',
              name='btnBrowse', parent=self, pos=wx.Point(423, 65),
              size=wx.Size(24, 29), style=wx.BU_EXACTFIT)
        self.btnBrowse.SetToolTipString(_('Folders tree'))
        self.btnBrowse.Bind(wx.EVT_BUTTON, self.OnBrowse,
              id=wxID_FINDREPLACEDLGBTNBROWSE)

        self._init_sizers()

    def __init__(self, parent, engine, view, bModeFindReplace = 1):
        self._init_ctrls(parent)
        
        # reset all sizes to default
        # ungraceful kludge, but allows to bypass Boa's
        # sizing limitations
        Utils.resetMinSize(self)
        
        # get the longest text size and apply it to all texts
        # XXX better to put the top controls in a flexgrid so this is automatic
        longest_text=self.staticText3.GetLabel()
        textSize = self.staticText3.GetTextExtent(longest_text)
        texts = (self.staticText1, self.staticText2,
                 self.staticText3, self.staticText4)        
        for text in texts:
            text.SetMinSize((textSize[0]+3,-1))
        
        # now set the sizer properly
        self.SetSizerAndFit(self.boxSizer1)
        
        self.engine = engine
        self.view = view
        # Bind enter event using acceleratorTable
        wxID_FINDRETURN = wx.NewId()
        self.Bind(wx.EVT_MENU, self.OnFindtxtTextEnter, id=wxID_FINDRETURN)
        self.findTxt.SetAcceleratorTable(wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_RETURN, wxID_FINDRETURN)]))
        wxID_REPLACERETURN = wx.NewId()
        self.Bind(wx.EVT_MENU, self.OnReplacetxtTextEnter, id=wxID_REPLACERETURN)
        self.replaceTxt.SetAcceleratorTable(wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_RETURN, wxID_FINDRETURN)]))
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
                self.replaceTxt.Enable(False)
                self.findBtn.Enable(False)
                self.replaceBtn.Enable(False)
                self.replaceAllBtn.Enable(False)
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

        wxID_DOFIND = wx.NewId()
        wxID_DOREPLACE = wx.NewId()
        self.Bind(wx.EVT_MENU, self.OnFindbtnButton, id=wxID_DOFIND)
        self.Bind(wx.EVT_MENU, self.OnReplacebtnButton, id=wxID_DOREPLACE)
        # bug in wxPython, esc key not working
        self.SetAcceleratorTable(
              wx.AcceleratorTable([ Utils.setupCloseWindowOnEscape(self),
                                  (wx.ACCEL_NORMAL, wx.WXK_F3, wxID_DOFIND),
                                  (wx.ACCEL_CTRL, wx.WXK_F3, wxID_DOREPLACE),
                                  ]))

        # workaround for above bug, bind key evt to all ctrls
        for ctrl in (self.findTxt, self.replaceTxt, self.directionRB, self.scopeRB,
                     self.optionsSB, self.caseSensitiveCB, self.wholeWordsCB,
                     self.wildcardCB, self.regExprCB, self.wrapCB,
                     self.closeOnFoundCB, self.findBtn, self.findAllBtn,
                     self.replaceBtn, self.replaceAllBtn, self.cancelBtn):
            ctrl.Bind(wx.EVT_KEY_UP, self.OnFindtxtChar)

        if not bModeFindReplace:
            self.findAllBtn.Enable(False)
            self.findBtn.Enable(False)
            self.replaceBtn.Enable(False)
            self.replaceAllBtn.Enable(False)
            self.engine.closeOnFound = True
            self.closeOnFoundCB.SetValue(engine.closeOnFound)
            self.directionRB.Enable(False)
            self.scopeRB.Enable(False)
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

    def OnFindbtnButton(self, event):
        self.find()

    def find(self):
        try:
            pattern = self.findTxt.GetValue()
            self.engine.findInSource(self.view, pattern)
            self.setComboBoxes('find')
            if self.engine.closeOnFound and not self.replaceTxt.GetValue():
                self.EndModal(wx.ID_OK)
            else:
                self._checkSelectionDlgOverlap()
        except FindError, err:
            wx.MessageBox(str(err), _('Find/Replace'), wx.OK | wx.ICON_INFORMATION, self)

    def findAll(self):
        pattern = self.findTxt.GetValue()
        if self.view.viewName == "Package":
            self.engine.findAllInPackage(self.view, pattern)
        elif self.view.viewName == "Application":
            self.engine.findAllInApp(self.view, pattern)
        else:
            self.engine.findAllInSource(self.view, pattern)
        self.setComboBoxes('find')
        self.EndModal(wx.ID_OK)

    def replace(self):
        try:
            pattern = self.findTxt.GetValue()
            replacement = self.replaceTxt.GetValue()
            self.engine.replaceInSource(self.view, pattern, replacement)
            self._checkSelectionDlgOverlap()
            self.setComboBoxes('replace')
        except FindError, err:
            wx.MessageBox(str(err), _('Find/Replace'), wx.OK | wx.ICON_INFORMATION, self)

    def replaceAll(self):
        pattern = self.findTxt.GetValue()
        replacement = self.replaceTxt.GetValue()
        self.engine.replaceAllInSource(self.view, pattern, replacement)
        self.setComboBoxes('replace')
        self.EndModal(wx.ID_OK)

    def findInFiles(self):
        names = []
        pattern = self.findTxt.GetValue()
        bRecursive = self.chkRecursiveSearch.GetValue()
        file_filter = string.split(self.cmbFileFilter.GetValue(), ';')
        folder = [self.cmbFolder.GetValue()]
        self.engine.addFolder(folder[0])
        self.engine.addSuffix(self.cmbFileFilter.GetValue())
        dlg = wx.ProgressDialog(_("Building file list from directory '%s'") % (folder[0]),
                       _('Searching...'), 100, self.view,
                        wx.PD_CAN_ABORT | wx.PD_APP_MODAL | wx.PD_AUTO_HIDE)
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
            self.EndModal(wx.ID_OK)


    def _validate(self, what):
        ##Doesn't matter how we want to search we need smth to search to.
        if not self.findTxt.GetValue():
            wx.MessageBox(_('There is nothing to find.'), _('Boa - Find/Replace'))
            return False
        if what in ['find', 'findAll']:
            pass
        elif what in ['replace', 'replaceAll']:
            if not self.replaceTxt.GetValue():
                wx.MessageBox(_('There is nothing to replace with.'), _('Boa - Find/Replace'))
                return False
        elif what == 'findInFiles':
            if not os.path.isdir( self.cmbFolder.GetValue() ):
                wx.MessageBox(_('The folder you entered is not valid folder.'), _('Boa - Find/Replace'))
                return False
        else:
            pass
        return True

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
        self.engine.wrap = int(self.wrapCB.GetValue())

    def OnCloseonfoundcbCheckbox(self, event):
        self.engine.closeOnFound = int(self.closeOnFoundCB.GetValue())

    _fudgeOffset = 6
    def _checkSelectionDlgOverlap(self):
        if self.view.viewName not in ('Package', 'Application'):
            selStart, selEnd = self.view.GetSelection()
            selStartLnNo = self.view.LineFromPosition(selStart)
            if selStart != selEnd and selStartLnNo == self.view.LineFromPosition(selEnd):
                chrHeight = self.view.GetCharHeight()
                selPos = self.view.ClientToScreen(self.view.PointFromPosition(selStart))
                selSize = wx.Size(self.view.ClientToScreen(
                      self.view.PointFromPosition(selEnd)).x - selPos.x, chrHeight)
                dlgPos, dlgSize = self.GetPosition(), self.GetSize()
                r = wx.IntersectRect(wx.Rect(selPos.x, selPos.y, selSize.x, selSize.y),
                                    wx.Rect(dlgPos.x, dlgPos.y, dlgSize.x, dlgSize.y))
                if r is not None:
                    # simply moves dialog above or below selection
                    # sometimes rather moving it to the sides would be more
                    # appropriate
                    mcp = self.ScreenToClient(wx.GetMousePosition())
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
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.Close()
        event.Skip()

    def OnBuildInFind(self, event):
        dlg = wx.SingleChoiceDialog(self, _('Find'), _('Build in finds'), self._mapBuildInFinds.keys())
        try:
            if dlg.ShowModal() == wx.ID_OK:
                selected = dlg.GetStringSelection()
                self.findTxt.SetValue(self._mapBuildInFinds[selected])
                self.regExprCB.SetValue(1)
                self.OnRegexprcbCheckbox(None)
        finally:
            dlg.Destroy()

        self.findBtn.SetFocus()


    def browseForDir(self, strFromFolder=''):
        strPath = ''
        dlgDirDialog = wx.DirDialog(self)
        dlgDirDialog.SetPath( strFromFolder )
        if dlgDirDialog.ShowModal() == wx.ID_OK:
            strPath = dlgDirDialog.GetPath()
        dlgDirDialog.Destroy()
        return strPath

    def OnBrowse(self, event):
        strNewPath = self.browseForDir()
        if strNewPath:
            self.cmbFolder.SetValue(strNewPath)

        self.findBtn.SetFocus()


if __name__ == '__main__':
    app = wx.PySimpleApp()
    testText = '''Find replace dialog test



Boa boa keyboard        bOa boa keyboard        boA boa keyboard
quick brown fox jumps over the lazy dog
\n\n\n\n\n\n\n\n
Boa Constructor         Boa Constructor         Boa Constructor
'''
    # Create a simple test environment (RB)

    def createFramedView(caption, View, model, parent=None, size=wx.DefaultSize):
        f = wx.Frame(parent, -1, caption, size=size)
        v = View(f, model)
        f.Center()
        f.Show(1)
        return f, v

    class PseudoStatusBar:
        def setHint(self, hint, htype='Info'): wx.LogMessage('Editor hint: %s'%hint)
    class PseudoEditor:
        def __init__(self): self.statusBar = PseudoStatusBar()
        def addBrowseMarker(self, lineNo): pass
        def addNewView(self, name, View): return createFramedView(name, View, self.model, self.parent, (400, 200))[1]
        def Disconnect(self, id): pass
        def setStatus(self, hint, htype='Info', ringBell=False): wx.LogMessage('Editor hint: %s'%hint)

    e = PseudoEditor()
    from Models.PythonEditorModels import ModuleModel
    m = ModuleModel(testText, 'test.py', e, True)
    from Views.PySourceView import PythonSourceView
    f, v = createFramedView('Find/Replace Dlg Tester (Cancel to quit)', PythonSourceView, m, size=(600, 400))
    v.refreshCtrl()
    e.model, e.parent = m, f
    from FindReplaceEngine import FindReplaceEngine
    finder = FindReplaceEngine()
    finder.addFind('boa')
    res = 0
    while res != wx.ID_CANCEL:
        dlg = FindReplaceDlg(f, finder, v)
        try: res = dlg.ShowModal()
        finally: dlg.Destroy()
        if res != wx.ID_CANCEL: wx.LogMessage('Reopening dialog for testing')
