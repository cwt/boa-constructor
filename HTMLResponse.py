#Boa:Frame:HTMLResponseFrm

from wxPython.wx import *
from wxPython.html import *

def create(parent, data):
    return HTMLResponseFrm(parent, data)

[wxID_HTMLRESPONSEFRMHTMLWINDOW, wxID_HTMLRESPONSEFRMTEXTCTRL, wxID_HTMLRESPONSEFRMNOTEBOOK1, wxID_HTMLRESPONSEFRM] = map(lambda _init_ctrls: wxNewId(), range(4))

class HTMLResponseFrm(wxFrame):
    def _init_coll_notebook1_Pages(self, parent):

        parent.AddPage(strText = 'Response', bSelect = true, pPage = self.htmlWindow, imageId = -1)
        parent.AddPage(strText = 'Source', bSelect = false, pPage = self.textCtrl, imageId = -1)

    def _init_utils(self): 
        pass

    def _init_ctrls(self, prnt): 
        wxFrame.__init__(self, size = wxSize(459, 486), id = wxID_HTMLRESPONSEFRM, title = 'HTML Response', parent = prnt, name = 'HTMLResponseFrm', style = wxSTAY_ON_TOP | wxDEFAULT_FRAME_STYLE, pos = wxPoint(311, 225))
        self._init_utils()

        self.notebook1 = wxNotebook(size = wxSize(451, 459), id = wxID_HTMLRESPONSEFRMNOTEBOOK1, parent = self, name = 'notebook1', style = 0, pos = wxPoint(0, 0))

        self.htmlWindow = wxHtmlWindow(size = wxSize(443, 433), parent = self.notebook1, pos = wxPoint(0, 0), name = 'htmlWindow', id = wxID_HTMLRESPONSEFRMHTMLWINDOW)

        self.textCtrl = wxTextCtrl(size = wxSize(443, 433), value = '', pos = wxPoint(0, 0), parent = self.notebook1, name = 'textCtrl', style = wxTE_MULTILINE, id = wxID_HTMLRESPONSEFRMTEXTCTRL)

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
        
        self.Center(wxBOTH)
    

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
    app = wxPySimpleApp()
    frame = create(None, testResponse)
    frame.Show(true)
    app.MainLoop()