from wxPython.wx import *
from wxPython.lib.activexwrapper import MakeActiveXClass
import win32com.client.gencache

acrobatModule = win32com.client.gencache.EnsureModule('{CA8A9783-280D-11CF-A24D-444553540000}', 0x0, 1, 3)

wxComPdfPtr = MakeActiveXClass(acrobatModule.Pdf)
class wxComPdf(wxComPdfPtr):
    def __init__(self, parent = None, id = -1, pos=wxDefaultPosition, size=wxDefaultSize, style=0, name=''):
        wxComPdfPtr.__init__(self, parent, id, pos, size, style)
        self.SetName(name)
