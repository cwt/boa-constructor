#Boa:Dialog:MaskedEditFormatCodesDlg

from wxPython.wx import *
from wxPython.lib.anchors import LayoutAnchors

formatCodes = [
 ('_', 'Allow spaces'),
 ('!', 'Force upper'),
 ('^', 'Force lower'),
 ('R', 'Right-align field(s)'),
 ('r', 'Right-insert in field(s) (implies R)'),
 ('<', 'Stay in field until explicit navigation out of it'),
 ('>', 'Allow insert/delete within partially filled fields'),
 (',', 'Allow comma to be typed as grouping character; auto-group/regroup digits in\ninteger fields (if result fits) when leaving such a field.'),
 ('-', 'Prepend and reserve leading space for sign to mask and allow signed values (negative #s shown in red by default)'),
 ('0', 'integer fields get leading zeros'),
 ('D', 'Date[/time] field'),
 ('T', 'Time field'),
 ('F', 'Auto-Fit: the control calulates its size from the length of the template mask'),
 ('V', 'Validate entered chars against ValidRegex, blocking invalid characters'),
 ('S', 'select entire field when navigating to new field'),
]

[wxID_MASKEDEDITFORMATCODESDLG, wxID_MASKEDEDITFORMATCODESDLGBTNCANCEL, 
 wxID_MASKEDEDITFORMATCODESDLGBTNOK, 
 wxID_MASKEDEDITFORMATCODESDLGCLBFORMATCODES, 
 wxID_MASKEDEDITFORMATCODESDLGSTATICTEXT1, 
 wxID_MASKEDEDITFORMATCODESDLGTCFORMATCODEPROPVAL, 
] = map(lambda _init_ctrls: wxNewId(), range(6))

class MaskedEditFormatCodesDlg(wxDialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_MASKEDEDITFORMATCODESDLG,
              name='MaskedEditFormatCodesDlg', parent=prnt, pos=wxPoint(433,
              218), size=wxSize(436, 399),
              style=wxRESIZE_BORDER | wxDEFAULT_DIALOG_STYLE,
              title='Masked Edit - Format Codes')
        self.SetClientSize(wxSize(428, 372))
        self.SetAutoLayout(True)
        self.Center(wxBOTH)

        self.clbFormatCodes = wxCheckListBox(choices=[],
              id=wxID_MASKEDEDITFORMATCODESDLGCLBFORMATCODES,
              name='clbFormatCodes', parent=self, pos=wxPoint(8, 33),
              size=wxSize(413, 258), style=wxLB_HSCROLL | wxLB_SINGLE,
              validator=wxDefaultValidator)
        self.clbFormatCodes.SetConstraints(LayoutAnchors(self.clbFormatCodes,
              True, True, True, True))
        EVT_CHECKLISTBOX(self.clbFormatCodes,
              wxID_MASKEDEDITFORMATCODESDLGCLBFORMATCODES,
              self.OnClbformatcodesChecklistbox)

        self.tcFormatCodePropVal = wxTextCtrl(id=wxID_MASKEDEDITFORMATCODESDLGTCFORMATCODEPROPVAL,
              name='tcFormatCodePropVal', parent=self, pos=wxPoint(8, 299),
              size=wxSize(413, 25), style=0, value=self.formatCode)
        self.tcFormatCodePropVal.SetConstraints(LayoutAnchors(self.tcFormatCodePropVal,
              True, False, True, True))

        self.btnOK = wxButton(id=wxID_OK, label='OK', name='btnOK', parent=self,
              pos=wxPoint(261, 340), size=wxSize(75, 23), style=0)
        self.btnOK.SetConstraints(LayoutAnchors(self.btnOK, False, False, True,
              True))

        self.btnCancel = wxButton(id=wxID_CANCEL, label='Cancel',
              name='btnCancel', parent=self, pos=wxPoint(346, 340),
              size=wxSize(75, 23), style=0)
        self.btnCancel.SetConstraints(LayoutAnchors(self.btnCancel, False,
              False, True, True))

        self.staticText1 = wxStaticText(id=wxID_MASKEDEDITFORMATCODESDLGSTATICTEXT1,
              label='A string of formatting codes that modify behavior of the control.',
              name='staticText1', parent=self, pos=wxPoint(8, 5),
              size=wxSize(409, 24), style=wxNO_BORDER | wxST_NO_AUTORESIZE)
        self.staticText1.SetConstraints(LayoutAnchors(self.staticText1, True,
              True, True, False))

    def __init__(self, parent, formatCode=''):
        self.formatCode = ''
        self.formatCode = formatCode
        
        self._init_ctrls(parent)

        if wxPlatform == '__WXGTK__': fontSize = 13
        else:                         fontSize = 9

        self.clbFormatCodes.SetFont(wxFont(fontSize, wxMODERN, wxNORMAL, wxBOLD))
        self.tcFormatCodePropVal.SetFont(wxFont(fontSize+1, wxMODERN, wxNORMAL, wxBOLD))
        
        for fc, desc in formatCodes:
            fmtCode = fc
            if len(fmtCode) < 4: 
                fmtCode = ' %s  '%fmtCode

            self.clbFormatCodes.Append('%s - %s'%(fmtCode, desc))
            if formatCode.find(fc) != -1:
                self.clbFormatCodes.Check(self.clbFormatCodes.GetCount()-1, true)

        self.rebuildFmtCodePropVal()

    def rebuildFmtCodePropVal(self):
        r = []
        for idx in range(self.clbFormatCodes.GetCount()):
            if self.clbFormatCodes.IsChecked(idx):
                r.append(formatCodes[idx][0])
                
        self.tcFormatCodePropVal.SetValue(''.join(r))
    
    def getFormatCode(self):
        return self.tcFormatCodePropVal.GetValue()

    def OnClbformatcodesChecklistbox(self, event):
        self.rebuildFmtCodePropVal()
            


if __name__ == '__main__':
    app = wxPySimpleApp()
    wxInitAllImageHandlers()
    dlg = MaskedEditFormatCodesDlg(None, 'F_,-')
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()
    app.MainLoop()
