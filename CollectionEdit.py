#----------------------------------------------------------------------
# Name:        CollectionEdit.py
# Purpose:     
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------

from wxPython.wx import *

#---------------------------------------------------------------------------

class TestToolBar(wxFrame):
    def __init__(self, parent):
        wxFrame.__init__(self, parent, -1, 'Collection editor',
                         wxPoint(0,0), wxSize(180, 250))


        tb = self.CreateToolBar(wxTB_HORIZONTAL|wxNO_BORDER)#|wxTB_FLAT)
        #tb = wxToolBar(self, -1, wxDefaultPosition, wxDefaultSize,
        #               wxTB_HORIZONTAL | wxNO_BORDER | wxTB_FLAT)
        #self.SetToolBar(tb)

#        self.CreateStatusBar()

        self.list = wxListCtrl(self, -1, wxDefaultPosition, wxDefaultSize,
                               wxLC_REPORT|wxSUNKEN_BORDER|wxLC_SINGLE_SEL |wxLC_NO_HEADER)
        self.list.InsertColumn(0, "Name")
#        self.list.SetColumnWidth(0, 200)

        EVT_LIST_ITEM_SELECTED(self.list, -1, self.OnItemSelect)
        EVT_LIST_ITEM_DESELECTED(self.list, -1, self.OnItemDeselect)
        self.selected = -1
        
        tb.AddTool(10, wxNoRefBitmap('bitmaps/new.bmp',   wxBITMAP_TYPE_BMP),
                        wxNullBitmap, false, -1, -1, "New", "Long help for 'New'")
        EVT_TOOL(self, 10, self.OnNewClick)
        EVT_TOOL_RCLICKED(self, 10, self.OnToolRClick)

        tb.AddTool(20, wxNoRefBitmap('bitmaps/delete.bmp',  wxBITMAP_TYPE_BMP),
                        wxNullBitmap, false, -1, -1, "Delete")
        EVT_TOOL(self, 20, self.OnDeleteClick)
        EVT_TOOL_RCLICKED(self, 20, self.OnToolRClick)

        tb.AddSeparator()
        tb.AddTool(30, wxNoRefBitmap('bitmaps/up.bmp',  wxBITMAP_TYPE_BMP),
                        wxNullBitmap, false, -1, -1, "Move up")
        EVT_TOOL(self, 30, self.OnUpClick)
        EVT_TOOL_RCLICKED(self, 30, self.OnToolRClick)

        tb.AddTool(40, wxNoRefBitmap('bitmaps/down.bmp', wxBITMAP_TYPE_BMP),
                        wxNullBitmap, false, -1, -1, "Move down")
        EVT_TOOL(self, 40, self.OnDownClick)
        EVT_TOOL_RCLICKED(self, 40, self.OnToolRClick)

        tb.Realize()

    def findSelected(self):
        for i in range(self.list.GetItemCount()):
            print self.list.GetItem(i).m_state
            
    def OnItemSelect(self, event):
        self.selected = event.m_itemIndex

    def OnItemDeselect(self, event):
        self.selected = -1
    
    def OnCloseWindow(self, event):
        self.Destroy()

    def OnNewClick(self, event):
        idx = self.list.GetItemCount()
        self.list.InsertStringItem(idx, 'NewItem'+`idx`)
        self.list.GetItem(idx).m_mask  = 3
#        self.list.SetColumnWidth(0, wxLIST_AUTOSIZE)
        self.list.SetItemState(idx, wxLIST_STATE_FOCUSED | wxLIST_STATE_SELECTED, wxLIST_STATE_FOCUSED | wxLIST_STATE_SELECTED)

    def OnDeleteClick(self, event):
        if self.selected >= 0:
            idx = self.selected
            self.list.DeleteItem(idx)
            if idx < self.list.GetItemCount():
                self.list.SetItemState(idx, wxLIST_STATE_SELECTED, wxLIST_STATE_SELECTED)
            elif  idx > 0:
                self.list.SetItemState(idx -1, wxLIST_STATE_SELECTED, wxLIST_STATE_SELECTED)
        
#        self.list.SetColumnWidth(0, wxLIST_AUTOSIZE)

    def OnToolClick(self, event):
        print "tool %s clicked\n" % event.GetId()

    def OnUpClick(self, event):
        if self.selected > 0:
            idx = self.selected
            name = self.list.GetItemText(idx)
            self.list.DeleteItem(idx)
            self.list.InsertStringItem(idx -1, name)
            self.list.SetItemState(idx -1, wxLIST_STATE_SELECTED, wxLIST_STATE_SELECTED)
        
    def OnDownClick(self, event):
        if (self.selected >= 0) and (self.selected < self.list.GetItemCount() -1):
            idx = self.selected
            name = self.list.GetItemText(idx)
            self.list.DeleteItem(idx)
            self.list.InsertStringItem(idx +1, name)
            self.list.SetItemState(idx +1, wxLIST_STATE_SELECTED, wxLIST_STATE_SELECTED)

    def OnToolRClick(self, event):
        print "tool %s right-clicked\n" % event.GetId()


#---------------------------------------------------------------------------

def runTest(frame):
    win = TestToolBar(frame)
    win.Show(true)

class MyApp(wxApp):
    def OnInit(self):
        runTest(NULL)
        return true

def main():
    app = MyApp(0)
    app.MainLoop()


if __name__ == '__main__':
    main()
