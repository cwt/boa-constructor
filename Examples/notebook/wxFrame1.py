#Boa:Frame:wxFrame1

from wxPython.wx import *

import wxDialog1

def create(parent):
    return wxFrame1(parent)

[wxID_WXFRAME1TXTEDITOR, wxID_WXFRAME1, wxID_WXFRAME1STATUSBAR1] = map(lambda _init_ctrls: wxNewId(), range(3))

[wxID_WXFRAME1FILEITEMS0, wxID_WXFRAME1FILEITEMS1, wxID_WXFRAME1FILEITEMS2, wxID_WXFRAME1FILEITEMS3, wxID_WXFRAME1FILEITEMS4] = map(lambda _init_coll_File_Items: wxNewId(), range(5))

[wxID_WXFRAME1HELPITEMS0] = map(lambda _init_coll_Help_Items: wxNewId(), range(1))

class wxFrame1(wxFrame):
    def _init_coll_Help_Items(self, parent):

        parent.Append(checkable = false, id = wxID_WXFRAME1HELPITEMS0, item = 'About', helpString = 'Display General Information about Notebook')
        EVT_MENU(self, wxID_WXFRAME1HELPITEMS0, self.OnHelpitems0Menu)

    def _init_coll_File_Items(self, parent):

        parent.Append(checkable = false, id = wxID_WXFRAME1FILEITEMS0, item = 'Open', helpString = 'Open')
        parent.Append(checkable = false, id = wxID_WXFRAME1FILEITEMS1, item = 'Save', helpString = 'Save')
        parent.Append(checkable = false, id = wxID_WXFRAME1FILEITEMS2, item = 'Save As', helpString = 'Save As')
        parent.Append(checkable = false, id = wxID_WXFRAME1FILEITEMS3, item = 'Close', helpString = 'Close')
        parent.Append(checkable = false, id = wxID_WXFRAME1FILEITEMS4, item = 'Exit', helpString = 'Exit')
        EVT_MENU(self, wxID_WXFRAME1FILEITEMS4, self.OnFileitems4Menu)
        EVT_MENU(self, wxID_WXFRAME1FILEITEMS0, self.OnFileitems0Menu)
        EVT_MENU(self, wxID_WXFRAME1FILEITEMS1, self.OnFileitems1Menu)
        EVT_MENU(self, wxID_WXFRAME1FILEITEMS2, self.OnFileitems2Menu)
        EVT_MENU(self, wxID_WXFRAME1FILEITEMS3, self.OnFileitems3Menu)

    def _init_coll_menuBar1_Menus(self, parent):

        parent.Append(title = 'File', menu = self.File)
        parent.Append(title = 'Help', menu = self.Help)

    def _init_coll_statusBar1_Fields(self, parent):
        parent.SetFieldsCount(1)

        parent.SetStatusText(text = 'Status', i = 0)

        parent.SetStatusWidths([-1])

    def _init_utils(self): 
        self.File = wxMenu(title = 'File')
        self._init_coll_File_Items(self.File)

        self.Help = wxMenu(title = 'Help')
        self._init_coll_Help_Items(self.Help)

        self.menuBar1 = wxMenuBar()

        self._init_coll_menuBar1_Menus(self.menuBar1)

    def _init_ctrls(self, prnt): 
        wxFrame.__init__(self, size = wxSize(480, 347), id = wxID_WXFRAME1, title = 'Notebook', parent = prnt, name = '', style = wxDEFAULT_FRAME_STYLE, pos = wxPoint(384, 346))
        self._init_utils()
        self.SetMenuBar(self.menuBar1)
        self.Show(true)

        self.statusBar1 = wxStatusBar(size = wxDefaultSize, parent = self, pos = wxPoint(56, 104), name = 'statusBar1', style = 0, id = wxID_WXFRAME1STATUSBAR1)
        self._init_coll_statusBar1_Fields(self.statusBar1)
        self.SetStatusBar(self.statusBar1)

        self.txtEditor = wxTextCtrl(size = wxSize(472, 280), value = '', pos = wxPoint(0, 0), parent = self, name = 'txtEditor', style = wxTE_MULTILINE, id = wxID_WXFRAME1TXTEDITOR)

    def __init__(self, parent): 
        self._init_ctrls(parent)
        self.FileName=None

    def OnFileitems4Menu(self, event):
        self.Close()

    def OnFileitems0Menu(self, event):
        dlg = wxFileDialog(self, "Choose a file", ".", "", "*.*", wxOPEN)
        try:
            if dlg.ShowModal() == wxID_OK:
                filename = dlg.GetPath()
                self.txtEditor.LoadFile(filename) 
                self.FileName=filename                   
        finally:
            dlg.Destroy()        

    def OnFileitems1Menu(self, event):
        if self.FileName == None:
            return self.OnFileitems2Menu(event)
        else:
            self.txtEditor.SaveFile(self.FileName)

    def OnFileitems2Menu(self, event):
        dlg = wxFileDialog(self, "Save File As", ".", "", "*.*", wxSAVE)
        try:
            if dlg.ShowModal() == wxID_OK:
                filename = dlg.GetPath()
                self.txtEditor.SaveFile(filename) 
                self.FileName=filename         
        finally:
            dlg.Destroy()

    def OnFileitems3Menu(self, event):
        self.FileName = None
        self.txtEditor.Clear()

    def OnHelpitems0Menu(self, event):
        dlg = wxDialog1.wxDialog1(self)
        try:
            dlg.ShowModal()
        finally:
            dlg.Destroy()  
