from BaseCompanions import WindowDTC
from EventCollections import *
import PaletteStore

PaletteStore.paletteLists['COM'] = []

class ComCtrlDTC(WindowDTC):
    GUID = '{00000000-0000-0000-0000-000000000000}'
    comModule = 'comModule'
    comImports = 'ComImports'

    def writeImports(self):
        return 'from wxPython.lib.bcrtl.activex.%s import %s' % (self.comModule, self.comImports)
    
    def designTimeControl(self, position, size, args = None):
        dtc = WindowDTC.designTimeControl(self, position, size, args)
        dtc.Enable(false)
        return dtc

# Com objects are individually tested and added (or not) to the palette so that
# only components which are installed on the user's machine will be added to 
# the Palette 

# Acrobat PDF control
try:
    from wxPython.lib.bcrtl.activex.acrobat import wxComPdf
except ImportError, error:
    print 'Acrobat not registered', error
else:
    class PdfComCDTC(ComCtrlDTC):
        GUID = '{CA8A9783-280D-11CF-A24D-444553540000}'
        comModule = 'acrobat'
        comImports = 'wxComPdf'
    
    PaletteStore.paletteLists['COM'].append(wxComPdf)
    PaletteStore.compInfo[wxComPdf] = ['AcrobatPdf', PdfComCDTC]

# Internet Explorer webbrowser
try:
    from wxPython.lib.bcrtl.activex.IE import *
except ImportError, error:    
    print 'Internet Explorer not registered', error
else:
    EventCategories['WebBrowserEvent'] = (EVT_CWB_BEFORENAVIGATE, 
     EVT_CWB_TITLECHANGE, EVT_CWB_DOWNLOADBEGIN, EVT_CWB_PROPERTYCHANGE, 
     EVT_CWB_COMMANDSTATECHANGE, EVT_CWB_FRAMEBEFORENAVIGATE, 
     EVT_CWB_WINDOWACTIVATE, EVT_CWB_NEWWINDOW, EVT_CWB_DOWNLOADCOMPLETE, 
     EVT_CWB_WINDOWRESIZE, EVT_CWB_WINDOWMOVE, EVT_CWB_PROGRESSCHANGE, 
     EVT_CWB_FRAMENEWWINDOW, EVT_CWB_STATUSTEXTCHANGE,
     EVT_CWB_FRAMENAVIGATECOMPLETE, EVT_CWB_QUIT, EVT_CWB_NAVIGATECOMPLETE,
    )
     
    class WebBrowserComCDTC(ComCtrlDTC):
        GUID = '{EAB22AC0-30C1-11CF-A7EB-0000C05BAE0B}'
        comModule = 'IE'
        comImports = '*'
        def events(self):
            return ComCtrlDTC.events(self) + ['WebBrowserEvent']
    
    PaletteStore.paletteLists['COM'].append(wxComWebBrowser)
    PaletteStore.compInfo[wxComWebBrowser] = ['IEWebBrowser', WebBrowserComCDTC]



# If any controls successfully installed add the page to the Palette 
if len(PaletteStore.paletteLists['COM']):
    PaletteStore.palette.append(['COM', 'Editor/Tabs/COM', PaletteStore.paletteLists['COM']])
    