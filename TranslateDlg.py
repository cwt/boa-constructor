#Boa:Dialog:wxDialog1

from wxPython.wx import *
from wxPython.lib.anchors import LayoutAnchors

from ExternalLib import babeliser
from Preferences import IS

def create(parent, phrase):
    return wxDialog1(parent, phrase)
#EVT_INIT_DIALOG
# * Für validating the output file catalog.xml should likewise be used a Perl module


[wxID_WXDIALOG1, wxID_WXDIALOG1CANCELBTN, wxID_WXDIALOG1CHOICE2, wxID_WXDIALOG1CHOICE3, wxID_WXDIALOG1OKBTN, wxID_WXDIALOG1STATICBITMAP1, wxID_WXDIALOG1STATICTEXT1, wxID_WXDIALOG1STATICTEXT2, wxID_WXDIALOG1STATICTEXT3, wxID_WXDIALOG1STATICTEXT4, wxID_WXDIALOG1TEXTCTRL1] = map(lambda _init_ctrls: wxNewId(), range(11))

class wxDialog1(wxDialog):
    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxDialog.__init__(self, id = wxID_WXDIALOG1, name = '', parent = prnt, pos = wxPoint(392, 231), size = wxSize(344, 166), style = wxDEFAULT_DIALOG_STYLE, title = 'Translate')
        self._init_utils()
        self.SetAutoLayout(true)

        self.staticText3 = wxStaticText(id = wxID_WXDIALOG1STATICTEXT3, label = 'To:', name = 'staticText3', parent = self, pos = wxPoint(8, 77), size = wxSize(16, 13), style = 0)

        self.textCtrl1 = wxTextCtrl(id = wxID_WXDIALOG1TEXTCTRL1, name = 'textCtrl1', parent = self, pos = wxPoint(48, 8), size = wxSize(278, 21), style = 0, value = self.phrase)
        self.textCtrl1.SetConstraints(LayoutAnchors(self.textCtrl1, true, true, true, false))

        self.staticText1 = wxStaticText(id = wxID_WXDIALOG1STATICTEXT1, label = 'Phrase:', name = 'staticText1', parent = self, pos = wxPoint(8, 13), size = wxSize(36, 13), style = 0)

        self.staticText2 = wxStaticText(id = wxID_WXDIALOG1STATICTEXT2, label = 'From:', name = 'staticText2', parent = self, pos = wxPoint(8, 45), size = wxSize(26, 13), style = 0)

        self.choice2 = wxChoice(choices = self.languages, id = wxID_WXDIALOG1CHOICE2, name = 'choice2', parent = self, pos = wxPoint(48, 40), size = wxSize(278, 21), style = 0, validator = wxDefaultValidator)
        self.choice2.SetSelection(0)
        self.choice2.SetConstraints(LayoutAnchors(self.choice2, true, true, true, false))

        self.choice3 = wxChoice(choices = self.languages, id = wxID_WXDIALOG1CHOICE3, name = 'choice3', parent = self, pos = wxPoint(48, 72), size = wxSize(278, 21), style = 0, validator = wxDefaultValidator)
        self.choice3.SetSelection(0)
        self.choice3.SetConstraints(LayoutAnchors(self.choice3, true, true, true, false))

        self.okBtn = wxButton(id = wxID_WXDIALOG1OKBTN, label = 'OK', name = 'okBtn', parent = self, pos = wxPoint(171, 104), size = wxSize(75, 23), style = 0)
        self.okBtn.SetConstraints(LayoutAnchors(self.okBtn, false, false, true, true))
        EVT_BUTTON(self.okBtn, wxID_WXDIALOG1OKBTN, self.OnButton1Button)

        self.cancelBtn = wxButton(id = wxID_WXDIALOG1CANCELBTN, label = 'Cancel', name = 'cancelBtn', parent = self, pos = wxPoint(251, 104), size = wxSize(75, 23), style = 0)
        self.cancelBtn.SetConstraints(LayoutAnchors(self.cancelBtn, false, false, true, true))
        EVT_BUTTON(self.cancelBtn, wxID_WXDIALOG1CANCELBTN, self.OnCancelbtnButton)

        self.staticText4 = wxStaticText(id = wxID_WXDIALOG1STATICTEXT4, label = 'Thanks to BabelFish and Jonathan Feinberg', name = 'staticText4', parent = self, pos = wxPoint(8, 104), size = wxSize(118, 27), style = wxST_NO_AUTORESIZE)

        self.staticBitmap1 = wxStaticBitmap(bitmap = self.babelBmp, id = wxID_WXDIALOG1STATICBITMAP1, name = 'staticBitmap1', parent = self, pos = wxPoint(136, 104), size = wxSize(28, 20), style = 0)

    def __init__(self, parent, phrase, languages=babeliser.available_languages):
        self.phrase = 'I love a reigning knight.'
        self.phrase = phrase
        self.languages = ['English', 'German', 'Etc']
        self.languages = languages
        self.babelBmp = IS.load('Images/Views/bfish.gif')
        self._init_ctrls(parent)
        self.translated = [phrase]
        
    def OnButton1Button(self, event):
        if self.okBtn.GetLabel() == 'OK':
            self.SetTitle('Translating...')
            wxBeginBusyCursor()
            try:
                try:
                    self.translated = babeliser.babelize(self.textCtrl1.GetValue(), 
                                      self.choice2.GetStringSelection(), 
                                      self.choice3.GetStringSelection())
                    if len(self.translated) > 1:
                        self.textCtrl1.SetValue(self.translated[1])
                        self.okBtn.SetLabel('Replace')
                        self.SetTitle('Translated')
                except Exception, error:
                    self.SetTitle('Translation failed %s'%str(error))
            finally:
                wxEndBusyCursor()
        else:
            self.EndModal(wxOK)

    def OnCancelbtnButton(self, event):
        self.EndModal(wxCANCEL)

if __name__ == '__main__':
    wxInitAllImageHandlers()
    app = wxPySimpleApp()
    dlg = create(None, 'Amo un cavaliere di regno.')
    try:
        if dlg.ShowModal() == wxOK and len(dlg.translated) > 1:
            wxMessageBox(dlg.translated[1], 'Translation')
    finally:
        dlg.Destroy()