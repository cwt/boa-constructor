from wxPython.wx import *
import Preferences

#-----Toolbar-------------------------------------------------------------------

class MyToolBar(wxToolBar):
    def __init__(self, *_args, **_kwargs):
        wxToolBar.__init__(self, _kwargs['parent'], _kwargs['id'],
          style = wxTB_HORIZONTAL|wxNO_BORDER|Preferences.flatTools)
        self.toolLst = []
        self.toolCount = 0

    def AddTool(self, id, bitmap, toggleBitmap = wxNullBitmap, shortHelpString = '', isToggle = false):
        wxToolBar.AddTool(self, id, bitmap, toggleBitmap, isToggle = isToggle,
            shortHelpString = shortHelpString)

        self.toolLst.append(id)
        self.toolCount = self.toolCount + 1

    def AddSeparator(self):
        wxToolBar.AddSeparator(self)
        self.toolLst.append(-1)
        self.toolCount = self.toolCount + 1

    def DeleteTool(self, id):
        wxToolBar.DeleteTool(self, id)
        self.toolLst.remove(id)
        self.toolCount = self.toolCount - 1

    def ClearTools(self):
        posLst = range(self.toolCount)
        posLst.reverse()
        for pos in posLst:
            self.DeleteToolByPos(pos)

        for wid in self.toolLst:
            if wid != -1:
                self.GetParent().Disconnect(wid),
        self.toolLst = []
        self.toolCount = 0

    def GetToolPopupPosition(self, id):
        margins = self.GetToolMargins()
        toolSize = self.GetToolSize()
        xPos = margins.x
        for tId in self.toolLst:
            if tId == id:
                return wxPoint(xPos, margins.y + toolSize.y)

            if tId == -1:
                xPos = xPos + self.GetToolSeparation()
            else:
                xPos = xPos + toolSize.x

        return wxPoint(0, 0)

    def PopupToolMenu(self, toolId, menu):
        self.PopupMenu(menu, self.GetToolPopupPosition(toolId))

class EditorToolBar(MyToolBar):
    pass

class EditorStatusBar(wxStatusBar):
    """ Displays information about the current view. Also global stats/
        progress bar etc. """
    def __init__(self, *_args, **_kwargs):
        wxStatusBar.__init__(self, _kwargs['parent'], _kwargs['id'], style = wxST_SIZEGRIP)
        self.SetFieldsCount(4)
        if wxPlatform == '__WXGTK__':
            imgWidth = 21
        else:
            imgWidth = 16
            
        self.SetStatusWidths([imgWidth, 400, 150, -1])

        rect = self.GetFieldRect(0)
        self.img = wxStaticBitmap(self, -1, wxNullBitmap, 
            (rect.x+1, rect.y+1), (16, 16))

        rect = self.GetFieldRect(2)
        self.progress = wxGauge(self, -1, 100, rect.GetPosition(), rect.GetSize())
        
        self.images = {'Info': Preferences.IS.load('Images/Shared/Info.bmp'),
                       'Warning': Preferences.IS.load('Images/Shared/Warning.bmp'),
                       'Error': Preferences.IS.load('Images/Shared/Error.bmp')}
        
    def setHint(self, hint, msgType = 'Info'):
        self.SetStatusText(hint, 1)
        self.img.SetToolTipString(hint)
        self.img.SetBitmap(self.images[msgType])

    def OnEditorNotification(self, event):
        self.setHint(event.message)
