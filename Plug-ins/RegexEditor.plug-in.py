#Boa:Frame:RegexEditorFrm

import re

from wxPython.wx import *
from wxPython.lib.anchors import LayoutAnchors
from wxPython.stc import *

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
] = map(lambda _init_ctrls: wxNewId(), range(14))

class RegexEditorFrm(wxFrame, Utils.FrameRestorerMixin):
    def _init_coll_statusBar_Fields(self, parent):
        # generated method, don't edit
        parent.SetFieldsCount(2)

        parent.SetStatusText(i=0, text='')
        parent.SetStatusText(i=1, text='')

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
        wxFrame.__init__(self, id=wxID_REGEXEDITORFRM, name='RegexEditorFrm',
              parent=prnt, pos=wxPoint(562, 278), size=wxSize(503, 509),
              style=wxDEFAULT_FRAME_STYLE, title='Regex Editor')
        self._init_utils()
        self.SetClientSize(wxSize(495, 482))

        self.panel = wxPanel(id=wxID_REGEXEDITORFRMPANEL, name='panel',
              parent=self, pos=wxPoint(0, 0), size=wxSize(495, 462),
              style=wxTAB_TRAVERSAL)
        self.panel.SetAutoLayout(True)

        self.staticText1 = wxStaticText(id=wxID_REGEXEDITORFRMSTATICTEXT1,
              label='Regular Expression', name='staticText1', parent=self.panel,
              pos=wxPoint(8, 8), size=wxSize(91, 13), style=0)

        self.txtRegex = wxTextCtrl(id=wxID_REGEXEDITORFRMTXTREGEX,
              name='txtRegex', parent=self.panel, pos=wxPoint(8, 32),
              size=wxSize(352, 120), style=wxTE_MULTILINE, value='')
        self.txtRegex.SetConstraints(LayoutAnchors(self.txtRegex, True, True,
              True, False))
        EVT_TEXT(self.txtRegex, wxID_REGEXEDITORFRMTXTREGEX, self.OnUpdate)

        self.staticText2 = wxStaticText(id=wxID_REGEXEDITORFRMSTATICTEXT2,
              label='String', name='staticText2', parent=self.panel,
              pos=wxPoint(8, 160), size=wxSize(27, 13), style=0)

        self.txtString = wxTextCtrl(id=wxID_REGEXEDITORFRMTXTSTRING,
              name='txtString', parent=self.panel, pos=wxPoint(8, 184),
              size=wxSize(351, 112), style=wxTE_MULTILINE, value='')
        self.txtString.SetConstraints(LayoutAnchors(self.txtString, True, True,
              True, False))
        EVT_TEXT(self.txtString, wxID_REGEXEDITORFRMTXTSTRING, self.OnUpdate)

        self.staticText3 = wxStaticText(id=wxID_REGEXEDITORFRMSTATICTEXT3,
              label='Match', name='staticText3', parent=self.panel,
              pos=wxPoint(8, 304), size=wxSize(30, 13), style=0)

        self.clbFlags = wxCheckListBox(choices=['IGNORECASE', 'LOCALE',
              'MULTILINE', 'DOTALL', 'UNICODE', 'VERBOSE'],
              id=wxID_REGEXEDITORFRMCLBFLAGS, name='clbFlags',
              parent=self.panel, pos=wxPoint(375, 32), size=wxSize(112, 120),
              style=0, validator=wxDefaultValidator)
        self.clbFlags.SetConstraints(LayoutAnchors(self.clbFlags, False, True,
              True, False))
        EVT_CHECKLISTBOX(self.clbFlags, wxID_REGEXEDITORFRMCLBFLAGS,
              self.OnUpdate)

        self.staticText4 = wxStaticText(id=wxID_REGEXEDITORFRMSTATICTEXT4,
              label='Groups', name='staticText4', parent=self.panel,
              pos=wxPoint(256, 304), size=wxSize(34, 13), style=0)

        self.rbAction = wxRadioBox(choices=['Search', 'Match'],
              id=wxID_REGEXEDITORFRMRBACTION, label='Action', majorDimension=1,
              name='rbAction', parent=self.panel, point=wxPoint(376, 176),
              size=wxSize(112, 120), style=wxRA_SPECIFY_COLS,
              validator=wxDefaultValidator)
        self.rbAction.SetConstraints(LayoutAnchors(self.rbAction, False, True,
              True, False))
        EVT_RADIOBOX(self.rbAction, wxID_REGEXEDITORFRMRBACTION, self.OnUpdate)

        self.statusBar = wxStatusBar(id=wxID_REGEXEDITORFRMSTATUSBAR,
              name='statusBar', parent=self, style=wxST_SIZEGRIP)
        self.statusBar.SetPosition(wxPoint(0, 462))
        self.statusBar.SetSize(wxSize(495, 20))
        self._init_coll_statusBar_Fields(self.statusBar)
        self.SetStatusBar(self.statusBar)

        self.staticText5 = wxStaticText(id=wxID_REGEXEDITORFRMSTATICTEXT5,
              label='Flags', name='staticText5', parent=self.panel,
              pos=wxPoint(378, 8), size=wxSize(25, 13), style=0)
        self.staticText5.SetConstraints(LayoutAnchors(self.staticText5, False,
              True, True, False))

        self.txtMatch = wxTextCtrl(id=wxID_REGEXEDITORFRMTXTMATCH,
              name='txtMatch', parent=self.panel, pos=wxPoint(8, 328),
              size=wxSize(232, 128), style=wxTE_MULTILINE, value='')
        self.txtMatch.SetConstraints(LayoutAnchors(self.txtMatch, True, True,
              False, True))

        self.lcGroups = wxListCtrl(id=wxID_REGEXEDITORFRMLCGROUPS,
              name='lcGroups', parent=self.panel, pos=wxPoint(256, 328),
              size=wxSize(231, 128), style=wxLC_REPORT,
              validator=wxDefaultValidator)
        self.lcGroups.SetConstraints(LayoutAnchors(self.lcGroups, True, True,
              True, True))
        self._init_coll_lcGroups_Columns(self.lcGroups)

    def __init__(self, parent):
        self._init_ctrls(parent)
        
        self.SetIcon(Preferences.IS.load('Images/Icons/Bevel.ico'))
        
        self.statusImages = \
              [wxArtProvider_GetBitmap(artId, wxART_TOOLBAR, (16, 16))
               for artId in (wxART_ERROR, wxART_INFORMATION)]

        rect = self.statusBar.GetFieldRect(0)
        self.sbImage = wxStaticBitmap(self.statusBar, -1, self.statusImages[0],
            (rect.x+1, rect.y+1), (16, 16))

        self.winConfOption = 'regexeditor'
        self.loadDims()

    def setDefaultDimensions(self):
        self.Center(wxBOTH)

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
                self.lcGroups.SetStringItem(idx-1, 2, grp)
        
    
    def setStatus(self, mo):
        if mo:
            self.statusBar.SetStatusText('Match', 1)
            self.sbImage.SetBitmap(self.statusImages[1])
        else:
            self.statusBar.SetStatusText('Failed to match', 1)
            self.sbImage.SetBitmap(self.statusImages[0])


if __name__ == '__main__':
    app = wxPySimpleApp()
    wxInitAllImageHandlers()
    frame = create(None)
    frame.Show()
    app.MainLoop()


#-------------------------------------------------------------------------------

def openRegexEditor(editor):
    frame = createRegexEditor(editor)
    frame.Show()
    
from Models import EditorHelper
EditorHelper.editorToolsReg.append( ('Regex editor', openRegexEditor) )
        