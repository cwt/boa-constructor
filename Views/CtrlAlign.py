#-----------------------------------------------------------------------------
# Name:        CtrlAlign.py
# Purpose:
#
# Author:      Riaan Booysen
#
# Created:     2000/09/11
# RCS-ID:      $Id$
# Copyright:   (c) 1999, 2000 Riaan Booysen
# Licence:     GPL
#-----------------------------------------------------------------------------
#Boa:Dialog:ControlAlignmentFrame

from wxPython.wx import *

# XXX Add 'Center in window' option

def create(parent):
    return ControlAlignmentFrame(parent)

[wxID_CONTROLALIGNMENTFRAME, wxID_CONTROLALIGNMENTFRAMECANCELBTN, wxID_CONTROLALIGNMENTFRAMEOKBTN, wxID_CONTROLALIGNMENTFRAMEPANEL1, wxID_CONTROLALIGNMENTFRAMERADIOBOX1, wxID_CONTROLALIGNMENTFRAMERADIOBOX2] = map(lambda _init_ctrls: wxNewId(), range(6))

class ControlAlignmentFrame(wxDialog):
    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wxDialog.__init__(self, id = wxID_CONTROLALIGNMENTFRAME, name = 'ControlAlignmentFrame', parent = prnt, pos = wxPoint(341, 140), size = wxSize(328, 219), style = wxDEFAULT_DIALOG_STYLE, title = 'Alignment')
        self._init_utils()
        self.SetClientSize(wxSize(320, 192))

        self.panel1 = wxPanel(id = wxID_CONTROLALIGNMENTFRAMEPANEL1, name = 'panel1', parent = self, pos = wxPoint(0, 0), size = wxSize(320, 192), style = wxTAB_TRAVERSAL)

        self.radioBox1 = wxRadioBox(choices = ['No change', 'Left sides', 'Centers', 'Right sides', 'Space equally'], id = wxID_CONTROLALIGNMENTFRAMERADIOBOX1, label = 'Horizontal', majorDimension = 1, name = 'radioBox1', parent = self.panel1, point = wxPoint(8, 8), size = wxSize(144, 144), style = wxRA_SPECIFY_COLS, validator = wxDefaultValidator)

        self.okBtn = wxButton(id = wxID_CONTROLALIGNMENTFRAMEOKBTN, label = 'OK', name = 'okBtn', parent = self.panel1, pos = wxPoint(160, 160), size = wxSize(72, 24), style = 0)
        EVT_BUTTON(self.okBtn, wxID_CONTROLALIGNMENTFRAMEOKBTN, self.OnOkbtnButton)

        self.cancelBtn = wxButton(id = wxID_CONTROLALIGNMENTFRAMECANCELBTN, label = 'Cancel', name = 'cancelBtn', parent = self.panel1, pos = wxPoint(240, 160), size = wxSize(72, 24), style = 0)
        EVT_BUTTON(self.cancelBtn, wxID_CONTROLALIGNMENTFRAMECANCELBTN, self.OnCancelbtnButton)

        self.radioBox2 = wxRadioBox(choices = ['No change', 'Tops', 'Centers', 'Bottoms', 'Space equally'], id = wxID_CONTROLALIGNMENTFRAMERADIOBOX2, label = 'Vertical', majorDimension = 1, name = 'radioBox2', parent = self.panel1, point = wxPoint(160, 8), size = wxSize(152, 144), style = wxRA_SPECIFY_COLS, validator = wxDefaultValidator)

    def __init__(self, parent, selection):
        self._init_ctrls(parent)
        self.choices = ('No change', 'No change')
        self.selection = selection
        self.Centre(wxBOTH)

    def OnOkbtnButton(self, event):
        hor = 0; ver = 1
        self.choices = (self.radioBox1.GetStringSelection(), self.radioBox2.GetStringSelection())

        selIdx = 0
        if len(self.selection):
            firstSel = self.selection[0]
            lastSel = self.selection[-1]
            firstSelPos = firstSel.position
            lastSelPos = lastSel.position
            selSize = len(self.selection)
        for sel in self.selection:
            domove = false
            newX, newY = sel.position.x, sel.position.y

            if self.choices[hor] == 'Left sides':
                if sel != firstSel:
                    domove = true
                    newX = firstSelPos.x
            elif self.choices[hor] == 'Centers':
                if sel != firstSel:
                    domove = true
                    newX = firstSelPos.x + firstSel.size.x / 2 - sel.size.x / 2
            elif self.choices[hor] == 'Right sides':
                if sel != firstSel:
                    domove = true
                    newX = firstSelPos.x + firstSel.size.x - sel.size.x
            elif self.choices[hor] == 'Space equally':
                if sel != firstSel and sel != lastSel:
                    domove = true
                    newX = (lastSelPos.x - firstSelPos.x) / (selSize-1) * selIdx \
                           + firstSelPos.x
#            elif self.choices[hor] == 'Center in window': pass # not implemented

            if self.choices[ver] == 'Tops':
                if sel != firstSel:
                    domove = true
                    newY = firstSelPos.y
            elif self.choices[ver] == 'Centers':
                if sel != firstSel:
                    domove = true
                    newY = firstSelPos.y + firstSel.size.y / 2 - sel.size.y / 2
            elif self.choices[ver] == 'Bottoms':
                if sel != firstSel:
                    domove = true
                    newY = firstSelPos.y + firstSel.size.y - sel.size.y
            elif self.choices[ver] == 'Space equally':
                if sel != firstSel and sel != lastSel:
                    domove = true
                    newY = (lastSelPos.y - firstSelPos.y) / (selSize-1) * selIdx \
                           + firstSelPos.y
#            elif self.choices[ver] == 'Center in window': pass

            if domove:
                sel.position  = wxPoint(newX, newY)
                sel.dragging = true
                sel.moveRelease()
                sel.positionUpdate()

            selIdx = selIdx + 1

        self.EndModal(wxOK)

    def OnCancelbtnButton(self, event):
        self.EndModal(wxCANCEL)
