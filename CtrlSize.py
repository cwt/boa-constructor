#Boa:Dialog:ControlSizeFrame

from wxPython.wx import *

def create(parent):
    return ControlSizeFrame(parent)

[wxID_CONTROLSIZEFRAMERADIOBOX2, wxID_CONTROLSIZEFRAMEWIDTHTC, wxID_CONTROLSIZEFRAMERADIOBOX1, wxID_CONTROLSIZEFRAMEPANEL1, wxID_CONTROLSIZEFRAMEHEIGHTTC, wxID_CONTROLSIZEFRAMEBUTTON1, wxID_CONTROLSIZEFRAMEBUTTON2, wxID_CONTROLSIZEFRAME] = map(lambda _init_ctrls: wxNewId(), range(8))

class ControlSizeFrame(wxDialog):
    def _init_utils(self): 
        pass

    def _init_ctrls(self, prnt): 
        wxDialog.__init__(self, size = wxSize(325, 192), id = wxID_CONTROLSIZEFRAME, title = 'Size', parent = prnt, name = 'ControlSizeFrame', style = wxDEFAULT_DIALOG_STYLE, pos = wxPoint(341, 140))
        self._init_utils()

        self.panel1 = wxPanel(size = wxSize(320, 168), parent = self, id = wxID_CONTROLSIZEFRAMEPANEL1, name = 'panel1', style = wxTAB_TRAVERSAL, pos = wxPoint(0, 0))

        self.radioBox1 = wxRadioBox(label = 'Width', id = wxID_CONTROLSIZEFRAMERADIOBOX1, choices = ['No change', 'Shrink to smallest', 'Grow to largest', 'Width:'], validator = wxDefaultValidator, majorDimension = 1, point = wxPoint(8, 8), parent = self.panel1, name = 'radioBox1', size = wxSize(144, 120), style = wxRA_SPECIFY_COLS)

        self.radioBox2 = wxRadioBox(label = 'Height', id = wxID_CONTROLSIZEFRAMERADIOBOX2, choices = ['No change', 'Shrink to smallest', 'Grow to largest', 'Height:'], validator = wxDefaultValidator, majorDimension = 1, point = wxPoint(160, 8), parent = self.panel1, name = 'radioBox2', size = wxSize(152, 120), style = wxRA_SPECIFY_COLS)

        self.button1 = wxButton(label = 'OK', id = wxID_CONTROLSIZEFRAMEBUTTON1, parent = self.panel1, name = 'button1', size = wxSize(72, 24), style = 0, pos = wxPoint(160, 136))

        self.button2 = wxButton(label = 'Cancel', id = wxID_CONTROLSIZEFRAMEBUTTON2, parent = self.panel1, name = 'button2', size = wxSize(72, 24), style = 0, pos = wxPoint(240, 136))

        self.widthTC = wxTextCtrl(size = wxSize(112, 24), value = '', pos = wxPoint(16, 88), parent = self.radioBox1, name = 'widthTC', style = 0, id = wxID_CONTROLSIZEFRAMEWIDTHTC)

        self.heightTC = wxTextCtrl(size = wxSize(120, 24), value = '', pos = wxPoint(16, 88), parent = self.radioBox2, name = 'heightTC', style = 0, id = wxID_CONTROLSIZEFRAMEHEIGHTTC)

    def __init__(self, parent): 
        self._init_ctrls(parent)
