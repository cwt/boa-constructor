#Boa:Dialog:ControlAlignmentFrame

from wxPython.wx import *

def create(parent):
    return ControlAlignmentFrame(parent)

[wxID_CONTROLALIGNMENTFRAMERADIOBOX2, wxID_CONTROLALIGNMENTFRAMEBUTTON2, wxID_CONTROLALIGNMENTFRAMERADIOBOX1, wxID_CONTROLALIGNMENTFRAMEBUTTON1, wxID_CONTROLALIGNMENTFRAMEPANEL1, wxID_CONTROLALIGNMENTFRAME] = map(lambda _init_ctrls: wxNewId(), range(6))

class ControlAlignmentFrame(wxDialog):
    def _init_utils(self): 
        pass

    def _init_ctrls(self, prnt): 
        wxDialog.__init__(self, size = wxSize(325, 216), id = wxID_CONTROLALIGNMENTFRAME, title = 'Alignment', parent = prnt, name = 'ControlAlignmentFrame', style = wxDEFAULT_DIALOG_STYLE, pos = wxPoint(341, 140))
        self._init_utils()

        self.panel1 = wxPanel(size = wxSize(320, 192), parent = self, id = wxID_CONTROLALIGNMENTFRAMEPANEL1, name = 'panel1', style = wxTAB_TRAVERSAL, pos = wxPoint(0, 0))

        self.radioBox1 = wxRadioBox(label = 'Horizontal', id = wxID_CONTROLALIGNMENTFRAMERADIOBOX1, choices = ['No change', 'Left sides', 'Centers', 'Right sides', 'Space equally', 'Center in window'], majorDimension = 1, point = wxPoint(8, 8), parent = self.panel1, name = 'radioBox1', size = wxSize(144, 144), validator = wxDefaultValidator, style = wxRA_SPECIFY_COLS)

        self.radioBox2 = wxRadioBox(label = 'Vertical', id = wxID_CONTROLALIGNMENTFRAMERADIOBOX2, choices = ['No change', 'Left sides', 'Centers', 'Right sides', 'Space equally', 'Center in window'], majorDimension = 1, point = wxPoint(160, 8), parent = self.panel1, name = 'radioBox2', size = wxSize(152, 144), validator = wxDefaultValidator, style = wxRA_SPECIFY_COLS)

        self.button1 = wxButton(label = 'OK', id = wxID_CONTROLALIGNMENTFRAMEBUTTON1, parent = self.panel1, name = 'button1', size = wxSize(72, 24), style = 0, pos = wxPoint(160, 160))

        self.button2 = wxButton(label = 'Cancel', id = wxID_CONTROLALIGNMENTFRAMEBUTTON2, parent = self.panel1, name = 'button2', size = wxSize(72, 24), style = 0, pos = wxPoint(240, 160))

    def __init__(self, parent): 
        self._init_ctrls(parent)
