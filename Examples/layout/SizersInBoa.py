#Boa:Frame:wxFrame1

from wxPython.wx import *

def create(parent):
    return wxFrame1(parent)

[wxID_WXFRAME1, wxID_WXFRAME1BUTTON1, wxID_WXFRAME1BUTTON10, 
 wxID_WXFRAME1BUTTON11, wxID_WXFRAME1BUTTON12, wxID_WXFRAME1BUTTON13, 
 wxID_WXFRAME1BUTTON14, wxID_WXFRAME1BUTTON15, wxID_WXFRAME1BUTTON16, 
 wxID_WXFRAME1BUTTON17, wxID_WXFRAME1BUTTON18, wxID_WXFRAME1BUTTON19, 
 wxID_WXFRAME1BUTTON2, wxID_WXFRAME1BUTTON20, wxID_WXFRAME1BUTTON21, 
 wxID_WXFRAME1BUTTON3, wxID_WXFRAME1BUTTON4, wxID_WXFRAME1BUTTON5, 
 wxID_WXFRAME1BUTTON6, wxID_WXFRAME1BUTTON7, wxID_WXFRAME1BUTTON8, 
 wxID_WXFRAME1BUTTON9, wxID_WXFRAME1NOTEBOOK1, wxID_WXFRAME1PANEL1, 
 wxID_WXFRAME1PANEL2, wxID_WXFRAME1PANEL3, wxID_WXFRAME1PANEL4, 
 wxID_WXFRAME1STATICBOX1, 
] = map(lambda _init_ctrls: wxNewId(), range(28))

class wxFrame1(wxFrame):
    def _init_coll_flexGridSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.button10, 0, border=10, flag=wxGROW | wxALL)
        parent.AddWindow(self.button11, 0, border=10, flag=wxALL)
        parent.AddWindow(self.button12, 0, border=10, flag=wxALL)
        parent.AddWindow(self.button13, 0, border=10,
              flag=wxALIGN_CENTER | wxALL)
        parent.AddWindow(self.button14, 0, border=10, flag=wxALL)
        parent.AddWindow(self.button15, 0, border=10, flag=wxALL)

    def _init_coll_staticBoxSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddSpacer(8, 8, border=0, flag=wxALIGN_CENTER)
        parent.AddWindow(self.button16, 0, border=0, flag=wxALIGN_CENTER)
        parent.AddWindow(self.button17, 1, border=0, flag=wxALIGN_CENTER)
        parent.AddWindow(self.button18, 0, border=0, flag=wxALIGN_CENTER)
        parent.AddSpacer(8, 8, border=0, flag=wxALIGN_CENTER)

    def _init_coll_gridSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.button4, 0, border=0, flag=0)
        parent.AddWindow(self.button5, 0, border=0, flag=0)
        parent.AddWindow(self.button6, 0, border=0, flag=0)
        parent.AddWindow(self.button7, 0, border=0, flag=0)
        parent.AddWindow(self.button8, 0, border=0, flag=0)
        parent.AddWindow(self.button9, 0, border=0, flag=0)

    def _init_coll_boxSizer2_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.button19, 0, border=8,
              flag=wxALL | wxALIGN_CENTER)
        parent.AddSpacer(16, 16, border=0, flag=0)
        parent.AddWindow(self.button20, 0, border=0, flag=wxALIGN_CENTER)
        parent.AddSpacer(16, 16, border=0, flag=0)
        parent.AddWindow(self.button21, 0, border=8,
              flag=wxALL | wxALIGN_CENTER)

    def _init_coll_flexGridSizer1_Growables(self, parent):
        # generated method, don't edit

        parent.AddGrowableRow(0)
        parent.AddGrowableCol(0)

    def _init_coll_boxSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.button1, 0, border=0, flag=wxALIGN_LEFT)
        parent.AddSizer(self.boxSizer2, 0, border=0, flag=wxALIGN_CENTER)
        parent.AddWindow(self.button3, 0, border=0, flag=wxALIGN_RIGHT)
        parent.AddWindow(self.button2, 1, border=0, flag=wxALIGN_CENTER)

    def _init_coll_notebook1_Pages(self, parent):
        # generated method, don't edit

        parent.AddPage(imageId=-1, page=self.panel1, select=True,
              text='Box Sizer')
        parent.AddPage(imageId=-1, page=self.panel2, select=False,
              text='Grid Sizer')
        parent.AddPage(imageId=-1, page=self.panel3, select=False,
              text='Flex Grid Sizer')
        parent.AddPage(imageId=-1, page=self.panel4, select=False,
              text='StaticBox Sizer')

    def _init_sizers(self):
        # generated method, don't edit
        self.notebookSizer1 = wxNotebookSizer(nb=self.notebook1)

        self.boxSizer1 = wxBoxSizer(orient=wxVERTICAL)

        self.gridSizer1 = wxGridSizer(cols=2, hgap=0, rows=3, vgap=0)

        self.flexGridSizer1 = wxFlexGridSizer(cols=3, hgap=0, rows=3, vgap=0)

        self.staticBoxSizer1 = wxStaticBoxSizer(box=self.staticBox1,
              orient=wxVERTICAL)

        self.boxSizer2 = wxBoxSizer(orient=wxHORIZONTAL)

        self._init_coll_boxSizer1_Items(self.boxSizer1)
        self._init_coll_gridSizer1_Items(self.gridSizer1)
        self._init_coll_flexGridSizer1_Growables(self.flexGridSizer1)
        self._init_coll_flexGridSizer1_Items(self.flexGridSizer1)
        self._init_coll_staticBoxSizer1_Items(self.staticBoxSizer1)
        self._init_coll_boxSizer2_Items(self.boxSizer2)

        self.panel1.SetSizer(self.boxSizer1)
        self.panel2.SetSizer(self.gridSizer1)
        self.panel3.SetSizer(self.flexGridSizer1)
        self.panel4.SetSizer(self.staticBoxSizer1)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxFrame.__init__(self, id=wxID_WXFRAME1, name='', parent=prnt,
              pos=wxPoint(302, 195), size=wxSize(458, 307),
              style=wxDEFAULT_FRAME_STYLE, title='Sizer demo')
        self.SetClientSize(wxSize(450, 280))
        self.Center(wxBOTH)

        self.notebook1 = wxNotebook(id=wxID_WXFRAME1NOTEBOOK1, name='notebook1',
              parent=self, pos=wxPoint(0, 0), size=wxSize(450, 280), style=0)

        self.panel1 = wxPanel(id=wxID_WXFRAME1PANEL1, name='panel1',
              parent=self.notebook1, pos=wxPoint(0, 0), size=wxSize(442, 254),
              style=wxTAB_TRAVERSAL)

        self.button1 = wxButton(id=wxID_WXFRAME1BUTTON1, label='button1',
              name='button1', parent=self.panel1, pos=wxPoint(0, 0),
              size=wxSize(75, 23), style=0)

        self.button2 = wxButton(id=wxID_WXFRAME1BUTTON2, label='button2',
              name='button2', parent=self.panel1, pos=wxPoint(183, 103),
              size=wxSize(75, 151), style=0)

        self.button3 = wxButton(id=wxID_WXFRAME1BUTTON3, label='button3',
              name='button3', parent=self.panel1, pos=wxPoint(367, 80),
              size=wxSize(75, 23), style=0)

        self.panel2 = wxPanel(id=wxID_WXFRAME1PANEL2, name='panel2',
              parent=self.notebook1, pos=wxPoint(0, 0), size=wxSize(442, 254),
              style=wxTAB_TRAVERSAL)

        self.button4 = wxButton(id=wxID_WXFRAME1BUTTON4, label='button4',
              name='button4', parent=self.panel2, pos=wxPoint(0, 0),
              size=wxSize(75, 23), style=0)

        self.button5 = wxButton(id=wxID_WXFRAME1BUTTON5, label='button5',
              name='button5', parent=self.panel2, pos=wxPoint(221, 0),
              size=wxSize(75, 23), style=0)

        self.button6 = wxButton(id=wxID_WXFRAME1BUTTON6, label='button6',
              name='button6', parent=self.panel2, pos=wxPoint(0, 84),
              size=wxSize(75, 23), style=0)

        self.button7 = wxButton(id=wxID_WXFRAME1BUTTON7, label='button7',
              name='button7', parent=self.panel2, pos=wxPoint(221, 84),
              size=wxSize(75, 23), style=0)

        self.button8 = wxButton(id=wxID_WXFRAME1BUTTON8, label='button8',
              name='button8', parent=self.panel2, pos=wxPoint(0, 168),
              size=wxSize(75, 23), style=0)

        self.button9 = wxButton(id=wxID_WXFRAME1BUTTON9, label='button9',
              name='button9', parent=self.panel2, pos=wxPoint(221, 168),
              size=wxSize(75, 23), style=0)

        self.panel3 = wxPanel(id=wxID_WXFRAME1PANEL3, name='panel3',
              parent=self.notebook1, pos=wxPoint(0, 0), size=wxSize(442, 254),
              style=wxTAB_TRAVERSAL)

        self.panel4 = wxPanel(id=wxID_WXFRAME1PANEL4, name='panel4',
              parent=self.notebook1, pos=wxPoint(0, 0), size=wxSize(442, 254),
              style=wxTAB_TRAVERSAL)

        self.staticBox1 = wxStaticBox(id=wxID_WXFRAME1STATICBOX1,
              label='staticBox1', name='staticBox1', parent=self.panel4,
              pos=wxPoint(0, 0), size=wxSize(442, 254), style=0)

        self.button10 = wxButton(id=wxID_WXFRAME1BUTTON10, label='button10',
              name='button10', parent=self.panel3, pos=wxPoint(10, 10),
              size=wxSize(232, 191), style=0)

        self.button11 = wxButton(id=wxID_WXFRAME1BUTTON11, label='button11',
              name='button11', parent=self.panel3, pos=wxPoint(262, 10),
              size=wxSize(75, 23), style=0)

        self.button12 = wxButton(id=wxID_WXFRAME1BUTTON12, label='button12',
              name='button12', parent=self.panel3, pos=wxPoint(357, 10),
              size=wxSize(75, 23), style=0)

        self.button13 = wxButton(id=wxID_WXFRAME1BUTTON13, label='button13',
              name='button13', parent=self.panel3, pos=wxPoint(88, 221),
              size=wxSize(75, 23), style=0)

        self.button14 = wxButton(id=wxID_WXFRAME1BUTTON14, label='button14',
              name='button14', parent=self.panel3, pos=wxPoint(262, 221),
              size=wxSize(75, 23), style=0)

        self.button15 = wxButton(id=wxID_WXFRAME1BUTTON15, label='button15',
              name='button15', parent=self.panel3, pos=wxPoint(357, 221),
              size=wxSize(75, 23), style=0)

        self.button16 = wxButton(id=wxID_WXFRAME1BUTTON16, label='button16',
              name='button16', parent=self.panel4, pos=wxPoint(183, 21),
              size=wxSize(75, 23), style=0)

        self.button17 = wxButton(id=wxID_WXFRAME1BUTTON17, label='button17',
              name='button17', parent=self.panel4, pos=wxPoint(161, 44),
              size=wxSize(120, 174), style=0)

        self.button18 = wxButton(id=wxID_WXFRAME1BUTTON18, label='button18',
              name='button18', parent=self.panel4, pos=wxPoint(128, 218),
              size=wxSize(185, 23), style=0)

        self.button19 = wxButton(id=wxID_WXFRAME1BUTTON19, label='button19',
              name='button19', parent=self.panel1, pos=wxPoint(70, 40),
              size=wxSize(75, 23), style=0)

        self.button20 = wxButton(id=wxID_WXFRAME1BUTTON20, label='button20',
              name='button20', parent=self.panel1, pos=wxPoint(169, 23),
              size=wxSize(104, 57), style=0)

        self.button21 = wxButton(id=wxID_WXFRAME1BUTTON21, label='button21',
              name='button21', parent=self.panel1, pos=wxPoint(297, 40),
              size=wxSize(75, 23), style=0)

        self._init_coll_notebook1_Pages(self.notebook1)

        self._init_sizers()

    def __init__(self, parent):
        self._init_ctrls(parent)


if __name__ == '__main__':
    app = wxPySimpleApp()
    wxInitAllImageHandlers()
    frame = create(None)
    frame.Show()

    app.MainLoop()
