#Boa:Dialog:wxDialog1

from wxPython.wx import *

def create(parent):
    return wxDialog1(parent)

[wxID_WXDIALOG1STATICTEXT1, wxID_WXDIALOG1STATICTEXT2, wxID_WXDIALOG1BUTTON1, wxID_WXDIALOG1STATICBITMAP1, wxID_WXDIALOG1] = map(lambda _init_ctrls: wxNewId(), range(5))

class wxDialog1(wxDialog):
    def _init_utils(self): 
        pass

    def _init_ctrls(self, prnt): 
        wxDialog.__init__(self, size = wxSize(328, 379), id = wxID_WXDIALOG1, title = 'About Notebook', parent = prnt, name = '', style = wxDEFAULT_DIALOG_STYLE, pos = wxPoint(472, 330))
        self._init_utils()
        self.SetBackgroundColour(wxColour(255, 255, 255))

        self.staticText1 = wxStaticText(label = 'Note Book - Simple Text Editor', id = wxID_WXDIALOG1STATICTEXT1, parent = self, name = 'staticText1', size = wxSize(232, 32), style = wxALIGN_CENTRE, pos = wxPoint(48, 24))
        self.staticText1.SetFont(wxFont(12, 74, 90, 90, 0, 'MS Sans Serif'))
        self.staticText1.SetBackgroundColour(wxColour(255, 255, 255))

        self.staticText2 = wxStaticText(label = 'This is my first Boa Constructor Application', id = wxID_WXDIALOG1STATICTEXT2, parent = self, name = 'staticText2', size = wxSize(199, 13), style = wxALIGN_CENTRE, pos = wxPoint(56, 72))
        self.staticText2.SetBackgroundColour(wxColour(64, 128, 128))

        self.staticBitmap1 = wxStaticBitmap(bitmap = wxBitmap('D:\\dev\\test2\\BOA.bmp', wxBITMAP_TYPE_BMP), id = wxID_WXDIALOG1STATICBITMAP1, parent = self, name = 'staticBitmap1', size = wxSize(236, 157), style = 0, pos = wxPoint(48, 104))

        self.button1 = wxButton(label = 'button1', id = wxID_WXDIALOG1BUTTON1, parent = self, name = 'button1', size = wxSize(72, 24), style = 0, pos = wxPoint(120, 296))
        self.button1.SetTitle('Close')
        EVT_BUTTON(self.button1, wxID_WXDIALOG1BUTTON1, self.OnButton1Button)

    def __init__(self, parent): 
        self._init_ctrls(parent)
        bmp = wxBitmap('Boa.bmp',  wxBITMAP_TYPE_BMP)
        self.staticBitmap1.SetBitmap(bmp)

    def OnButton1Button(self, event):
        self.Close()
