#Boa:Dialog:CVSResultsDlg

import wx

def create(parent):
    return CVSResultsDlg(parent)

[wxID_CVSRESULTSDLG, wxID_CVSRESULTSDLGBUTTON1, wxID_CVSRESULTSDLGBUTTON2, 
 wxID_CVSRESULTSDLGBUTTON3, wxID_CVSRESULTSDLGTEXTCTRL1, 
] = [wx.NewId() for _init_ctrls in range(5)]

class CVSResultsDlg(wx.Dialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_CVSRESULTSDLG, name='CVSResultsDlg',
              parent=prnt, pos=wx.Point(138, 124), size=wx.Size(488, 323),
              style=wx.DEFAULT_DIALOG_STYLE, title='CVS Results')
        self.SetClientSize(wx.Size(480, 296))

        self.textCtrl1 = wx.TextCtrl(id=wxID_CVSRESULTSDLGTEXTCTRL1,
              name='textCtrl1', parent=self, pos=wx.Point(0, 0),
              size=wx.Size(480, 256), style=0, value='textCtrl1')

        self.button1 = wx.Button(id=wxID_CVSRESULTSDLGBUTTON1, label='Close',
              name='button1', parent=self, pos=wx.Point(176, 264),
              size=wx.Size(72, 24), style=0)

        self.button2 = wx.Button(id=wxID_CVSRESULTSDLGBUTTON2, label='Copy',
              name='button2', parent=self, pos=wx.Point(256, 264),
              size=wx.Size(72, 24), style=0)

        self.button3 = wx.Button(id=wxID_CVSRESULTSDLGBUTTON3,
              label='Decorate open modules', name='button3', parent=self,
              pos=wx.Point(336, 264), size=wx.Size(136, 24), style=0)

    def __init__(self, parent):
        self._init_ctrls(parent)
