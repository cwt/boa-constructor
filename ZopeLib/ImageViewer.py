#Boa:MiniFrame:ImageViewer

from wxPython.wx import *
import os, string, tempfile

def create(parent):
    return ImageViewer(parent)

imgs = {'.bmp' : wxBITMAP_TYPE_BMP,
        '.gif' : wxBITMAP_TYPE_GIF,
        '.png' : wxBITMAP_TYPE_PNG,
        '.jpg' : wxBITMAP_TYPE_JPEG}

[wxID_IMAGEVIEWER, wxID_IMAGEVIEWERSASHWINDOW1, wxID_IMAGEVIEWERSTATICBITMAP1] = map(lambda _init_ctrls: wxNewId(), range(3))

class ImageViewer(wxMiniFrame):
    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxMiniFrame.__init__(self, id = wxID_IMAGEVIEWER, name = 'ImageViewer', parent = prnt, pos = wxPoint(401, 286), size = wxSize(32, 32), style = wxDEFAULT_FRAME_STYLE | wxSTAY_ON_TOP, title = 'Image viewer')
        self._init_utils()
        self.SetClientSize(wxSize(32, 32))

        self.sashWindow1 = wxSashWindow(id = wxID_IMAGEVIEWERSASHWINDOW1, name = 'sashWindow1', parent = self, pos = wxPoint(0, 0), size = wxSize(221, 185), style = wxSW_BORDER | wxTHICK_FRAME | wxSW_3D)
        self.sashWindow1.SetExtraBorderSize(self.borderSize)
        self.sashWindow1.SetMinimumSizeX(24)
        self.sashWindow1.SetMinimumSizeY(24)
        EVT_SIZE(self.sashWindow1, self.OnSashwindow1Size)

        self.staticBitmap1 = wxStaticBitmap(bitmap = wxNullBitmap, id = wxID_IMAGEVIEWERSTATICBITMAP1, name = 'staticBitmap1', parent = self.sashWindow1, pos = wxPoint(9, 9), size = wxSize(203, 167), style = 0)

    def __init__(self, parent, doubleClickCallback=None):
        self.borderSize = 9
        self._init_utils()
        self._init_ctrls(parent)
        self.Centre(wxBOTH)
        
        if doubleClickCallback:
            EVT_LEFT_DCLICK(self.staticBitmap1, doubleClickCallback)

    def showImage(self, filename, node = None):
        if node is not None:
            fn = tempfile.mktemp(os.path.splitext(node.name)[-1])
            open(fn, 'wb').write(node.load())
        else:
            fn = filename

        self.SetTitle('Image Viewer - %s' %(os.path.basename(fn)))
        bmp = wxImage(fn, imgs[string.lower(os.path.splitext(fn)[-1])]).ConvertToBitmap()
        self.sashWindow1.SetClientSize(wxSize(bmp.GetWidth()+self.borderSize*2,
                                              bmp.GetHeight()+self.borderSize*2))
        self.SetClientSize(self.sashWindow1.GetSize())
        self.staticBitmap1.SetBitmap(bmp)

        if node is not None:
            os.remove(fn)

        self.Centre(wxBOTH)
        self.Show(true)

    def OnSashwindow1Size(self, event):
        self.sashWindow1.Refresh()
        #self.staticBitmap1.Refresh()
        event.Skip()


if __name__ == '__main__':
    app = wxPySimpleApp()
    wxInitAllImageHandlers()
    frame = create(None)
    frame.Show(true)
    frame.showImage('../Images/Modules/wxFrame_s.png')
    app.MainLoop()
