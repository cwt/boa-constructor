#Boa:Dialog:CreationOrderDlg

from wxPython.wx import *
from wxPython.help import *

import Preferences, Utils

def create(parent):
    return CreationOrderDlg(parent)

[wxID_CREATIONORDERDLG, wxID_CREATIONORDERDLGBBDOWN, wxID_CREATIONORDERDLGBBUP, wxID_CREATIONORDERDLGBTCANCEL, wxID_CREATIONORDERDLGBTOK, wxID_CREATIONORDERDLGCONTEXTHELPBUTTON1, wxID_CREATIONORDERDLGLBOBJECTS, wxID_CREATIONORDERDLGPANEL1, wxID_CREATIONORDERDLGSTATICBOX1] = map(lambda _init_ctrls: wxNewId(), range(9))

class CreationOrderDlg(wxDialog):
    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxDialog.__init__(self, id = wxID_CREATIONORDERDLG, name = 'CreationOrderDlg', parent = prnt, pos = wxPoint(230, 132), size = wxSize(280, 281), style = wxDEFAULT_DIALOG_STYLE, title = 'Change creation order')
        self._init_utils()
        self.SetClientSize(wxSize(272, 254))

        self.panel1 = wxPanel(id = wxID_CREATIONORDERDLGPANEL1, name = 'panel1', parent = self, pos = wxPoint(0, 0), size = wxSize(272, 254), style = wxTAB_TRAVERSAL)
        self.panel1.SetHelpText('This dialog manages the order of controls on the level (share a parent). When the parent is recreated, the onjects will be recreated in the new order.')

        self.staticBox1 = wxStaticBox(id = wxID_CREATIONORDERDLGSTATICBOX1, label = 'Current creation/tab order', name = 'staticBox1', parent = self.panel1, pos = wxPoint(8, 0), size = wxSize(256, 208), style = 0)

        self.lbObjects = wxListBox(choices = [], id = wxID_CREATIONORDERDLGLBOBJECTS, name = 'lbObjects', parent = self.panel1, pos = wxPoint(16, 16), size = wxSize(200, 184), style = 0, validator = wxDefaultValidator)

        self.bbUp = wxBitmapButton(bitmap = self.bmpUp, id = wxID_CREATIONORDERDLGBBUP, name = 'bbUp', parent = self.panel1, pos = wxPoint(224, 72), size = wxSize(24, 24), style = wxBU_AUTODRAW, validator = wxDefaultValidator)
        EVT_BUTTON(self.bbUp, wxID_CREATIONORDERDLGBBUP, self.OnBbupButton)

        self.bbDown = wxBitmapButton(bitmap = self.bmpDown, id = wxID_CREATIONORDERDLGBBDOWN, name = 'bbDown', parent = self.panel1, pos = wxPoint(224, 104), size = wxSize(24, 24), style = wxBU_AUTODRAW, validator = wxDefaultValidator)
        EVT_BUTTON(self.bbDown, wxID_CREATIONORDERDLGBBDOWN, self.OnBbdownButton)

        self.btOK = wxButton(id = wxID_CREATIONORDERDLGBTOK, label = 'OK', name = 'btOK', parent = self.panel1, pos = wxPoint(112, 224), size = wxSize(72, 24), style = 0)
        EVT_BUTTON(self.btOK, wxID_CREATIONORDERDLGBTOK, self.OnBtokButton)

        self.btCancel = wxButton(id = wxID_CREATIONORDERDLGBTCANCEL, label = 'Cancel', name = 'btCancel', parent = self.panel1, pos = wxPoint(192, 224), size = wxSize(72, 24), style = 0)
        EVT_BUTTON(self.btCancel, wxID_CREATIONORDERDLGBTCANCEL, self.OnBtcancelButton)

        self.contextHelpButton1 = wxContextHelpButton(parent = self.panel1, pos = wxPoint(8, 229), size = wxSize(20, 19), style = wxBU_AUTODRAW)

    def __init__(self, parent, controls, allctrls):
        self.bmpUp = Preferences.IS.load('Images/Shared/up.png')
        self.bmpDown = Preferences.IS.load('Images/Shared/down.png')
        self._init_ctrls(parent)

        self.ctrlIdxs, self.ctrlNames = [], []
        controls.sort()
        for idx, name in controls:
            self.ctrlIdxs.append(idx)
            self.ctrlNames.append(name)

        self.allCtrlIdxs, self.allCtrlNames = [], []
        allctrls.sort()
        for idx, name in allctrls:
            self.allCtrlIdxs.append(idx)
            self.allCtrlNames.append(name)

        self.lbObjects.InsertItems(self.ctrlNames, 0)

    def OnBbupButton(self, event):
        selIdx = self.lbObjects.GetSelection()
        if selIdx < 0: return
        newIdx = max(0, selIdx - 1)

        self.moveObject(selIdx, newIdx)

    def OnBbdownButton(self, event):
        selIdx = self.lbObjects.GetSelection()
        if selIdx < 0: return
        newIdx = min(len(self.ctrlNames)-1, selIdx + 1)

        self.moveObject(selIdx, newIdx)

    def OnBtokButton(self, event):
        self.EndModal(wxID_OK)

    def OnBtcancelButton(self, event):
        self.EndModal(wxID_CANCEL)

    def moveObject(self, selIdx, newIdx):
        if selIdx != newIdx:
            lbSel = newIdx
            if newIdx > selIdx:
                newIdx, selIdx = selIdx, newIdx
            name = self.ctrlNames[selIdx]
            newName = self.ctrlNames[newIdx]
            del self.ctrlNames[selIdx]
            self.allCtrlNames.remove(name)
            self.lbObjects.Delete(selIdx)

            self.ctrlNames.insert(newIdx, name)
            self.allCtrlNames.insert(self.allCtrlNames.index(newName), name)
            self.lbObjects.InsertItems([name], newIdx)

            self.lbObjects.SetSelection(lbSel)


if __name__ == '__main__':
    app = wxPySimpleApp()
    wxInitAllImageHandlers()

    dlg = CreationOrderDlg(None, [(0, 'ctrl1'), (1, 'ctrl2'), (5, 'ctrl3')],
                    [(0, 'ctrl1'), (1, 'ctrl2'), (2, 'ctrl4'), (3, 'ctrl5'), (5, 'ctrl3')])
    try:
        dlg.ShowModal()
        print zip(dlg.allCtrlIdxs, dlg.allCtrlNames)
    finally:
        dlg.Destroy()
