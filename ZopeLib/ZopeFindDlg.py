#-----------------------------------------------------------------------------
# Name:        ZopeFindDlg.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2002
# RCS-ID:      $Id$
# Copyright:   (c) 2002 - 2003
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Dialog:ZopeFindDlg

from wxPython.wx import *

def create(parent):
    return ZopeFindDlg(parent)

[wxID_ZOPEFINDDLG, wxID_ZOPEFINDDLGBUTTON1, wxID_ZOPEFINDDLGBUTTON2,
 wxID_ZOPEFINDDLGMETATYPE, wxID_ZOPEFINDDLGOBJIDS, wxID_ZOPEFINDDLGRECURSE,
 wxID_ZOPEFINDDLGSEARCHTEXT, wxID_ZOPEFINDDLGSTATICTEXT1,
 wxID_ZOPEFINDDLGSTATICTEXT2, wxID_ZOPEFINDDLGSTATICTEXT3,
] = map(lambda _init_ctrls: wxNewId(), range(10))

class ZopeFindDlg(wxDialog):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_ZOPEFINDDLG, name='ZopeFindDlg',
              parent=prnt, pos=wxPoint(653, 438), size=wxSize(319, 188),
              style=wxDEFAULT_DIALOG_STYLE, title='Zope find dialog')
        self._init_utils()
        self.SetClientSize(wxSize(311, 161))
        self.Center(wxBOTH)

        self.staticText1 = wxStaticText(id=wxID_ZOPEFINDDLGSTATICTEXT1,
              label='Find objects of type:', name='staticText1', parent=self,
              pos=wxPoint(8, 8), size=wxSize(120, 16), style=0)

        self.metaType = wxChoice(choices=['All types'],
              id=wxID_ZOPEFINDDLGMETATYPE, name='metaType', parent=self,
              pos=wxPoint(136, 8), size=wxSize(168, 21), style=0,
              validator=wxDefaultValidator)
        self.metaType.SetSelection(0)
        self.metaType.Enable(false)

        self.staticText2 = wxStaticText(id=wxID_ZOPEFINDDLGSTATICTEXT2,
              label='with ids:\n(comma separated)', name='staticText2',
              parent=self, pos=wxPoint(8, 40), size=wxSize(120, 32), style=0)

        self.objIds = wxTextCtrl(id=wxID_ZOPEFINDDLGOBJIDS, name='objIds',
              parent=self, pos=wxPoint(136, 40), size=wxSize(168, 21), style=0,
              value='')

        self.staticText3 = wxStaticText(id=wxID_ZOPEFINDDLGSTATICTEXT3,
              label='containing:', name='staticText3', parent=self,
              pos=wxPoint(8, 72), size=wxSize(72, 16), style=0)

        self.searchText = wxTextCtrl(id=wxID_ZOPEFINDDLGSEARCHTEXT,
              name='searchText', parent=self, pos=wxPoint(136, 72),
              size=wxSize(168, 21), style=0, value='')

        self.button1 = wxButton(id=wxID_OK, label='Find', name='button1',
              parent=self, pos=wxPoint(144, 128), size=wxSize(75, 23), style=0)

        self.button2 = wxButton(id=wxID_CANCEL, label='Cancel', name='button2',
              parent=self, pos=wxPoint(228, 128), size=wxSize(76, 23), style=0)

        self.recurse = wxCheckBox(id=wxID_ZOPEFINDDLGRECURSE, label='recurse',
              name='recurse', parent=self, pos=wxPoint(8, 104), size=wxSize(73,
              13), style=0)
        self.recurse.SetValue(true)

    def __init__(self, parent):
        self._init_ctrls(parent)

        self.button1.SetFocus()
        self.objIds.SetFocus()


if __name__ == '__main__':
    app = wxPySimpleApp()
    wxInitAllImageHandlers()
    dlg = create(None)
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()
