#Boa:Dialog:Dialog1

import wx

def create(parent):
    return Dialog1(parent)

[wxID_DIALOG1, wxID_DIALOG1BUTTON1, wxID_DIALOG1STATICBITMAP1, 
 wxID_DIALOG1STATICTEXT1, wxID_DIALOG1STATICTEXT2, 
] = [wx.NewId() for _init_ctrls in range(5)]

class Dialog1(wx.Dialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_DIALOG1, name='Dialog1', parent=prnt,
              pos=wx.Point(472, 330), size=wx.Size(328, 379),
              style=wx.DEFAULT_DIALOG_STYLE, title='About Notebook')
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.SetClientSize(wx.Size(320, 352))

        self.staticText1 = wx.StaticText(id=wxID_DIALOG1STATICTEXT1,
              label='Note Book - Simple Text Editor', name='staticText1',
              parent=self, pos=wx.Point(48, 24), size=wx.Size(216, 20),
              style=wx.ALIGN_CENTRE)
        self.staticText1.SetFont(wx.Font(12, 74, 90, 90, 0, 'MS Sans Serif'))
        self.staticText1.SetBackgroundColour(wx.Colour(255, 255, 255))

        self.staticText2 = wx.StaticText(id=wxID_DIALOG1STATICTEXT2,
              label='This is my first Boa Constructor Application',
              name='staticText2', parent=self, pos=wx.Point(56, 72),
              size=wx.Size(199, 13), style=wx.ALIGN_CENTRE)
        self.staticText2.SetBackgroundColour(wx.Colour(64, 128, 128))

        self.staticBitmap1 = wx.StaticBitmap(bitmap=wx.Bitmap('Boa.jpg',
              wx.BITMAP_TYPE_JPEG), id=wxID_DIALOG1STATICBITMAP1,
              name='staticBitmap1', parent=self, pos=wx.Point(48, 104),
              size=wx.Size(236, 157), style=0)

        self.button1 = wx.Button(id=wxID_DIALOG1BUTTON1, label='button1',
              name='button1', parent=self, pos=wx.Point(120, 296),
              size=wx.Size(72, 24), style=0)
        self.button1.SetTitle('Close')
        self.button1.Bind(wx.EVT_BUTTON, self.OnButton1Button,
              id=wxID_DIALOG1BUTTON1)

    def __init__(self, parent):
        self._init_ctrls(parent)

    def OnButton1Button(self, event):
        self.Close()
