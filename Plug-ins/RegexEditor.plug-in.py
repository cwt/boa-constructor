#Boa:Frame:RegexEditorFrm

import re

import wx
from wx.lib.anchors import LayoutAnchors
import wx.stc

import Preferences, Utils

reFlags = {'IGNORECASE': re.IGNORECASE, 'LOCALE': re.LOCALE,
           'MULTILINE': re.MULTILINE, 'DOTALL': re.DOTALL,
           'UNICODE': re.UNICODE, 'VERBOSE': re.VERBOSE}

def createRegexEditor(parent):
    return RegexEditorFrm(parent)

[wxID_REGEXEDITORFRM, wxID_REGEXEDITORFRMCLBFLAGS,
 wxID_REGEXEDITORFRMLCGROUPS, wxID_REGEXEDITORFRMPANEL,
 wxID_REGEXEDITORFRMRBACTION, wxID_REGEXEDITORFRMSTATICTEXT1,
 wxID_REGEXEDITORFRMSTATICTEXT2, wxID_REGEXEDITORFRMSTATICTEXT3,
 wxID_REGEXEDITORFRMSTATICTEXT4, wxID_REGEXEDITORFRMSTATICTEXT5,
 wxID_REGEXEDITORFRMSTATUSBAR, wxID_REGEXEDITORFRMTXTMATCH,
 wxID_REGEXEDITORFRMTXTREGEX, wxID_REGEXEDITORFRMTXTSTRING,
] = [wx.NewId() for _init_ctrls in range(14)]

class RegexEditorFrm(wx.Frame, Utils.FrameRestorerMixin):
    def _init_coll_statusBar_Fields(self, parent):
        # generated method, don't edit
        parent.SetFieldsCount(2)

        parent.SetStatusText(number=0, text='')
        parent.SetStatusText(number=1, text='')

        parent.SetStatusWidths([16, -1])

    def _init_coll_lcGroups_Columns(self, parent):
        # generated method, don't edit

        parent.InsertColumn(col=0, format=wxLIST_FORMAT_LEFT, heading='#',
              width=35)
        parent.InsertColumn(col=1, format=wxLIST_FORMAT_LEFT, heading='Name',
              width=75)
        parent.InsertColumn(col=2, format=wxLIST_FORMAT_LEFT, heading='Value',
              width=117)

    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_REGEXEDITORFRM, name='RegexEditorFrm',
              parent=prnt, pos=wx.Point(562, 278), size=wx.Size(503, 509),
              style=wx.DEFAULT_FRAME_STYLE, title='Regex Editor')
        self._init_utils()
        self.SetClientSize(wx.Size(495, 482))

        self.panel = wx.Panel(id=wxID_REGEXEDITORFRMPANEL, name='panel',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(495, 462),
              style=wx.TAB_TRAVERSAL)
        self.panel.SetAutoLayout(True)

        self.staticText1 = wx.StaticText(id=wxID_REGEXEDITORFRMSTATICTEXT1,
              label='Regular Expression', name='staticText1', parent=self.panel,
              pos=wx.Point(8, 8), size=wx.Size(91, 13), style=0)

        self.txtRegex = wx.TextCtrl(id=wxID_REGEXEDITORFRMTXTREGEX,
              name='txtRegex', parent=self.panel, pos=wx.Point(8, 32),
              size=wx.Size(352, 120), style=wx.TE_MULTILINE, value='')
        self.txtRegex.SetConstraints(LayoutAnchors(self.txtRegex, True, True,
              True, False))
        self.txtRegex.Bind(wx.EVT_TEXT, self.OnUpdate, id=wxID_REGEXEDITORFRMTXTREGEX)

        self.staticText2 = wx.StaticText(id=wxID_REGEXEDITORFRMSTATICTEXT2,
              label='String', name='staticText2', parent=self.panel,
              pos=wx.Point(8, 160), size=wx.Size(27, 13), style=0)

        self.txtString = wx.TextCtrl(id=wxID_REGEXEDITORFRMTXTSTRING,
              name='txtString', parent=self.panel, pos=wx.Point(8, 184),
              size=wx.Size(351, 112), style=wx.TE_MULTILINE, value='')
        self.txtString.SetConstraints(LayoutAnchors(self.txtString, True, True,
              True, False))
        self.txtString.Bind(wx.EVT_TEXT, self.OnUpdate, id=wxID_REGEXEDITORFRMTXTSTRING)

        self.staticText3 = wx.StaticText(id=wxID_REGEXEDITORFRMSTATICTEXT3,
              label='Match', name='staticText3', parent=self.panel,
              pos=wx.Point(8, 304), size=wx.Size(30, 13), style=0)

        self.clbFlags = wx.CheckListBox(choices=['IGNORECASE', 'LOCALE',
              'MULTILINE', 'DOTALL', 'UNICODE', 'VERBOSE'],
              id=wxID_REGEXEDITORFRMCLBFLAGS, name='clbFlags',
              parent=self.panel, pos=wx.Point(375, 32), size=wx.Size(112, 120),
              style=0)
        self.clbFlags.SetConstraints(LayoutAnchors(self.clbFlags, False, True,
              True, False))
        self.clbFlags.Bind(wx.EVT_CHECKLISTBOX, self.OnUpdate, id=wxID_REGEXEDITORFRMCLBFLAGS)

        self.staticText4 = wx.StaticText(id=wxID_REGEXEDITORFRMSTATICTEXT4,
              label='Groups', name='staticText4', parent=self.panel,
              pos=wx.Point(256, 304), size=wx.Size(34, 13), style=0)

        self.rbAction = wx.RadioBox(choices=['Search', 'Match'],
              id=wxID_REGEXEDITORFRMRBACTION, label='Action', majorDimension=1,
              name='rbAction', parent=self.panel, point=wx.Point(376, 176),
              size=wx.Size(112, 120), style=wx.RA_SPECIFY_COLS)
        self.rbAction.SetConstraints(LayoutAnchors(self.rbAction, False, True,
              True, False))
        self.rbAction.Bind(wx.EVT_RADIOBOX, self.OnUpdate, id=wxID_REGEXEDITORFRMRBACTION)

        self.statusBar = wx.StatusBar(id=wxID_REGEXEDITORFRMSTATUSBAR,
              name='statusBar', parent=self, style=wx.ST_SIZEGRIP)
        self.statusBar.SetPosition(wx.Point(0, 462))
        self.statusBar.SetSize(wx.Size(495, 20))
        self._init_coll_statusBar_Fields(self.statusBar)
        self.SetStatusBar(self.statusBar)

        self.staticText5 = wx.StaticText(id=wxID_REGEXEDITORFRMSTATICTEXT5,
              label='Flags', name='staticText5', parent=self.panel,
              pos=wx.Point(378, 8), size=wx.Size(25, 13), style=0)
        self.staticText5.SetConstraints(LayoutAnchors(self.staticText5, False,
              True, True, False))

        self.txtMatch = wx.TextCtrl(id=wxID_REGEXEDITORFRMTXTMATCH,
              name='txtMatch', parent=self.panel, pos=wx.Point(8, 328),
              size=wx.Size(232, 128), style=wx.TE_MULTILINE, value='')
        self.txtMatch.SetConstraints(LayoutAnchors(self.txtMatch, True, True,
              False, True))

        self.lcGroups = wx.ListCtrl(id=wxID_REGEXEDITORFRMLCGROUPS,
              name='lcGroups', parent=self.panel, pos=wx.Point(256, 328),
              size=wx.Size(231, 128), style=wx.LC_REPORT,
              validator=wxDefaultValidator)
        self.lcGroups.SetConstraints(LayoutAnchors(self.lcGroups, True, True,
              True, True))
        self._init_coll_lcGroups_Columns(self.lcGroups)

    def __init__(self, parent):
        self._init_ctrls(parent)

        self.SetIcon(Preferences.IS.load('Images/Icons/Bevel.ico'))

        self.statusImages = \
              [wx.ArtProvider.GetBitmap(artId, wx.ART_TOOLBAR, (16, 16))
               for artId in (wx.ART_ERROR, wx.ART_INFORMATION)]

        rect = self.statusBar.GetFieldRect(0)
        self.sbImage = wx.StaticBitmap(self.statusBar, -1, self.statusImages[0],
            (rect.x+1, rect.y+1), (16, 16))

        self.winConfOption = 'regexeditor'
        self.loadDims()

    def setDefaultDimensions(self):
        self.Center(wx.BOTH)

    def OnUpdate(self, event):
        string = self.txtString.GetValue()
        regex = self.txtRegex.GetValue()

        flags = 0
        for idx in range(self.clbFlags.GetCount()):
            if self.clbFlags.IsChecked(idx):
                flags |= reFlags[self.clbFlags.GetString(idx)]

        try:
            ro = re.compile(regex, flags)
        except Exception, err:
            self.statusBar.SetStatusText('Error: %s: %s'%(err.__class__, err), 1)
            self.sbImage.SetBitmap(self.statusImages[0])
            return

        if self.rbAction.GetSelection():
            mo = ro.match(string)
        else:
            mo = ro.search(string)

        self.setStatus(mo)
        self.lcGroups.DeleteAllItems()
        if not mo:
            self.txtMatch.SetValue('')
        else:
            s, e = mo.span()
            self.txtMatch.SetValue(string[s:e])

            namedGrpVals = {}
            for name, val in mo.groupdict().items():
                namedGrpVals[val] = name

            grps = []
            for idx, grp in zip(range(1, len(mo.groups())+1), mo.groups()):
                name = namedGrpVals.get(grp, '')
                self.lcGroups.InsertStringItem(idx-1, str(idx))
                self.lcGroups.SetStringItem(idx-1, 1, name)
                self.lcGroups.SetStringItem(idx-1, 2, str(grp))


    def setStatus(self, mo):
        if mo:
            self.statusBar.SetStatusText('Match', 1)
            self.sbImage.SetBitmap(self.statusImages[1])
        else:
            self.statusBar.SetStatusText('Failed to match', 1)
            self.sbImage.SetBitmap(self.statusImages[0])


#-------------------------------------------------------------------------------

def openRegexEditor(editor):
    frame = createRegexEditor(editor)
    frame.Show()

from Models import EditorHelper
EditorHelper.editorToolsReg.append( ('Regex editor', openRegexEditor) )
