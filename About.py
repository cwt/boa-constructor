from wxPython.wx   import *
from wxPython.html import *
import wxPython.lib.wxpTag

import __version__
import Preferences, Utils

#"#AC76DE"
about_html = '''
<hmtl>
<body bgcolor="#99ccff">
<center>
<table bgcolor="#FFFFFF" width="100%%">
  <tr>
    <td align="center"><h2><br>
    <img src="%s"><br>
    <font color="#006600">Constructor</font> <font size="-1">v<i>%s</i></font></h2>%s</td>
  </tr>
</table>
%s
</body>
</html>
'''

progress_text = '''
<wxp class="wxStaticText">
  <param name="label" value="-                                                                -">
  <param name="id"    value="%d">
  <param name="style" value="wxALIGN_CENTER">
</wxp>
'''

credits_html = '''
<hmtl>
<body bgcolor="#99ccff">
<center>
<table bgcolor="#FFFFFF" width="100%%">
  <tr>
    <td align="center"><h3>Credits</h3><br>
    <br>
<b>The Boa Team</b><br>
<br>
Riaan Booysen <riaan@e.co.za><br>
Shane Hathaway <shane@digicool.com><br>
Kevin Gill <kevin@telcotek.com><br>
Robert Boulanger <robert@boulanger.de><br>
<p>
<b>Many thanks to</b><br>
<br>
Guido van Rossum and PythonLabs for Python<br>
<br>
wxPython (Robin Dunn) & wxWindows (Julian Smart, Robert Roebling, Vadim Zeitlin, et al.)<br>
<br>
Neil Hodgson for Scintilla<br>
moduleparse.py borrows from pyclbrs.py - standard python library<br>
PythonInterpreter.py by Fredrik Lundh<br>
Debugger based on IDLE's debugger by Guido van Rossum<br>
Mozilla, Delphi, WinCVS for iconic inspirations<br>
Cyclops, ndiff, reindent by Tim Peters<br>
Client.py and the DateTime package from Digital Creations for Zope integration<br>
Kevin Light for reports, fixes and ideas.
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
<p>A RAD GUI building IDE for <b>wxPython</b>
</p>
<p><a href="Boa">http://boa-constructor.sourceforge.net</a><br></u>
&copy;1999-2001 <b>Riaan Booysen</b>. riaan@e.co.za<br>
<a href="Credits">Credits</a>
</p>
<p><font size=-1 color="#000077">wxPlatform: %s %d.%d.%d</font></p>
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

def createSplash(parent):
    return AboutBoxSplash(parent)

def createNormal(parent):
    return AboutBox(parent)

[wxID_ABOUTBOX] = map(lambda _init_ctrls: wxNewId(), range(1))

class AboutBoxMixin:
    def __init__(self, parent):
        self._init_ctrls(parent)

        self.SetBackgroundColour(wxBLACK)
        self.html = Utils.wxUrlClickHtmlWindow(self, -1 )
        Utils.EVT_HTML_URL_CLICK(self.html, self.OnLinkClick)
        self.setPage()
        self.SetAutoLayout(true)
        lc = wxLayoutConstraints()
        lc.top.SameAs(self, wxTop, 5)
        lc.left.SameAs(self, wxLeft, 5)
        lc.bottom.SameAs(self, wxBottom, 5)
        lc.right.SameAs(self, wxRight, 5)
        self.html.SetConstraints(lc)
        self.Layout()
        self.Center(wxBOTH)
        EVT_BUTTON(self, wxID_YES, self.OnNews)
        self.SetAcceleratorTable(wxAcceleratorTable([(0, WXK_ESCAPE, wxID_OK)]))

    def OnNews(self, event):
        self.html.LoadPage('http://boa-constructor.sourceforge.net/News.html')

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
                  Preferences.toPyPath('Images/Shared/PythonPowered.gif'),
                  Preferences.toPyPath('Images/Shared/wxPyButton.png'),
                  Preferences.toPyPath('Images/Shared/wxWinButton.png')))
        elif clicked == 'Back':
            self.setPage()
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


class AboutBox(AboutBoxMixin, wxDialog):
    def _init_ctrls(self, prnt):
        wxDialog.__init__(self, size = wxSize(400,525), pos = (-1, -1), id = wxID_ABOUTBOX, title = 'About Boa Constructor', parent = prnt, name = 'AboutBox', style = wxDEFAULT_DIALOG_STYLE)

    def setPage(self):
        self.html.SetPage((about_html % (Preferences.toPyPath('Images/Shared/Boa.jpg'),
          __version__.ver, '', about_text % (wxPlatform, wxMAJOR_VERSION, wxMINOR_VERSION, wxRELEASE_NUMBER))))

class AboutBoxSplash(AboutBoxMixin, wxFrame):
    def _init_ctrls(self, prnt):
        wxFrame.__init__(self, size = wxSize(400,280), pos = (-1, -1), id = wxID_ABOUTBOX, title = 'Boa Constructor', parent = prnt, name = 'AboutBoxSplash', style = wxSIMPLE_BORDER)
        self.progressId = wxNewId()

    def setPage(self):
        self.html.SetPage(about_html % (Preferences.toPyPath('Images/Shared/Boa.jpg'),
          __version__.ver, progress_text % self.progressId, ''))

        self.label = self.FindWindowById(self.progressId)
        self.label.SetBackgroundColour(wxWHITE)
        sys.stdout = StaticTextPF(self.label)

    def Destroy(self):
        if sys:
            sys.stdout = sys.__stdout__
        wxFrame.Destroy(self)

class StaticTextPF(Utils.PseudoFile):
    def write(self, s):
        ss = string.strip(s)
        if ss:
            self.output.SetLabel(ss)
        if sys:
            sys.__stdout__.write(s)
        wxYield()
