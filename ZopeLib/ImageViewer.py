#Boa:MiniFrame:ImageViewer

from wxPython.wx import *
import os, string

def create(parent):
    return ImageViewer(parent)

imgs = {'.bmp' : wxBITMAP_TYPE_BMP,
        '.gif' : wxBITMAP_TYPE_GIF,
        '.png' : wxBITMAP_TYPE_PNG,
        '.jpg' : wxBITMAP_TYPE_JPEG}

[wxID_IMAGEVIEWER, wxID_IMAGEVIEWERSTATICBITMAP1] = map(lambda _init_ctrls: NewId(), range(2))

class ImageViewer(wxMiniFrame):
    def _init_utils(self): 
        pass

    def _init_ctrls(self, prnt): 
        wxMiniFrame.__init__(self, size = wxSize(446, 282), id = wxID_IMAGEVIEWER, title = 'Image viewer', parent = prnt, name = 'ImageViewer', style = wxDEFAULT_FRAME_STYLE | wxSTAY_ON_TOP, pos = wxPoint(357, 303))

        self.staticBitmap1 = wxStaticBitmap(bitmap = wxNullBitmap, id = wxID_IMAGEVIEWERSTATICBITMAP1, parent = self, name = 'staticBitmap1', size = wxDefaultSize, style = 0, pos = wxPoint(8, 8))

    def __init__(self, parent): 
        self._init_utils()
        self._init_ctrls(parent)
        self.Centre(wxBOTH)

    def showImage(self, filename):
        self.SetTitle('Image Viewer - %s' %(os.path.basename(filename)))
        bmp = wxImage(filename, imgs[string.lower(os.path.splitext(filename)[1])]).ConvertToBitmap()
        self.SetClientSize(wxSize(bmp.GetWidth(), bmp.GetHeight())) 
        self.staticBitmap1.SetBitmap(bmp)
            
        self.Centre(wxBOTH)
        self.Show(true)

    def OnCloseWindow(self, event):
        self.Show(false)
        
