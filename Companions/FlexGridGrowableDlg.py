#-----------------------------------------------------------------------------
# Name:        FlexGridGrowableDlg.py
# Purpose:     Managing growable rows and columns for the wxFlexGridSizer
#
# Author:      Riaan Booysen
#
# Created:     2003
# RCS-ID:      $Id$
# Copyright:   (c) 2003
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Dialog:FlexGridGrowablesDlg

from wxPython.wx import *
from wxPython.lib.buttons import *

[wxID_FLEXGRIDGROWABLESDLG, wxID_FLEXGRIDGROWABLESDLGBUTTON1, 
 wxID_FLEXGRIDGROWABLESDLGBUTTON2, wxID_FLEXGRIDGROWABLESDLGBUTTON3, 
 wxID_FLEXGRIDGROWABLESDLGGRIDWIN, 
] = map(lambda _init_ctrls: wxNewId(), range(5))

if wxPlatform == '__WXMAC__':
    ToggleButton = wxGenToggleButton
    EVT_TOGGLE = EVT_BUTTON
else:
    ToggleButton = wxToggleButton
    EVT_TOGGLE = EVT_TOGGLEBUTTON

class FlexGridGrowablesDlg(wxDialog):
    def _init_coll_boxSizer2_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.button3, 0, border=20, flag=wxALL | wxALIGN_RIGHT)
        parent.AddWindow(self.button1, 0, border=20,
              flag=wxRIGHT | wxTOP | wxBOTTOM | wxALIGN_RIGHT)
        parent.AddWindow(self.button2, 0, border=20,
              flag=wxRIGHT | wxTOP | wxBOTTOM | wxALIGN_RIGHT)

    def _init_coll_boxSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddSizer(self.flex, 1, border=0, flag=wxGROW | wxALL)
        parent.AddSizer(self.boxSizer2, 0, border=0, flag=wxALIGN_RIGHT)

    def _init_sizers(self):
        # generated method, don't edit
        self.boxSizer1 = wxBoxSizer(orient=wxVERTICAL)

        self.flex = wxFlexGridSizer(cols=self.numCols, hgap=0,
              rows=self.numRows, vgap=0)

        self.boxSizer2 = wxBoxSizer(orient=wxHORIZONTAL)

        self._init_coll_boxSizer1_Items(self.boxSizer1)
        self._init_coll_boxSizer2_Items(self.boxSizer2)

        self.SetSizer(self.boxSizer1)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_FLEXGRIDGROWABLESDLG,
              name='FlexGridGrowablesDlg', parent=prnt, pos=wxPoint(139, 88),
              size=wxSize(435, 279),
              style=wxRESIZE_BORDER | wxDEFAULT_DIALOG_STYLE,
              title='Define Growable Rows and Columns (resize to test)')
        self.SetClientSize(wxSize(427, 252))
        EVT_SIZE(self, self.OnFlexgridgrowablesdlgSize)

        self.button1 = wxButton(id=wxID_OK, label='OK', name='button1',
              parent=self, pos=wxPoint(237, 209), size=wxSize(75, 23), style=0)

        self.button2 = wxButton(id=wxID_CANCEL, label='Cancel', name='button2',
              parent=self, pos=wxPoint(332, 209), size=wxSize(75, 23), style=0)

        self.gridWin = wxWindow(id=wxID_FLEXGRIDGROWABLESDLGGRIDWIN,
              name='gridWin', parent=self, pos=wxPoint(32, 32), size=wxSize(200,
              100), style=0)
        EVT_PAINT(self.gridWin, self.OnGridwinPaint)

        self.button3 = wxButton(id=wxID_FLEXGRIDGROWABLESDLGBUTTON3,
              label='Editor', name='button3', parent=self, pos=wxPoint(142,
              209), size=wxSize(75, 23), style=0)
        self.button3.Enable(False)

        self._init_sizers()

    def __init__(self, parent, rows, cols):
        self.numRows = 4
        self.numRows = len(rows)+1
        self.numCols = 4
        self.numCols = len(cols)+1
        
        self._init_ctrls(parent)
        
        self.rows = rows
        self.cols = cols
        
        self.colIds = {}
        self.colBtns = []
        for idx, col in zip(range(len(cols)), cols):
            wid = wxNewId()
            tb = ToggleButton(self, wid, str(idx))
            if col: tb.SetValue(1)
            self.colIds[wid] = (idx, col)
            self.colBtns.append(tb)
            EVT_TOGGLE(tb, wid, self.OnToggleCol)
            
        self.rowIds = {}
        self.rowBtns = []
        for idx, row in zip(range(len(rows)), rows):
            wid = wxNewId()
            tb = ToggleButton(self, wid, str(idx))
            if row: tb.SetValue(1)
            self.rowIds[wid] = (idx, row)
            self.rowBtns.append(tb)
            EVT_TOGGLE(tb, wid, self.OnToggleRow)

        self.setupFlexSizer()
        
        if not rows or not cols:
            self.gridWin.Show(false)

        self.boxSizer1.Fit(self)

        # set current size as minimum size
        s = self.GetSize()
        self.SetSizeHints(s.width, s.height, -1, -1)
        wxCallAfter(self.gridWin.Refresh)

    def OnToggleCol(self, event):
        idx, col = self.colIds[event.GetId()]
        self.cols[idx] = not col
        self.colIds[event.GetId()] = idx, not col
        
        self.setupFlexSizer()

    def OnToggleRow(self, event):
        idx, row = self.rowIds[event.GetId()]
        self.rows[idx] = not row
        self.rowIds[event.GetId()] = idx, not row
        
        self.setupFlexSizer()

    def OnFlexgridgrowablesdlgSize(self, event):
        if self.rows and self.cols:
            tlPos = self.colBtns[0].GetPosition()
            tlSize = self.colBtns[0].GetSize()
            trPos = self.colBtns[-1].GetPosition()
            trSize = self.colBtns[-1].GetSize()
            blPos = self.rowBtns[-1].GetPosition()
            blSize = self.rowBtns[-1].GetSize()
            self.gridWin.SetDimensions(tlPos.x, tlPos.y + tlSize.height, 
                  trPos.x + trSize.width - tlPos.x, 
                  blPos.y + blSize.height - tlSize.height)

        # let sizers update
        event.Skip()

    def OnGridwinPaint(self, event):
        dc = wxPaintDC(self.gridWin)
        brush = wxBrush(wxWHITE)
        dc.SetBackground(brush)
        dc.Clear()
        dc.SetPen(wxBLACK_PEN)
        
        w, h = self.gridWin.GetSize().asTuple()
        x = 0
        for vl in range(len(self.colBtns)):
            dc.DrawLine(x-1, 0, x-1, h)
            x += self.colBtns[vl].GetSize().width

        y = 0
        for hl in range(len(self.rowBtns)):
            dc.DrawLine(0, y-1, w, y-1)
            y += self.rowBtns[hl].GetSize().height

    def setupFlexSizer(self):
        self.boxSizer1.RemovePos(0)
        self.flex = wxFlexGridSizer(cols=self.numCols, hgap=0,
              rows=self.numRows, vgap=0)
        self.boxSizer1.Insert(0, self.flex, 1, border=0, flag=wxGROW | wxALL)
              
        rows, cols = self.rows, self.cols
        self.flex.Add(10, 10)
        for idx, col in zip(range(len(cols)), cols):
            self.flex.Add(self.colBtns[idx], 0, wxGROW)
            if col:
                self.flex.AddGrowableCol(idx+1)

        for idx, row in zip(range(len(rows)), rows):
            self.flex.Add(self.rowBtns[idx], 0, wxGROW)
            for s in range(len(cols)):
                self.flex.Add(10, 10)
            if row:
                self.flex.AddGrowableRow(idx+1)
        
        self.boxSizer1.Layout()
        # needed to repaint the custom drawn window
        wxPostEvent(self, wxSizeEvent(self.GetSize(), self.GetId()))

if __name__ == '__main__':
    app = wxPySimpleApp()
    wxInitAllImageHandlers()
    dlg = FlexGridGrowablesDlg(None, [1, 0], [1, 0, 0])
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()
    app.MainLoop()
