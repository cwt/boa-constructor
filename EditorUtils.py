from wxPython.wx import *
import Preferences

#-----Toolbar-------------------------------------------------------------------

class MyToolBar(wxToolBar):
    def __init__(self, parent, winid):
        wxToolBar.__init__(self, parent, winid,
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
    def __init__(self, parent):
        wxStatusBar.__init__(self, parent, -1, style = wxST_SIZEGRIP)
        self.SetFieldsCount(4)
        self.SetStatusWidths([16, 400, 150, -1])#30, 30,

        self.h = self.GetClientSize().y

#        self.col = wxStaticText(self, -1, '0   ', wxPoint(3, 4))
#        self.row = wxStaticText(self, -1, '0   ', wxPoint(37, 4))
        self.hint = wxStaticText(self, -1, ' ', wxPoint(28, 4),
          wxSize(390, self.h -5), style = wxST_NO_AUTORESIZE | wxALIGN_LEFT)
        self.progress = wxGauge(self, -1, 100,
          pos = wxPoint(422+Preferences.editorProgressFudgePosX, 2),
          size = wxSize(150, self.h -2 + Preferences.editorProgressFudgeSizeY))
        self.img = wxStaticBitmap(self, -1, wxNullBitmap, (1, 3), (16, 16))
        
        self.images = {'Info': Preferences.IS.load('Images/Shared/Info.bmp'),
                       'Warning': Preferences.IS.load('Images/Shared/Warning.bmp'),
                       'Error': Preferences.IS.load('Images/Shared/Error.bmp')}
        
    def setHint(self, hint, msgType = 'Info'):
        self.hint.SetLabel(hint)
        self.hint.SetSize(wxSize(390, self.h -5))
        self.hint.SetToolTipString(hint)
        self.img.SetBitmap(self.images[msgType])

    def OnEditorNotification(self, event):
        self.setHint(event.message)
