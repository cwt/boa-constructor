#Boa:Frame:wxFrame1

""" Examples of using Frame Attributes to implement internationalisation
integration compatible with the Designer. See wxFrame1.__init__ """

from gettext import gettext as _

from wxPython.wx import *

def create(parent):
    return wxFrame1(parent)

ENG, AFR = range(2)
GlobalLang = AFR

[wxID_WXFRAME1, wxID_WXFRAME1BUTTON1, wxID_WXFRAME1BUTTON2,
 wxID_WXFRAME1STATICTEXT1,
] = map(lambda _init_ctrls: wxNewId(), range(4))

class wxFrame1(wxFrame):
    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxFrame.__init__(self, id=wxID_WXFRAME1, name='', parent=prnt,
              pos=wxPoint(324, 193), size=wxSize(173, 149),
              style=wxDEFAULT_FRAME_STYLE, title='i18n')
        self._init_utils()
        self.SetClientSize(wxSize(165, 122))
        self.SetBackgroundColour(wxColour(128, 128, 255))

        self.staticText1 = wxStaticText(id=wxID_WXFRAME1STATICTEXT1,
              label=self.ST1Text, name='staticText1', parent=self,
              pos=wxPoint(8, 8), size=wxSize(136, 16), style=0)

        self.button1 = wxButton(id=wxID_WXFRAME1BUTTON1, label=self.BT1Text,
              name='button1', parent=self, pos=wxPoint(8, 48), size=wxSize(136,
              23), style=0)

        self.button2 = wxButton(id=wxID_WXFRAME1BUTTON2, label=self.BT2Text,
              name='button2', parent=self, pos=wxPoint(8, 80), size=wxSize(136,
              23), style=0)

    def __init__(self, parent):
        """ Attributes defined before _init_ctrls can be referenced in the
            generated code. The first version should be a constant definition
            and will be used by the Designer, the second version is used
            (by overwriting the first) at runtime. """

        # example 1: looking up languages by indexing a tuple
        self.ST1Text = 'Text (design-time)'
        self.ST1Text = ('Text', 'Teks')[GlobalLang]
        self.BT1Text = 'Button (design-time)'
        self.BT1Text = ('Button', 'Knoppie')[GlobalLang]

        # example 2: using gettext
        self.BT2Text = _('gettext format')

        self._init_ctrls(parent)


if __name__ == '__main__':
    app = wxPySimpleApp()
    frame = create(None)
    frame.Show(true)
    app.MainLoop()
