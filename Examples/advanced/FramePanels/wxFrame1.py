#Boa:Frame:wxFrame1

from wxPython.wx import *

from wxPanel1 import wxPanel1
from wxPanel2 import wxPanel2
from wxPanel3 import wxPanel3

def create(parent):
    return wxFrame1(parent)

[wxID_WXFRAME1, wxID_WXFRAME1NOTEBOOK1, wxID_WXFRAME1PANEL1,
 wxID_WXFRAME1PANEL2, wxID_WXFRAME1PANEL3, wxID_WXFRAME1PANEL4,
 wxID_WXFRAME1PANEL5, wxID_WXFRAME1PANEL6, wxID_WXFRAME1PANEL7,
] = map(lambda _init_ctrls: wxNewId(), range(9))

class wxFrame1(wxFrame):
    _custom_classes = {'wxPanel': ['wxPanel1', 'wxPanel2', 'wxPanel3']}
    def _init_coll_notebook1_Pages(self, parent):
        # generated method, don't edit

        parent.AddPage(select=false, imageId=-1, page=self.panel1,
              text='Pages0')
        parent.AddPage(select=false, imageId=-1, page=self.panel2,
              text='Pages1')
        parent.AddPage(select=true, imageId=-1, page=self.panel3,
              text='Pages2')

    def _init_utils(self):
        # generated method, don't edit
        pass

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxFrame.__init__(self, id=wxID_WXFRAME1, name='', parent=prnt,
              pos=wxPoint(306, 164), size=wxSize(491, 364),
              style=wxDEFAULT_FRAME_STYLE, title='wxFrame1')
        self._init_utils()
        self.SetClientSize(wxSize(483, 337))

        self.notebook1 = wxNotebook(id=wxID_WXFRAME1NOTEBOOK1, name='notebook1',
              parent=self, pos=wxPoint(0, 0), size=wxSize(483, 337), style=0)

        self.panel1 = wxPanel1(id=wxID_WXFRAME1PANEL1, name='panel1',
              parent=self.notebook1, pos=wxPoint(0, 0), size=wxSize(475, 311),
              style=wxTAB_TRAVERSAL)

        self.panel2 = wxPanel2(id=wxID_WXFRAME1PANEL2, name='panel2',
              parent=self.notebook1, pos=wxPoint(0, 0), size=wxSize(475, 311),
              style=wxTAB_TRAVERSAL)

        self.panel3 = wxPanel(id=wxID_WXFRAME1PANEL3, name='panel3',
              parent=self.notebook1, pos=wxPoint(0, 0), size=wxSize(475, 311),
              style=wxTAB_TRAVERSAL)

        self.panel4 = wxPanel3(id=wxID_WXFRAME1PANEL4, name='panel4',
              parent=self.panel3, pos=wxPoint(16, 16), size=wxSize(200, 100),
              style=wxRAISED_BORDER | wxTAB_TRAVERSAL)

        self.panel5 = wxPanel3(id=wxID_WXFRAME1PANEL5, name='panel5',
              parent=self.panel3, pos=wxPoint(16, 136), size=wxSize(200, 100),
              style=wxSTATIC_BORDER | wxTAB_TRAVERSAL)

        self.panel6 = wxPanel3(id=wxID_WXFRAME1PANEL6, name='panel6',
              parent=self.panel3, pos=wxPoint(232, 16), size=wxSize(200, 100),
              style=wxSUNKEN_BORDER | wxTAB_TRAVERSAL)

        self.panel7 = wxPanel3(id=wxID_WXFRAME1PANEL7, name='panel7',
              parent=self.panel3, pos=wxPoint(232, 136), size=wxSize(200, 100),
              style=wxSIMPLE_BORDER | wxTAB_TRAVERSAL)

        self._init_coll_notebook1_Pages(self.notebook1)

    def __init__(self, parent):
        self._init_ctrls(parent)
