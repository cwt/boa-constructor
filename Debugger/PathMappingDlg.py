#Boa:Dialog:PathsMappingDlg

import pprint 

from wxPython.wx import *

from PathsPanel import PathsPanel

def create(parent):
    return PathsMappingDlg(parent)

[wxID_PATHSMAPPINGDLG, wxID_PATHSMAPPINGDLGCANCELBTN, 
 wxID_PATHSMAPPINGDLGOKBTN, wxID_PATHSMAPPINGDLGPATHSPANEL, 
] = map(lambda _init_ctrls: wxNewId(), range(4))

class PathsMappingDlg(wxDialog):
    _custom_classes = {'wxPanel': ['PathsPanel']}
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_PATHSMAPPINGDLG, name='PathsMappingDlg',
              parent=prnt, pos=wxPoint(345, 257), size=wxSize(487, 233),
              style=wxDEFAULT_DIALOG_STYLE,
              title='Edit client/sever paths mapping')
        self.SetClientSize(wxSize(479, 206))

        self.pathsPanel = PathsPanel(id=wxID_PATHSMAPPINGDLGPATHSPANEL,
              name='pathsPanel', parent=self, pos=wxPoint(0, 0),
              size=wxSize(480, 152), style=wxTAB_TRAVERSAL)

        self.okBtn = wxButton(id=wxID_OK, label='OK', name='okBtn', parent=self,
              pos=wxPoint(312, 168), size=wxSize(75, 23), style=0)
        EVT_BUTTON(self.okBtn, wxID_PATHSMAPPINGDLGOKBTN, self.OnOkbtnButton)

        self.cancelBtn = wxButton(id=wxID_CANCEL, label='Cancel',
              name='cancelBtn', parent=self, pos=wxPoint(392, 168),
              size=wxSize(75, 23), style=0)

    def __init__(self, parent, paths):
        self._init_ctrls(parent)
        
        self.pathsPanel.init_paths(paths)

        import Utils
        self.conf = Utils.createAndReadConfig('Explorer')
        self.writeConfig = Utils.writeConfig

    def OnOkbtnButton(self, event):
        if self.conf:
            paths = self.pathsPanel.read_paths()
            
            if self.conf.has_section('debugger.remote'):
                self.conf.set('debugger.remote', 'paths', pprint.pformat(paths))
                self.writeConfig(self.conf)
                
        self.EndModal(wxID_OK)


def showPathsMappingDlg(parent, paths):
    dlg = PathsMappingDlg(parent, paths)
    try:
        if dlg.ShowModal() != wxID_OK:
            return None
        else:
            return dlg.pathsPanel.read_paths()
    finally:
        dlg.Destroy()



if __name__ == '__main__':
    app = wxPySimpleApp()
    wxInitAllImageHandlers()
    print showPathsMappingDlg(None, [('1', '2'), ('3', '4')])
    app.MainLoop()
