#Boa:Frame:wxFrame1

# Please note that the source assumeswxPython 2.3.3 or higher.

from wxPython.wx import *

import wxDialog1

def create(parent):
    return wxFrame1(parent)

[wxID_WXFRAME1, wxID_WXFRAME1STATUSBAR1, wxID_WXFRAME1TXTEDITOR, 
] = map(lambda _init_ctrls: wxNewId(), range(3))

[wxID_WXFRAME1FILEITEMS0, wxID_WXFRAME1FILEITEMS1, wxID_WXFRAME1FILEITEMS2, 
 wxID_WXFRAME1FILEITEMS3, wxID_WXFRAME1FILEITEMS4, 
] = map(lambda _init_coll_File_Items: wxNewId(), range(5))

[wxID_WXFRAME1HELPITEMS0] = map(lambda _init_coll_Help_Items: wxNewId(), range(1))

class wxFrame1(wxFrame):
    def _init_coll_Help_Items(self, parent):
        # generated method, don't edit

        parent.Append(helpString='Display General Information about Notebook',
              id=wxID_WXFRAME1HELPITEMS0, item='About', kind=wxITEM_NORMAL)
        EVT_MENU(self, wxID_WXFRAME1HELPITEMS0, self.OnHelpitems0Menu)

    def _init_coll_File_Items(self, parent):
        # generated method, don't edit

        parent.Append(helpString='Open', id=wxID_WXFRAME1FILEITEMS0,
              item='Open', kind=wxITEM_NORMAL)
        parent.Append(helpString='Save', id=wxID_WXFRAME1FILEITEMS1,
              item='Save', kind=wxITEM_NORMAL)
        parent.Append(helpString='Save As', id=wxID_WXFRAME1FILEITEMS2,
              item='Save As', kind=wxITEM_NORMAL)
        parent.Append(helpString='Close', id=wxID_WXFRAME1FILEITEMS3,
              item='Close', kind=wxITEM_NORMAL)
        parent.Append(helpString='Exit', id=wxID_WXFRAME1FILEITEMS4,
              item='Exit', kind=wxITEM_NORMAL)
        EVT_MENU(self, wxID_WXFRAME1FILEITEMS4, self.OnFileitems4Menu)
        EVT_MENU(self, wxID_WXFRAME1FILEITEMS0, self.OnFileitems0Menu)
        EVT_MENU(self, wxID_WXFRAME1FILEITEMS1, self.OnFileitems1Menu)
        EVT_MENU(self, wxID_WXFRAME1FILEITEMS2, self.OnFileitems2Menu)
        EVT_MENU(self, wxID_WXFRAME1FILEITEMS3, self.OnFileitems3Menu)

    def _init_coll_menuBar1_Menus(self, parent):
        # generated method, don't edit

        parent.Append(menu=self.File, title='File')
        parent.Append(menu=self.Help, title='Help')

    def _init_coll_statusBar1_Fields(self, parent):
        # generated method, don't edit
        parent.SetFieldsCount(1)

        parent.SetStatusText(i=0, text='Status')

        parent.SetStatusWidths([-1])

    def _init_utils(self):
        # generated method, don't edit
        self.File = wxMenu(title='')
        self._init_coll_File_Items(self.File)

        self.Help = wxMenu(title='')
        self._init_coll_Help_Items(self.Help)

        self.menuBar1 = wxMenuBar()

        self._init_coll_menuBar1_Menus(self.menuBar1)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxFrame.__init__(self, id=wxID_WXFRAME1, name='', parent=prnt,
              pos=wxPoint(384, 346), size=wxSize(480, 347),
              style=wxDEFAULT_FRAME_STYLE, title='Notebook')
        self._init_utils()
        self.SetMenuBar(self.menuBar1)

        self.statusBar1 = wxStatusBar(id=wxID_WXFRAME1STATUSBAR1,
              name='statusBar1', parent=self, style=0)
        self._init_coll_statusBar1_Fields(self.statusBar1)
        self.SetStatusBar(self.statusBar1)

        self.txtEditor = wxTextCtrl(id=wxID_WXFRAME1TXTEDITOR, name='txtEditor',
              parent=self, pos=wxPoint(0, 0), size=wxSize(472, 281),
              style=wxTE_MULTILINE, value='')

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
