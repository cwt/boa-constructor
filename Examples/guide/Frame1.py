#Boa:Frame:Frame1

# Please note that the source assumes wxPython 2.5 or higher.

import wx

import Dialog1

def create(parent):
    return Frame1(parent)

[wxID_FRAME1, wxID_FRAME1STATUSBAR1, wxID_FRAME1TXTEDITOR, 
] = [wx.NewId() for _init_ctrls in range(3)]

[wxID_FRAME1FILEITEMS0, wxID_FRAME1FILEITEMS1, wxID_FRAME1FILEITEMS2, 
 wxID_FRAME1FILEITEMS3, wxID_FRAME1FILEITEMS4, 
] = [wx.NewId() for _init_coll_File_Items in range(5)]

[wxID_FRAME1HELPITEMS0] = [wx.NewId() for _init_coll_Help_Items in range(1)]

class Frame1(wx.Frame):
    def _init_coll_menuBar1_Menus(self, parent):
        # generated method, don't edit

        parent.Append(menu=self.File, title='File')
        parent.Append(menu=self.Help, title='Help')

    def _init_coll_File_Items(self, parent):
        # generated method, don't edit

        parent.Append(help='Open', id=wxID_FRAME1FILEITEMS0,
              kind=wx.ITEM_NORMAL, text='Open')
        parent.Append(help='Save', id=wxID_FRAME1FILEITEMS1,
              kind=wx.ITEM_NORMAL, text='Save')
        parent.Append(help='Save As', id=wxID_FRAME1FILEITEMS2,
              kind=wx.ITEM_NORMAL, text='Save As')
        parent.Append(help='Close', id=wxID_FRAME1FILEITEMS3,
              kind=wx.ITEM_NORMAL, text='Close')
        parent.Append(help='Exit', id=wxID_FRAME1FILEITEMS4,
              kind=wx.ITEM_NORMAL, text='Exit')
        self.Bind(wx.EVT_MENU, self.OnFileitems4Menu, id=wxID_FRAME1FILEITEMS4)
        self.Bind(wx.EVT_MENU, self.OnFileitems0Menu, id=wxID_FRAME1FILEITEMS0)
        self.Bind(wx.EVT_MENU, self.OnFileitems1Menu, id=wxID_FRAME1FILEITEMS1)
        self.Bind(wx.EVT_MENU, self.OnFileitems2Menu, id=wxID_FRAME1FILEITEMS2)
        self.Bind(wx.EVT_MENU, self.OnFileitems3Menu, id=wxID_FRAME1FILEITEMS3)

    def _init_coll_Help_Items(self, parent):
        # generated method, don't edit

        parent.Append(help='Display General Information about Notebook',
              id=wxID_FRAME1HELPITEMS0, kind=wx.ITEM_NORMAL, text='About')
        self.Bind(wx.EVT_MENU, self.OnHelpitems0Menu, id=wxID_FRAME1HELPITEMS0)

    def _init_coll_statusBar1_Fields(self, parent):
        # generated method, don't edit
        parent.SetFieldsCount(1)

        parent.SetStatusText(number=0, text='Status')

        parent.SetStatusWidths([-1])

    def _init_utils(self):
        # generated method, don't edit
        self.File = wx.Menu(title='')

        self.Help = wx.Menu(title='')

        self.menuBar1 = wx.MenuBar()

        self._init_coll_File_Items(self.File)
        self._init_coll_Help_Items(self.Help)
        self._init_coll_menuBar1_Menus(self.menuBar1)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_FRAME1, name='Frame1', parent=prnt,
              pos=wx.Point(384, 346), size=wx.Size(480, 347),
              style=wx.DEFAULT_FRAME_STYLE, title='Notebook')
        self._init_utils()
        self.SetMenuBar(self.menuBar1)
        self.SetClientSize(wx.Size(472, 320))

        self.statusBar1 = wx.StatusBar(id=wxID_FRAME1STATUSBAR1,
              name='statusBar1', parent=self, style=0)
        self._init_coll_statusBar1_Fields(self.statusBar1)
        self.SetStatusBar(self.statusBar1)

        self.txtEditor = wx.TextCtrl(id=wxID_FRAME1TXTEDITOR, name='txtEditor',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(472, 281),
              style=wx.TE_MULTILINE, value='')

    def __init__(self, parent):
        self._init_ctrls(parent)
        self.FileName=None

    def OnFileitems4Menu(self, event):
        self.Close()

    def OnFileitems0Menu(self, event):
        dlg = wx.FileDialog(self, 'Choose a file', '.', '', '*.*', wx.OPEN)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                self.txtEditor.SetValue(open(filename, 'rb').read())
                self.FileName=filename
        finally:
            dlg.Destroy()

    def OnFileitems1Menu(self, event):
        if self.FileName == None:
            return self.OnFileitems2Menu(event)
        else:
            self.txtEditor.SaveFile(self.FileName)

    def OnFileitems2Menu(self, event):
        dlg = wx.FileDialog(self, 'Save File As', '.', '', '*.*', wx.SAVE)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                self.txtEditor.SaveFile(filename)
                self.FileName=filename
        finally:
            dlg.Destroy()

    def OnFileitems3Menu(self, event):
        self.FileName = None
        self.txtEditor.Clear()
        

    def OnHelpitems0Menu(self, event):
        dlg = Dialog1.create(self)
        try:
            dlg.ShowModal()
        finally:
            dlg.Destroy()
