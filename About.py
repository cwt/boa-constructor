#-----------------------------------------------------------------------------
# Name:        About.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2000
# RCS-ID:      $Id$
# Copyright:   (c) 2000 - 2003
# Licence:     GPL
#-----------------------------------------------------------------------------

import sys, time, re, string
from thread import start_new_thread

from wxPython.wx   import *
from wxPython.html import *
import wxPython
import wxPython.lib.wxpTag

import __version__
import Preferences, Utils

# XXX Replace img tags with wxpTags/wxStaticBitmap controls and load from
# XXX ImageStore

prog_update = re.compile('<<(?P<cnt>[0-9]+)/(?P<tot>[0-9]+)>>')

about_html = '''
<html>
<body bgcolor="#99ccff">
<center>
<table cellpadding="5" bgcolor="#FFFFFF" width="100%%">
  <tr>
    <td align="center"><br>
    <img src="%s"><br>
    <font color="#006600" size="+4"><b>Constructor</b></font><br><strong>v%s</strong>%s</td>
  </tr>
</table>
%s
</body>
</html>
'''
progress_text = '''<p>
<wxp class="wxStaticText">
  <param name="label" value="  ">
  <param name="id"    value="%d">
  <param name="style" value="wxALIGN_CENTER | wxCLIP_CHILDREN | wxST_NO_AUTORESIZE">
  <param name="size"  value="wxSize(352, 20)">
</wxp>
<wxp class="wxWindow">
  <param name="id"    value="%d">
  <param name="size"  value="wxSize(352, 16)">
</wxp>'''


credits_html = '''
<html>
<body bgcolor="#99ccff">
<center>
<table bgcolor="#FFFFFF" width="100%%">
  <tr>
    <td align="center"><h3>Credits</h3><br>
    <br>
<b>The Boa Team</b><br>
<br>
Riaan Booysen (riaan@e.co.za)<p>
Shane Hathaway (shane@digicool.com)<br>
Kevin Gill (kevin@telcotek.com)<br>
Robert Boulanger (robert@boulanger.de)<br>
Tim Hochberg (tim.hochberg@ieee.org)<br>
Kevin Light (klight@walkertechnical.com)<br>
<p>
<b>Many thanks to</b><br>
<br>
Guido van Rossum and PythonLabs for Python<br>
<br>
wxPython (Robin Dunn) & wxWindows (Julian Smart, Robert Roebling, Vadim Zeitlin, et al.)<br>
Neil Hodgson for Scintilla<br>
<br>
moduleparse.py borrows from pyclbrs.py - standard python library<br>
PythonInterpreter.py by Fredrik Lundh<br>
Debugger based on IDLE's debugger by Guido van Rossum<br>
Mozilla, Delphi, WinCVS for iconic inspirations<br>
Cyclops, ndiff, reindent by Tim Peters<br>
Client.py, WebDAV, DateTime package and the Zope Book from Zope Corporation for Zope integration<br>
PyChecker by Neal Norwitz & Eric C. Newton<br>
py2exe by Thomas Heller<br>
babeliser.py by Jonathan Feinberg and Babelfish for translation<br>
David Adams' Speller, an xml-rpc spellchecker server<br>
Jeff Sasmor for wxStyledTextCtrl docs<br>
Hernan M. Foffani for ZopeShelf from which the Zope Book was converted<br>
<p>
Mike Fletcher for reports, ideas and patches (MakePy dialog and much improved UML layout)<br>
<p>
<b>Boa interfaces with the following external applications, thanks to their authors</b><br>
Zope, CVS, SSH, SCP<br>
<p>
Last but not least, a very big thank you to <a href="TBS">Tangible Business Software</a> for partially
sponsoring my time on this project.<br>
<p>
<b>Boa Constructor is built on:</b><br>
<a href="Python"><img src="%s"></a>&nbsp;
<a href="wxPython"><img src="%s"></a>&nbsp;
<a href="wxWindows"><img src="%s"></a><br>
<br>
<a href="Back">Back</a><br>
    </td>
  </tr>
</table>
</body>
</html>
'''

about_text = '''
<p>A <b>Python</b> IDE and <b>wxPython</b> GUI builder
</p>
<p><a href="Boa">http://boa-constructor.sourceforge.net</a><br></u>
&copy;1999-2003 <b>Riaan Booysen</b>. <a href="MailMe">riaan@e.co.za</a><br>
<a href="Credits">Credits</a>
</p>
<p><font size=-1 color="#000077">Python %s</font><br>
<font size=-1 color="#000077">wxPlatform: %s %s</font></p>
<hr>
<wxp class="wxButton">
  <param name="label" value="Okay">
  <param name="id"    value="wxID_OK">
</wxp>
</center>
<br><br>
<p>
<p>
<center>
<font size=-1><i>for <font color="#AA0000"><b>Bonnie</b></font></i></font>
</center>
</p>
</p>
'''

def createSplash(parent, modTot, fileTot):
    return AboutBoxSplash(parent, modTot, fileTot)

def createNormal(parent):
    return AboutBox(parent)

[wxID_ABOUTBOX] = map(lambda _init_ctrls: wxNewId(), range(1))

class AboutBoxMixin:
    border = 7
    def __init__(self, parent, modTot=0, fileTot=0):
        self._init_ctrls(parent)

        self.moduleTotal = modTot
        self.fileTotal = fileTot

        self.blackback = wxWindow(self, -1, pos=(0, 0),
              size=self.GetClientSize(), style=wxCLIP_CHILDREN)
        self.blackback.SetBackgroundColour(wxBLACK)

        self.html = Utils.wxUrlClickHtmlWindow(self.blackback)#, -1, style=wxCLIP_CHILDREN)
        Utils.EVT_HTML_URL_CLICK(self.html, self.OnLinkClick)
        self.setPage()
        self.blackback.SetAutoLayout(true)
        lc = wxLayoutConstraints()
        lc.top.SameAs(self.blackback, wxTop, self.border)
        lc.left.SameAs(self.blackback, wxLeft, self.border)
        lc.bottom.SameAs(self.blackback, wxBottom, self.border)
        lc.right.SameAs(self.blackback, wxRight, self.border)
        self.html.SetConstraints(lc)
        self.blackback.Layout()
        self.Center(wxBOTH)
        self.SetAcceleratorTable(wxAcceleratorTable([(0, WXK_ESCAPE, wxID_OK)]))

    def gotoInternetUrl(self, url):
        try:
            import webbrowser
        except ImportError:
            wxMessageBox('Please point your browser at: %s' % url)
        else:
            webbrowser.open(url)

    def OnLinkClick(self, event):
        clicked = event.linkinfo[0]
        if clicked == 'Credits':
            self.html.SetPage(credits_html % (
                  Utils.toPyPath('Images/Shared/PythonPowered.gif'),
                  Utils.toPyPath('Images/Shared/wxPyButton.png'),
                  Utils.toPyPath('Images/Shared/wxWinButton.png')))
        elif clicked == 'Back':
            self.setPage()
            #self.html.HistoryBack()
        elif clicked == 'Python':
            self.gotoInternetUrl('http://www.python.org')
        elif clicked == 'wxPython':
            self.gotoInternetUrl('http://wxpython.org')
        elif clicked == 'wxWindows':
            self.gotoInternetUrl('http://www.wxwindows.org')
        elif clicked == 'Boa':
            self.gotoInternetUrl('http://boa-constructor.sourceforge.net')
        elif clicked == 'TBS':
            self.gotoInternetUrl('http://www.tbs.co.za')
        elif clicked == 'MailMe':
            self.gotoInternetUrl('mailto:riaan@e.co.za')


class AboutBox(AboutBoxMixin, wxDialog):
    def _init_ctrls(self, prnt):
        wxDialog.__init__(self, size=wxSize(410, 545), pos=(-1, -1),
              id=wxID_ABOUTBOX, title='About Boa Constructor', parent=prnt,
              name='AboutBox', style=wxDEFAULT_DIALOG_STYLE)

    def setPage(self):
        self.html.SetPage((about_html % (
              Utils.toPyPath('Images/Shared/Boa.jpg'), __version__.version,
              '', about_text % (sys.version, wxPlatform, wxPython.__version__))))
DefAboutBox = AboutBox

class AboutBoxSplash(AboutBoxMixin, wxFrame):
    progressBorder = 2
    fileOpeningFactor = 10
    def _init_ctrls(self, prnt):
        wxFrame.__init__(self, size=wxSize(410, 320), pos=(-1, -1),
              id=wxID_ABOUTBOX, title='Boa Constructor', parent=prnt,
              name='AboutBoxSplash', style=wxSIMPLE_BORDER)
        self.progressId = wxNewId()
        self.gaugePId = wxNewId()
        self.SetBackgroundColour(wxColour(0x99, 0xcc, 0xff))

    def setPage(self):
        self.html.SetPage(about_html % (Utils.toPyPath('Images/Shared/Boa.jpg'),
          __version__.version, progress_text % (self.progressId, self.gaugePId), ''))

        self.label = self.FindWindowById(self.progressId)
        self.label.SetBackgroundColour(wxWHITE)
        parentWidth = self.label.GetParent().GetClientSize().x
        self.label.SetSize((parentWidth - 40, self.label.GetSize().y))

        gaugePrnt = self.FindWindowById(self.gaugePId)
        gaugePrnt.SetBackgroundColour(wxColour(0x99, 0xcc, 0xff))
        gaugeSze = gaugePrnt.GetClientSize()
        self.gauge = wxGauge(gaugePrnt, -1,
              range=self.moduleTotal+self.fileTotal*self.fileOpeningFactor,
              style=wxGA_HORIZONTAL|wxGA_SMOOTH,
              pos=(self.progressBorder, self.progressBorder),
              size=(gaugeSze.x - 2 * self.progressBorder,
                    gaugeSze.y - 2 * self.progressBorder))
        self.gauge.SetBackgroundColour(wxColour(0xff, 0x33, 0x00))
        # route all printing thru the text on the splash screen
        sys.stdout = StaticTextPF(self.label)
        start_new_thread(self.monitorModuleCount, ())

        EVT_MOD_CNT_UPD(self, self.OnUpdateProgress)

    def monitorModuleCount(self):
        self._live = true
        lastCnt = 0
        if sys and len(sys.modules) >= self.moduleTotal:
            wx.wxPostEvent(self, ModCntUpdateEvent(self.moduleTotal, 'importing'))
        else:
            while self._live and sys and len(sys.modules) < self.moduleTotal:
                mc = len(sys.modules)
                if mc > lastCnt:
                    lastCnt = mc
                    wx.wxPostEvent(self, ModCntUpdateEvent(mc, 'importing'))
                time.sleep(0.125)

    def Destroy(self):
        self._live = false
        self.gauge = None

        if sys:
            sys.stdout = sys.__stdout__
        wxFrame.Destroy(self)

    def OnUpdateProgress(self, event):
        self._live = event.tpe == 'importing' and self._live
        if self.gauge:
            cnt = event.cnt
            if event.tpe == 'opening':
                cnt = cnt * self.fileOpeningFactor + self.moduleTotal
            self.gauge.SetValue(min(self.gauge.GetRange(), cnt))

class StaticTextPF(Utils.PseudoFile):
    def write(self, s):
        if not wxThread_IsMain():
            locker = wxMutexGuiLocker()

        res = prog_update.search(s)
        if res:
            cnt = int(res.group('cnt'))
            wx.wxPostEvent(self.output.GetGrandParent().GetParent(),
                  ModCntUpdateEvent(cnt, 'opening'))
            s = s[:res.start()]

        ss = string.strip(s)
        if ss:
            self.output.SetLabel(ss)

        if sys:
            sys.__stdout__.write(s)
        wxYield()

wxEVT_MOD_CNT_UPD = wxNewId()

def EVT_MOD_CNT_UPD(win, func):
    win.Connect(-1, -1, wxEVT_MOD_CNT_UPD, func)

class ModCntUpdateEvent(wxPyEvent):
    def __init__(self, cnt, tpe):
        wxPyEvent.__init__(self)
        self.SetEventType(wxEVT_MOD_CNT_UPD)
        self.cnt = cnt
        self.tpe = tpe

if __name__ == '__main__':
    app = wxPySimpleApp()
    wxInitAllImageHandlers()
    frame = createNormal(None)
    frame.ShowModal()
