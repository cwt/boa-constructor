#----------------------------------------------------------------------
# Name:        Infofields.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     1999
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#----------------------------------------------------------------------
#Boa:Frame:wxFrame1

import wx

def create(parent):
    return wxFrame1(parent)

[wxID_WXFRAME1, wxID_WXFRAME1PANEL1, wxID_WXFRAME1STATICTEXT1, 
 wxID_WXFRAME1STATICTEXT2, wxID_WXFRAME1STATICTEXT3, wxID_WXFRAME1STATICTEXT4, 
 wxID_WXFRAME1STATICTEXT5, wxID_WXFRAME1STATICTEXT6, wxID_WXFRAME1STATICTEXT7, 
 wxID_WXFRAME1TEXTCTRL1, 
] = [wx.NewId() for _init_ctrls in range(10)]

class wxFrame1(wx.Frame):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=-1, name='', parent=prnt, pos=wx.Point(264,
              221), size=wx.Size(322, 258), style=wx.DEFAULT_FRAME_STYLE,
              title='')
        self.SetClientSize(wx.Size(314, 231))

        self.panel1 = wx.Panel(id=193, name='panel1', parent=self,
              pos=wx.Point(0, 0), size=wx.Size(314, 231),
              style=wx.TAB_TRAVERSAL)
        self.panel1.SetClientSize(wx.Size(315, 231))

        self.staticText1 = wx.StaticText(id=223, label='Name:',
              name='staticText1', parent=self.panel1, pos=wx.Point(10, 11),
              size=wx.Size(31, 13), style=0)
        self.staticText1.SetClientSize(wx.Size(31, 13))

        self.staticText2 = wx.StaticText(id=231, label='Purpose:',
              name='staticText2', parent=self.panel1, pos=wx.Point(8, 33),
              size=wx.Size(42, 13), style=0)
        self.staticText2.SetClientSize(wx.Size(42, 13))

        self.staticText3 = wx.StaticText(id=239, label='Author:',
              name='staticText3', parent=self.panel1, pos=wx.Point(10, 77),
              size=wx.Size(34, 13), style=0)
        self.staticText3.SetClientSize(wx.Size(34, 13))

        self.staticText4 = wx.StaticText(id=247, label='Created:',
              name='staticText4', parent=self.panel1, pos=wx.Point(10, 105),
              size=wx.Size(40, 13), style=0)
        self.staticText4.SetClientSize(wx.Size(40, 13))

        self.staticText5 = wx.StaticText(id=255, label='RCS-ID:',
              name='staticText5', parent=self.panel1, pos=wx.Point(12, 134),
              size=wx.Size(39, 13), style=0)
        self.staticText5.SetClientSize(wx.Size(39, 13))

        self.staticText6 = wx.StaticText(id=263, label='Copyright:',
              name='staticText6', parent=self.panel1, pos=wx.Point(13, 157),
              size=wx.Size(47, 13), style=0)
        self.staticText6.SetClientSize(wx.Size(47, 13))

        self.staticText7 = wx.StaticText(id=271, label='Licence:',
              name='staticText7', parent=self.panel1, pos=wx.Point(13, 184),
              size=wx.Size(41, 13), style=0)
        self.staticText7.SetClientSize(wx.Size(41, 13))

        self.textCtrl1 = wx.TextCtrl(id=280, name='textCtrl1',
              parent=self.panel1, pos=wx.Point(68, 8), size=wx.Size(198, 17),
              style=0, value='textCtrl1')
        self.textCtrl1.SetClientSize(wx.Size(194, 13))

    def __init__(self, parent):
        self._init_utils()
        self._init_ctrls(parent)
