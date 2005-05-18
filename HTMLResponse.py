#Boa:Frame:HTMLResponseFrm

import string

import wx
import wx.html

def create(parent, data):
    return HTMLResponseFrm(parent, data)

[wxID_HTMLRESPONSEFRM, wxID_HTMLRESPONSEFRMHTMLWINDOW, 
 wxID_HTMLRESPONSEFRMNOTEBOOK1, wxID_HTMLRESPONSEFRMTEXTCTRL, 
] = [wx.NewId() for _init_ctrls in range(4)]

class HTMLResponseFrm(wx.Frame):
    def _init_coll_notebook1_Pages(self, parent):
        # generated method, don't edit

        parent.AddPage(imageId=-1, page=self.htmlWindow, select=True,
              text='Response')
        parent.AddPage(imageId=-1, page=self.textCtrl, select=False,
              text='Source')

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_HTMLRESPONSEFRM, name='HTMLResponseFrm',
              parent=prnt, pos=wx.Point(311, 225), size=wx.Size(429, 286),
              style=wx.STAY_ON_TOP | wx.DEFAULT_FRAME_STYLE,
              title='HTML Response')
        self.SetClientSize(wx.Size(421, 259))

        self.notebook1 = wx.Notebook(id=wxID_HTMLRESPONSEFRMNOTEBOOK1,
              name='notebook1', parent=self, pos=wx.Point(0, 0),
              size=wx.Size(421, 259), style=0)

        self.htmlWindow = wx.html.HtmlWindow(id=wxID_HTMLRESPONSEFRMHTMLWINDOW,
              name='htmlWindow', parent=self.notebook1, pos=wx.Point(0, 0),
              size=wx.Size(413, 233))

        self.textCtrl = wx.TextCtrl(id=wxID_HTMLRESPONSEFRMTEXTCTRL,
              name='textCtrl', parent=self.notebook1, pos=wx.Point(0, 0),
              size=wx.Size(413, 233), style=wx.TE_MULTILINE, value='')

        self._init_coll_notebook1_Pages(self.notebook1)

    def __init__(self, parent, data):
        self._init_ctrls(parent)

        # remove zope urls, they don't work :(
        while 1:
            posStart = string.find(data, '"http://')
            if posStart == -1: break
            posEnd = string.find(data, '"', posStart + 1)
            data = data[:posStart]+'"ignoreresource"'+data[posEnd+1:]

        self.htmlWindow.SetPage(data)
        self.textCtrl.SetValue(data)

        self.Center(wx.BOTH)


testResponse = '''Unexpected Zope error value: <html><head><title>ZOA</title></head><body bgcolor="#FFFFFF">


<table border="0" width="100%">
<tr valign="TOP">

<td width="10%" align="center">
<img src="http://localhost:8080/p_/ZButton" alt="Zope">
</td>

<td width="90%">
  <h2>Zope Error</h2>
  <p>Zope has encountered an error while publishing this resource.</p>

  <p>
  <strong>Error Type: SyntaxError</strong><br>
  <strong>Error Value: invalid syntax</strong><br>
  </p>

  <hr noshade>

  <p>Troubleshooting Suggestions</p>

  <ul>
    <li>The URL may be incorrect.</li>
  <li>The parameters passed to this resource may be incorrect.</li>
  <li>A resource that this resource relies on may be encountering an error.</li>
  </ul>

  <p>For more detailed information about the error, please
  refer to the HTML source for this page.
  </p>

  <p>If the error persists please contact the site maintainer.
  Thank you for your patience.
  </p>
</td></tr>
</table>


<p><a href="http://www.zope.org/Credits" target="_top"><img src="http://localhost:8080/p_/ZopeButton" width="115" height="50" border="0" alt="Powered by Zope" /></a></p></body></html>
'''

if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = create(None, testResponse)
    frame.Show(True)
    app.MainLoop()
