#Boa:Frame:ResourceModuleFrm

from wxPython.wx import *

import Boa_img

BoaSectionIcons = ('Palette', 'Editor', 'Designer', 'Inspector', 'Debugger', 
                   'Collection Editor', 'Class Browser', 'Output & Errors',
                   'Help', 'Shell', 'Explorer', 'Zope')

def create(parent):
    return ResourceModuleFrm(parent)

[wxID_RESOURCEMODULEFRM, wxID_RESOURCEMODULEFRMBITMAPBUTTON, 
 wxID_RESOURCEMODULEFRMLISTVIEW, 
] = map(lambda _init_ctrls: wxNewId(), range(3))

[wxID_RESOURCEMODULEFRMTOOLBAR1TOOLS0, wxID_RESOURCEMODULEFRMTOOLBAR1TOOLS1, 
 wxID_RESOURCEMODULEFRMTOOLBAR1TOOLS2, wxID_RESOURCEMODULEFRMTOOLBAR1TOOLS3, 
 wxID_RESOURCEMODULEFRMTOOLBAR1TOOLS4, wxID_RESOURCEMODULEFRMTOOLBAR1TOOLS5, 
 wxID_RESOURCEMODULEFRMTOOLBAR1TOOLS6, 
] = map(lambda _init_coll_toolBar_Tools: wxNewId(), range(7))

class ResourceModuleFrm(wxFrame):
    def _init_coll_images_Images(self, parent):
        # generated method, don't edit

        parent.Add(bitmap=Boa_img.getPaletteBitmap(), mask=wxNullBitmap)
        parent.Add(bitmap=Boa_img.getEditorBitmap(), mask=wxNullBitmap)
        parent.Add(bitmap=Boa_img.getDesignerBitmap(), mask=wxNullBitmap)
        parent.Add(bitmap=Boa_img.getInspectorBitmap(), mask=wxNullBitmap)
        parent.Add(bitmap=Boa_img.getDebuggerBitmap(), mask=wxNullBitmap)
        parent.Add(bitmap=Boa_img.getCollectionEditorBitmap(),
              mask=wxNullBitmap)
        parent.Add(bitmap=Boa_img.getClassBrowserBitmap(), mask=wxNullBitmap)
        parent.Add(bitmap=Boa_img.getOutputErrorBitmap(), mask=wxNullBitmap)
        parent.Add(bitmap=Boa_img.getHelpBitmap(), mask=wxNullBitmap)
        parent.Add(bitmap=Boa_img.getShellBitmap(), mask=wxNullBitmap)
        parent.Add(bitmap=Boa_img.getExplorerBitmap(), mask=wxNullBitmap)
        parent.Add(bitmap=Boa_img.getZopeBitmap(), mask=wxNullBitmap)

    def _init_utils(self):
        # generated method, don't edit
        self.images = wxImageList(height=16, width=16)
        self._init_coll_images_Images(self.images)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxFrame.__init__(self, id=wxID_RESOURCEMODULEFRM,
              name='ResourceModuleFrm', parent=prnt, pos=wxPoint(604, 403),
              size=wxSize(419, 260), style=wxDEFAULT_FRAME_STYLE,
              title='Images using a Resource Module built with img2py')
        self._init_utils()
        self.SetClientSize(wxSize(411, 233))
        self.SetBackgroundColour(wxColour(0, 128, 255))
        self.SetSizeHints(419, 260, 419, 260)
        self.Center(wxBOTH)

        self.bitmapButton = wxBitmapButton(bitmap=Boa_img.getBoaButtonBitmap(),
              id=wxID_RESOURCEMODULEFRMBITMAPBUTTON, name='bitmapButton',
              parent=self, pos=wxPoint(16, 67), size=wxSize(112, 88),
              style=wxBU_AUTODRAW, validator=wxDefaultValidator)
        EVT_BUTTON(self.bitmapButton, wxID_RESOURCEMODULEFRMBITMAPBUTTON,
              self.OnBitmapbuttonButton)

        self.listView = wxListView(id=wxID_RESOURCEMODULEFRMLISTVIEW,
              name='listView', parent=self, pos=wxPoint(148, 27),
              size=wxSize(247, 176), style=wxLC_SINGLE_SEL | wxLC_ICON,
              validator=wxDefaultValidator)
        self.listView.SetImageList(self.images, wxIMAGE_LIST_NORMAL)
        self.listView.SetBackgroundColour(wxColour(255, 255, 242))
        EVT_LIST_ITEM_ACTIVATED(self.listView, wxID_RESOURCEMODULEFRMLISTVIEW,
              self.OnListviewListItemActivated)

    def __init__(self, parent):
        self._init_ctrls(parent)
        for i, name in zip(range(len(BoaSectionIcons)), BoaSectionIcons):
            self.listView.InsertImageStringItem(i, name, i)

    def OnBitmapbuttonButton(self, event):
        self.Close()

    def OnListviewListItemActivated(self, event):
        event.Skip()


if __name__ == '__main__':
    app = wxPySimpleApp()
    wxInitAllImageHandlers()
    frame = create(None)
    frame.Show()

    app.MainLoop()
