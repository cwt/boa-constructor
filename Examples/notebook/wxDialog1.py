#Boa:Dialog:wxDialog1

from wxPython.wx import *

def create(parent):
    return wxDialog1(parent)

[wxID_WXDIALOG1, wxID_WXDIALOG1BUTTON1, wxID_WXDIALOG1STATICBITMAP1,
 wxID_WXDIALOG1STATICTEXT1, wxID_WXDIALOG1STATICTEXT2,
] = map(lambda _init_ctrls: wxNewId(), range(5))

class wxDialog1(wxDialog):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_WXDIALOG1, name='', parent=prnt,
              pos=wxPoint(472, 330), size=wxSize(328, 379),
              style=wxDEFAULT_DIALOG_STYLE, title='About Notebook')
        self._init_utils()
        self.SetBackgroundColour(wxColour(255, 255, 255))
        self.SetClientSize(wxSize(320, 352))

        self.staticText1 = wxStaticText(id=wxID_WXDIALOG1STATICTEXT1,
              label='Note Book - Simple Text Editor', name='staticText1',
              parent=self, pos=wxPoint(48, 24), size=wxSize(216, 20),
              style=wxALIGN_CENTRE)
        self.staticText1.SetFont(wxFont(12, 74, 90, 90, 0, 'MS Sans Serif'))
        self.staticText1.SetBackgroundColour(wxColour(255, 255, 255))

        self.staticText2 = wxStaticText(id=wxID_WXDIALOG1STATICTEXT2,
              label='This is my first Boa Constructor Application',
              name='staticText2', parent=self, pos=wxPoint(56, 72),
              size=wxSize(199, 13), style=wxALIGN_CENTRE)
        self.staticText2.SetBackgroundColour(wxColour(64, 128, 128))

        self.staticBitmap1 = wxStaticBitmap(bitmap=wxBitmap('Boa.jpg',
              wxBITMAP_TYPE_JPEG), id=wxID_WXDIALOG1STATICBITMAP1,
              name='staticBitmap1', parent=self, pos=wxPoint(48, 104),
              size=wxSize(236, 157), style=0)

        self.button1 = wxButton(id=wxID_WXDIALOG1BUTTON1, label='button1',
              name='button1', parent=self, pos=wxPoint(120, 296),
              size=wxSize(72, 24), style=0)
        self.button1.SetTitle('Close')
        EVT_BUTTON(self.button1, wxID_WXDIALOG1BUTTON1, self.OnButton1Button)

    def __init__(self, parent):
        self._init_ctrls(parent)

    def OnButton1Button(self, event):
        self.Close()
