#Boa:FramePanel:PathsPanel

from wxPython.wx import *
from wxPython.grid import *

[wxID_PATHSPANEL, wxID_PATHSPANELADD_BTN, wxID_PATHSPANELGRID, 
 wxID_PATHSPANELREMOVE_BTN, wxID_PATHSPANELSTATICBOX1, 
] = map(lambda _init_ctrls: wxNewId(), range(5))

class PathsPanel(wxPanel):
    def _init_coll_staticBoxSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.grid, 1, border=8, flag=wxALL | wxGROW)
        parent.AddSizer(self.boxSizer1, 0, border=0, flag=wxALIGN_RIGHT)

    def _init_coll_boxSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.add_btn, 0, border=8, flag=wxALL | wxALIGN_RIGHT)
        parent.AddWindow(self.remove_btn, 0, border=8,
              flag=wxBOTTOM | wxTOP | wxRIGHT)

    def _init_sizers(self):
        # generated method, don't edit
        self.staticBoxSizer1 = wxStaticBoxSizer(box=self.staticBox1,
              orient=wxVERTICAL)

        self.boxSizer1 = wxBoxSizer(orient=wxHORIZONTAL)

        self._init_coll_staticBoxSizer1_Items(self.staticBoxSizer1)
        self._init_coll_boxSizer1_Items(self.boxSizer1)

        self.SetSizer(self.staticBoxSizer1)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxPanel.__init__(self, id=wxID_PATHSPANEL, name='PathsPanel',
              parent=prnt, pos=wxPoint(316, 277), size=wxSize(523, 274),
              style=wxTAB_TRAVERSAL)
        self.SetClientSize(wxSize(515, 247))

        self.staticBox1 = wxStaticBox(id=wxID_PATHSPANELSTATICBOX1,
              label='Sever to client filepath mappings', name='staticBox1',
              parent=self, pos=wxPoint(0, 0), size=wxSize(515, 247), style=0)

        self.grid = wxGrid(id=wxID_PATHSPANELGRID, name='grid', parent=self,
              pos=wxPoint(13, 21), size=wxSize(489, 173),
              style=wxSUNKEN_BORDER)
        self.grid.SetDefaultRowSize(20)
        self.grid.SetColLabelSize(20)
        self.grid.SetRowLabelSize(0)

        self.add_btn = wxButton(id=wxID_PATHSPANELADD_BTN, label='Add',
              name='add_btn', parent=self, pos=wxPoint(344, 210),
              size=wxSize(75, 24), style=0)
        EVT_BUTTON(self.add_btn, wxID_PATHSPANELADD_BTN, self.OnAdd_btnButton)

        self.remove_btn = wxButton(id=wxID_PATHSPANELREMOVE_BTN, label='Remove',
              name='remove_btn', parent=self, pos=wxPoint(427, 210),
              size=wxSize(75, 24), style=0)
        EVT_BUTTON(self.remove_btn, wxID_PATHSPANELREMOVE_BTN,
              self.OnRemove_btnButton)

        self._init_sizers()

    def __init__(self, parent, id, pos, size, style, name):
        self._init_ctrls(parent)

        self.SetDimensions(pos.x, pos.y, size.x, size.y)
        
    def init_paths(self, paths):
        self.paths = paths
        numRows = len(self.paths)
        self.grid.CreateGrid(numRows, 2)
        self.grid.SetColLabelValue(0, 'Map server filenames starting with')
        self.grid.SetColLabelValue(1, 'To client filenames starting with')
        colWidth = self.grid.GetClientSize().x/2
        self.grid.SetColSize(0, colWidth)
        self.grid.SetColSize(1, colWidth)
        
        for row, (svr, clnt) in zip(range(numRows), self.paths):
            self.grid.SetCellValue(row, 0, svr)
            self.grid.SetCellValue(row, 1, clnt)
        self.grid.ForceRefresh()
    
    def read_paths(self):
        self.grid.SaveEditControlValue()
        return  [(self.grid.GetCellValue(row, 0), self.grid.GetCellValue(row, 1))
                 for row in range(self.grid.GetNumberRows())]

    def OnAdd_btnButton(self, event):
        self.grid.AppendRows(1)

    def OnRemove_btnButton(self, event):
        row = self.grid.GetGridCursorRow()
        if row != -1:
            self.grid.DeleteRows(row, 1)

