#Boa:Wizard:wxWizard1

from wxPython.wx import *
from wxPython.wizard import *

def create(parent):
    return wxWizard1(parent)

def run(parent):
    wizard = create(parent)
        
    import wxPyWizardPage1, wxPyWizardPage2
    import wxWizardPageSimple1, wxWizardPageSimple2
        
    pwpage1 = wxPyWizardPage1.wxPyWizardPage1(wizard)
    pwpage2 = wxPyWizardPage2.wxPyWizardPage2(wizard)
    wspage1 = wxWizardPageSimple1.wxWizardPageSimple1(wizard)
    wspage2 = wxWizardPageSimple2.wxWizardPageSimple2(wizard)

    pwpage1.SetNext(pwpage2)
    pwpage2._next = wspage1
    pwpage2._prev = pwpage1
    wspage1.SetPrev(pwpage2)
    wxWizardPageSimple_Chain(wspage1, wspage2)

    return wizard.RunWizard(pwpage1)


[wxID_WXWIZARD1, wxID_WXWIZARD1BUTTON1, wxID_WXWIZARD1STATICTEXT1, 
] = map(lambda _init_ctrls: wxNewId(), range(3))

class wxWizard1(wxWizard):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxWizard.__init__(self, bitmap=wxBitmap('WizImage.png',
              wxBITMAP_TYPE_PNG), id=wxID_WXWIZARD1, parent=prnt,
              pos=wxPoint(333, 205), title='wxWizard Example')
        EVT_WIZARD_PAGE_CHANGING(self, wxID_WXWIZARD1,
              self.OnWxwizard1WizardPageChanging)
        EVT_WIZARD_PAGE_CHANGED(self, wxID_WXWIZARD1,
              self.OnWxwizard1WizardPageChanged)

        self.button1 = wxButton(id=wxID_WXWIZARD1BUTTON1, label='debug',
              name='button1', parent=self, pos=wxPoint(8, 312), size=wxSize(40,
              23), style=0)
        EVT_BUTTON(self.button1, wxID_WXWIZARD1BUTTON1, self.OnButton1Button)

        self.staticText1 = wxStaticText(id=wxID_WXWIZARD1STATICTEXT1,
              label='(status)', name='staticText1', parent=self, pos=wxPoint(8,
              293), size=wxSize(34, 13), style=0)

    def __init__(self, parent):
        self._init_ctrls(parent)

    def OnButton1Button(self, event):
        wxLogMessage(`self.GetChildren()`) #GetSizer().

    def OnWxwizard1WizardPageChanging(self, event):
        self.staticText1.SetLabel('Changing...')

    def OnWxwizard1WizardPageChanged(self, event):
        self.staticText1.SetLabel('Changed to %s'%event.GetPage().GetName())
