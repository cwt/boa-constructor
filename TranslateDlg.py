#Boa:Dialog:TranslateDialog

from wxPython.wx import *
from wxPython.lib.anchors import LayoutAnchors

from ExternalLib import babeliser
import Preferences, Utils
from Preferences import IS

def create(parent, phrase):
    return TranslateDialog(parent, phrase)

[wxID_TRANSLATEDIALOG, wxID_TRANSLATEDIALOGCANCELBTN, wxID_TRANSLATEDIALOGCHOICE2, wxID_TRANSLATEDIALOGCHOICE3, wxID_TRANSLATEDIALOGOKBTN, wxID_TRANSLATEDIALOGSTATICBITMAP1, wxID_TRANSLATEDIALOGSTATICTEXT1, wxID_TRANSLATEDIALOGSTATICTEXT2, wxID_TRANSLATEDIALOGSTATICTEXT3, wxID_TRANSLATEDIALOGSTATICTEXT4, wxID_TRANSLATEDIALOGTEXTCTRL1] = map(lambda _init_ctrls: wxNewId(), range(11))

class TranslateDialog(wxDialog):
    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxDialog.__init__(self, id = wxID_TRANSLATEDIALOG, name = 'TranslateDialog', parent = prnt, pos = wxPoint(392, 231), size = wxSize(344, 166), style = wxDEFAULT_DIALOG_STYLE, title = 'Translate')
        self._init_utils()
        self.SetAutoLayout(true)
        self.SetClientSize(wxSize(336, 139))

        self.staticText3 = wxStaticText(id = wxID_TRANSLATEDIALOGSTATICTEXT3, label = 'To:', name = 'staticText3', parent = self, pos = wxPoint(8, 77), size = wxSize(16, 13), style = 0)

        self.textCtrl1 = wxTextCtrl(id = wxID_TRANSLATEDIALOGTEXTCTRL1, name = 'textCtrl1', parent = self, pos = wxPoint(48, 8), size = wxSize(278, 21), style = 0, value = self.phrase)
        self.textCtrl1.SetConstraints(LayoutAnchors(self.textCtrl1, true, true, true, false))

        self.staticText1 = wxStaticText(id = wxID_TRANSLATEDIALOGSTATICTEXT1, label = 'Phrase:', name = 'staticText1', parent = self, pos = wxPoint(8, 13), size = wxSize(36, 13), style = 0)

        self.staticText2 = wxStaticText(id = wxID_TRANSLATEDIALOGSTATICTEXT2, label = 'From:', name = 'staticText2', parent = self, pos = wxPoint(8, 45), size = wxSize(26, 13), style = 0)

        self.choice2 = wxChoice(choices = self.languages, id = wxID_TRANSLATEDIALOGCHOICE2, name = 'choice2', parent = self, pos = wxPoint(48, 40), size = wxSize(278, 21), style = 0, validator = wxDefaultValidator)
        self.choice2.SetSelection(0)
        self.choice2.SetConstraints(LayoutAnchors(self.choice2, true, true, true, false))

        self.choice3 = wxChoice(choices = self.languages, id = wxID_TRANSLATEDIALOGCHOICE3, name = 'choice3', parent = self, pos = wxPoint(48, 72), size = wxSize(278, 21), style = 0, validator = wxDefaultValidator)
        self.choice3.SetSelection(0)
        self.choice3.SetConstraints(LayoutAnchors(self.choice3, true, true, true, false))

        self.okBtn = wxButton(id = wxID_TRANSLATEDIALOGOKBTN, label = 'OK', name = 'okBtn', parent = self, pos = wxPoint(171, 104), size = wxSize(75, 23), style = 0)
        self.okBtn.SetConstraints(LayoutAnchors(self.okBtn, false, false, true, true))
        EVT_BUTTON(self.okBtn, wxID_TRANSLATEDIALOGOKBTN, self.OnButton1Button)

        self.cancelBtn = wxButton(id = wxID_TRANSLATEDIALOGCANCELBTN, label = 'Cancel', name = 'cancelBtn', parent = self, pos = wxPoint(251, 104), size = wxSize(75, 23), style = 0)
        self.cancelBtn.SetConstraints(LayoutAnchors(self.cancelBtn, false, false, true, true))
        EVT_BUTTON(self.cancelBtn, wxID_TRANSLATEDIALOGCANCELBTN, self.OnCancelbtnButton)

        self.staticText4 = wxStaticText(id = wxID_TRANSLATEDIALOGSTATICTEXT4, label = 'Thanks to BabelFish and Jonathan Feinberg', name = 'staticText4', parent = self, pos = wxPoint(8, 104), size = wxSize(118, 27), style = wxST_NO_AUTORESIZE)

        self.staticBitmap1 = wxStaticBitmap(bitmap = self.babelBmp, id = wxID_TRANSLATEDIALOGSTATICBITMAP1, name = 'staticBitmap1', parent = self, pos = wxPoint(136, 104), size = wxSize(28, 20), style = 0)

    def __init__(self, parent, phrase, languages=babeliser.available_languages):
        self.phrase = 'I love a reigning knight.'
        self.phrase = phrase
        self.languages = ['English', 'German', 'Etc']
        self.languages = languages
        self.babelBmp = IS.load('Images/Views/bfish.gif')
        self._init_ctrls(parent)
        self.translated = [phrase]

        self.SetAcceleratorTable(
              wxAcceleratorTable([ Utils.setupCloseWindowOnEscape(self) ]))

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

#---Spell checking (curtesy of David Adams' Speller)----------------------------

from ExternalLib import xmlrpclib

eolPlaceHolder = '|\||_'
def spellCheck(text):
    svr = xmlrpclib.Server('http://www.stuffeddog.com/speller/speller-rpc.cgi')
    text = string.replace(text, '\n', eolPlaceHolder)
    mistakes = svr.speller.spellCheck(text)
    insertOffset = 0
    newText = text
    for mistake in mistakes:
        suggests = ' ['+string.join(mistake['suggestions'], '|')+']'
        pivot = mistake['location']+len(mistake['word'])+insertOffset -1
        newText = newText[:pivot] + suggests + newText[pivot:]
        insertOffset = insertOffset + len(suggests)
    return string.replace(newText, eolPlaceHolder, '\n')

if __name__ == '__main__':
    if 1:
        wxInitAllImageHandlers()
        app = wxPySimpleApp()
        dlg = create(None, 'Amo un cavaliere di regno.')
        try:
            if dlg.ShowModal() == wxOK and len(dlg.translated) > 1:
                wxMessageBox(dlg.translated[1], 'Translation')
        finally:
            dlg.Destroy()
    else:
        print spellCheck('Boa is a fantastik \nintigrated envirooment')
